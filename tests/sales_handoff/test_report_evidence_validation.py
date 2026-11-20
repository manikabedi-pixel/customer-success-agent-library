from agents.sales_handoff.report_generator import (
    generate_markdown_report,
)


def make_draft(excerpts):
    return {
        "deal": {
            "deal_id": "TEST-001",
            "deal_name": "Test Customer Handoff",
            "amount": 10000,
            "stage": "closedwon",
        },
        "customer": {
            "name": "Test Customer",
        },
        "stakeholders": [],
        "sales_intelligence": [
            {
                "category": "customer_request",
                "value": "Salesforce integration",
                "status": "customer_requested",
                "evidence": (
                    "Customer requested Salesforce integration."
                ),
                "source_note_ids": ["NOTE-001"],
                "requires_verification": True,
            }
        ],
        "missing_information": [],
        "onboarding_risks": [],
        "source_notes": [
            {
                "source_id": "NOTE-001",
                "source_type": "test_note",
                "timestamp": "2026-11-20T00:00:00Z",
                "evidence_excerpts": excerpts,
            }
        ],
        "requires_human_review": True,
        "status": "draft",
    }


def test_report_shows_matching_evidence():
    draft = make_draft([
        "Customer requested Salesforce integration."
    ])

    report = generate_markdown_report(draft)

    assert "### Evidence Validation Assessment" in report
    assert "**Facts With Matching Excerpts:** 1" in report
    assert "Fact 1: Evidence excerpt matched" in report
    assert "**Human Review Required:** YES" in report


def test_report_shows_mismatching_evidence():
    draft = make_draft([
        "Customer requested executive dashboards."
    ])

    report = generate_markdown_report(draft)

    assert "**Facts With Matching Excerpts:** 0" in report
    assert "Fact 1: Evidence excerpt mismatch" in report


def test_report_shows_missing_excerpts():
    draft = make_draft([])

    report = generate_markdown_report(draft)

    assert "**Facts With Preserved Excerpts:** 0" in report
    assert "Fact 1: Evidence excerpt unavailable" in report


def test_report_keeps_human_approval_pending():
    draft = make_draft([
        "Customer requested Salesforce integration."
    ])

    report = generate_markdown_report(draft)

    assert "**Human Review Required:** YES" in report
    assert "**Decision:** Pending review" in report
    assert "DRAFT" in report