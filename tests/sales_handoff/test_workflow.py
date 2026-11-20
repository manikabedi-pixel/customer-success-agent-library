import json
from unittest.mock import patch

from agents.sales_handoff.workflow import run_workflow


def test_report_mode_without_api_calls(tmp_path):
    """Report mode should use existing JSON without calling APIs."""

    deal_id = "TEST-004"

    fake_draft = {
        "deal": {
            "deal_id": deal_id,
            "deal_name": "Example Enterprise Deal",
            "amount": "50000",
            "stage": "closedwon",
        },
        "customer": {
            "name": "Example Software",
        },
        "stakeholders": [],
        "sales_intelligence": [],
        "missing_information": [],
        "onboarding_risks": [],
        "requires_human_review": True,
        "status": "draft",
    }

    json_path = tmp_path / f"hubspot_handoff_{deal_id}.json"
    json_path.write_text(
        json.dumps(fake_draft),
        encoding="utf-8",
    )

    with (
        patch(
            "agents.sales_handoff.workflow.OUTPUT_DIR",
            tmp_path,
        ),
        patch(
            "agents.sales_handoff.workflow.build_handoff_draft"
        ) as mock_builder,
    ):
        result = run_workflow(
            deal_id=deal_id,
            mode="report",
        )

    # Report mode must not invoke the live handoff builder.
    mock_builder.assert_not_called()

    # Existing JSON should remain unchanged.
    # Original handoff fields should remain unchanged.
    for key, value in fake_draft.items():
        assert result[key] == value
    # Quality scoring should be added to the returned handoff.
    assert "quality_score" in result
    assert 0 <= result["quality_score"]["score"] <= 100
    assert result["quality_score"]["requires_human_review"] is True
    # Report mode must not modify the existing JSON file.
    saved_draft = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved_draft == fake_draft

    # Markdown report should be generated.
    markdown_path = tmp_path / f"hubspot_handoff_{deal_id}.md"

    assert markdown_path.exists()

    report = markdown_path.read_text(encoding="utf-8")

    assert "Example Software" in report
    assert "Example Enterprise Deal" in report
    assert "**Human Review Required:** YES" in report
    assert "**Decision:** Pending review" in report

def test_live_mode_generates_json_and_markdown(tmp_path):
    """Live mode should generate both files using a mocked builder."""
    deal_id = "TEST-005"
    fake_draft = {

        "deal": {
            "deal_id": deal_id,
            "deal_name": "Acme Enterprise Subscription",
            "amount": "80000",
            "stage": "closedwon",
        },

        "customer": {
            "name": "Acme Software",
        },
        "stakeholders": [],
        "sales_intelligence": [],
        "missing_information": [],
        "onboarding_risks": [],
        "requires_human_review": True,
        "status": "draft",
    }

    with (
        patch(
            "agents.sales_handoff.workflow.OUTPUT_DIR",
            tmp_path,
        ),

        patch(
            "agents.sales_handoff.workflow.build_handoff_draft",
            return_value=fake_draft,
        ) as mock_builder,
    ):

        result = run_workflow(
            deal_id=deal_id,
            mode="live",
        )

    # Confirm the builder was called for the correct deal.
    mock_builder.assert_called_once_with(deal_id)
    # Confirm the workflow returned the expected draft.
    assert result == fake_draft
    # Confirm both output files were created.
    json_path = tmp_path / f"hubspot_handoff_{deal_id}.json"
    markdown_path = tmp_path / f"hubspot_handoff_{deal_id}.md"
    assert json_path.exists()
    assert markdown_path.exists()
    # Confirm the JSON contains the correct customer.
    saved_draft = json.loads(json_path.read_text(encoding="utf-8"))
    assert saved_draft["customer"]["name"] == "Acme Software"
    # Confirm the Markdown contains the correct customer.
    report = markdown_path.read_text(encoding="utf-8")
    assert "Acme Software" in report
    assert "Acme Enterprise Subscription" in report
    # Confirm human review safeguards.
    assert "**Human Review Required:** YES" in report
    assert "**Decision:** Pending review" in report

import pytest

@pytest.mark.parametrize(
    "status, requires_review",
    [
        ("approved", True),
        ("draft", False),
    ],
)

def test_workflow_rejects_unsafe_handoffs(
    tmp_path,
    status,
    requires_review,
):

    """Reject handoffs that bypass draft or human-review safeguards."""
    deal_id = "TEST-SAFETY"
    unsafe_draft = {
        "deal": {
            "deal_id": deal_id,
            "deal_name": "Safety Test Deal",
        },

        "customer": {
            "name": "Safety Test Customer",
        },
        "stakeholders": [],
        "sales_intelligence": [],
        "missing_information": [],
        "onboarding_risks": [],
        "status": status,
        "requires_human_review": requires_review,
    }

    with (
        patch(
            "agents.sales_handoff.workflow.OUTPUT_DIR",
            tmp_path,
        ),

        patch(
            "agents.sales_handoff.workflow.build_handoff_draft",
            return_value=unsafe_draft,
        ),
    ):

        with pytest.raises(ValueError):
            run_workflow(
                deal_id=deal_id,
                mode="live",
            )
    # Unsafe handoffs must not produce Markdown reports.

    markdown_path = (
        tmp_path / f"hubspot_handoff_{deal_id}.md"
    )

    assert not markdown_path.exists()

    # Unsafe handoffs must not produce JSON files either.
    json_path = tmp_path / f"hubspot_handoff_{deal_id}.json"

    assert not json_path.exists()