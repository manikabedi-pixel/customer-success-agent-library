from datetime import datetime, timezone
from typing import Any

from agents.onboarding_coordinator.blocker_detector import (
    detect_task_issues,
    summarize_task_issues,
)
from agents.onboarding_coordinator.coordination_rules import (
    assess_coordination_readiness,
    can_begin_coordination,
)
from agents.onboarding_coordinator.milestone_tracker import (
    calculate_overall_progress,
    find_milestones_requiring_attention,
)
from agents.onboarding_coordinator.schemas import CoordinationState
from agents.onboarding_coordinator.task_tracker import (
    find_unassigned_tasks,
)


def generate_coordination_report(
    state: CoordinationState,
    ai_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate a read-only coordination report.

    This function does not authorize or execute onboarding work.
    """

    issues = detect_task_issues(state)
    issue_summary = summarize_task_issues(issues)

    progress = calculate_overall_progress(state)
    readiness = assess_coordination_readiness(state)

    unassigned_tasks = find_unassigned_tasks(state)

    attention_items = find_milestones_requiring_attention(state)

    if ai_result is None:
        ai_result = {
            "status": "skipped",
            "recommendations": [],
        }

    return {
        "agent": "onboarding_coordinator",
        "version": "0.0.9",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "DRAFT — HUMAN REVIEW REQUIRED",
        "deal_id": state.deal_id,
        "customer_name": state.customer_name,
        "source_plan_status": state.source_plan_status,
        "approval": {
            "verified": state.approval.verified,
            "decision": state.approval.decision,
        },
        "coordination": {
            "can_begin_internal_coordination": can_begin_coordination(state),
            "external_execution_authorized": False,
        },
        "progress": progress,
        "readiness": readiness,
        "unassigned_tasks": unassigned_tasks,
        "issues": issues,
        "issue_summary": issue_summary,
        "milestones_requiring_attention": attention_items,
        "ai": {
            "status": ai_result.get("status", "unknown"),
            "recommendations": ai_result.get(
                "recommendations", []
            ),
        },
        "requires_human_review": True,
        "approved": False,
        "can_execute_onboarding": False,
    }