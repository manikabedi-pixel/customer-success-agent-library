from integrations.crm.service import collect_deal_context


def build_handoff_input(deal_id: str) -> dict:
    """
    Transform HubSpot CRM data into a structured
    handoff input.

    No AI calls.
    No changes to HubSpot records.
    """

    context = collect_deal_context(deal_id)

    deal = context["deal"].get("properties", {})

    company_record = context.get("company") or {}
    company = company_record.get("properties", {})

    stakeholders = []

    for contact in context.get("contacts", []):
        properties = contact.get("properties", {})

        first_name = properties.get("firstname") or ""
        last_name = properties.get("lastname") or ""

        stakeholders.append({
            "contact_id": str(contact.get("id", "")),
            "name": f"{first_name} {last_name}".strip(),
            "job_title": properties.get("jobtitle"),
            "email": properties.get("email"),
        })

    source_notes = []

    for note in context.get("notes", []):
        source_notes.append({
            "source_type": "hubspot_note",
            "source_id": note["note_id"],
            "text": note["clean_text"],
            "timestamp": note.get("timestamp"),
        })

    return {
        "source_system": "hubspot",
        "deal_id": str(context["deal"].get("id", deal_id)),
        "deal_name": deal.get("dealname"),
        "deal_amount": deal.get("amount"),
        "deal_stage": deal.get("dealstage"),
        "company": {
            "company_id": str(company_record.get("id", "")),
            "name": company.get("name"),
            "industry": company.get("industry"),
            "domain": company.get("domain"),
        },
        "stakeholders": stakeholders,
        "source_notes": source_notes,
        "retrieved_at": context["retrieved_at"],
        "review_status": "pending_human_review",
    }