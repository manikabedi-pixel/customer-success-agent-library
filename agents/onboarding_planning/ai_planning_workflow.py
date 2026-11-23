from typing import Any

from agents.onboarding_planning.ai_planner import (
    generate_ai_planning_suggestions,
)
from agents.onboarding_planning.ai_validation import (
    validate_ai_suggestions,
)


def prepare_ai_planning_suggestions(
    extracted: dict[str, Any],
    client: Any = None,
) -> dict[str, Any]:
    """
    Prepare optional AI suggestions.

    A failed AI call must not block deterministic planning.
    """

    requirements = extracted.get("requirements", [])

    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list.")

    if not requirements:
        return {
            "suggestions": [],
            "ai_status": "skipped",
            "requires_human_review": True,
        }

    try:
        raw_suggestions = generate_ai_planning_suggestions(
            requirements=requirements,
            client=client,
        )

        validated = validate_ai_suggestions(
            raw_suggestions,
            requirements,
        )

        return {
            "suggestions": validated,
            "ai_status": "completed",
            "requires_human_review": True,
        }

    except Exception as error:
        return {
            "suggestions": [],
            "ai_status": "failed",
            "error_type": type(error).__name__,
            "requires_human_review": True,
        }