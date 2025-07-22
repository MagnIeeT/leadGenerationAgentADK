"""Pydantic schemas for the Lead Generation workflow."""

from pydantic import BaseModel, Field
from typing import List

class Lead(BaseModel):
    """The structure of a single potential lead."""
    company_name: str = Field(description="The name of the company.")
    country_of_origin: str = Field(description="The country where the company is headquartered.")
    business_description: str = Field(description="A brief, one-sentence description of the company's business.")

class LeadFinderOutput(BaseModel):
    """The structure of the final output from the Lead Finder Agent."""
    potential_leads: List[Lead] = Field(description="A list of potential leads that match the criteria.")

class LeadSignalAnalyzerOutput(BaseModel):
    """The structure of the output from the Lead Signal Analyzer Agent."""
    summary: str = Field(description="A summary of the pre-investment signals found for the lead.")
    sources: List[str] = Field(description="A list of source URLs to support the findings.")
