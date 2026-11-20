def generate_quality_recommendations(draft: dict) -> list[str]:
    """
    Generate actionable recommendations from handoff data.

    Uses existing facts and missing information.
    Does not call HubSpot or OpenAI.
    """

    recommendations = []

    missing_information = draft.get("missing_information", [])
    facts = draft.get("sales_intelligence", [])
    risks = draft.get("onboarding_risks", [])

    # 1. Resolve missing information.
    for item in missing_information:
        recommendations.append(
            f"Resolve missing information: {item}"
        )

    # 2. Verify unconfirmed commitments.
    for fact in facts:
        if fact.get("status") == "discussed_unconfirmed":
            recommendations.append(
                f"Verify before committing: {fact.get('value', 'Unspecified item')}"
            )

    # 3. Clarify customer requests.
    for fact in facts:
        if fact.get("status") == "customer_requested":
            recommendations.append(
                f"Confirm scope and feasibility: {fact.get('value', 'Unspecified request')}"
            )

    # 4. Review onboarding risks.
    for risk in risks:
        if isinstance(risk, dict):
            description = risk.get(
                "description",
                risk.get("risk", "Unspecified risk"),
            )
        else:
            description = str(risk)

        recommendations.append(
            f"Review onboarding risk: {description}"
        )

    # 5. Check evidence coverage.
    if not facts:
        recommendations.append(
            "Collect and validate sales discovery information before handoff."
        )
    else:
        unsupported = [
            fact for fact in facts
            if not fact.get("evidence")
            or not fact.get("source_note_ids")
        ]

        if unsupported:
            recommendations.append(
                "Verify source evidence for extracted sales intelligence."
            )

    # Remove duplicate recommendations while preserving order.
    return list(dict.fromkeys(recommendations))