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



