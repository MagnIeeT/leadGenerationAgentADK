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
Lead Generation Orchestrator Agent and its sub-components.
"""

import os
from typing import AsyncGenerator
from google.adk.agents import (
    BaseAgent,
    LlmAgent,
    ParallelAgent,
    SequentialAgent,
)
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event
from google.adk.tools import google_search
from google.genai.types import Content, Part
from .prompt import (
    LEAD_FINDER_PROMPT,
    LEAD_SIGNAL_ANALYZER_PROMPT,
    REPORT_COMPILER_PROMPT,
)
from .schemas import LeadFinderOutput, LeadSignalAnalyzerOutput
from ..pattern_discovery.agent import validator_agent_template # Reuse the validator

# Lead Finder Agent
lead_finder_agent = LlmAgent(
    name="LeadFinderAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-2.5-pro"),
    instruction=LEAD_FINDER_PROMPT,
    tools=[google_search],
    output_key="lead_finder_output",
)

# Lead Formatter Agent (similar to the company formatter)
lead_formatter_agent = LlmAgent(
    name="LeadFormatterAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-2.0-flash"),
    instruction="Format the unstructured text from the Lead Finder into the `LeadFinderOutput` JSON schema.",
    output_schema=LeadFinderOutput,
    output_key="leads_found_structured",
)

# Lead Signal Analyzer Agent Template (Researcher)
lead_signal_analyzer_template = LlmAgent(
    name="LeadSignalAnalyzerAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-2.5-pro"),
    instruction=LEAD_SIGNAL_ANALYZER_PROMPT,
    tools=[google_search],
    output_key="lead_signal_analyzer_output", # Save unstructured output
)

# Lead Signal Formatter Agent Template (Formatter)
lead_signal_formatter_template = LlmAgent(
    name="LeadSignalFormatterAgent",
    model=os.getenv("GEN_FAST_MODEL", "gemini-2.0-flash"),
    instruction="""Format the following unstructured text from the Lead Signal Analyzer into the `LeadSignalAnalyzerOutput` JSON schema.

{unstructured_text}
""",
    output_schema=LeadSignalAnalyzerOutput,
    output_key="lead_analysis_findings", # Save structured output
)

# Report Compiler Agent
report_compiler_agent = LlmAgent(
    name="ReportCompilerAgent",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-2.5-pro"),
    instruction=REPORT_COMPILER_PROMPT,
)

# Report Orchestrator Agent
class ReportOrchestratorAgent(BaseAgent):
    """
    Gathers all the parallel lead research findings and formats them into a
    single string for the ReportCompilerAgent.
    """
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        all_findings = []
        leads_found_structured = ctx.session.state.get("leads_found_structured")
        if leads_found_structured:
            leads_list = leads_found_structured.get("potential_leads", [])
            for i, lead_data in enumerate(leads_list):
                validation_result = ctx.session.state.get(f"lead_validation_result_{i}")
                analysis_findings = ctx.session.state.get(f"lead_analysis_findings_{i}")

                if validation_result and validation_result.get("is_valid"):
                    finding_str = f"--- Lead: {lead_data.get('company_name')} ---\n"
                    if analysis_findings:
                        summary = analysis_findings.get('summary', 'No summary available.')
                        sources = analysis_findings.get('sources', [])
                        finding_str += f"Analysis Summary: {summary}\n"
                        finding_str += "Sources:\n" + "\n".join(f"- {source}" for source in sources)
                    else:
                        finding_str += "No analysis findings available.\n"
                    all_findings.append(finding_str)
        
        ctx.session.state["all_lead_findings"] = "\n\n".join(all_findings)
        yield Event(author=self.name, content=Content(parts=[Part(text="Lead findings consolidated.")]))

report_orchestrator_agent = ReportOrchestratorAgent(name="ReportOrchestrator")

# Lead Research Orchestrator Agent
class LeadResearchOrchestratorAgent(BaseAgent):
    """
    Dynamically creates and runs a parallel workflow to validate and analyze
    a list of potential leads.
    """
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        leads_found_structured = ctx.session.state.get("leads_found_structured")
        if not leads_found_structured:
            yield Event(author=self.name, content=Content(parts=[Part(text="No leads to analyze.")]))
            return

        leads_list = leads_found_structured.get("potential_leads", [])
        
        research_pipelines = []
        for i, lead_data in enumerate(leads_list):
            research_pipeline = SequentialAgent(
                name=f"LeadResearchPipeline_{i}",
                sub_agents=[
                    LlmAgent(
                        name=f"LeadValidator_{i}",
                        instruction=validator_agent_template.instruction.format(
                            company_to_validate=lead_data, **ctx.session.state
                        ),
                        model=validator_agent_template.model,
                        output_schema=validator_agent_template.output_schema,
                        output_key=f"lead_validation_result_{i}",
                    ),
                    LlmAgent(
                        name=f"LeadSignalAnalyzer_{i}",
                        instruction=lead_signal_analyzer_template.instruction.format(
                            company_data=lead_data, **ctx.session.state
                        ),
                        model=lead_signal_analyzer_template.model,
                        tools=lead_signal_analyzer_template.tools,
                        output_key=f"lead_signal_analyzer_output_{i}",
                    ),
                    LlmAgent(
                        name=f"LeadSignalFormatter_{i}",
                        instruction=lead_signal_formatter_template.instruction.format(
                            unstructured_text=f"{{lead_signal_analyzer_output_{i}}}"
                        ),
                        model=lead_signal_formatter_template.model,
                        output_schema=lead_signal_formatter_template.output_schema,
                        output_key=f"lead_analysis_findings_{i}",
                    ),
                ],
            )
            research_pipelines.append(research_pipeline)
        
        parallel_researcher = ParallelAgent(
            name="DynamicLeadResearcher",
            sub_agents=research_pipelines,
        )

        async for event in parallel_researcher.run_async(ctx):
            yield event

lead_research_orchestrator_agent = LeadResearchOrchestratorAgent(name="LeadResearchOrchestrator")

# Main Lead Generation Agent
lead_generation_agent = SequentialAgent(
    name="LeadGenerationAgent",
    sub_agents=[
        lead_finder_agent,
        lead_formatter_agent,
        lead_research_orchestrator_agent,
        report_orchestrator_agent,
        report_compiler_agent,
    ],
    description="Orchestrates the workflow for finding and qualifying new investment leads.",
)
