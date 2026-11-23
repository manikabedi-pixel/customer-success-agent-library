import json

from agents.customer_data_migration.source_loader import (
    extract_deal_id,
    load_agent_sources,
    load_json_file,
)


def test_load_valid_json(tmp_path):
    path = tmp_path / "source.json"

    path.write_text(
        json.dumps({"deal_id": "123"}),
        encoding="utf-8",
    )

    result = load_json_file(path)

    assert result["deal_id"] == "123"


def test_reject_json_array(tmp_path):
    path = tmp_path / "source.json"

    path.write_text(
        json.dumps([1, 2, 3]),
        encoding="utf-8",
    )

    try:
        load_json_file(path)

    except ValueError:
        pass

    else:
        raise AssertionError(
            "Expected ValueError for non-object JSON"
        )


def test_extract_top_level_deal_id():
    assert extract_deal_id({
        "deal_id": "123"
    }) == "123"


def test_extract_metadata_deal_id():
    assert extract_deal_id({
        "metadata": {
            "deal_id": "456"
        }
    }) == "456"


def test_missing_deal_id():
    assert extract_deal_id({
        "customer_name": "Example"
    }) is None


def test_load_matching_source(tmp_path):
    path = tmp_path / "agent1.json"

    path.write_text(
        json.dumps({
            "deal_id": "123",
            "customer_name": "Example",
        }),
        encoding="utf-8",
    )

    result = load_agent_sources(
        deal_id="123",
        source_paths={
            "agent_1": path,
        },
    )

    assert "agent_1" in result.sources
    assert result.missing_sources == []
    assert result.warnings == []


def test_reject_mismatched_source(tmp_path):
    path = tmp_path / "agent1.json"

    path.write_text(
        json.dumps({
            "deal_id": "999",
        }),
        encoding="utf-8",
    )

    result = load_agent_sources(
        deal_id="123",
        source_paths={
            "agent_1": path,
        },
    )

    assert "agent_1" not in result.sources
    assert any(
        "mismatch" in warning
        for warning in result.warnings
    )


def test_missing_source_file(tmp_path):
    path = tmp_path / "missing.json"

    result = load_agent_sources(
        deal_id="123",
        source_paths={
            "agent_2": path,
        },
    )

    assert result.missing_sources == ["agent_2"]
    assert result.sources == {}


def test_unverified_source_is_flagged(tmp_path):
    path = tmp_path / "agent3.json"

    path.write_text(
        json.dumps({
            "issues": [],
        }),
        encoding="utf-8",
    )

    result = load_agent_sources(
        deal_id="123",
        source_paths={
            "agent_3": path,
        },
    )

    assert "agent_3" not in result.sources

    assert any(
        "could not be verified" in warning
        for warning in result.warnings
    )


def test_invalid_json_is_not_loaded(tmp_path):
    path = tmp_path / "invalid.json"

    path.write_text(
        "{invalid-json",
        encoding="utf-8",
    )

    result = load_agent_sources(
        deal_id="123",
        source_paths={
            "agent_1": path,
        },
    )

    assert "agent_1" not in result.sources
    assert result.warnings

def test_extract_agent_1_nested_deal_id():
    data = {
        "deal": {
            "deal_id": "373031837427",
            "deal_name": "Northstar Software",
        }
    }

    assert extract_deal_id(data) == "373031837427"


def test_extract_agent_1_nested_numeric_deal_id():
    data = {
        "deal": {
            "deal_id": 373031837427,
        }
    }

    assert extract_deal_id(data) == "373031837427"