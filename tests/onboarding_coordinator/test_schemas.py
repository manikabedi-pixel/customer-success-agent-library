from dataclasses import asdict

from agents.onboarding_coordinator.schemas import (
    ApprovalRecord,
    CoordinationBlocker,
    CoordinationMilestone,
    CoordinationState,
    CoordinationTask,
)


def test_task_safe_defaults():
    task = CoordinationTask(
        task_id="TASK-001",
        title="Confirm implementation scope",
    )

    assert task.status == "proposed"
    assert task.completion_percentage == 0
    assert task.owner is None
    assert task.due_date is None
    assert task.requires_human_review is True


def test_task_dependencies_are_independent():
    first = CoordinationTask(
        task_id="TASK-001",
        title="Discovery",
    )

    second = CoordinationTask(
        task_id="TASK-002",
        title="Planning",
    )

    first.dependencies.append("TASK-003")

    assert second.dependencies == []


def test_milestone_safe_defaults():
    milestone = CoordinationMilestone(
        milestone_id="MILESTONE-001",
        title="Technical Discovery",
    )

    assert milestone.status == "proposed"
    assert milestone.completion_percentage == 0
    assert milestone.tasks == []


def test_blocker_safe_defaults():
    blocker = CoordinationBlocker(
        blocker_id="BLOCKER-001",
        description="Integration scope not confirmed",
    )

    assert blocker.severity == "unassessed"
    assert blocker.status == "open"
    assert blocker.owner is None


def test_approval_record_is_unverified():
    approval = ApprovalRecord(
        reviewer_id="reviewer-123",
        decision="approved",
    )

    assert approval.decision == "approved"
    assert approval.verified is False


def test_coordination_state_is_not_authorized():
    state = CoordinationState(
        deal_id="DEAL-123",
        customer_name="Example Customer",
    )

    assert state.source_plan_status == "unverified"
    assert state.requires_human_review is True
    assert state.execution_authorized is False
    assert state.approval.verified is False


def test_coordination_state_lists_are_independent():
    first = CoordinationState(deal_id="DEAL-001")
    second = CoordinationState(deal_id="DEAL-002")

    first.blockers.append(
        CoordinationBlocker(
            blocker_id="BLOCKER-001",
            description="Missing technical owner",
        )
    )

    assert second.blockers == []


def test_coordination_state_can_be_serialized():
    state = CoordinationState(
        deal_id="DEAL-123",
        milestones=[
            CoordinationMilestone(
                milestone_id="MILESTONE-001",
                title="Discovery",
                tasks=[
                    CoordinationTask(
                        task_id="TASK-001",
                        title="Confirm scope",
                    )
                ],
            )
        ],
    )

    result = asdict(state)

    assert result["deal_id"] == "DEAL-123"
    assert result["milestones"][0]["tasks"][0]["task_id"] == "TASK-001"
    assert result["execution_authorized"] is False