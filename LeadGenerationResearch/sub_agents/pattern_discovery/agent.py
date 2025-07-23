# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Pattern Discovery Orchestrator Agent and its sub-components.
"""
import os
from typing import AsyncGenerator
from google.adk.agents import (
    Agent,
    BaseAgent,
    LlmAgent,
    ParallelAgent,
    SequentialAgent
)
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools import google_search
from google.genai.types import Content, Part
from .prompt import (
    COMPANY_FINDER_PROMPT,
    FORMATTER_PROMPT,
    VALIDATOR_PROMPT,
    SIGNAL_SEARCHER_PROMPT,
    SYNTHESIZER_PROMPT,
)
from .schemas import CompanyFinderOutput, ValidationResult, SignalSearcherOutput

# Company Finder Agent
company_finder_agent = LlmAgent(
    name="CompanyFinderAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-2.5-pro"),
    instruction=COMPANY_FINDER_PROMPT,
    tools=[google_search],
    output_key="company_finder_output",
)

# Company Formatter Agent
company_formatter_agent = LlmAgent(
    name="CompanyFormatterAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-2.0-flash"),
    instruction=FORMATTER_PROMPT,
    output_schema=CompanyFinderOutput,
    output_key="companies_found_structured",
    description="Takes unstructured text about companies and formats it into a valid JSON object.",
)

# Validator Agent Template
validator_agent_template = LlmAgent(
    name="ValidatorAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-2.0-flash"),
    instruction=VALIDATOR_PROMPT,
    output_schema=ValidationResult,
    description="Validates a single company to ensure it is a foreign entity that has recently invested in the target market.",
)

# Signal Searcher Agent Template (Researcher)
signal_searcher_agent_template = LlmAgent(
    name="SignalSearcherAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-2.5-pro"),
    instruction=SIGNAL_SEARCHER_PROMPT,
    tools=[google_search],
    output_key="signal_searcher_output", # Save unstructured output
    description="Researches a single, validated company to find its pre-investment signals.",
)

# Signal Formatter Agent Template (Formatter)
signal_formatter_agent_template = LlmAgent(
    name="SignalFormatterAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-2.0-flash"),
    instruction="""Format the following unstructured text from the Signal Searcher into the `SignalSearcherOutput` JSON schema.

{unstructured_text}
""",
    output_schema=SignalSearcherOutput,
    output_key="research_findings", # Save structured output
)

# Pattern Synthesizer Agent
pattern_synthesizer_agent = LlmAgent(
    name="PatternSynthesizerAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-2.5-pro"),
    instruction=SYNTHESIZER_PROMPT,
    output_key="discovered_patterns",
    description="Analyzes research from multiple signal searchers and synthesizes the common patterns.",
)

# Synthesizer Orchestrator Agent
class SynthesizerOrchestratorAgent(BaseAgent):
    """
    Gathers all the parallel research findings and formats them into a single
    string for the PatternSynthesizerAgent.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        all_findings = []
        
        companies_found_structured = ctx.session.state.get("companies_found_structured")
        companies_list = []
        if companies_found_structured:
            companies_list = companies_found_structured.get("companies_found", [])

        if not companies_list:
            ctx.session.state["all_research_findings"] = "No companies were found to consolidate."
            yield Event(author=self.name, content=Content(parts=[Part(text="No research findings to consolidate.")]))
            return
        
        num_companies = len(companies_list)

        for i in range(num_companies):
            validation_result = ctx.session.state.get(f"validation_result_{i}")
            research_findings = ctx.session.state.get(f"research_findings_{i}")

            finding_str = f"--- Company {i+1} ---\n"
            if validation_result:
                finding_str += f"Validation: {'VALID' if validation_result.get('is_valid') else 'INVALID'}\n"
                finding_str += f"Reasoning: {validation_result.get('reasoning')}\n"
            
            if research_findings:
                # The research_findings object is now a dictionary.
                finding_str += f"Research Summary: {research_findings.get('summary')}\n"
                finding_str += f"Sources: {', '.join(research_findings.get('sources', []))}\n"
            
            all_findings.append(finding_str)
        
        # Save the consolidated findings to a new state variable.
        ctx.session.state["all_research_findings"] = "\n".join(all_findings)
        
        yield Event(author=self.name, content=Content(parts=[Part(text="Research findings consolidated.")]))

synthesizer_orchestrator_agent = SynthesizerOrchestratorAgent(name="SynthesizerOrchestrator")

# Research Orchestrator Agent (Replaces Validation & Signal Research Orchestrators)
class ResearchOrchestratorAgent(BaseAgent):
    """
    Dynamically creates and runs a parallel workflow to validate and research
    a list of companies.
    """

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        companies_found_structured = ctx.session.state.get("companies_found_structured")
        if not companies_found_structured:
            yield Event(author=self.name, content=Content(parts=[Part(text="No companies to research.")]))
            return

        companies_list = companies_found_structured.get("companies_found", [])
        
        research_pipelines = []
        for i, company_data in enumerate(companies_list):
            # For each company, create a simple sequential pipeline of (Validator -> Searcher -> Formatter).
            research_pipeline = SequentialAgent(
                name=f"CompanyResearchPipeline_{i}",
                sub_agents=[
                    LlmAgent(
                        name=f"ValidatorAgent_{i}",
                        instruction=validator_agent_template.instruction.format(
                            company_to_validate=company_data, **ctx.session.state
                        ),
                        model=validator_agent_template.model,
                        output_schema=validator_agent_template.output_schema,
                        output_key=f"validation_result_{i}",
                    ),
                    LlmAgent(
                        name=f"SignalSearcher_{i}",
                        instruction=signal_searcher_agent_template.instruction.format(
                            company_data=company_data, **ctx.session.state
                        ),
                        model=signal_searcher_agent_template.model,
                        tools=signal_searcher_agent_template.tools,
                        output_key=f"signal_searcher_output_{i}",
                    ),
                    LlmAgent(
                        name=f"SignalFormatter_{i}",
                        instruction=signal_formatter_agent_template.instruction.format(
                            unstructured_text=f"{{signal_searcher_output_{i}}}"
                        ),
                        model=signal_formatter_agent_template.model,
                        output_schema=signal_formatter_agent_template.output_schema,
                        output_key=f"research_findings_{i}",
                    ),
                ],
            )
            research_pipelines.append(research_pipeline)
        
        # Create a new, temporary ParallelAgent to run all the pipelines.
        parallel_researcher = ParallelAgent(
            name="DynamicParallelResearcher",
            sub_agents=research_pipelines,
        )

        async for event in parallel_researcher.run_async(ctx):
            yield event

research_orchestrator_agent = ResearchOrchestratorAgent(name="ResearchOrchestrator")

# Main Pattern Discovery Agent
pattern_discovery_agent = SequentialAgent(
    name="PatternDiscoveryAgent",
    sub_agents=[
        company_finder_agent,
        company_formatter_agent,
        research_orchestrator_agent,
        synthesizer_orchestrator_agent,
        pattern_synthesizer_agent,
    ],
    description="Orchestrates the technical steps of discovering investment patterns."
)
