from typing import Any

from agents.onboarding_coordinator.schemas import (
    CoordinationMilestone,
    CoordinationState,
)


VALID_TASK_STATUSES = {
    "proposed",
    "not_started",
    "in_progress",
    "blocked",
    "completed",
}


def calculate_milestone_progress(
    milestone: CoordinationMilestone,
) -> dict[str, Any]:
    """
    Calculate reported milestone progress.

    This does not verify actual task completion.
    """

    total_tasks = len(milestone.tasks)

    status_counts = {
        status: 0
        for status in VALID_TASK_STATUSES
    }

    for task in milestone.tasks:
        if task.status not in VALID_TASK_STATUSES:
            raise ValueError(
                f"Invalid task status for {task.task_id}: "
                f"{task.status}"
            )

        status_counts[task.status] += 1

    completed_tasks = status_counts["completed"]
    blocked_tasks = status_counts["blocked"]

    completion_percentage = (
        round((completed_tasks / total_tasks) * 100, 2)
        if total_tasks
        else 0.0
    )

    return {
        "milestone_id": milestone.milestone_id,
        "title": milestone.title,
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "blocked_tasks": blocked_tasks,
        "status_counts": status_counts,
        "reported_completion_percentage": completion_percentage,
        "verified_completion_percentage": None,
        "completion_verified": False,
        "requires_human_review": True,
    }


def calculate_overall_progress(
    state: CoordinationState,
) -> dict[str, Any]:
    """
    Calculate overall reported onboarding progress.

    Task counts are used rather than averaging milestone
    percentages, so large and small milestones are weighted
    appropriately.
    """

    milestone_results = [
        calculate_milestone_progress(milestone)
        for milestone in state.milestones
    ]

    total_tasks = sum(
        result["total_tasks"]
        for result in milestone_results
    )

    completed_tasks = sum(
        result["completed_tasks"]
        for result in milestone_results
    )

    blocked_tasks = sum(
        result["blocked_tasks"]
        for result in milestone_results
    )

    completion_percentage = (
        round((completed_tasks / total_tasks) * 100, 2)
        if total_tasks
        else 0.0
    )

    return {
        "deal_id": state.deal_id,
        "total_milestones": len(state.milestones),
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "blocked_tasks": blocked_tasks,
        "reported_completion_percentage": completion_percentage,
        "verified_completion_percentage": None,
        "completion_verified": False,
        "milestones": milestone_results,
        "requires_human_review": True,
        "execution_authorized": state.execution_authorized,
    }


def find_milestones_requiring_attention(
    state: CoordinationState,
) -> list[dict[str, Any]]:
    """
    Identify milestones needing human attention.

    This function does not modify milestone or task statuses.
    """

    attention_items = []

    for milestone in state.milestones:
        progress = calculate_milestone_progress(milestone)

        missing_owner_ids = [
            task.task_id
            for task in milestone.tasks
            if not isinstance(task.owner, str)
            or not task.owner.strip()
        ]

        missing_due_date_ids = [
            task.task_id
            for task in milestone.tasks
            if not task.due_date
        ]

        reasons = []

        if progress["blocked_tasks"] > 0:
            reasons.append("blocked_tasks")

        if missing_owner_ids:
            reasons.append("missing_owners")

        if missing_due_date_ids:
            reasons.append("missing_due_dates")

        if progress["total_tasks"] == 0:
            reasons.append("no_tasks")

        if reasons:
            attention_items.append({
                "milestone_id": milestone.milestone_id,
                "title": milestone.title,
                "reasons": reasons,
                "missing_owner_task_ids": missing_owner_ids,
                "missing_due_date_task_ids": missing_due_date_ids,
                "blocked_tasks": progress["blocked_tasks"],
                "requires_human_review": True,
            })

    return attention_items