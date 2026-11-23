import json
from pathlib import Path
from unittest.mock import patch

import pytest

from run_onboarding import run_onboarding


@pytest.fixture
def handoff_file(tmp_path):
    handoff = {
        "deal": {
            "deal_id": "DEAL-123",
            "deal_name": "Example Deal",
        },
        "customer": {
            "name": "Example Customer",
        },
        "sales_intelligence": [
            {
                "category": "integration",
                "value": "CRM integration requested",
                "status": "extracted",
                "evidence": "CRM integration discussed",
                "requires_verification": True,
                "source_note_ids": ["NOTE-001"],
            }
        ],
        "missing_information": [
            "Implementation owner not confirmed"
        ],
        "onboarding_risks": [
            {
                "description": "Integration scope unclear",
                "reason": "Technical requirements need review",
                "source_note_ids": ["NOTE-001"],
            }
        ],
        "source_notes": [],
        "requires_human_review": True,
        "status": "DRAFT — HUMAN REVIEW REQUIRED",
    }

    path = tmp_path / "handoff.json"
    path.write_text(json.dumps(handoff), encoding="utf-8")
    return path


def test_report_mode_generates_both_files(tmp_path, handoff_file):
    output_dir = tmp_path / "outputs"

    result = run_onboarding(
        handoff_path=str(handoff_file),
        mode="report",
        output_dir=str(output_dir),
    )

    assert result["milestones"] == 1
    assert result["tasks"] == 1
    assert result["risks"] == 1
    assert result["ai_status"] == "skipped"
    assert result["approved"] is False
    assert result["can_execute_onboarding"] is False

    assert Path(result["json_report"]).is_file()
    assert Path(result["markdown_report"]).is_file()


def test_report_mode_does_not_call_openai(tmp_path, handoff_file):
    with patch(
        "run_onboarding.prepare_ai_planning_suggestions"
    ) as mock_ai:
        run_onboarding(
            handoff_path=str(handoff_file),
            mode="report",
            output_dir=str(tmp_path / "outputs"),
        )

    mock_ai.assert_not_called()


def test_ai_mode_uses_validated_suggestions(tmp_path, handoff_file):
    mock_ai_result = {
        "ai_status": "completed",
        "suggestions": [
            {
                "requirement_id": "REQ-001",
                "suggested_activity": "Confirm integration scope",
                "rationale": "Integration mentioned in handoff",
                "requires_human_review": True,
                "status": "proposed",
            }
        ],
        "requires_human_review": True,
    }

    with patch(
        "run_onboarding.prepare_ai_planning_suggestions",
        return_value=mock_ai_result,
    ):
        result = run_onboarding(
            handoff_path=str(handoff_file),
            mode="ai",
            output_dir=str(tmp_path / "outputs"),
        )

    assert result["ai_status"] == "completed"
    assert result["ai_suggestions"] == 1
    assert result["approved"] is False


def test_invalid_mode_rejected(tmp_path, handoff_file):
    with pytest.raises(ValueError, match="Mode"):
        run_onboarding(
            handoff_path=str(handoff_file),
            mode="invalid",
            output_dir=str(tmp_path / "outputs"),
        )


def test_missing_handoff_rejected(tmp_path):
    with pytest.raises(FileNotFoundError):
        run_onboarding(
            handoff_path=str(tmp_path / "missing.json"),
            mode="report",
        )