from integrations.crm.hubspot import HubSpotCRMAdapter
from integrations.crm.normalization import normalize_hubspot_note


def main():
    deal_id = input("Enter HubSpot Deal ID: ").strip()

    crm = HubSpotCRMAdapter()

    note_ids = crm.get_associated_note_ids(deal_id)

    for note_id in note_ids:
        note = crm.get_note(note_id)

        raw_html = note.get("properties", {}).get(
            "hs_note_body", ""
        )

        clean_text = normalize_hubspot_note(raw_html)

        print("\n=== CLEAN SALES NOTES ===")
        print(clean_text)


if __name__ == "__main__":
    main()