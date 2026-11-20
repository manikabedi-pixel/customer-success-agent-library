from integrations.crm.service import collect_deal_context


def main():
    deal_id = input("Enter HubSpot Deal ID: ").strip()

    if not deal_id:
        raise ValueError("Deal ID is required.")

    context = collect_deal_context(deal_id)

    deal = context["deal"]["properties"]
    company = context["company"]

    print("\n=== HUBSPOT CRM CONTEXT ===")

    print("Source:", context["source"])
    print("Deal:", deal.get("dealname"))
    print("Amount:", deal.get("amount"))

    if company:
        print(
            "Company:",
            company.get("properties", {}).get("name"),
        )

    print("Associated contacts:", len(context["contacts"]))
    print("Associated notes:", len(context["notes"]))

    for note in context["notes"]:
        print("\nNote ID:", note["note_id"])
        print("Clean text:")
        print(note["clean_text"])

    print("\nStatus:", context["status"])


if __name__ == "__main__":
    main()