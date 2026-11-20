import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from integrations.crm.handoff_input import build_handoff_input

from agents.sales_handoff.extraction import (
    extract_sales_intelligence,
    validate_extraction_evidence,
)

from agents.sales_handoff.handoff_rules import (
    identify_missing_information,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sales_handoff"


def build_handoff_draft(deal_id: str) -> dict:
    """
    Generate a Sales-to-CS handoff draft from HubSpot data.

    Steps:
    1. Retrieve deal information from HubSpot.
    2. Extract sales intelligence using OpenAI.
    3. Validate extracted evidence.
    4. Identify missing information.
    5. Identify onboarding risks.
    6. Generate a structured handoff draft.

    This function does not modify HubSpot.
    """

    # --------------------------------------------------
    # STEP 1: Retrieve HubSpot CRM data
    # --------------------------------------------------

    handoff_input = build_handoff_input(deal_id)

    source_notes = handoff_input["source_notes"]

    sales_notes = [
        note["text"]
        for note in source_notes
        if note["text"].strip()
    ]

    if not sales_notes:
        raise ValueError(
            "Cannot generate AI handoff: no readable sales notes."
        )

    # --------------------------------------------------
    # STEP 2: Extract sales intelligence using OpenAI
    # --------------------------------------------------

    extraction = extract_sales_intelligence(sales_notes)

    # --------------------------------------------------
    # STEP 3: Validate supporting evidence
    # --------------------------------------------------

    validated = validate_extraction_evidence(
        extraction,
        sales_notes,
    )

    # --------------------------------------------------
    # STEP 4: Attach HubSpot source note IDs
    # --------------------------------------------------

    extracted_facts = []

    for fact in validated.extracted_facts:
        fact_data = fact.model_dump()

        matching_source_ids = [
            note["source_id"]
            for note in source_notes
            if fact.evidence in note["text"]
        ]

        # Do not include facts without matching source evidence.
        if not matching_source_ids:
            continue

        fact_data["source_note_ids"] = matching_source_ids

        extracted_facts.append(fact_data)

    # --------------------------------------------------
    # STEP 5: Identify missing information
    # --------------------------------------------------

    missing_information = identify_missing_information(
        extracted_facts
    )

    # --------------------------------------------------
    # STEP 6: Identify onboarding risks
    # --------------------------------------------------

    onboarding_risks = []

    for fact in extracted_facts:
        status = fact["status"]
        value = fact["value"]
        source_note_ids = fact["source_note_ids"]

        if status == "discussed_unconfirmed":
            onboarding_risks.append({
                "description": value,
                "reason": "Discussed but not confirmed",
                "source_note_ids": source_note_ids,
            })

        if status == "customer_requested":
            onboarding_risks.append({
                "description": value,
                "reason": "Customer request requires scope confirmation",
                "source_note_ids": source_note_ids,
            })

    # --------------------------------------------------
    # STEP 7: Build the structured handoff draft
    # --------------------------------------------------

    draft = {
        "agent": "sales_to_cs_handoff",
        "version": "0.5.3",
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "source_system": "hubspot",
        "execution_mode": "live",

        "deal": {
            "deal_id": handoff_input["deal_id"],
            "deal_name": handoff_input["deal_name"],
            "amount": handoff_input["deal_amount"],
            "stage": handoff_input["deal_stage"],
        },

        "customer": handoff_input["company"],
        "stakeholders": handoff_input["stakeholders"],
        "sales_intelligence": extracted_facts,
        "missing_information": missing_information,
        "onboarding_risks": onboarding_risks,

 "source_notes": [
    {
        "source_id": note["source_id"],
        "source_type": note["source_type"],
        "timestamp": note["timestamp"],
        "evidence_excerpts": list(dict.fromkeys(
            fact["evidence"]
            for fact in extracted_facts
            if str(note["source_id"]) in {
                str(source_id)
                for source_id in fact.get("source_note_ids", [])
            }
            and isinstance(fact.get("evidence"), str)
            and fact["evidence"].strip()
            and fact["evidence"] in note["text"]
        )),
    }
    for note in source_notes
],

        "requires_human_review": True,
        "status": "draft",
    }

    return draft


def main():
    """
    Command-line entry point for generating a handoff.
    """

    parser = argparse.ArgumentParser(
        description="Generate a HubSpot Sales-to-CS Handoff Draft."
    )

    parser.add_argument(
        "--deal-id",
        required=True,
        help="HubSpot deal ID",
    )

    parser.add_argument(
        "--mode",
        choices=["live"],
        required=True,
        help="AI execution mode. Currently supports live only.",
    )

    args = parser.parse_args()

    # Generate the handoff draft.
    draft = build_handoff_draft(args.deal_id)

    # Create output directory if it does not exist.
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        OUTPUT_DIR
        / f"hubspot_handoff_{args.deal_id}.json"
    )

    # Save the structured JSON handoff.
    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            draft,
            file,
            indent=2,
        )

    # Display execution summary.
    print("\n=== SALES-TO-CS HANDOFF DRAFT ===")

    print(
        "Deal:",
        draft["deal"]["deal_name"],
    )

    print(
        "Customer:",
        draft["customer"]["name"],
    )

    print(
        "Extracted facts:",
        len(draft["sales_intelligence"]),
    )

    print(
        "Missing information:",
        len(draft["missing_information"]),
    )

    print(
        "Onboarding risks:",
        len(draft["onboarding_risks"]),
    )

    print(
        "Status:",
        draft["status"],
    )

    print("Human review required: YES")

    print("\nOutput:", output_path)


if __name__ == "__main__":
    main()