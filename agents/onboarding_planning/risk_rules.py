from typing import Any


def normalize_onboarding_risks(
    handoff: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Preserve risks identified by Agent #1.

    Risk descriptions are not treated as verified facts.
    """

    raw_risks = handoff.get("onboarding_risks", [])

    if not isinstance(raw_risks, list):
        raise ValueError(
            "onboarding_risks must be a list."
        )

    normalized = []

    for index, risk in enumerate(raw_risks, start=1):
        if not isinstance(risk, dict):
            raise ValueError(
                "Each onboarding risk must be an object."
            )

        description = risk.get("description")

        if not isinstance(description, str) or not description.strip():
            raise ValueError(
                "Each onboarding risk requires a description."
            )

        source_ids = risk.get("source_note_ids", [])

        if not isinstance(source_ids, list):
            raise ValueError(
                "Risk source_note_ids must be a list."
            )

        normalized.append({
            "risk_id": f"RISK-{index:03d}",
            "description": description.strip(),
            "reason": risk.get("reason"),
            "source_note_ids": [
                str(source_id)
                for source_id in source_ids
            ],
            "status": "requires_review",
            "requires_human_review": True,
        })

    return normalized