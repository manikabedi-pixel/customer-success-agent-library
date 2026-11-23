import pytest

from agents.onboarding_planning.risk_rules import (
    normalize_onboarding_risks,
)


def test_normalize_risks():
    handoff = {
        "onboarding_risks": [
            {
                "description": "Integration requirements unclear",
                "reason": "Technical scope not confirmed",
                "source_note_ids": ["NOTE-001"],
            }
        ]
    }

    result = normalize_onboarding_risks(handoff)

    assert len(result) == 1
    assert result[0]["risk_id"] == "RISK-001"
    assert result[0]["status"] == "requires_review"
    assert result[0]["source_note_ids"] == ["NOTE-001"]


def test_empty_risks():
    assert normalize_onboarding_risks({}) == []


def test_invalid_risk_rejected():
    with pytest.raises(ValueError, match="description"):
        normalize_onboarding_risks({
            "onboarding_risks": [{}]
        })