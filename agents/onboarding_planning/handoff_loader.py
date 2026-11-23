import json
from pathlib import Path
from typing import Any


def get_handoff_deal_id(
    handoff: dict[str, Any],
) -> str:
    """
    Support both the current Agent #1 report format
    and older sample handoff formats.
    """

    deal = handoff.get("deal")

    if isinstance(deal, dict):
        deal_id = deal.get("deal_id")

        if isinstance(deal_id, str) and deal_id.strip():
            return deal_id.strip()

        if isinstance(deal_id, int) and not isinstance(
            deal_id, bool
        ):
            return str(deal_id)

    deal_id = handoff.get("deal_id")

    if isinstance(deal_id, str) and deal_id.strip():
        return deal_id.strip()

    if isinstance(deal_id, int) and not isinstance(
        deal_id, bool
    ):
        return str(deal_id)

    raise ValueError(
        "Invalid handoff: deal_id is required."
    )


def load_handoff(path: str | Path) -> dict[str, Any]:
    """Load a saved Agent #1 handoff report."""

    handoff_path = Path(path)

    if not handoff_path.is_file():
        raise FileNotFoundError(
            f"Handoff file not found: {handoff_path}"
        )

    try:
        with handoff_path.open(
            "r", encoding="utf-8"
        ) as file:
            handoff = json.load(file)

    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid handoff JSON: {error.msg}"
        ) from error

    if not isinstance(handoff, dict):
        raise ValueError(
            "Invalid handoff: expected a JSON object."
        )

    get_handoff_deal_id(handoff)

    for field_name in (
        "sales_intelligence",
        "source_notes",
        "missing_information",
        "onboarding_risks",
    ):
        value = handoff.get(field_name, [])

        if not isinstance(value, list):
            raise ValueError(
                f"Invalid handoff: {field_name} "
                "must be a list."
            )

    return handoff


def get_handoff_review_status(
    handoff: dict[str, Any],
) -> str:
    """
    Saved JSON is not an authoritative approval record.
    """
    return "unverified"