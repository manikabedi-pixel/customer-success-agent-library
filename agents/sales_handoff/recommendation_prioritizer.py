def prioritize_recommendations(recommendations: list[str]) -> list[dict]:
    """
    Assign priorities to handoff recommendations.

    Uses deterministic rules.
    Does not call HubSpot or OpenAI.
    """

    prioritized = []

    for recommendation in recommendations:
        text = recommendation.lower()

        if (
            "implementation owner" in text
            or "delivery timeline" in text
            or "before committing" in text
        ):
            priority = "Critical"
            rank = 1

        elif (
            "missing information" in text
            or "scope" in text
            or "feasibility" in text
            or "source evidence" in text
            or "onboarding risks" in text
        ):
            priority = "High"
            rank = 2

        elif "onboarding risk" in text:
            priority = "Medium"
            rank = 3

        else:
            priority = "Low"
            rank = 4

        prioritized.append({
            "recommendation": recommendation,
            "priority": priority,
            "rank": rank,
        })

    return sorted(
        prioritized,
        key=lambda item: item["rank"],
    )