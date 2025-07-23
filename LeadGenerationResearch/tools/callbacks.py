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

"""Callbacks for the Lead Generation Agent."""

from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import get_user_choice
from google.adk.agents import LlmAgent
from datetime import datetime
from typing import Optional
from google.genai.types import Content

def before_agent_run(callback_context: CallbackContext) -> Optional[Content]:
    """A callback function to initialize and manage the conversation context."""
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    callback_context.state["current_time"] = current_time
    callback_context.state["current_year"] = datetime.now().year
    
    # Initialize default state values.
    if "country" not in callback_context.state:
        callback_context.state["country"] = ""
    if "industry" not in callback_context.state:
        callback_context.state["industry"] = ""
    if "stage" not in callback_context.state:
        callback_context.state["stage"] = "initial"
    if "k" not in callback_context.state:
        callback_context.state["k"] = None
    if "m" not in callback_context.state:
        callback_context.state["m"] = None
    
    return None

def after_tool_run(
    tool, args, tool_context: ToolContext, tool_response
) -> None:
    """A callback to process the output of key tools and update the state."""
    # Import agent and schema locally to avoid circular dependencies.
    from ..sub_agents.intent_extractor.agent import (
        intent_extractor_agent,
        IntentExtractionResult,
    )
    from ..sub_agents.pattern_discovery.agent import company_finder_agent, pattern_discovery_agent

    # Case 1: The tool that just ran was the intent extractor.
    if tool is intent_extractor_agent:
        extraction_result = tool_context.state.get("intent_extraction_result")
        if isinstance(extraction_result, IntentExtractionResult):
            if extraction_result.country:
                tool_context.state["country"] = extraction_result.country
            if extraction_result.industry:
                tool_context.state["industry"] = extraction_result.industry
            tool_context.state["stage"] = extraction_result.stage

    # Case 2: The tool that just ran was the pattern discovery agent.
    elif tool is pattern_discovery_agent:
        if tool_context.state.get("discovered_patterns"):
            tool_context.state["stage"] = "patterns_shown"

    # Case 3: The tool that just ran was the user choice tool.
    elif tool is get_user_choice:
        # The output of get_user_choice is the value the user selected.
        if tool_response:
            # The `get_user_choice` tool can be called for different reasons.
            # We use the `context` from the tool call to decide what to do.
            choice_context = args.get("context")
            if choice_context == "set_k_for_patterns":
                tool_context.state["k"] = tool_response
            elif choice_context == "confirm_lead_generation":
                if tool_response == "Yes, find leads":
                    tool_context.state["stage"] = "lead_generation"
                else:
                    # Reset the state to start over.
                    tool_context.state["stage"] = "initial"
                    tool_context.state["country"] = ""
                    tool_context.state["industry"] = ""
                    tool_context.state["k"] = None
            elif choice_context == "set_m_for_leads":
                tool_context.state["m"] = tool_response
