from integrations.crm.handoff_input import build_handoff_input


def main():
    deal_id = input("Enter HubSpot Deal ID: ").strip()

    if not deal_id:
        raise ValueError("Deal ID is required.")

    handoff_input = build_handoff_input(deal_id)

    print("\n=== HANDOFF INPUT ===")

    print("Deal:", handoff_input["deal_name"])
    print("Amount:", handoff_input["deal_amount"])
    print("Company:", handoff_input["company"]["name"])

    print("\n=== STAKEHOLDERS ===")

    for stakeholder in handoff_input["stakeholders"]:
        print(
            stakeholder["name"],
            "-",
            stakeholder["job_title"],
        )

    print("\n=== SOURCE NOTES ===")

    for note in handoff_input["source_notes"]:
        print("Source ID:", note["source_id"])
        print("Text:", note["text"])

    print("\nReview status:", handoff_input["review_status"])


if __name__ == "__main__":
    main()