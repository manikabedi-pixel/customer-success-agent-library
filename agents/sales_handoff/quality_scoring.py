def calculate_handoff_quality(draft: dict) -> dict:
    """
    Calculate a preliminary handoff quality score.

    This is a rules-based score, not an AI judgment.
    It does not approve the handoff.
    """

    facts = draft.get("sales_intelligence", [])
    missing = draft.get("missing_information", [])
    risks = draft.get("onboarding_risks", [])

    # 1. Evidence coverage: 30 points
    if facts:
        supported = sum(
            1
            for fact in facts
            if fact.get("evidence")
            and fact.get("source_note_ids")
        )
        evidence_score = round(30 * supported / len(facts))
    else:
        evidence_score = 0

    # 2. Missing information: 25 points
    missing_score = max(0, 25 - 5 * len(missing))

    # 3. Unconfirmed commitments: 20 points
    unconfirmed = sum(
        1
        for fact in facts
        if fact.get("status") == "discussed_unconfirmed"
    )
    commitment_score = max(0, 20 - 5 * unconfirmed)

    # 4. Onboarding risks: 15 points
    risk_score = max(0, 15 - 3 * len(risks))

    # 5. Human-review safeguards: 10 points
    review_score = (
        10
        if draft.get("status") == "draft"
        and draft.get("requires_human_review") is True
        else 0
    )

    total = (
        evidence_score
        + missing_score
        + commitment_score
        + risk_score
        + review_score
    )

    # An empty handoff cannot be considered high quality.

    # Missing facts may mean missing customer context,

    # not that the handoff has no outstanding issues.

    if not facts:
        total = min(total, 40)

    if total >= 85:
        rating = "High quality — human review required"
    elif total >= 65:
        rating = "Moderate quality — clarification recommended"
    else:
        rating = "Low quality — significant clarification needed"

    return {
        "score": total,
        "maximum_score": 100,
        "rating": rating,
        "breakdown": {
            "evidence_coverage": evidence_score,
            "missing_information": missing_score,
            "unconfirmed_commitments": commitment_score,
            "onboarding_risks": risk_score,
            "human_review_safeguards": review_score,
        },
        "requires_human_review": True,
    }