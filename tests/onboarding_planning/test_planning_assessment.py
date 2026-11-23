from agents.onboarding_planning.planning_assessment import (
    assess_onboarding_plan,
)
from agents.onboarding_planning.schemas import (
    OnboardingMilestone,
    OnboardingPlan,
    OnboardingTask,
)


def test_assessment_identifies_missing_owners_and_dates():
    plan = OnboardingPlan(
        deal_id="DEAL-123",
        milestones=[
            OnboardingMilestone(
                milestone_id="M-001",
                title="Discovery",
                tasks=[
                    OnboardingTask(
                        task_id="TASK-001",
                        title="Confirm integration scope",
                    )
                ],
            )
        ],
    )

    result = assess_onboarding_plan(plan, {})

    assert result["total_tasks"] == 1
    assert len(result["tasks_without_owners"]) == 1
    assert len(result["tasks_without_due_dates"]) == 1
    assert result["approved"] is False
    assert result["can_execute_onboarding"] is False


def test_assessment_preserves_handoff_risks():
    plan = OnboardingPlan(deal_id="DEAL-123")

    handoff = {
        "onboarding_risks": [
            {
                "description": "Migration scope unclear",
                "reason": "Source data not assessed",
                "source_note_ids": ["NOTE-123"],
            }
        ]
    }

    result = assess_onboarding_plan(plan, handoff)

    assert len(result["onboarding_risks"]) == 1
    assert result["requires_human_review"] is True