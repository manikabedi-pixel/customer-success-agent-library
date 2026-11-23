import json
from pathlib import Path
from unittest.mock import patch

import pytest

from run_coordinator import run_coordinator


def make_source_report():
    return {
        "deal_id": "DEAL-123",
        "customer_name": "Example Customer",
        "version": "0.1.0",
        "approved": False,
        "onboarding_plan": {
            "deal_id": "DEAL-123",
            "milestones": [
                {
                    "milestone_id": "MILESTONE-001",
                    "title": "Technical Discovery",
                    "tasks": [
                        {
                            "task_id": "TASK-001",
                            "title": "Confirm integration scope",
                            "owner": None,
                            "due_date": None,
                            "dependencies": [],
                            "source_references": ["NOTE-001"],
                        }
                    ],
                }
            ],
        },
    }


def write_source_report(tmp_path):
    path = tmp_path / "source.json"

    path.write_text(
        json.dumps(make_source_report()),
        encoding="utf-8",
    )

    return path


def test_report_mode_generates_files(tmp_path):
    source_path = write_source_report(tmp_path)
    output_dir = tmp_path / "outputs"

    summary = run_coordinator(
        plan_path=source_path,
        mode="report",
        output_dir=output_dir,
    )

    assert summary["mode"] == "report"
    assert summary["milestones"] == 1
    assert summary["tasks"] == 1
    assert summary["issues"] == 2

    assert Path(summary["json_report"]).exists()
    assert Path(summary["markdown_report"]).exists()


def test_report_mode_does_not_call_ai(tmp_path):
    source_path = write_source_report(tmp_path)

    with patch(
        "run_coordinator.run_ai_coordination"
    ) as mocked_ai:
        summary = run_coordinator(
            plan_path=source_path,
            mode="report",
            output_dir=tmp_path / "outputs",
        )

    mocked_ai.assert_not_called()
    assert summary["ai_status"] == "skipped"


def test_ai_mode_includes_recommendations(tmp_path):
    source_path = write_source_report(tmp_path)

    mocked_result = {
        "status": "completed",
        "recommendations": [
            {
                "task_id": "TASK-001",
                "issue_type": "missing_owner",
                "recommended_action": "Confirm owner.",
                "rationale": "Owner is missing.",
                "status": "proposed",
                "approved": False,
                "requires_human_review": True,
            }
        ],
        "requires_human_review": True,
        "approved": False,
    }

    with patch(
        "run_coordinator.run_ai_coordination",
        return_value=mocked_result,
    ):
        summary = run_coordinator(
            plan_path=source_path,
            mode="ai",
            output_dir=tmp_path / "outputs",
        )

    assert summary["ai_status"] == "completed"
    assert summary["ai_recommendations"] == 1
    assert summary["approved"] is False


def test_ai_failure_does_not_authorize_execution(tmp_path):
    source_path = write_source_report(tmp_path)

    with patch(
        "run_coordinator.run_ai_coordination",
        return_value={
            "status": "failed",
            "recommendations": [],
            "requires_human_review": True,
            "approved": False,
        },
    ):
        summary = run_coordinator(
            plan_path=source_path,
            mode="ai",
            output_dir=tmp_path / "outputs",
        )

    assert summary["ai_status"] == "failed"
    assert summary["can_execute_onboarding"] is False


def test_invalid_mode_rejected(tmp_path):
    source_path = write_source_report(tmp_path)

    with pytest.raises(ValueError, match="Mode"):
        run_coordinator(
            plan_path=source_path,
            mode="execute",
            output_dir=tmp_path / "outputs",
        )


def test_report_and_ai_use_different_filenames(tmp_path):
    source_path = write_source_report(tmp_path)
    output_dir = tmp_path / "outputs"

    report_summary = run_coordinator(
        plan_path=source_path,
        mode="report",
        output_dir=output_dir,
    )

    with patch(
        "run_coordinator.run_ai_coordination",
        return_value={
            "status": "completed",
            "recommendations": [],
            "requires_human_review": True,
            "approved": False,
        },
    ):
        ai_summary = run_coordinator(
            plan_path=source_path,
            mode="ai",
            output_dir=output_dir,
        )

    assert (
        report_summary["json_report"]
        != ai_summary["json_report"]
    )

    assert Path(report_summary["json_report"]).exists()
    assert Path(ai_summary["json_report"]).exists()


def test_generated_json_remains_unapproved(tmp_path):
    source_path = write_source_report(tmp_path)

    summary = run_coordinator(
        plan_path=source_path,
        mode="report",
        output_dir=tmp_path / "outputs",
    )

    report = json.loads(
        Path(summary["json_report"]).read_text(
            encoding="utf-8"
        )
    )

    assert report["approved"] is False
    assert report["can_execute_onboarding"] is False
    assert report["requires_human_review"] is True