from datetime import datetime, timezone

from integrations.crm.hubspot import HubSpotCRMAdapter
from integrations.crm.normalization import normalize_hubspot_note


def collect_deal_context(deal_id: str) -> dict:
    """
    Collect live HubSpot CRM context for a deal.

    Read-only operation.
    No AI calls are made.
    """

    crm = HubSpotCRMAdapter()

    deal = crm.get_deal(deal_id)
    company = crm.get_associated_company(deal_id)
    contacts = crm.get_associated_contacts(deal_id)

    notes = []

    for note_id in crm.get_associated_note_ids(deal_id):
        note = crm.get_note(note_id)
        properties = note.get("properties", {})

        raw_html = properties.get("hs_note_body") or ""

        notes.append({
            "note_id": str(note_id),
            "raw_html": raw_html,
            "clean_text": normalize_hubspot_note(raw_html),
            "timestamp": properties.get("hs_timestamp"),
        })

    return {
        "source": "hubspot",
        "retrieved_at": datetime.now(timezone.utc).isoformat(),
        "deal": deal,
        "company": company,
        "contacts": contacts,
        "notes": notes,
        "status": "source_data_only",
    }