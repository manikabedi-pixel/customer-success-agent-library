def generate_review_checklist(draft: dict) -> list[str]:
    """
    Generate human-review tasks from the handoff's
    extracted facts and missing information.

    No HubSpot or OpenAI API calls.
    """

    checklist = []

    facts = draft.get("sales_intelligence", [])
    missing_information = draft.get("missing_information", [])

    # Review missing information.
    for item in missing_information:
        checklist.append(f"Resolve missing information: {item}")

    # Review customer requests.
    for fact in facts:
        if fact["status"] == "customer_requested":
            checklist.append(
                f"Confirm scope and approval for: {fact['value']}"
            )

        # Review unconfirmed discussions and timelines.
        elif fact["status"] == "discussed_unconfirmed":
            checklist.append(
                f"Verify before treating as a commitment: {fact['value']}"
            )

    # Universal handoff safety checks.
    checklist.extend([
        "Verify stakeholder contact information.",
        "Review customer requests against the signed agreement.",
        "Confirm no unapproved sales commitments are treated as deliverables.",
    ])

    # Remove duplicate tasks while preserving order.
    return list(dict.fromkeys(checklist))