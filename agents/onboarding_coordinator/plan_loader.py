import json
from pathlib import Path
from typing import Any

from agents.onboarding_coordinator.schemas import (
    CoordinationMilestone,
    CoordinationState,
    CoordinationTask,
)


def load_onboarding_report(
    path: str | Path,
) -> dict[str, Any]:
    """
    Load an Agent #2 onboarding report.

    Imported approval claims are not trusted.
    """

    report_path = Path(path)

    if not report_path.is_file():
        raise FileNotFoundError(
            f"Onboarding report not found: {report_path}"
        )

    try:
        with report_path.open("r", encoding="utf-8") as file:
            report = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid onboarding report JSON: {error.msg}"
        ) from error

    if not isinstance(report, dict):
        raise ValueError(
            "Onboarding report must be a JSON object."
        )

    deal_id = report.get("deal_id")

    if not isinstance(deal_id, str) or not deal_id.strip():
        raise ValueError(
            "Onboarding report requires a valid deal_id."
        )

    plan = report.get("onboarding_plan")

    if not isinstance(plan, dict):
        raise ValueError(
            "Onboarding report requires onboarding_plan."
        )

    plan_deal_id = plan.get("deal_id")

    if plan_deal_id != deal_id:
        raise ValueError(
            "Report and onboarding plan deal IDs do not match."
        )

    milestones = plan.get("milestones")

    if not isinstance(milestones, list):
        raise ValueError(
            "Onboarding plan milestones must be a list."
        )

    return report


def convert_task(
    task: dict[str, Any],
) -> CoordinationTask:
    """Convert an Agent #2 task into an Agent #3 task."""

    if not isinstance(task, dict):
        raise ValueError("Task must be an object.")

    task_id = task.get("task_id")
    title = task.get("title")

    if not isinstance(task_id, str) or not task_id.strip():
        raise ValueError("Task requires a valid task_id.")

    if not isinstance(title, str) or not title.strip():
        raise ValueError("Task requires a valid title.")

    dependencies = task.get("dependencies", [])
    source_references = task.get("source_references", [])

    if not isinstance(dependencies, list):
        raise ValueError("Task dependencies must be a list.")

    if not isinstance(source_references, list):
        raise ValueError("Task source_references must be a list.")

    return CoordinationTask(
        task_id=task_id,
        title=title,
        description=task.get("description", ""),
        owner=task.get("owner"),
        due_date=task.get("due_date"),
        dependencies=dependencies.copy(),
        source_references=source_references.copy(),

        # Imported task status is not execution authority.
        status="proposed",
        completion_percentage=0,
        requires_human_review=True,
    )


def convert_milestone(
    milestone: dict[str, Any],
) -> CoordinationMilestone:
    """Convert an Agent #2 milestone."""

    if not isinstance(milestone, dict):
        raise ValueError("Milestone must be an object.")

    milestone_id = milestone.get("milestone_id")
    title = milestone.get("title")

    if not isinstance(milestone_id, str) or not milestone_id.strip():
        raise ValueError(
            "Milestone requires a valid milestone_id."
        )

    if not isinstance(title, str) or not title.strip():
        raise ValueError(
            "Milestone requires a valid title."
        )

    raw_tasks = milestone.get("tasks", [])

    if not isinstance(raw_tasks, list):
        raise ValueError(
            "Milestone tasks must be a list."
        )

    return CoordinationMilestone(
        milestone_id=milestone_id,
        title=title,
        tasks=[
            convert_task(task)
            for task in raw_tasks
        ],
        target_date=milestone.get("target_date"),

        # Reset imported execution-related state.
        status="proposed",
        completion_percentage=0,
    )


def build_coordination_state(
    report: dict[str, Any],
) -> CoordinationState:
    """
    Build an unapproved coordination state.

    Approval cannot be inherited from imported JSON.
    """

    plan = report.get("onboarding_plan")

    if not isinstance(plan, dict):
        raise ValueError(
            "Report requires onboarding_plan."
        )

    deal_id = report.get("deal_id")

    if not isinstance(deal_id, str) or not deal_id.strip():
        raise ValueError("Report requires a valid deal_id.")

    if plan.get("deal_id") != deal_id:
        raise ValueError(
            "Report and onboarding plan deal IDs do not match."
        )

    milestones = plan.get("milestones")

    if not isinstance(milestones, list):
        raise ValueError(
            "Onboarding plan milestones must be a list."
        )

    return CoordinationState(
        deal_id=deal_id,
        customer_name=report.get("customer_name"),
        milestones=[
            convert_milestone(milestone)
            for milestone in milestones
        ],
        source_plan_status="unverified",
        requires_human_review=True,
        execution_authorized=False,
        metadata={
            "source_agent": "onboarding_planning",
            "source_report_version": report.get("version"),
            "imported_as": "unverified_draft",
        },
    )