import pytest

from agents.sales_handoff.report_generator import (
    generate_markdown_report,
)


def make_draft(evidence, excerpts, source_ids=None):
    if source_ids is None:
        source_ids = ["NOTE-001"]

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
                "source_note_ids": source_ids,
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
    "evidence, excerpts, expected_action",
    [
        (
            "Customer requested Salesforce integration.",
            ["Customer requested Salesforce integration."],
            "Review the original CRM note to confirm "
            "the excerpt supports the claim.",
        ),
        (
            "Customer requested Salesforce integration.",
            ["Customer requested executive dashboards."],
            "Compare the extracted evidence with the "
            "original CRM note and resolve the mismatch.",
        ),
        (
            "Customer requested Salesforce integration.",
            [],
            "Retrieve the original CRM note and verify "
            "the supporting evidence.",
        ),
        (
            "",
            ["Customer requested Salesforce integration."],
            "Obtain supporting evidence before relying "
            "on this claim.",
        ),
    ],
)
def test_report_generates_correct_evidence_review_action(
    evidence,
    excerpts,
    expected_action,
):
    draft = make_draft(evidence, excerpts)

    report = generate_markdown_report(draft)

    assert "**Recommended Evidence Review Actions:**" in report
    assert f"- Fact 1: {expected_action}" in report


def test_invalid_source_reference_requires_review():
    draft = make_draft(
        evidence="Customer requested Salesforce integration.",
        excerpts=["Customer requested Salesforce integration."],
        source_ids=["NOTE-999"],
    )

    report = generate_markdown_report(draft)

    assert (
        "Fact 1: Retrieve the original CRM note "
        "and verify the supporting evidence."
    ) in report

    assert "**Invalid References:** 1" in report


def test_report_preserves_human_review_requirement():
    draft = make_draft(
        evidence="Customer requested Salesforce integration.",
        excerpts=["Customer requested Salesforce integration."],
    )

    report = generate_markdown_report(draft)

    assert "**Human Review Required:** YES" in report
    assert "**Decision:** Pending review" in report
    assert "DRAFT" in report