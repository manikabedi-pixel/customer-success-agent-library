import pytest

from agents.onboarding_coordinator.ai_validation import (
    validate_coordination_recommendations,
)


ISSUES = [
    {
        "task_id": "TASK-001",
        "issue_type": "missing_owner",
        "description": "Task has no owner.",
    },
    {
        "task_id": "TASK-002",
        "issue_type": "missing_due_date",
        "description": "Task has no due date.",
    },
]


def make_recommendation():
    return {
        "task_id": "TASK-001",
        "issue_type": "missing_owner",
        "recommended_action": "Confirm task ownership.",
        "rationale": "No owner is assigned.",
        "requires_human_review": True,
    }


def test_valid_recommendation():
    result = validate_coordination_recommendations(
        {"recommendations": [make_recommendation()]},
        ISSUES,
    )

    assert len(result) == 1
    assert result[0]["approved"] is False


def test_unknown_task_rejected():
    recommendation = make_recommendation()
    recommendation["task_id"] = "TASK-999"

    with pytest.raises(ValueError, match="unknown issue"):
        validate_coordination_recommendations(
            {"recommendations": [recommendation]},
            ISSUES,
        )


def test_unknown_issue_type_rejected():
    recommendation = make_recommendation()
    recommendation["issue_type"] = "overdue"

    with pytest.raises(ValueError, match="unknown issue"):
        validate_coordination_recommendations(
            {"recommendations": [recommendation]},
            ISSUES,
        )


def test_missing_action_rejected():
    recommendation = make_recommendation()
    recommendation["recommended_action"] = ""

    with pytest.raises(ValueError, match="action"):
        validate_coordination_recommendations(
            {"recommendations": [recommendation]},
            ISSUES,
        )


def test_missing_rationale_rejected():
    recommendation = make_recommendation()
    recommendation["rationale"] = ""

    with pytest.raises(ValueError, match="rationale"):
        validate_coordination_recommendations(
            {"recommendations": [recommendation]},
            ISSUES,
        )


def test_human_review_required():
    recommendation = make_recommendation()
    recommendation["requires_human_review"] = False

    with pytest.raises(ValueError, match="human review"):
        validate_coordination_recommendations(
            {"recommendations": [recommendation]},
            ISSUES,
        )


def test_duplicate_recommendation_rejected():
    recommendation = make_recommendation()

    with pytest.raises(ValueError, match="Duplicate"):
        validate_coordination_recommendations(
            {
                "recommendations": [
                    recommendation,
                    recommendation,
                ]
            },
            ISSUES,
        )


def test_unexpected_fields_removed():
    recommendation = make_recommendation()
    recommendation["execute_now"] = True

    result = validate_coordination_recommendations(
        {"recommendations": [recommendation]},
        ISSUES,
    )

    assert "execute_now" not in result[0]
    assert result[0]["approved"] is False