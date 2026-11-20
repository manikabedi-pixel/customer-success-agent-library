from agents.sales_handoff.readiness_assessment import (
    assess_onboarding_readiness,
)


def make_fact(status="confirmed", supported=True):
    return {
        "status": status,
        "value": "Improve executive reporting",
        "evidence": (
            "Customer confirmed reporting needs."
            if supported else ""
        ),
        "source_note_ids": (
            ["NOTE-001"] if supported else []
        ),
    }


def make_source_notes():
    return [
        {
            "note_id": "NOTE-001",
            "body": "Customer confirmed reporting needs.",
        }
    ]


def test_complete_handoff_ready_for_human_review():
    draft = {
        "sales_intelligence": [make_fact()],
        "missing_information": [],
        "source_notes": make_source_notes(),
    }

    result = assess_onboarding_readiness(draft)

    assert result["readiness"] == "Ready for human review"
    assert result["supported_facts"] == 1
    assert result["source_validation"]["valid"] is True
    assert result["approved"] is False
    assert result["requires_human_review"] is True


def test_missing_information_requires_clarification():
    draft = {
        "sales_intelligence": [make_fact()],
        "missing_information": [
            "Implementation owner missing"
        ],
        "source_notes": make_source_notes(),
    }

    result = assess_onboarding_readiness(draft)

    assert result["readiness"] == "Clarification required"
    assert len(result["reasons"]) == 1
    assert result["source_validation"]["valid"] is True


def test_unconfirmed_timeline_requires_clarification():
    draft = {
        "sales_intelligence": [
            make_fact(status="discussed_unconfirmed")
        ],
        "missing_information": [],
        "source_notes": make_source_notes(),
    }

    result = assess_onboarding_readiness(draft)

    assert result["readiness"] == "Clarification required"
    assert any(
        "unconfirmed" in reason
        for reason in result["reasons"]
    )
    assert result["source_validation"]["valid"] is True


def test_empty_handoff_has_insufficient_information():
    draft = {
        "sales_intelligence": [],
        "missing_information": [],
        "source_notes": [],
    }

    result = assess_onboarding_readiness(draft)

    assert result["readiness"] == "Insufficient information"
    assert result["supported_facts"] == 0
    assert result["approved"] is False


def test_unsupported_facts_have_insufficient_information():
    draft = {
        "sales_intelligence": [
            make_fact(supported=False)
        ],
        "missing_information": [],
        "source_notes": make_source_notes(),
    }

    result = assess_onboarding_readiness(draft)

    assert result["readiness"] == "Insufficient information"
    assert result["supported_facts"] == 0
    assert result["source_validation"]["valid"] is False


def test_partially_supported_handoff_requires_clarification():
    draft = {
        "sales_intelligence": [
            make_fact(supported=True),
            make_fact(supported=False),
        ],
        "missing_information": [],
        "source_notes": make_source_notes(),
    }

    result = assess_onboarding_readiness(draft)

    assert result["readiness"] == "Clarification required"
    assert result["supported_facts"] == 1
    assert result["total_facts"] == 2


def test_invalid_source_reference_requires_clarification():
    draft = {
        "sales_intelligence": [
            {
                "status": "confirmed",
                "value": "Salesforce integration requested",
                "evidence": "Customer requested Salesforce integration.",
                "source_note_ids": ["NOTE-999"],
            }
        ],
        "missing_information": [],
        "source_notes": make_source_notes(),
    }

    result = assess_onboarding_readiness(draft)

    assert result["readiness"] == "Clarification required"
    assert result["source_validation"]["valid"] is False
    assert result["approved"] is False
    assert result["requires_human_review"] is True


def test_missing_source_notes_prevents_ready_status():
    draft = {
        "sales_intelligence": [make_fact()],
        "missing_information": [],
        "source_notes": [],
    }

    result = assess_onboarding_readiness(draft)

    assert result["readiness"] == "Clarification required"
    assert result["source_validation"]["valid"] is False