from typing import Any


def validate_coordination_recommendations(
    ai_result: dict[str, Any],
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Validate AI recommendations against supplied issues.

    Structural validation does not establish factual accuracy.
    """

    if not isinstance(ai_result, dict):
        raise ValueError("AI result must be an object.")

    recommendations = ai_result.get("recommendations")

    if not isinstance(recommendations, list):
        raise ValueError(
            "AI recommendations must be a list."
        )

    valid_pairs = {
        (issue["task_id"], issue["issue_type"])
        for issue in issues
    }

    validated = []
    seen_pairs = set()

    for recommendation in recommendations:

        if not isinstance(recommendation, dict):
            raise ValueError(
                "Each recommendation must be an object."
            )

        task_id = recommendation.get("task_id")
        issue_type = recommendation.get("issue_type")

        if (task_id, issue_type) not in valid_pairs:
            raise ValueError(
                "AI recommendation references an unknown issue."
            )

        if (task_id, issue_type) in seen_pairs:
            raise ValueError(
                "Duplicate AI recommendation."
            )

        action = recommendation.get("recommended_action")
        rationale = recommendation.get("rationale")

        if not isinstance(action, str) or not action.strip():
            raise ValueError(
                "Recommended action is required."
            )

        if not isinstance(rationale, str) or not rationale.strip():
            raise ValueError(
                "Recommendation rationale is required."
            )

        if recommendation.get("requires_human_review") is not True:
            raise ValueError(
                "AI recommendations must require human review."
            )

        validated.append({
            "task_id": task_id,
            "issue_type": issue_type,
            "recommended_action": action.strip(),
            "rationale": rationale.strip(),
            "status": "proposed",
            "approved": False,
            "requires_human_review": True,
        })

        seen_pairs.add((task_id, issue_type))

    return validated