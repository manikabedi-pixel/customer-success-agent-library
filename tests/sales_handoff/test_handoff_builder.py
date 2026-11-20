from unittest.mock import patch, MagicMock

from agents.sales_handoff.hubspot_handoff import (
    build_handoff_draft,
)


def test_build_handoff_draft_without_api_calls():

    # Simulated HubSpot data
    fake_handoff_input = {
        "deal_id": "TEST-001",
        "deal_name": "Test Enterprise Deal",
        "deal_amount": "72000",
        "deal_stage": "closedwon",
        "company": {
            "company_id": "COMPANY-001",
            "name": "Test Software",
        },
        "stakeholders": [],
        "source_notes": [
            {
                "source_id": "NOTE-001",
                "source_type": "hubspot_note",
                "timestamp": "2026-01-01T00:00:00Z",
                "text": (
                    "The technical implementation owner has not yet "
                    "been identified. "
                    "The exact dashboard scope remains undefined."
                ),
            }
        ],
    }

    # Simulated AI-extracted facts
    fake_facts = [
        {
            "category": "stakeholder",
            "value": "Technical implementation owner not identified",
            "status": "missing",
            "evidence": (
                "The technical implementation owner has not yet "
                "been identified."
            ),
            "requires_verification": True,
        },
        {
            "category": "business_objective",
            "value": "Dashboard scope undefined",
            "status": "missing",
            "evidence": "The exact dashboard scope remains undefined.",
            "requires_verification": True,
        },
    ]

    fake_extraction = MagicMock()
    fake_extraction.extracted_facts = []

    for fact in fake_facts:
        mock_fact = MagicMock()
        mock_fact.model_dump.return_value = fact
        mock_fact.evidence = fact["evidence"]
        fake_extraction.extracted_facts.append(mock_fact)

    with (
        patch(
            "agents.sales_handoff.hubspot_handoff.build_handoff_input",
            return_value=fake_handoff_input,
        ),
        patch(
            "agents.sales_handoff.hubspot_handoff.extract_sales_intelligence",
            return_value=fake_extraction,
        ),
        patch(
            "agents.sales_handoff.hubspot_handoff.validate_extraction_evidence",
            return_value=fake_extraction,
        ),
    ):
        draft = build_handoff_draft("TEST-001")

    # Validate deal information
    assert draft["deal"]["deal_id"] == "TEST-001"
    assert draft["customer"]["name"] == "Test Software"

    # Validate extracted facts
    assert len(draft["sales_intelligence"]) == 2

    # Validate source attribution
    for fact in draft["sales_intelligence"]:
        assert fact["source_note_ids"] == ["NOTE-001"]

    # Validate missing information
    assert "Technical implementation owner not identified" in (
        draft["missing_information"]
    )
    assert "Executive dashboard scope is undefined" in (
        draft["missing_information"]
    )

    # Validate safety controls
    assert draft["requires_human_review"] is True
    assert draft["status"] == "draft"

def test_rejects_facts_without_source_evidence():
    """
    A fact without matching source evidence must not
    appear in the final handoff.
    """

    fake_handoff_input = {
        "deal_id": "TEST-002",
        "deal_name": "Evidence Safety Test",
        "deal_amount": "50000",
        "deal_stage": "closedwon",
        "company": {
            "company_id": "COMPANY-002",
            "name": "Example Software",
        },
        "stakeholders": [],
        "source_notes": [
            {
                "source_id": "NOTE-002",
                "source_type": "hubspot_note",
                "timestamp": "2026-01-01T00:00:00Z",
                "text": (
                    "The customer requested Salesforce integration."
                ),
            }
        ],
    }

    # Simulated AI output containing one supported fact
    # and one invented commitment.
    fake_facts = [
        {
            "category": "integration",
            "value": "Salesforce integration requested",
            "status": "customer_requested",
            "evidence": (
                "The customer requested Salesforce integration."
            ),
            "requires_verification": True,
        },
        {
            "category": "timeline",
            "value": "Implementation guaranteed within two weeks",
            "status": "confirmed",
            "evidence": (
                "Implementation guaranteed within two weeks."
            ),
            "requires_verification": False,
        },
    ]

    fake_extraction = MagicMock()
    fake_extraction.extracted_facts = []

    for fact in fake_facts:
        mock_fact = MagicMock()
        mock_fact.model_dump.return_value = fact
        mock_fact.evidence = fact["evidence"]
        fake_extraction.extracted_facts.append(mock_fact)

    with (
        patch(
            "agents.sales_handoff.hubspot_handoff.build_handoff_input",
            return_value=fake_handoff_input,
        ),
        patch(
            "agents.sales_handoff.hubspot_handoff.extract_sales_intelligence",
            return_value=fake_extraction,
        ),
        patch(
            "agents.sales_handoff.hubspot_handoff.validate_extraction_evidence",
            return_value=fake_extraction,
        ),
    ):
        draft = build_handoff_draft("TEST-002")

    # Only the supported fact should survive.
    assert len(draft["sales_intelligence"]) == 1

    fact = draft["sales_intelligence"][0]

    assert fact["category"] == "integration"
    assert fact["status"] == "customer_requested"
    assert fact["source_note_ids"] == ["NOTE-002"]

    # The invented implementation commitment must be absent.
    assert not any(
        "guaranteed within two weeks" in item["value"].lower()
        for item in draft["sales_intelligence"]
    )

    # Human review must still be required.
    assert draft["requires_human_review"] is True
    assert draft["status"] == "draft"