from typing import Any

from agents.onboarding_planning.dependency_rules import (
    assess_task_dependencies,
)
from agents.onboarding_planning.risk_rules import (
    normalize_onboarding_risks,
)
from agents.onboarding_planning.schemas import OnboardingPlan


def assess_onboarding_plan(
    plan: OnboardingPlan,
    handoff: dict[str, Any],
) -> dict[str, Any]:
    """
    Assess a draft onboarding plan.

    Does not modify or approve the plan.
    """

    tasks = [
        task
        for milestone in plan.milestones
        for task in milestone.tasks
    ]

    tasks_without_owners = [
        {
            "task_id": task.task_id,
            "title": task.title,
        }
        for task in tasks
        if not task.owner
    ]

    tasks_without_due_dates = [
        {
            "task_id": task.task_id,
            "title": task.title,
        }
        for task in tasks
        if not task.due_date
    ]

    dependencies = assess_task_dependencies(plan)

    risks = normalize_onboarding_risks(handoff)

    return {
        "deal_id": plan.deal_id,
        "total_tasks": len(tasks),
        "tasks_without_owners": tasks_without_owners,
        "tasks_without_due_dates": tasks_without_due_dates,
        "dependency_assessment": dependencies,
        "onboarding_risks": risks,
        "missing_information": plan.missing_information.copy(),
        "requires_human_review": True,
        "approved": False,
        "can_execute_onboarding": False,
    }