import json

import pytest

from agents.customer_data_migration.workflow import (
    run_migration_workflow,
)


def test_workflow_generates_both_reports(tmp_path):
    result = run_migration_workflow(
        deal_id="TEST-001",
        customer_name="Synthetic Customer",
        output_dir=tmp_path,
        source_paths={},
    )

    assert result.json_path.exists()
    assert result.markdown_path.exists()


def test_workflow_preserves_deal_id(tmp_path):
    result = run_migration_workflow(
        deal_id="TEST-002",
        output_dir=tmp_path,
        source_paths={},
    )

    assert result.report["deal_id"] == "TEST-002"


def test_workflow_requires_human_review(tmp_path):
    result = run_migration_workflow(
        deal_id="TEST-003",
        output_dir=tmp_path,
        source_paths={},
    )

    assert result.report["requires_human_review"] is True


def test_workflow_never_authorizes_migration(tmp_path):
    result = run_migration_workflow(
        deal_id="TEST-004",
        output_dir=tmp_path,
        source_paths={},
    )

    assert result.report["migration_authorized"] is False


def test_workflow_handles_missing_sources(tmp_path):
    result = run_migration_workflow(
        deal_id="TEST-005",
        output_dir=tmp_path,
        source_paths={
            "agent_1": tmp_path / "missing.json",
        },
    )

    assert result.report["readiness_status"] == (
        "scope_not_established"
    )

    assert result.report["metadata"]["source_loading"][
        "missing_sources"
    ]


def test_workflow_generates_valid_json(tmp_path):
    result = run_migration_workflow(
        deal_id="TEST-006",
        output_dir=tmp_path,
        source_paths={},
    )

    saved = json.loads(
        result.json_path.read_text(encoding="utf-8")
    )

    assert saved["deal_id"] == "TEST-006"


def test_workflow_rejects_empty_deal_id(tmp_path):
    with pytest.raises(ValueError):
        run_migration_workflow(
            deal_id="",
            output_dir=tmp_path,
            source_paths={},
        )


def test_workflow_report_contains_recommendation(tmp_path):
    result = run_migration_workflow(
        deal_id="TEST-007",
        output_dir=tmp_path,
        source_paths={},
    )

    assert len(result.report["recommendations"]) == 1

    assert (
        "historical data migration"
        in result.report["recommendations"][0]["description"]
    )