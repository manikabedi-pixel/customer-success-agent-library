from agents.onboarding_planning.markdown_renderer import (
    render_onboarding_markdown,
)


def test_markdown_contains_review_warning():
    report = {
        "deal_id": "DEAL-123",
        "customer_name": "Example Customer",
        "onboarding_plan": {
            "objectives": [],
            "milestones": [],
        },
        "planning_assessment": {
            "onboarding_risks": [],
            "missing_information": [],
        },
        "ai_planning": {
            "ai_status": "skipped",
            "suggestions": [],
        },
    }

    markdown = render_onboarding_markdown(report)

    assert "DRAFT — HUMAN REVIEW REQUIRED" in markdown
    assert "Not approved" in markdown
    assert "Not authorized" in markdown


def test_markdown_includes_ai_suggestions():
    report = {
        "deal_id": "DEAL-123",
        "customer_name": "Example Customer",
        "onboarding_plan": {
            "objectives": [],
            "milestones": [],
        },
        "planning_assessment": {
            "onboarding_risks": [],
            "missing_information": [],
        },
        "ai_planning": {
            "ai_status": "completed",
            "suggestions": [
                {
                    "requirement_id": "REQ-001",
                    "suggested_activity": "Confirm CRM integration",
                    "rationale": "Integration mentioned in handoff",
                }
            ],
        },
    }

    markdown = render_onboarding_markdown(report)

    assert "Confirm CRM integration" in markdown
    assert "Integration mentioned in handoff" in markdown