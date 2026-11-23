from unittest.mock import patch

from agents.onboarding_coordinator.ai_coordination_workflow import (
    run_ai_coordination,
)


ISSUES = [
    {
        "task_id": "TASK-001",
        "issue_type": "missing_owner",
        "description": "Task has no owner.",
    }
]


def test_ai_workflow_success():
    ai_response = {
        "recommendations": [
            {
                "task_id": "TASK-001",
                "issue_type": "missing_owner",
                "recommended_action": "Confirm owner.",
                "rationale": "Owner is missing.",
                "requires_human_review": True,
            }
        ]
    }

    with patch(
        "agents.onboarding_coordinator.ai_coordination_workflow."
        "generate_coordination_recommendations",
        return_value=ai_response,
    ):
        result = run_ai_coordination(ISSUES)

    assert result["status"] == "completed"
    assert len(result["recommendations"]) == 1
    assert result["approved"] is False


def test_ai_workflow_validation_failure():
    with patch(
        "agents.onboarding_coordinator.ai_coordination_workflow."
        "generate_coordination_recommendations",
        return_value={"recommendations": "invalid"},
    ):
        result = run_ai_coordination(ISSUES)

    assert result["status"] == "failed"
    assert result["recommendations"] == []


def test_ai_workflow_generation_failure():
    with patch(
        "agents.onboarding_coordinator.ai_coordination_workflow."
        "generate_coordination_recommendations",
        side_effect=ValueError("AI unavailable"),
    ):
        result = run_ai_coordination(ISSUES)

    assert result["status"] == "failed"
    assert result["approved"] is False


def test_ai_workflow_skips_empty_issues():
    result = run_ai_coordination([])

    assert result["status"] == "skipped"
    assert result["recommendations"] == []