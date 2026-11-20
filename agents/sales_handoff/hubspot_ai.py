import argparse

from integrations.crm.handoff_input import build_handoff_input

from agents.sales_handoff.extraction import (
    extract_sales_intelligence,
    validate_extraction_evidence,
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Extract sales intelligence from a HubSpot deal."
    )

    parser.add_argument(
        "--deal-id",
        required=True,
        help="HubSpot deal ID",
    )

    parser.add_argument(
        "--mode",
        choices=["inspect", "live"],
        default="inspect",
        help=(
            "inspect: show CRM source notes without AI calls; "
            "live: run OpenAI extraction."
        ),
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    handoff_input = build_handoff_input(args.deal_id)

    sales_notes = [
        note["text"]
        for note in handoff_input["source_notes"]
        if note["text"].strip()
    ]

    if not sales_notes:
        raise ValueError(
            "No readable sales notes were found for this deal."
        )

    print("\n=== HUBSPOT SALES INTELLIGENCE ===")
    print("Deal:", handoff_input["deal_name"])
    print("Company:", handoff_input["company"]["name"])
    print("Sales notes:", len(sales_notes))

    if args.mode == "inspect":
        print("\nMode: INSPECT")
        print("OpenAI API calls: NONE")

        for note in handoff_input["source_notes"]:
            print("\nSource ID:", note["source_id"])
            print(note["text"])

        print("\nAI extraction not executed.")
        return

    print("\nMode: LIVE")
    print("OpenAI API calls: ENABLED")

    extraction = extract_sales_intelligence(sales_notes)

    validated = validate_extraction_evidence(
        extraction,
        sales_notes,
    )

    print("\n=== VALIDATED EXTRACTED FACTS ===")

    for fact in validated.extracted_facts:
        print("\nCategory:", fact.category)
        print("Value:", fact.value)
        print("Status:", fact.status)
        print("Evidence:", fact.evidence)

    print("\nStatus: DRAFT")
    print("Human review required: YES")


if __name__ == "__main__":
    main()