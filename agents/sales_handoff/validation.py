from agents.sales_handoff.schemas import Deal


def validate_handoff(deal: Deal) -> list[str]:
    missing_information = []

    if not deal.business_objectives:
        missing_information.append(
            "Customer business objectives are missing"
        )

    if not deal.stakeholders:
        missing_information.append(
            "Customer stakeholders are missing"
        )

    if not deal.implementation_requirements:
        missing_information.append(
            "Implementation requirements are missing"
        )

    if not deal.expected_go_live_date:
        missing_information.append(
            "Expected go-live date is not confirmed"
        )

    if not deal.implementation_owner:
        missing_information.append(
            "Implementation owner is not assigned"
        )

    return missing_information