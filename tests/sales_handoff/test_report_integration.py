from agents.sales_handoff.report_generator import (
    generate_markdown_report,
)


def make_draft():
    return {
        "deal": {
            "deal_id": "TEST-001",
            "deal_name": "Test Enterprise Deal",
            "amount": 72000,
            "stage": "closedwon",
        },
        "customer": {"name": "Test Customer"},
        "stakeholders": [],
        "sales_intelligence": [
            {
                "category": "integration",
                "status": "customer_requested",
                "value": "Salesforce integration requested",
                "evidence": "Customer requested Salesforce integration.",
                "source_note_ids": ["NOTE-001"],
            },
            {
                "category": "timeline",
                "status": "discussed_unconfirmed",
                "value": "Six-week implementation timeline",
                "evidence": "Six weeks discussed but not agreed.",
                "source_note_ids": ["NOTE-001"],
            },
            {
                "category": "ownership",
                "status": "missing",
                "value": "Implementation owner missing",
                "evidence": "No implementation owner identified.",
                "source_note_ids": ["NOTE-001"],
            },
        ],
        "missing_information": [
            "Implementation owner missing"
        ],
        "onboarding_risks": [
            {
                "description": "Salesforce integration requested",
                "source_note_ids": ["NOTE-001"],
            }
        ],
        "source_notes": [],
        "status": "draft",
        "requires_human_review": True,
    }


def test_report_contains_quality_and_readiness():
    report = generate_markdown_report(make_draft())

    assert "### Handoff Quality Assessment" in report
    assert "**Quality Score:**" in report

    assert "### Onboarding Readiness Assessment" in report
    assert "**Readiness:** Clarification required" in report


def test_report_consolidates_and_prioritizes_recommendations():
    report = generate_markdown_report(make_draft())

    combined = (
        "Confirm scope, feasibility, and onboarding risks: "
        "Salesforce integration requested"
    )

    assert combined in report
    assert f"**[High]** {combined}" in report

    assert (
        "Review onboarding risk: Salesforce integration requested"
        not in report
    )


def test_report_preserves_human_review_safeguards():
    report = generate_markdown_report(make_draft())

    assert "> **DRAFT — HUMAN REVIEW REQUIRED**" in report
    assert "## 9. Human Review Checklist" in report
    assert "## 10. Handoff Approval" in report
    assert "**Decision:** Pending review" in report
    assert "**Human Review Required:** YES" in report


def test_report_preserves_ten_numbered_sections():
    report = generate_markdown_report(make_draft())

    for number in range(1, 11):
        assert report.count(f"\n## {number}. ") == 1