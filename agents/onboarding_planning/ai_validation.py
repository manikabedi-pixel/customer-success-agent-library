from typing import Any


def validate_ai_suggestions(
    suggestions: list[dict[str, Any]],
    requirements: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Validate AI planning suggestions.

    Only explicitly permitted fields are retained.
    """

    if not isinstance(suggestions, list):
        raise ValueError("suggestions must be a list.")

    requirement_ids = {
        item["requirement_id"]
        for item in requirements
    }

    validated = []
    seen_ids = set()

    for suggestion in suggestions:
        if not isinstance(suggestion, dict):
            raise ValueError(
                "Each AI suggestion must be an object."
            )

        requirement_id = suggestion.get("requirement_id")

        if requirement_id not in requirement_ids:
            raise ValueError(
                f"Unknown requirement_id: {requirement_id}"
            )

        if requirement_id in seen_ids:
            raise ValueError(
                f"Duplicate requirement_id: {requirement_id}"
            )

        activity = suggestion.get("suggested_activity")
        rationale = suggestion.get("rationale")

        if not isinstance(activity, str) or not activity.strip():
            raise ValueError(
                "suggested_activity must be a nonempty string."
            )

        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(
                "rationale must be a nonempty string."
            )

        if suggestion.get("requires_human_review") is not True:
            raise ValueError(
                "AI suggestions must require human review."
            )

        validated.append({
            "requirement_id": requirement_id,
            "suggested_activity": activity.strip(),
            "rationale": rationale.strip(),
            "requires_human_review": True,
            "status": "proposed",
        })

        seen_ids.add(requirement_id)

    if seen_ids != requirement_ids:
        raise ValueError(
            "AI must return exactly one suggestion "
            "for each requirement."
        )

    return validated