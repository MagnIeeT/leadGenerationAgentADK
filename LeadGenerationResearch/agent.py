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

"""Lead Generation Agent v3 - Simplified Interactive Agent."""

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
import os
from google.adk.tools import get_user_choice


# Import agent components from their new, organized locations
from .tools.callbacks import before_agent_run, after_tool_run
from .tools.agent_tools import agent_tools
from .prompt import ROOT_AGENT_INSTRUCTION


# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

root_agent = Agent(
    name="InteractiveLeadGenerator",
    model=os.getenv("GEN_ADVANCED_MODEL", "gemini-2.5-pro"),
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[
        get_user_choice,
        *agent_tools,
    ],
    before_agent_callback=[before_agent_run],
    after_tool_callback=[after_tool_run],
)



