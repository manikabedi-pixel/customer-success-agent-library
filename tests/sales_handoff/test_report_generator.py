from agents.sales_handoff.report_generator import (
    generate_markdown_report,
)


def test_generate_markdown_report():
    # Synthetic data: no HubSpot or OpenAI calls.
    draft = {
        "deal": {
            "deal_id": "TEST-003",
            "deal_name": "Example Enterprise Subscription",
            "amount": "50000",
            "stage": "closedwon",
        },
        "customer": {
            "name": "Example Software",
        },
        "stakeholders": [
            {
                "name": "Alex Morgan",
                "job_title": "VP Operations",
            }
        ],
        "sales_intelligence": [
            {
                "category": "business_objective",
                "value": "Improve customer reporting",
                "status": "confirmed",
                "evidence": "The customer wants to improve reporting.",
                "source_note_ids": ["NOTE-003"],
            },
            {
                "category": "integration",
                "value": "Salesforce integration requested",
                "status": "customer_requested",
                "evidence": "The customer requested Salesforce integration.",
                "source_note_ids": ["NOTE-003"],
            },
            {
                "category": "timeline",
                "value": "Six-week implementation discussed",
                "status": "discussed_unconfirmed",
                "evidence": "A six-week implementation was discussed.",
                "source_note_ids": ["NOTE-003"],
            },
            {
                "category": "stakeholder",
                "value": "Implementation owner not identified",
                "status": "missing",
                "evidence": "The implementation owner has not been identified.",
                "source_note_ids": ["NOTE-003"],
            },
        ],
        "missing_information": [
            "Implementation owner not identified",
        ],
        "onboarding_risks": [
            {
                "description": "Six-week implementation discussed",
                "reason": "Discussed but not confirmed",
                "source_note_ids": ["NOTE-003"],
            }
        ],
        "requires_human_review": True,
        "status": "draft",
    }

    report = generate_markdown_report(draft)

    # Customer and deal information
    assert "Example Software" in report
    assert "Example Enterprise Subscription" in report

    # Confirmed business objective
    assert "Improve customer reporting" in report

    # Customer request
    assert "Salesforce integration requested" in report

    # Unconfirmed timeline
    assert "Six-week implementation discussed" in report

    # Missing information
    assert "Implementation owner not identified" in report

    # Source attribution
    assert "NOTE-003" in report

    # Dynamic review checklist
    assert "Confirm scope and approval for:" in report

    # Human approval safeguards
    assert "**Decision:** Pending review" in report
    assert "**Human Review Required:** YES" in report

    # All 10 sections must appear exactly once
    for number in range(1, 11):
        assert report.count(f"## {number}. ") == 1