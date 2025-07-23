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

"""Intent Extractor Agent - Extracts country, industry, stage, and intent from user queries."""

import os
from google.adk.agents import LlmAgent
from .schemas import IntentExtractionResult

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from .prompt import INTENT_EXTRACTOR_PROMPT


# Create intent extractor agent
intent_extractor_agent = LlmAgent(
    name="intent_extractor_agent",
    model=os.getenv("LEAD_GEN_TRIAGE_MODEL", "gemini-2.0-flash"),
    instruction=INTENT_EXTRACTOR_PROMPT,
    output_schema=IntentExtractionResult,
    output_key="intent_extraction_result",
    description="Extracts user intent, country, industry, and conversation stage from queries",
)
