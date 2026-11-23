import pytest

from agents.onboarding_planning.ai_validation import (
    validate_ai_suggestions,
)


REQUIREMENTS = [
    {
        "requirement_id": "REQ-001",
        "description": "CRM integration required",
    }
]


def test_valid_ai_suggestion():
    suggestions = [
        {
            "requirement_id": "REQ-001",
            "suggested_activity": "Confirm integration scope",
            "rationale": "Integration requirement identified",
            "requires_human_review": True,
        }
    ]

    result = validate_ai_suggestions(
        suggestions,
        REQUIREMENTS,
    )

    assert len(result) == 1
    assert result[0]["status"] == "proposed"


def test_unknown_requirement_rejected():
    suggestions = [
        {
            "requirement_id": "REQ-999",
            "suggested_activity": "Confirm integration",
            "rationale": "Integration requirement",
            "requires_human_review": True,
        }
    ]

    with pytest.raises(ValueError, match="Unknown"):
        validate_ai_suggestions(
            suggestions,
            REQUIREMENTS,
        )


def test_missing_human_review_rejected():
    suggestions = [
        {
            "requirement_id": "REQ-001",
            "suggested_activity": "Confirm integration",
            "rationale": "Integration requirement",
            "requires_human_review": False,
        }
    ]

    with pytest.raises(ValueError, match="human review"):
        validate_ai_suggestions(
            suggestions,
            REQUIREMENTS,
        )


def test_duplicate_requirement_rejected():
    suggestion = {
        "requirement_id": "REQ-001",
        "suggested_activity": "Confirm integration",
        "rationale": "Integration requirement",
        "requires_human_review": True,
    }

    with pytest.raises(ValueError, match="Duplicate"):
        validate_ai_suggestions(
            [suggestion, suggestion],
            REQUIREMENTS,
        )


def test_ai_cannot_add_unapproved_fields():
    suggestions = [
        {
            "requirement_id": "REQ-001",
            "suggested_activity": "Confirm integration",
            "rationale": "Integration requirement",
            "requires_human_review": True,
            "approved": True,
            "owner": "Customer Success Manager",
            "due_date": "2026-12-01",
        }
    ]

    result = validate_ai_suggestions(
        suggestions,
        REQUIREMENTS,
    )

    assert "approved" not in result[0]
    assert "owner" not in result[0]
    assert "due_date" not in result[0]