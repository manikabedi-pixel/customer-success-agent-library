import pytest

from agents.onboarding_coordinator.coordination_rules import (
    ApprovalDecision,
    assess_coordination_readiness,
    can_begin_coordination,
    record_trusted_approval,
)
from agents.onboarding_coordinator.schemas import (
    ApprovalRecord,
    CoordinationMilestone,
    CoordinationState,
    CoordinationTask,
)


def make_state():
    return CoordinationState(
        deal_id="DEAL-123",
        milestones=[
            CoordinationMilestone(
                milestone_id="MILESTONE-001",
                title="Technical Discovery",
                tasks=[
                    CoordinationTask(
                        task_id="TASK-001",
                        title="Confirm integration scope",
                    )
                ],
            )
        ],
    )


def test_imported_plan_cannot_begin_coordination():
    state = make_state()

    assert can_begin_coordination(state) is False
    assert state.execution_authorized is False


def test_imported_approval_claim_is_not_trusted():
    state = make_state()

    state.approval = ApprovalRecord(
        reviewer_id="reviewer-123",
        decision="approved",
        verified=False,
    )

    assert can_begin_coordination(state) is False


def test_readiness_identifies_missing_owners_and_dates():
    state = make_state()

    result = assess_coordination_readiness(state)

    assert result["missing_owners"] == ["TASK-001"]
    assert result["missing_dates"] == ["TASK-001"]


def test_trusted_approval_enables_internal_coordination():
    state = make_state()

    decision = ApprovalDecision(
        deal_id="DEAL-123",
        reviewer_id="reviewer-123",
        decision="approved",
        evidence_reference="APPROVAL-001",
    )

    record_trusted_approval(state, decision)

    assert state.approval.verified is True
    assert can_begin_coordination(state) is True
    assert state.execution_authorized is False


def test_rejection_does_not_enable_coordination():
    state = make_state()

    decision = ApprovalDecision(
        deal_id="DEAL-123",
        reviewer_id="reviewer-123",
        decision="rejected",
        evidence_reference="REJECTION-001",
    )

    record_trusted_approval(state, decision)

    assert can_begin_coordination(state) is False
    assert state.execution_authorized is False


def test_wrong_deal_approval_rejected():
    state = make_state()

    decision = ApprovalDecision(
        deal_id="DEAL-999",
        reviewer_id="reviewer-123",
        decision="approved",
        evidence_reference="APPROVAL-001",
    )

    with pytest.raises(ValueError, match="deal ID"):
        record_trusted_approval(state, decision)


def test_missing_reviewer_rejected():
    state = make_state()

    decision = ApprovalDecision(
        deal_id="DEAL-123",
        reviewer_id="",
        decision="approved",
        evidence_reference="APPROVAL-001",
    )

    with pytest.raises(ValueError, match="Reviewer ID"):
        record_trusted_approval(state, decision)


def test_missing_evidence_rejected():
    state = make_state()

    decision = ApprovalDecision(
        deal_id="DEAL-123",
        reviewer_id="reviewer-123",
        decision="approved",
        evidence_reference="",
    )

    with pytest.raises(ValueError, match="evidence"):
        record_trusted_approval(state, decision)


def test_invalid_decision_rejected():
    state = make_state()

    decision = ApprovalDecision(
        deal_id="DEAL-123",
        reviewer_id="reviewer-123",
        decision="pending",
        evidence_reference="APPROVAL-001",
    )

    with pytest.raises(ValueError, match="Decision"):
        record_trusted_approval(state, decision)