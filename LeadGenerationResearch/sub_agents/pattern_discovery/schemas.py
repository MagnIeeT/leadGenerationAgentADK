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

"""Pydantic schemas for the Pattern Discovery workflow."""

from pydantic import BaseModel, Field
from typing import List, Optional

class Company(BaseModel):
    """The structure of a single company found by the agent."""
    company_name: str = Field(description="The name of the company.")
    country_of_origin: str = Field(description="The country where the company is headquartered.")
    investment_type: str = Field(description="The nature of the investment (e.g., new office, acquisition).")
    investment_date: str = Field(description="The date of the investment (e.g., 2023-Q4).")
    source_url: str = Field(description="The URL of the source article or press release.")
    business_description: str = Field(description="A brief, one-sentence description of the company's business.")

class CompanyFinderOutput(BaseModel):
    """The structure of the final output from the Company Finder Agent."""
    companies_found: List[Company] = Field(description="A list of companies that match the criteria.")

class ValidationResult(BaseModel):
    """The structure of the validation result for a single company."""
    company_name: str = Field(description="The name of the company.")
    is_valid: bool = Field(description="True if the company meets all validation criteria.")
    reasoning: str = Field(description="A brief explanation of the validation decision.")
    corrected_country_of_origin: Optional[str] = Field(
        default=None,
        description="The corrected country of origin, if the original was wrong."
    )

class SignalSearcherOutput(BaseModel):
    """The structure of the output from the Signal Searcher Agent."""
    summary: str = Field(description="A summary of the pre-investment signals found.")
    sources: List[str] = Field(description="A list of source URLs to support the findings.")
