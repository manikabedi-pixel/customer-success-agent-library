def consolidate_recommendations(
    recommendations: list[str],
) -> list[str]:
    """
    Consolidate exact overlapping customer-request and risk actions.

    Preserves unrelated recommendations.
    Does not call external APIs.
    """

    request_prefix = "Confirm scope and feasibility: "
    risk_prefix = "Review onboarding risk: "

    request_values = {
        item[len(request_prefix):]
        for item in recommendations
        if item.startswith(request_prefix)
    }

    risk_values = {
        item[len(risk_prefix):]
        for item in recommendations
        if item.startswith(risk_prefix)
    }

    overlapping_values = request_values & risk_values

    consolidated = []
    seen = set()

    for recommendation in recommendations:
        if recommendation.startswith(request_prefix):
            value = recommendation[len(request_prefix):]

            if value in overlapping_values:
                recommendation = (
                    "Confirm scope, feasibility, and onboarding risks: "
                    f"{value}"
                )

        elif recommendation.startswith(risk_prefix):
            value = recommendation[len(risk_prefix):]

            if value in overlapping_values:
                continue

        if recommendation not in seen:
            consolidated.append(recommendation)
            seen.add(recommendation)

    return consolidated