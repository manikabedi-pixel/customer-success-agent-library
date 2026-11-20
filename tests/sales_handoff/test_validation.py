import json
from pathlib import Path

from agents.sales_handoff.schemas import Deal
from agents.sales_handoff.validation import validate_handoff
from agents.sales_handoff.service import generate_handoff_brief


def load_sample_deal():

    project_root = Path(__file__).resolve().parents[2]

    input_path = (
        project_root
        / "sample_data"
        / "sales_handoff"
        / "deal_001.json"
    )

    with open(input_path, "r", encoding="utf-8") as file:
        return Deal.model_validate(json.load(file))


def test_missing_information_detection():

    deal = load_sample_deal()

    missing = validate_handoff(deal)

    assert "Expected go-live date is not confirmed" in missing

    assert "Implementation owner is not assigned" in missing


def test_handoff_requires_human_review():

    deal = load_sample_deal()

    handoff = generate_handoff_brief(deal)

    assert handoff["requires_human_review"] is True

    assert handoff["status"] == "draft"


def test_customer_information():

    deal = load_sample_deal()

    handoff = generate_handoff_brief(deal)

    assert handoff["customer_name"] == "Acme Analytics"

    assert handoff["product"] == "Enterprise Analytics Platform"