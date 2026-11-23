from unittest.mock import patch

from agents.onboarding_planning.ai_planning_workflow import (
    prepare_ai_planning_suggestions,
)


def test_empty_requirements_skip_ai():
    result = prepare_ai_planning_suggestions({
        "requirements": [],
    })

    assert result["ai_status"] == "skipped"
    assert result["suggestions"] == []


def test_ai_failure_returns_safe_fallback():
    extracted = {
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "description": "CRM integration",
            }
        ],
    }

    with patch(
        "agents.onboarding_planning.ai_planning_workflow."
        "generate_ai_planning_suggestions",
        side_effect=RuntimeError("API unavailable"),
    ):
        result = prepare_ai_planning_suggestions(
            extracted
        )

    assert result["ai_status"] == "failed"
    assert result["suggestions"] == []
    assert result["requires_human_review"] is True


def test_valid_ai_response_is_preserved():
    extracted = {
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "description": "CRM integration",
            }
        ],
    }

    mock_response = [
        {
            "requirement_id": "REQ-001",
            "suggested_activity": "Confirm integration scope",
            "rationale": "Integration requirement identified",
            "requires_human_review": True,
        }
    ]

    with patch(
        "agents.onboarding_planning.ai_planning_workflow."
        "generate_ai_planning_suggestions",
        return_value=mock_response,
    ):
        result = prepare_ai_planning_suggestions(
            extracted
        )

    assert result["ai_status"] == "completed"
    assert len(result["suggestions"]) == 1