import json

import pytest

from agents.onboarding_coordinator.plan_loader import (
    build_coordination_state,
    convert_milestone,
    convert_task,
    load_onboarding_report,
)


def make_report():
    return {
        "deal_id": "DEAL-123",
        "customer_name": "Example Customer",
        "version": "0.0.9",
        "approved": False,
        "onboarding_plan": {
            "deal_id": "DEAL-123",
            "milestones": [
                {
                    "milestone_id": "MILESTONE-001",
                    "title": "Technical Discovery",
                    "target_date": None,
                    "tasks": [
                        {
                            "task_id": "TASK-001",
                            "title": "Confirm integration scope",
                            "description": "CRM integration discussed",
                            "owner": None,
                            "due_date": None,
                            "dependencies": [],
                            "source_references": ["NOTE-001"],
                            "status": "proposed",
                        }
                    ],
                }
            ],
        },
    }


def test_load_valid_report(tmp_path):
    path = tmp_path / "report.json"
    path.write_text(
        json.dumps(make_report()),
        encoding="utf-8",
    )

    report = load_onboarding_report(path)

    assert report["deal_id"] == "DEAL-123"


def test_missing_report_raises_error(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_onboarding_report(tmp_path / "missing.json")


def test_invalid_json_rejected(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("{invalid", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid"):
        load_onboarding_report(path)


def test_mismatched_deal_ids_rejected(tmp_path):
    report = make_report()
    report["onboarding_plan"]["deal_id"] = "DEAL-999"

    path = tmp_path / "report.json"
    path.write_text(json.dumps(report), encoding="utf-8")

    with pytest.raises(ValueError, match="deal IDs"):
        load_onboarding_report(path)


def test_task_preserves_source_references():
    task = {
        "task_id": "TASK-001",
        "title": "Confirm scope",
        "dependencies": ["TASK-002"],
        "source_references": ["NOTE-123"],
    }

    converted = convert_task(task)

    assert converted.dependencies == ["TASK-002"]
    assert converted.source_references == ["NOTE-123"]


def test_task_import_resets_status():
    task = {
        "task_id": "TASK-001",
        "title": "Confirm scope",
        "status": "completed",
        "completion_percentage": 100,
    }

    converted = convert_task(task)

    assert converted.status == "proposed"
    assert converted.completion_percentage == 0


def test_milestone_import_resets_status():
    milestone = {
        "milestone_id": "MILESTONE-001",
        "title": "Discovery",
        "status": "completed",
        "completion_percentage": 100,
        "tasks": [],
    }

    converted = convert_milestone(milestone)

    assert converted.status == "proposed"
    assert converted.completion_percentage == 0


def test_coordination_state_remains_unapproved():
    report = make_report()

    report["approved"] = True
    report["can_execute_onboarding"] = True

    state = build_coordination_state(report)

    assert state.execution_authorized is False
    assert state.approval.verified is False
    assert state.requires_human_review is True


def test_coordination_state_preserves_milestones():
    state = build_coordination_state(make_report())

    assert len(state.milestones) == 1
    assert len(state.milestones[0].tasks) == 1
    assert state.milestones[0].tasks[0].task_id == "TASK-001"


def test_invalid_task_rejected():
    with pytest.raises(ValueError, match="task_id"):
        convert_task({"title": "Missing ID"})