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
