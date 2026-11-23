from agents.onboarding_planning.dependency_rules import (
    assess_task_dependencies,
)
from agents.onboarding_planning.schemas import (
    OnboardingMilestone,
    OnboardingPlan,
    OnboardingTask,
)


def test_valid_dependency():
    plan = OnboardingPlan(
        deal_id="DEAL-123",
        milestones=[
            OnboardingMilestone(
                milestone_id="M-001",
                title="Discovery",
                tasks=[
                    OnboardingTask(
                        task_id="TASK-001",
                        title="Confirm scope",
                    ),
                    OnboardingTask(
                        task_id="TASK-002",
                        title="Prepare plan",
                        dependencies=["TASK-001"],
                    ),
                ],
            )
        ],
    )

    result = assess_task_dependencies(plan)

    assert len(result["valid_dependencies"]) == 1
    assert result["has_dependency_issues"] is False


def test_missing_dependency():
    plan = OnboardingPlan(
        deal_id="DEAL-123",
        milestones=[
            OnboardingMilestone(
                milestone_id="M-001",
                title="Discovery",
                tasks=[
                    OnboardingTask(
                        task_id="TASK-001",
                        title="Prepare plan",
                        dependencies=["TASK-999"],
                    ),
                ],
            )
        ],
    )

    result = assess_task_dependencies(plan)

    assert len(result["missing_dependencies"]) == 1
    assert result["has_dependency_issues"] is True


def test_self_dependency():
    plan = OnboardingPlan(
        deal_id="DEAL-123",
        milestones=[
            OnboardingMilestone(
                milestone_id="M-001",
                title="Discovery",
                tasks=[
                    OnboardingTask(
                        task_id="TASK-001",
                        title="Prepare plan",
                        dependencies=["TASK-001"],
                    ),
                ],
            )
        ],
    )

    result = assess_task_dependencies(plan)

    assert len(result["self_dependencies"]) == 1
    assert result["has_dependency_issues"] is True