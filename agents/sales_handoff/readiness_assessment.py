from agents.sales_handoff.source_validation import (
    validate_source_references,
)


def assess_onboarding_readiness(draft: dict) -> dict:
    """
    Assess whether a Sales-to-CS handoff is ready for human review.

    Checks:
    - Extracted sales intelligence
    - Supporting evidence
    - Missing information
    - Unconfirmed commitments
    - Source-note reference validity

    This assessment does not approve the handoff.
    No HubSpot or OpenAI API calls are made.
    """

    # 1. Extract handoff information
    facts = draft.get("sales_intelligence", [])
    missing = draft.get("missing_information", [])

    # 2. Identify facts with supporting evidence
    supported_facts = [
        fact
        for fact in facts
        if fact.get("evidence")
        and fact.get("source_note_ids")
    ]

    # 3. Identify unconfirmed commitments
    unconfirmed = [
        fact
        for fact in facts
        if fact.get("status") == "discussed_unconfirmed"
    ]

    # 4. Validate source-note references
    source_validation = validate_source_references(draft)

    # 5. Generate assessment reasons
    reasons = []

    if not facts:
        reasons.append(
            "No sales intelligence has been extracted."
        )

    if facts and not supported_facts:
        reasons.append(
            "No extracted facts have supporting evidence."
        )

    if len(supported_facts) < len(facts):
        reasons.append(
            "Some extracted facts lack supporting evidence."
        )

    if missing:
        reasons.append(
            f"{len(missing)} missing-information item(s) "
            "require clarification."
        )

    if unconfirmed:
        reasons.append(
            f"{len(unconfirmed)} discussed commitment(s) "
            "remain unconfirmed."
        )

    if not source_validation["valid"]:
        reasons.append(
            "Some source references are missing or invalid."
        )

    # 6. Determine onboarding readiness
    if not facts or not supported_facts:
        readiness = "Insufficient information"

    elif (
        missing
        or unconfirmed
        or len(supported_facts) < len(facts)
        or not source_validation["valid"]
    ):
        readiness = "Clarification required"

    else:
        readiness = "Ready for human review"

    # 7. Return assessment
    return {
        "readiness": readiness,
        "reasons": list(dict.fromkeys(reasons)),
        "supported_facts": len(supported_facts),
        "total_facts": len(facts),
        "source_validation": source_validation,
        "requires_human_review": True,
        "approved": False,
    }