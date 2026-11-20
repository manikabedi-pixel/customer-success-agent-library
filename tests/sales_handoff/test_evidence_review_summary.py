import pytest

from agents.sales_handoff.report_generator import (
    generate_markdown_report,
)


def make_draft(evidence, excerpts):
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
                "evidence": evidence,
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


@pytest.mark.parametrize(
    "evidence, excerpts, expected_line",
    [
        (
            "Customer requested Salesforce integration.",
            ["Customer requested Salesforce integration."],
            "**Matching Evidence Excerpts:** 1",
        ),
        (
            "Customer requested Salesforce integration.",
            ["Customer requested executive dashboards."],
            "**Evidence Mismatches:** 1",
        ),
        (
            "Customer requested Salesforce integration.",
            [],
            "**Unavailable Evidence Excerpts:** 1",
        ),
        (
            "",
            ["Customer requested Salesforce integration."],
            "**Facts Missing Extracted Evidence:** 1",
        ),
    ],
)
def test_evidence_review_summary(
    evidence,
    excerpts,
    expected_line,
):
    draft = make_draft(evidence, excerpts)

    report = generate_markdown_report(draft)

    assert "### Evidence Review Summary" in report
    assert "**Total Facts:** 1" in report
    assert expected_line in report
    assert "**Human Review Required:** YES" in report


def test_matching_evidence_needs_no_additional_investigation():
    draft = make_draft(
        "Customer requested Salesforce integration.",
        ["Customer requested Salesforce integration."],
    )

    report = generate_markdown_report(draft)

    assert (
        "**Facts Requiring Evidence Investigation:** 0"
        in report
    )


def test_missing_excerpt_requires_investigation():
    draft = make_draft(
        "Customer requested Salesforce integration.",
        [],
    )

    report = generate_markdown_report(draft)

    assert (
        "**Facts Requiring Evidence Investigation:** 1"
        in report
    )


def test_human_approval_remains_pending():
    draft = make_draft(
        "Customer requested Salesforce integration.",
        ["Customer requested Salesforce integration."],
    )

    report = generate_markdown_report(draft)

    assert "**Decision:** Pending review" in report
    assert "DRAFT" in report