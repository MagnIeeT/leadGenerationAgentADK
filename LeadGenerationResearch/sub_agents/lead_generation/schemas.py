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
