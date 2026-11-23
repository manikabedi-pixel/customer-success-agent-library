import pytest

from agents.onboarding_coordinator.milestone_tracker import (
    calculate_milestone_progress,
    calculate_overall_progress,
    find_milestones_requiring_attention,
)
from agents.onboarding_coordinator.schemas import (
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
                        status="completed",
                        owner="Technical Lead",
                        due_date="2026-12-01",
                    ),
                    CoordinationTask(
                        task_id="TASK-002",
                        title="Review technical requirements",
                        status="in_progress",
                    ),
                ],
            ),
            CoordinationMilestone(
                milestone_id="MILESTONE-002",
                title="Data Readiness",
                tasks=[
                    CoordinationTask(
                        task_id="TASK-003",
                        title="Assess migration",
                        status="blocked",
                    ),
                ],
            ),
        ],
    )


def test_milestone_progress():
    state = make_state()

    result = calculate_milestone_progress(
        state.milestones[0]
    )

    assert result["total_tasks"] == 2
    assert result["completed_tasks"] == 1
    assert result["reported_completion_percentage"] == 50.0


def test_completion_is_not_verified():
    state = make_state()

    result = calculate_milestone_progress(
        state.milestones[0]
    )

    assert result["completion_verified"] is False
    assert result["verified_completion_percentage"] is None


def test_blocked_tasks_counted():
    state = make_state()

    result = calculate_milestone_progress(
        state.milestones[1]
    )

    assert result["blocked_tasks"] == 1


def test_overall_progress():
    state = make_state()

    result = calculate_overall_progress(state)

    assert result["total_milestones"] == 2
    assert result["total_tasks"] == 3
    assert result["completed_tasks"] == 1
    assert result["blocked_tasks"] == 1
    assert result["reported_completion_percentage"] == 33.33


def test_overall_progress_not_verified():
    state = make_state()

    result = calculate_overall_progress(state)

    assert result["completion_verified"] is False
    assert result["execution_authorized"] is False


def test_empty_milestone():
    milestone = CoordinationMilestone(
        milestone_id="MILESTONE-EMPTY",
        title="Empty Milestone",
    )

    result = calculate_milestone_progress(milestone)

    assert result["total_tasks"] == 0
    assert result["reported_completion_percentage"] == 0.0


def test_invalid_task_status_rejected():
    milestone = CoordinationMilestone(
        milestone_id="MILESTONE-001",
        title="Discovery",
        tasks=[
            CoordinationTask(
                task_id="TASK-001",
                title="Confirm scope",
                status="unknown_status",
            )
        ],
    )

    with pytest.raises(ValueError, match="Invalid task status"):
        calculate_milestone_progress(milestone)


def test_find_milestones_requiring_attention():
    state = make_state()

    result = find_milestones_requiring_attention(state)

    assert len(result) == 2

    assert "missing_owners" in result[0]["reasons"]
    assert "blocked_tasks" in result[1]["reasons"]


def test_progress_calculation_does_not_modify_tasks():
    state = make_state()

    original_status = state.milestones[0].tasks[0].status

    calculate_overall_progress(state)

    assert state.milestones[0].tasks[0].status == original_status


def test_empty_state_progress():
    state = CoordinationState(
        deal_id="DEAL-EMPTY",
    )

    result = calculate_overall_progress(state)

    assert result["total_tasks"] == 0
    assert result["reported_completion_percentage"] == 0.0
    assert result["completion_verified"] is False