from datetime import date

from agents.onboarding_coordinator.blocker_detector import (
    detect_task_issues,
    summarize_task_issues,
)
from agents.onboarding_coordinator.schemas import (
    CoordinationMilestone,
    CoordinationState,
    CoordinationTask,
)


TEST_TODAY = date(2026, 11, 23)


def make_state(tasks):
    return CoordinationState(
        deal_id="DEAL-123",
        milestones=[
            CoordinationMilestone(
                milestone_id="MILESTONE-001",
                title="Technical Discovery",
                tasks=tasks,
            )
        ],
    )


def test_detect_blocked_task():
    state = make_state([
        CoordinationTask(
            task_id="TASK-001",
            title="Confirm scope",
            status="blocked",
        )
    ])

    issues = detect_task_issues(state, TEST_TODAY)

    assert any(
        issue["issue_type"] == "blocked"
        for issue in issues
    )


def test_detect_missing_owner():
    state = make_state([
        CoordinationTask(
            task_id="TASK-001",
            title="Confirm scope",
        )
    ])

    issues = detect_task_issues(state, TEST_TODAY)

    assert any(
        issue["issue_type"] == "missing_owner"
        for issue in issues
    )


def test_detect_missing_due_date():
    state = make_state([
        CoordinationTask(
            task_id="TASK-001",
            title="Confirm scope",
        )
    ])

    issues = detect_task_issues(state, TEST_TODAY)

    assert any(
        issue["issue_type"] == "missing_due_date"
        for issue in issues
    )


def test_detect_overdue_task():
    state = make_state([
        CoordinationTask(
            task_id="TASK-001",
            title="Confirm scope",
            owner="CS Manager",
            due_date="2026-11-01",
        )
    ])

    issues = detect_task_issues(state, TEST_TODAY)

    assert any(
        issue["issue_type"] == "overdue"
        for issue in issues
    )


def test_completed_task_not_overdue():
    state = make_state([
        CoordinationTask(
            task_id="TASK-001",
            title="Confirm scope",
            owner="CS Manager",
            due_date="2026-11-01",
            status="completed",
        )
    ])

    issues = detect_task_issues(state, TEST_TODAY)

    assert not any(
        issue["issue_type"] == "overdue"
        for issue in issues
    )


def test_detect_invalid_due_date():
    state = make_state([
        CoordinationTask(
            task_id="TASK-001",
            title="Confirm scope",
            due_date="not-a-date",
        )
    ])

    issues = detect_task_issues(state, TEST_TODAY)

    assert any(
        issue["issue_type"] == "invalid_due_date"
        for issue in issues
    )


def test_detect_missing_dependency():
    state = make_state([
        CoordinationTask(
            task_id="TASK-001",
            title="Confirm scope",
            dependencies=["TASK-999"],
        )
    ])

    issues = detect_task_issues(state, TEST_TODAY)

    assert any(
        issue["issue_type"] == "missing_dependency"
        for issue in issues
    )


def test_detect_self_dependency():
    state = make_state([
        CoordinationTask(
            task_id="TASK-001",
            title="Confirm scope",
            dependencies=["TASK-001"],
        )
    ])

    issues = detect_task_issues(state, TEST_TODAY)

    assert any(
        issue["issue_type"] == "self_dependency"
        for issue in issues
    )


def test_valid_dependency_not_flagged():
    state = make_state([
        CoordinationTask(
            task_id="TASK-001",
            title="Discovery",
        ),
        CoordinationTask(
            task_id="TASK-002",
            title="Implementation",
            dependencies=["TASK-001"],
        ),
    ])

    issues = detect_task_issues(state, TEST_TODAY)

    assert not any(
        "dependency" in issue["issue_type"]
        for issue in issues
    )


def test_summarize_issues():
    issues = [
        {
            "task_id": "TASK-001",
            "issue_type": "missing_owner",
        },
        {
            "task_id": "TASK-001",
            "issue_type": "missing_due_date",
        },
        {
            "task_id": "TASK-002",
            "issue_type": "blocked",
        },
    ]

    summary = summarize_task_issues(issues)

    assert summary["total_issues"] == 3
    assert summary["issue_counts"]["missing_owner"] == 1
    assert summary["issue_counts"]["blocked"] == 1
    assert summary["affected_task_ids"] == [
        "TASK-001",
        "TASK-002",
    ]


def test_detector_does_not_modify_tasks():
    task = CoordinationTask(
        task_id="TASK-001",
        title="Confirm scope",
        status="blocked",
    )

    state = make_state([task])

    detect_task_issues(state, TEST_TODAY)

    assert task.status == "blocked"
    assert task.owner is None