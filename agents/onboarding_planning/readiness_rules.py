from typing import Any

from agents.onboarding_planning.handoff_loader import (
    get_handoff_deal_id,
    get_handoff_review_status,
)

def assess_handoff_for_planning(
    handoff: dict[str, Any],
) -> dict[str, Any]:
    """
    Determine whether handoff data can be used to prepare
    a draft onboarding plan.

    This function does not approve onboarding execution.
    """

    deal_id = get_handoff_deal_id(handoff)

    missing_information = handoff.get(
        "missing_information", []
    )

    if not isinstance(missing_information, list):
        raise ValueError(
            "missing_information must be a list."
        )

    unresolved_questions = [
        "Confirm handoff information with the responsible "
        "Sales and Customer Success reviewers."
    ]

    if missing_information:
        unresolved_questions.append(
            "Resolve missing handoff information before "
            "confirming the onboarding plan."
        )

    return {
        "deal_id": deal_id,
        "source_handoff_status": get_handoff_review_status(
            handoff
        ),
        "can_generate_draft": True,
        "can_execute_onboarding": False,
        "requires_human_review": True,
        "approved": False,
        "missing_information": missing_information.copy(),
        "unresolved_questions": unresolved_questions,
    }