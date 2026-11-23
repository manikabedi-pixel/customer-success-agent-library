from agents.onboarding_coordinator.report_generator import (
    generate_coordination_report,
)
from agents.onboarding_coordinator.schemas import (
    CoordinationMilestone,
    CoordinationState,
    CoordinationTask,
)


def make_state():
    return CoordinationState(
        deal_id="DEAL-123",
        customer_name="Example Customer",
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


def test_report_identifies_customer():
    report = generate_coordination_report(make_state())

    assert report["deal_id"] == "DEAL-123"
    assert report["customer_name"] == "Example Customer"


def test_report_is_unapproved():
    report = generate_coordination_report(make_state())

    assert report["approved"] is False
    assert report["can_execute_onboarding"] is False
    assert report["requires_human_review"] is True


def test_report_contains_progress():
    report = generate_coordination_report(make_state())

    assert report["progress"]["total_milestones"] == 1
    assert report["progress"]["total_tasks"] == 1


def test_report_contains_issues():
    report = generate_coordination_report(make_state())

    assert report["issue_summary"]["total_issues"] == 2


def test_report_skips_ai_by_default():
    report = generate_coordination_report(make_state())

    assert report["ai"]["status"] == "skipped"
    assert report["ai"]["recommendations"] == []


def test_report_includes_ai_recommendations():
    ai_result = {
        "status": "completed",
        "recommendations": [
            {
                "task_id": "TASK-001",
                "issue_type": "missing_owner",
                "recommended_action": "Confirm owner.",
                "rationale": "No owner is assigned.",
                "requires_human_review": True,
            }
        ],
    }

    report = generate_coordination_report(
        make_state(),
        ai_result=ai_result,
    )

    assert len(report["ai"]["recommendations"]) == 1
    assert report["approved"] is False