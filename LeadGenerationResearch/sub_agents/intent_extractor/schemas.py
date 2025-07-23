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

"""Pydantic schemas for the Intent Extractor Agent."""

from pydantic import BaseModel, Field
from typing import Optional, Literal

class IntentExtractionResult(BaseModel):
    country: Optional[str] = Field(
        default=None,
        description="Target country for lead generation. Examples: 'Thailand', 'Singapore', 'Malaysia'"
    )
    industry: Optional[str] = Field(
        default=None,
        description="Target industry sector. Examples: 'fintech', 'healthcare', 'SaaS', 'e-commerce'"
    )
    stage: Literal["pattern_discovery", "lead_generation", "follow_up", "chitchat"] = Field(
        description="Current conversation stage determining next action"
    )
    intent: Literal["find_leads", "find_patterns", "company_research", "general_chat"] = Field(
        description="User's primary intent or goal"
    )
    confidence: float = Field(
        description="Confidence score for the extraction (0.0 to 1.0)"
    )
    reasoning: str = Field(
        description="Brief explanation of the extraction decisions"
    )
