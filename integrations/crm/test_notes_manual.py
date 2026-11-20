import requests

from integrations.crm.hubspot import HubSpotCRMAdapter


def main():
    deal_id = input("Enter your HubSpot Deal ID: ").strip()

    crm = HubSpotCRMAdapter()

    note_ids = crm.get_associated_note_ids(deal_id)

    print("\n=== ASSOCIATED SALES NOTES ===")
    print(f"Found {len(note_ids)} note(s).")

    for note_id in note_ids:
        print("\nNote ID:", note_id)

        try:
            note = crm.get_note(note_id)

            properties = note.get("properties", {})

            print("Note content:")
            print(properties.get("hs_note_body"))

        except requests.exceptions.HTTPError as error:
            response = error.response

            print("\nUnable to retrieve note content.")

            if response is not None:
                print("HTTP status:", response.status_code)

                try:
                    details = response.json()

                    print("Category:", details.get("category"))
                    print("Message:", details.get("message"))

                except ValueError:
                    print("HubSpot returned a non-JSON response.")


if __name__ == "__main__":
    main()