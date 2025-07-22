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
