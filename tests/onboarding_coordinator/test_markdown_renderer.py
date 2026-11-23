from agents.onboarding_coordinator.markdown_renderer import (
    render_coordination_markdown,
)
from agents.onboarding_coordinator.report_generator import (
    generate_coordination_report,
)
from agents.onboarding_coordinator.schemas import (
    CoordinationMilestone,
    CoordinationState,
    CoordinationTask,
)


def make_report():
    state = CoordinationState(
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

    return generate_coordination_report(state)


def test_markdown_contains_customer():
    markdown = render_coordination_markdown(make_report())

    assert "Example Customer" in markdown
    assert "DEAL-123" in markdown


def test_markdown_contains_milestone():
    markdown = render_coordination_markdown(make_report())

    assert "Technical Discovery" in markdown


def test_markdown_contains_issue_details():
    markdown = render_coordination_markdown(make_report())

    assert "missing_owner" in markdown
    assert "missing_due_date" in markdown


def test_markdown_contains_review_checklist():
    markdown = render_coordination_markdown(make_report())

    assert "Human Review Checklist" in markdown
    assert "Confirm task owners" in markdown


def test_markdown_does_not_authorize_execution():
    markdown = render_coordination_markdown(make_report())

    assert "does not authorize onboarding execution" in markdown