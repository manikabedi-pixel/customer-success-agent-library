from dataclasses import dataclass
from datetime import datetime, timezone

from agents.onboarding_coordinator.schemas import (
    ApprovalRecord,
    CoordinationState,
)


@dataclass(frozen=True)
class ApprovalDecision:
    deal_id: str
    reviewer_id: str
    decision: str
    evidence_reference: str


def assess_coordination_readiness(
    state: CoordinationState,
) -> dict:
    """Assess whether coordination can proceed."""

    missing_owners = [
        task.task_id
        for milestone in state.milestones
        for task in milestone.tasks
        if not task.owner
    ]

    missing_dates = [
        task.task_id
        for milestone in state.milestones
        for task in milestone.tasks
        if not task.due_date
    ]

    return {
        "deal_id": state.deal_id,
        "source_plan_status": state.source_plan_status,
        "approval_verified": state.approval.verified,
        "approval_decision": state.approval.decision,
        "missing_owners": missing_owners,
        "missing_dates": missing_dates,
        "execution_authorized": state.execution_authorized,
        "requires_human_review": state.requires_human_review,
    }


def record_trusted_approval(
    state: CoordinationState,
    decision: ApprovalDecision,
) -> CoordinationState:
    """
    Record a human decision supplied by a trusted caller.

    This function does not authenticate the reviewer.
    The caller is responsible for verifying identity and authority.
    """

    if decision.deal_id != state.deal_id:
        raise ValueError("Approval deal ID does not match.")

    if decision.decision not in {"approved", "rejected"}:
        raise ValueError("Decision must be approved or rejected.")

    if not decision.reviewer_id.strip():
        raise ValueError("Reviewer ID is required.")

    if not decision.evidence_reference.strip():
        raise ValueError("Approval evidence reference is required.")

    state.approval = ApprovalRecord(
        reviewer_id=decision.reviewer_id,
        reviewed_at=datetime.now(timezone.utc).isoformat(),
        decision=decision.decision,
        evidence_reference=decision.evidence_reference,
        verified=True,
    )

    state.source_plan_status = (
        "approved" if decision.decision == "approved"
        else "rejected"
    )

    # Plan approval is not permission to perform external actions.
    state.execution_authorized = False

    state.requires_human_review = (
        decision.decision != "approved"
    )

    return state


def can_begin_coordination(
    state: CoordinationState,
) -> bool:
    """
    Determine whether internal coordination tracking may begin.

    This does not authorize external actions.
    """

    return (
        state.approval.verified is True
        and state.approval.decision == "approved"
        and state.source_plan_status == "approved"
    )