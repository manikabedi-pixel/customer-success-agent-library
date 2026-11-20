from agents.sales_handoff.quality_recommendations import (
    generate_quality_recommendations,
)


def test_recommendations_from_customer_facts():
    draft = {
        "missing_information": [
            "Technical implementation owner not identified"
        ],
        "sales_intelligence": [
            {
                "status": "customer_requested",
                "value": "Salesforce integration requested",
                "evidence": "Customer requested Salesforce integration.",
                "source_note_ids": ["NOTE-001"],
            },
            {
                "status": "discussed_unconfirmed",
                "value": "Six-week implementation timeline",
                "evidence": "Timeline discussed but not agreed.",
                "source_note_ids": ["NOTE-001"],
            },
        ],
        "onboarding_risks": [
            {
                "description": "Implementation timeline is unconfirmed"
            }
        ],
    }

    recommendations = generate_quality_recommendations(draft)

    assert len(recommendations) == 4

    assert any(
        "Technical implementation owner" in item
        for item in recommendations
    )

    assert any(
        "Salesforce integration" in item
        for item in recommendations
    )

    assert any(
        "Six-week implementation timeline" in item
        for item in recommendations
    )


def test_empty_handoff_recommends_collecting_information():
    draft = {
        "missing_information": [],
        "sales_intelligence": [],
        "onboarding_risks": [],
    }

    recommendations = generate_quality_recommendations(draft)

    assert (
        "Collect and validate sales discovery information before handoff."
        in recommendations
    )


def test_missing_evidence_generates_recommendation():
    draft = {
        "missing_information": [],
        "sales_intelligence": [
            {
                "status": "confirmed",
                "value": "Improve reporting",
                "evidence": "",
                "source_note_ids": [],
            }
        ],
        "onboarding_risks": [],
    }

    recommendations = generate_quality_recommendations(draft)

    assert (
        "Verify source evidence for extracted sales intelligence."
        in recommendations
    )


def test_duplicate_recommendations_are_removed():
    draft = {
        "missing_information": [
            "Implementation owner missing",
            "Implementation owner missing",
        ],
        "sales_intelligence": [],
        "onboarding_risks": [],
    }

    recommendations = generate_quality_recommendations(draft)

    assert recommendations.count(
        "Resolve missing information: Implementation owner missing"
    ) == 1