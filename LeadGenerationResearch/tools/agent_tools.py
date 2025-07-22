"""Agents to be used as tools by the main Lead Generation Agent."""

from google.adk.tools.agent_tool import AgentTool
from ..sub_agents.intent_extractor.agent import intent_extractor_agent
from ..sub_agents.pattern_discovery.agent import pattern_discovery_agent
from ..sub_agents.lead_generation.agent import lead_generation_agent

agent_tools = [
    AgentTool(agent=intent_extractor_agent),
    AgentTool(agent=pattern_discovery_agent),
    AgentTool(agent=lead_generation_agent),
]
