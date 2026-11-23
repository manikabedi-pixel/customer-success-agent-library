from datetime import date
from typing import Any

from agents.onboarding_coordinator.schemas import (
    CoordinationState,
)


def detect_task_issues(
    state: CoordinationState,
    today: date | None = None,
) -> list[dict[str, Any]]:
    """
    Detect onboarding task issues.

    This function is read-only and does not modify task status.
    """

    if today is None:
        today = date.today()

    tasks = [
        task
        for milestone in state.milestones
        for task in milestone.tasks
    ]

    task_lookup = {}

    for task in tasks:
        task_lookup.setdefault(task.task_id, []).append(task)

    issues = []

    for task in tasks:

        if task.status == "blocked":
            issues.append({
                "task_id": task.task_id,
                "issue_type": "blocked",
                "description": "Task is reported as blocked.",
                "requires_human_review": True,
            })

        if not isinstance(task.owner, str) or not task.owner.strip():
            issues.append({
                "task_id": task.task_id,
                "issue_type": "missing_owner",
                "description": "Task has no assigned owner.",
                "requires_human_review": True,
            })

        if not task.due_date:
            issues.append({
                "task_id": task.task_id,
                "issue_type": "missing_due_date",
                "description": "Task has no due date.",
                "requires_human_review": True,
            })

        else:
            try:
                due_date = date.fromisoformat(task.due_date)

            except (TypeError, ValueError):
                issues.append({
                    "task_id": task.task_id,
                    "issue_type": "invalid_due_date",
                    "description": "Task due date is invalid.",
                    "requires_human_review": True,
                })

            else:
                if (
                    due_date < today
                    and task.status != "completed"
                ):
                    issues.append({
                        "task_id": task.task_id,
                        "issue_type": "overdue",
                        "description": (
                            f"Task due date {due_date.isoformat()} "
                            "has passed."
                        ),
                        "requires_human_review": True,
                    })

        for dependency_id in task.dependencies:

            matches = task_lookup.get(dependency_id, [])

            if dependency_id == task.task_id:
                issue_type = "self_dependency"
                description = "Task depends on itself."

            elif len(matches) == 0:
                issue_type = "missing_dependency"
                description = (
                    f"Dependency {dependency_id} does not exist."
                )

            elif len(matches) > 1:
                issue_type = "ambiguous_dependency"
                description = (
                    f"Dependency {dependency_id} is not unique."
                )

            else:
                continue

            issues.append({
                "task_id": task.task_id,
                "issue_type": issue_type,
                "description": description,
                "requires_human_review": True,
            })

    return issues


def summarize_task_issues(
    issues: list[dict[str, Any]],
) -> dict[str, Any]:
    """Summarize detected task issues."""

    issue_counts = {}

    for issue in issues:
        issue_type = issue["issue_type"]

        issue_counts[issue_type] = (
            issue_counts.get(issue_type, 0) + 1
        )

    return {
        "total_issues": len(issues),
        "issue_counts": issue_counts,
        "affected_task_ids": sorted({
            issue["task_id"]
            for issue in issues
        }),
        "requires_human_review": bool(issues),
    }