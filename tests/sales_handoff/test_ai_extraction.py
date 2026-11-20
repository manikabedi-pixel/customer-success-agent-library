from agents.sales_handoff.ai_schemas import (
    ExtractedFact,
    SalesIntelligenceExtraction,
)

from agents.sales_handoff.extraction import (
    validate_extraction_evidence,
)


def test_valid_evidence_is_preserved():

    notes = [
        "The customer requested Salesforce integration."
    ]

    extraction = SalesIntelligenceExtraction(
        extracted_facts=[
            ExtractedFact(
                category="integration",
                value="Salesforce integration",
                status="customer_requested",
                evidence=(
                    "The customer requested Salesforce integration."
                ),
                requires_verification=True,
            )
        ],
        missing_information=[],
        potential_risks=[],
        summary="Customer requested Salesforce integration.",
    )

    result = validate_extraction_evidence(
        extraction,
        notes,
    )

    assert len(result.extracted_facts) == 1


def test_unsupported_evidence_is_rejected():

    notes = [
        "The customer requested Salesforce integration."
    ]

    extraction = SalesIntelligenceExtraction(
        extracted_facts=[
            ExtractedFact(
                category="timeline",
                value="Implementation guaranteed in 2 weeks",
                status="confirmed",
                evidence="Implementation guaranteed in 2 weeks",
                requires_verification=False,
            )
        ],
        missing_information=[],
        potential_risks=[],
        summary="Implementation guaranteed in 2 weeks.",
    )

    result = validate_extraction_evidence(
        extraction,
        notes,
    )

    assert len(result.extracted_facts) == 0


def test_missing_evidence_is_rejected():

    notes = [
        "The customer requested Salesforce integration."
    ]

    extraction = SalesIntelligenceExtraction(
        extracted_facts=[
            ExtractedFact(
                category="integration",
                value="Salesforce integration",
                status="confirmed",
                evidence="",
                requires_verification=False,
            )
        ],
        missing_information=[],
        potential_risks=[],
        summary="Salesforce integration confirmed.",
    )

    result = validate_extraction_evidence(
        extraction,
        notes,
    )

    assert len(result.extracted_facts) == 0