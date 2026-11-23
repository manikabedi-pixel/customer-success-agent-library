import pytest

from agents.onboarding_coordinator.schemas import (
    CoordinationMilestone,
    CoordinationState,
    CoordinationTask,
)
from agents.onboarding_coordinator.task_tracker import (
    OwnerAssignmentProposal,
    find_unassigned_tasks,
    get_all_tasks,
    propose_owner_assignment,
    validate_owner_proposals,
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
                    ),
                    CoordinationTask(
                        task_id="TASK-002",
                        title="Review technical requirements",
                        owner="Technical Lead",
                    ),
                ],
            )
        ],
    )


def test_get_all_tasks():
    state = make_state()

    tasks = get_all_tasks(state)

    assert len(tasks) == 2


def test_find_unassigned_tasks():
    state = make_state()

    unassigned = find_unassigned_tasks(state)

    assert len(unassigned) == 1
    assert unassigned[0]["task_id"] == "TASK-001"


def test_propose_owner_assignment():
    state = make_state()

    proposal = propose_owner_assignment(
        state,
        task_id="TASK-001",
        proposed_owner="Implementation Specialist",
        rationale="Technical discovery responsibility requires review",
    )

    assert proposal.task_id == "TASK-001"
    assert proposal.proposed_owner == "Implementation Specialist"
    assert proposal.requires_human_review is True


def test_proposal_does_not_modify_task():
    state = make_state()

    propose_owner_assignment(
        state,
        task_id="TASK-001",
        proposed_owner="Implementation Specialist",
        rationale="Proposed technical owner",
    )

    assert state.milestones[0].tasks[0].owner is None


def test_unknown_task_rejected():
    state = make_state()

    with pytest.raises(ValueError, match="exactly one"):
        propose_owner_assignment(
            state,
            task_id="TASK-999",
            proposed_owner="Implementation Specialist",
            rationale="Proposed technical owner",
        )


def test_empty_owner_rejected():
    state = make_state()

    with pytest.raises(ValueError, match="Proposed owner"):
        propose_owner_assignment(
            state,
            task_id="TASK-001",
            proposed_owner="",
            rationale="Proposed technical owner",
        )


def test_validate_owner_proposals():
    state = make_state()

    proposals = [
        OwnerAssignmentProposal(
            task_id="TASK-001",
            proposed_owner="Implementation Specialist",
            rationale="Requires technical ownership review",
        )
    ]

    result = validate_owner_proposals(
        state,
        proposals,
    )

    assert len(result) == 1
    assert result[0]["approved"] is False
    assert result[0]["status"] == "proposed"


def test_duplicate_proposals_rejected():
    state = make_state()

    proposal = OwnerAssignmentProposal(
        task_id="TASK-001",
        proposed_owner="Implementation Specialist",
        rationale="Technical ownership",
    )

    with pytest.raises(ValueError, match="Duplicate"):
        validate_owner_proposals(
            state,
            [proposal, proposal],
        )


def test_unapproved_proposals_required():
    state = make_state()

    proposal = OwnerAssignmentProposal(
        task_id="TASK-001",
        proposed_owner="Implementation Specialist",
        rationale="Technical ownership",
        status="approved",
    )

    with pytest.raises(ValueError, match="unapproved"):
        validate_owner_proposals(
            state,
            [proposal],
        )


def test_missing_rationale_rejected():
    state = make_state()

    with pytest.raises(ValueError, match="rationale"):
        propose_owner_assignment(
            state,
            task_id="TASK-001",
            proposed_owner="Implementation Specialist",
            rationale="",
        )