from typing import Any

from agents.onboarding_planning.handoff_loader import (
    get_handoff_deal_id,
)


def normalize_requirement(
    item: dict[str, Any],
    index: int,
) -> dict[str, Any]:
    """
    Convert an Agent #1 intelligence record into
    a draft onboarding planning requirement.

    Preserve source evidence without treating it
    as independently verified.
    """

    if not isinstance(item, dict):
        raise ValueError(
            "Sales intelligence item must be an object."
        )

    value = item.get("value")

    if not isinstance(value, str) or not value.strip():
        raise ValueError(
            "Sales intelligence item requires a value."
        )

    source_note_ids = item.get("source_note_ids", [])

    if not isinstance(source_note_ids, list):
        raise ValueError(
            "source_note_ids must be a list."
        )

    if any(
        not isinstance(source_id, (str, int))
        or isinstance(source_id, bool)
        for source_id in source_note_ids
    ):
        raise ValueError(
            "source_note_ids must contain strings or integers."
        )

    category = item.get("category", "uncategorized")
    status = item.get("status", "unknown")
    evidence = item.get("evidence")

    if not isinstance(category, str):
        category = "uncategorized"

    if not isinstance(status, str):
        status = "unknown"

    if evidence is not None and not isinstance(evidence, str):
        raise ValueError(
            "evidence must be a string or null."
        )

    return {
        "requirement_id": f"REQ-{index:03d}",
        "category": category,
        "description": value.strip(),
        "source_status": status,
        "evidence": evidence,
        "source_note_ids": [
            str(source_id)
            for source_id in source_note_ids
        ],
        "requires_verification": True,
        "planning_status": "proposed",
    }


def extract_onboarding_requirements(
    handoff: dict[str, Any],
) -> dict[str, Any]:
    """
    Extract planning inputs from a saved handoff.

    This function does not approve or execute
    onboarding activities.
    """

    deal_id = get_handoff_deal_id(handoff)

    sales_intelligence = handoff.get(
        "sales_intelligence", []
    )

    if not isinstance(sales_intelligence, list):
        raise ValueError(
            "sales_intelligence must be a list."
        )

    requirements = []

    for index, item in enumerate(
        sales_intelligence, start=1
    ):
        requirements.append(
            normalize_requirement(item, index)
        )

    missing_information = handoff.get(
        "missing_information", []
    )

    if not isinstance(missing_information, list):
        raise ValueError(
            "missing_information must be a list."
        )

    return {
        "deal_id": deal_id,
        "requirements": requirements,
        "missing_information": missing_information.copy(),
        "requires_human_review": True,
        "approved": False,
    }