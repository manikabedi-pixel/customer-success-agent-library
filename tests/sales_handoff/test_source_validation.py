from agents.sales_handoff.source_validation import (
    validate_source_references,
)


def test_valid_source_id_reference():
    draft = {
        "sales_intelligence": [
            {"source_note_ids": ["427498006250"]}
        ],
        "source_notes": [
            {"source_id": "427498006250"}
        ],
    }

    result = validate_source_references(draft)

    assert result["valid"] is True
    assert result["known_note_count"] == 1
    assert result["invalid_references"] == []
    assert result["facts_without_sources"] == []


def test_legacy_note_id_reference():
    draft = {
        "sales_intelligence": [
            {"source_note_ids": ["NOTE-001"]}
        ],
        "source_notes": [
            {"note_id": "NOTE-001"}
        ],
    }

    result = validate_source_references(draft)

    assert result["valid"] is True


def test_legacy_id_reference():
    draft = {
        "sales_intelligence": [
            {"source_note_ids": ["NOTE-002"]}
        ],
        "source_notes": [
            {"id": "NOTE-002"}
        ],
    }

    result = validate_source_references(draft)

    assert result["valid"] is True


def test_invalid_source_reference():
    draft = {
        "sales_intelligence": [
            {"source_note_ids": ["NOTE-999"]}
        ],
        "source_notes": [
            {"source_id": "NOTE-001"}
        ],
    }

    result = validate_source_references(draft)

    assert result["valid"] is False
    assert result["invalid_references"] == [
        {
            "fact_index": 0,
            "source_note_id": "NOTE-999",
        }
    ]


def test_fact_without_source_reference():
    draft = {
        "sales_intelligence": [
            {"source_note_ids": []}
        ],
        "source_notes": [
            {"source_id": "NOTE-001"}
        ],
    }

    result = validate_source_references(draft)

    assert result["valid"] is False
    assert result["facts_without_sources"] == [0]


def test_multiple_facts_share_one_valid_source():
    draft = {
        "sales_intelligence": [
            {"source_note_ids": ["427498006250"]},
            {"source_note_ids": ["427498006250"]},
            {"source_note_ids": ["427498006250"]},
        ],
        "source_notes": [
            {"source_id": "427498006250"}
        ],
    }

    result = validate_source_references(draft)

    assert result["valid"] is True
    assert result["known_note_count"] == 1
    assert result["invalid_references"] == []


def test_numeric_and_string_ids_match():
    draft = {
        "sales_intelligence": [
            {"source_note_ids": ["427498006250"]}
        ],
        "source_notes": [
            {"source_id": 427498006250}
        ],
    }

    result = validate_source_references(draft)

    assert result["valid"] is True


def test_empty_handoff():
    draft = {
        "sales_intelligence": [],
        "source_notes": [],
    }

    result = validate_source_references(draft)

    assert result["valid"] is True
    assert result["known_note_count"] == 0