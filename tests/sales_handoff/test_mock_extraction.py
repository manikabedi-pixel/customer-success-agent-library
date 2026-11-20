from pathlib import Path

from agents.sales_handoff.mock_extraction import (
    load_mock_extraction,
)

from agents.sales_handoff.extraction import (
    validate_extraction_evidence,
)

from agents.sales_handoff.schemas import Deal

import json


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SAMPLE_DATA_DIR = (
    PROJECT_ROOT
    / "sample_data"
    / "sales_handoff"
)


def test_mock_extraction_loads():
    fixture_path = (
        SAMPLE_DATA_DIR
        / "mock_extraction_002.json"
    )

    extraction = load_mock_extraction(
        fixture_path
    )

    assert len(extraction.extracted_facts) == 7


def test_mock_timeline_is_unconfirmed():
    fixture_path = (
        SAMPLE_DATA_DIR
        / "mock_extraction_002.json"
    )

    extraction = load_mock_extraction(
        fixture_path
    )

    timeline_facts = [
        fact
        for fact in extraction.extracted_facts
        if fact.category == "timeline"
    ]

    assert len(timeline_facts) == 1

    assert (
        timeline_facts[0].status
        == "discussed_unconfirmed"
    )


def test_mock_evidence_validation():
    fixture_path = (
        SAMPLE_DATA_DIR
        / "mock_extraction_002.json"
    )

    deal_path = (
        SAMPLE_DATA_DIR
        / "deal_002.json"
    )

    extraction = load_mock_extraction(
        fixture_path
    )

    with deal_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        deal = Deal.model_validate(
            json.load(file)
        )

    validated = validate_extraction_evidence(
        extraction,
        deal.sales_notes,
    )

    assert len(validated.extracted_facts) == 7