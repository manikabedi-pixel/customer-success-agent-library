import json

import pytest

from agents.onboarding_planning.handoff_loader import (
    get_handoff_review_status,
    load_handoff,
)


def test_load_valid_handoff(tmp_path):
    path = tmp_path / "handoff.json"

    path.write_text(
        json.dumps({
            "deal_id": "DEAL-123",
            "sales_intelligence": [],
            "source_notes": [],
        }),
        encoding="utf-8",
    )

    result = load_handoff(path)

    assert result["deal_id"] == "DEAL-123"


def test_missing_handoff_file_raises_error(tmp_path):
    path = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_handoff(path)


def test_malformed_json_raises_error(tmp_path):
    path = tmp_path / "invalid.json"
    path.write_text("{ invalid }", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid handoff JSON"):
        load_handoff(path)


def test_handoff_must_be_dictionary(tmp_path):
    path = tmp_path / "handoff.json"
    path.write_text("[]", encoding="utf-8")

    with pytest.raises(ValueError, match="expected a JSON object"):
        load_handoff(path)


def test_handoff_requires_deal_id(tmp_path):
    path = tmp_path / "handoff.json"
    path.write_text(
        json.dumps({"sales_intelligence": []}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="deal_id is required"):
        load_handoff(path)


def test_sales_intelligence_must_be_list(tmp_path):
    path = tmp_path / "handoff.json"
    path.write_text(
        json.dumps({
            "deal_id": "DEAL-123",
            "sales_intelligence": "invalid",
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="sales_intelligence"):
        load_handoff(path)


def test_unapproved_handoff_remains_unverified():
    handoff = {
        "deal_id": "DEAL-123",
        "approved": False,
    }

    assert get_handoff_review_status(handoff) == "unverified"


def test_missing_approval_remains_unverified():
    handoff = {"deal_id": "DEAL-123"}

    assert get_handoff_review_status(handoff) == "unverified"


def test_approved_flag_does_not_establish_authorization():
    handoff = {
        "deal_id": "DEAL-123",
        "approved": True,
    }
    assert get_handoff_review_status(handoff) == "unverified"

def test_load_current_agent_report_format(tmp_path):
    path = tmp_path / "handoff.json"

    path.write_text(
        json.dumps({
            "agent": "sales_to_cs_handoff",
            "deal": {
                "deal_id": "373031837427",
            },
            "customer": {
                "name": "Example Customer",
            },
            "sales_intelligence": [],
            "source_notes": [],
            "onboarding_risks": [],
            "missing_information": [],
        }),
        encoding="utf-8",
    )

    result = load_handoff(path)

    assert result["deal"]["deal_id"] == "373031837427"


def test_current_report_without_deal_id_is_rejected(
    tmp_path,
):
    path = tmp_path / "handoff.json"

    path.write_text(
        json.dumps({
            "deal": {},
            "sales_intelligence": [],
        }),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="deal_id"):
        load_handoff(path)