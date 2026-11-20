from agents.sales_handoff.schemas import Deal
from agents.sales_handoff.validation import validate_handoff


def generate_handoff_brief(deal: Deal) -> dict:

    missing_information = validate_handoff(deal)

    handoff_brief = {
        "deal_id": deal.deal_id,
        "customer_name": deal.customer.company_name,
        "product": deal.commercial_details.product,
        "business_objectives": deal.business_objectives,
        "stakeholders": [
            stakeholder.model_dump()
            for stakeholder in deal.stakeholders
        ],
        "implementation_requirements": (
            deal.implementation_requirements
        ),
        "expected_go_live_date": deal.expected_go_live_date,
        "implementation_owner": deal.implementation_owner,
        "missing_information": missing_information,
        "requires_human_review": bool(missing_information),
        "status": "draft"
    }

    return handoff_brief