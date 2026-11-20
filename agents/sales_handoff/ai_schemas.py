from typing import Literal

from pydantic import BaseModel, Field


InformationStatus = Literal[
    "confirmed",
    "customer_requested",
    "discussed_unconfirmed",
    "missing",
]


class ExtractedFact(BaseModel):
    category: str = Field(
        description=(
            "Category such as business_objective, "
            "integration, migration, timeline, or stakeholder"
        )
    )

    value: str = Field(
        description="Information extracted from the sales notes"
    )

    status: InformationStatus = Field(
        description="Classification of the information"
    )

    evidence: str = Field(
        description=(
            "Exact supporting quotation from the provided "
            "sales notes. Empty string if no evidence exists."
        )
    )

    requires_verification: bool = Field(
        description=(
            "True when the information needs human confirmation"
        )
    )


class SalesIntelligenceExtraction(BaseModel):
    extracted_facts: list[ExtractedFact]

    missing_information: list[str]

    potential_risks: list[str]

    summary: str