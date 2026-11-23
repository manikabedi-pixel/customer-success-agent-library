from dataclasses import asdict

from agents.onboarding_planning.schemas import (
    OnboardingMilestone,
    OnboardingPlan,
    OnboardingTask,
)


def test_task_defaults_are_safe():
    task = OnboardingTask(
        task_id="TASK-001",
        title="Confirm implementation owner",
    )

    assert task.owner is None
    assert task.due_date is None
    assert task.dependencies == []
    assert task.source_references == []
    assert task.status == "proposed"


def test_milestone_contains_tasks():
    task = OnboardingTask(
        task_id="TASK-001",
        title="Schedule kickoff",
    )

    milestone = OnboardingMilestone(
        milestone_id="MILESTONE-001",
        title="Kickoff preparation",
        tasks=[task],
    )

    assert len(milestone.tasks) == 1
    assert milestone.tasks[0].title == "Schedule kickoff"


def test_plan_requires_human_review_by_default():
    plan = OnboardingPlan(deal_id="DEAL-123")

    assert plan.source_handoff_status == "unverified"
    assert plan.requires_human_review is True
    assert plan.approved is False


def test_plan_can_be_serialized_to_dictionary():
    plan = OnboardingPlan(
        deal_id="DEAL-123",
        customer_name="Example SaaS Customer",
        objectives=["Improve onboarding efficiency"],
    )

    result = asdict(plan)

    assert result["deal_id"] == "DEAL-123"
    assert result["objectives"] == [
        "Improve onboarding efficiency"
    ]
    assert result["milestones"] == []
    assert result["approved"] is False


def test_task_lists_are_not_shared_between_instances():
    first = OnboardingTask(
        task_id="TASK-001",
        title="First task",
    )
    second = OnboardingTask(
        task_id="TASK-002",
        title="Second task",
    )

    first.dependencies.append("TASK-000")

    assert second.dependencies == []