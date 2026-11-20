import requests

from integrations.crm.hubspot import HubSpotCRMAdapter


def main():
    deal_id = input("Enter your HubSpot Deal ID: ").strip()

    if not deal_id:
        raise ValueError("Deal ID is required.")

    crm = HubSpotCRMAdapter()

    # Retrieve deal
    deal = crm.get_deal(deal_id)

    print("\n=== DEAL ===")
    print("Name:", deal["properties"].get("dealname"))
    print("Amount:", deal["properties"].get("amount"))
    print("Stage:", deal["properties"].get("dealstage"))

    # Retrieve company
    try:
        company = crm.get_associated_company(deal_id)

    except requests.exceptions.HTTPError as error:
        response = error.response

        print("\n=== HUBSPOT COMPANY ACCESS ERROR ===")

        if response is None:
            print("No HTTP response was available.")
            return

        print("HTTP status:", response.status_code)

        try:
            details = response.json()

            print("Category:", details.get("category"))
            print("Message:", details.get("message"))

            for item in details.get("errors", []):
                print("Detail:", item.get("message"))

        except ValueError:
            print("HubSpot returned a non-JSON error response.")

        return

    print("\n=== COMPANY ===")

    if company:
        print("Name:", company["properties"].get("name"))
    else:
        print("No associated company found.")

    # Retrieve contacts
    contacts = crm.get_associated_contacts(deal_id)

    print("\n=== CONTACTS ===")

    if contacts:
        for contact in contacts:
            properties = contact["properties"]

            print(
                "-",
                properties.get("firstname"),
                properties.get("lastname"),
                "|",
                properties.get("jobtitle"),
            )
    else:
        print("No associated contacts found.")


if __name__ == "__main__":
    main()