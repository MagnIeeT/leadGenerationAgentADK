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
