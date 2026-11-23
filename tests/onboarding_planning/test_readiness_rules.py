import pytest

from agents.onboarding_planning.readiness_rules import (
    assess_handoff_for_planning,
)


def test_unapproved_handoff_can_generate_draft():
    handoff = {
        "deal_id": "DEAL-123",
        "approved": False,
    }

    result = assess_handoff_for_planning(handoff)

    assert result["can_generate_draft"] is True
    assert result["can_execute_onboarding"] is False
    assert result["approved"] is False


def test_approved_flag_does_not_authorize_execution():
    handoff = {
        "deal_id": "DEAL-123",
        "approved": True,
    }

    result = assess_handoff_for_planning(handoff)

    assert result["source_handoff_status"] == "unverified"
    assert result["can_execute_onboarding"] is False
    assert result["requires_human_review"] is True


def test_missing_information_is_preserved():
    handoff = {
        "deal_id": "DEAL-123",
        "missing_information": [
            "Implementation owner not confirmed",
        ],
    }

    result = assess_handoff_for_planning(handoff)

    assert result["missing_information"] == [
        "Implementation owner not confirmed"
    ]

    assert any(
        "Resolve missing handoff information" in question
        for question in result["unresolved_questions"]
    )


def test_missing_deal_id_is_rejected():
    with pytest.raises(ValueError, match="deal_id"):
        assess_handoff_for_planning({})


def test_invalid_missing_information_is_rejected():
    handoff = {
        "deal_id": "DEAL-123",
        "missing_information": "invalid",
    }

    with pytest.raises(
        ValueError,
        match="missing_information",
    ):
        assess_handoff_for_planning(handoff)


def test_missing_information_list_is_not_modified():
    original = ["Confirm technical requirements"]

    handoff = {
        "deal_id": "DEAL-123",
        "missing_information": original,
    }

    result = assess_handoff_for_planning(handoff)

    result["missing_information"].append(
        "Confirm project timeline"
    )

    assert original == ["Confirm technical requirements"]

def test_readiness_supports_nested_deal_id():
    handoff = {
        "deal": {
            "deal_id": "373031837427",
        },
        "missing_information": [],
    }

    result = assess_handoff_for_planning(handoff)

    assert result["deal_id"] == "373031837427"
    assert result["can_generate_draft"] is True
    assert result["can_execute_onboarding"] is False