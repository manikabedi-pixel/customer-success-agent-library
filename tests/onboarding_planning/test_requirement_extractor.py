import pytest

from agents.onboarding_planning.requirement_extractor import (
    extract_onboarding_requirements,
    normalize_requirement,
)


def test_normalize_requirement_preserves_evidence():
    item = {
        "category": "implementation_requirement",
        "value": "Customer needs CRM integration",
        "status": "extracted",
        "evidence": "Integration discussed during sales call",
        "requires_verification": False,
        "source_note_ids": ["NOTE-123"],
    }

    result = normalize_requirement(item, 1)

    assert result["requirement_id"] == "REQ-001"
    assert result["description"] == (
        "Customer needs CRM integration"
    )
    assert result["evidence"] == (
        "Integration discussed during sales call"
    )
    assert result["source_note_ids"] == ["NOTE-123"]

    # Evidence is preserved, but not treated as approval.
    assert result["requires_verification"] is True
    assert result["planning_status"] == "proposed"


def test_extract_requirements_from_current_handoff():
    handoff = {
        "deal": {
            "deal_id": "373031837427",
            "deal_name": "Example Deal",
        },
        "sales_intelligence": [
            {
                "category": "business_objective",
                "value": "Improve onboarding efficiency",
                "status": "extracted",
                "evidence": "Customer requested faster onboarding",
                "requires_verification": True,
                "source_note_ids": ["NOTE-001"],
            }
        ],
        "missing_information": [
            "Implementation owner not confirmed"
        ],
    }

    result = extract_onboarding_requirements(handoff)

    assert result["deal_id"] == "373031837427"
    assert len(result["requirements"]) == 1
    assert result["approved"] is False
    assert result["requires_human_review"] is True

    assert result["missing_information"] == [
        "Implementation owner not confirmed"
    ]


def test_extract_supports_legacy_handoff():
    handoff = {
        "deal_id": "DEAL-123",
        "sales_intelligence": [],
    }

    result = extract_onboarding_requirements(handoff)

    assert result["deal_id"] == "DEAL-123"
    assert result["requirements"] == []


def test_missing_requirement_value_is_rejected():
    item = {
        "category": "implementation_requirement",
        "source_note_ids": [],
    }

    with pytest.raises(ValueError, match="requires a value"):
        normalize_requirement(item, 1)


def test_invalid_source_note_ids_are_rejected():
    item = {
        "value": "Configure integration",
        "source_note_ids": "NOTE-001",
    }

    with pytest.raises(ValueError, match="source_note_ids"):
        normalize_requirement(item, 1)


def test_source_note_ids_are_normalized_to_strings():
    item = {
        "value": "Configure integration",
        "source_note_ids": [123, "NOTE-456"],
    }

    result = normalize_requirement(item, 1)

    assert result["source_note_ids"] == [
        "123",
        "NOTE-456",
    ]


def test_extraction_does_not_modify_original():
    item = {
        "category": "business_objective",
        "value": "Improve adoption",
        "source_note_ids": ["NOTE-001"],
    }

    handoff = {
        "deal_id": "DEAL-123",
        "sales_intelligence": [item],
        "missing_information": ["Confirm owner"],
    }

    result = extract_onboarding_requirements(handoff)

    result["requirements"][0]["source_note_ids"].append(
        "NOTE-999"
    )
    result["missing_information"].append(
        "Confirm timeline"
    )

    assert item["source_note_ids"] == ["NOTE-001"]
    assert handoff["missing_information"] == [
        "Confirm owner"
    ]


def test_approved_flag_does_not_approve_requirements():
    handoff = {
        "deal_id": "DEAL-123",
        "approved": True,
        "sales_intelligence": [
            {
                "value": "Deliver integration by April",
                "requires_verification": False,
                "source_note_ids": ["NOTE-001"],
            }
        ],
    }

    result = extract_onboarding_requirements(handoff)

    assert result["approved"] is False
    assert (
        result["requirements"][0]["requires_verification"]
        is True
    )