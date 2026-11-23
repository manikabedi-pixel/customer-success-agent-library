from typing import Any

from agents.onboarding_coordinator.ai_coordinator import (
    generate_coordination_recommendations,
)
from agents.onboarding_coordinator.ai_validation import (
    validate_coordination_recommendations,
)


def run_ai_coordination(
    issues: list[dict[str, Any]],
    client: Any = None,
) -> dict[str, Any]:
    """
    Generate and validate AI recommendations.

    Fail safely if generation or validation fails.
    """

    if not issues:
        return {
            "status": "skipped",
            "recommendations": [],
            "requires_human_review": False,
            "approved": False,
        }

    try:
        ai_result = generate_coordination_recommendations(
            issues=issues,
            client=client,
        )

        recommendations = validate_coordination_recommendations(
            ai_result=ai_result,
            issues=issues,
        )

        return {
            "status": "completed",
            "recommendations": recommendations,
            "requires_human_review": True,
            "approved": False,
        }

    except (ValueError, TypeError, KeyError, RuntimeError) as error:
        return {
            "status": "failed",
            "recommendations": [],
            "error": str(error),
            "requires_human_review": True,
            "approved": False,
        }