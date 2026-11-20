import argparse
import json
from pathlib import Path

from agents.sales_handoff.schemas import Deal
from agents.sales_handoff.service import generate_handoff_brief

from agents.sales_handoff.extraction import (
    extract_sales_intelligence,
    validate_extraction_evidence,
)

from agents.sales_handoff.mock_extraction import (
    load_mock_extraction,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

SAMPLE_DATA_DIR = (
    PROJECT_ROOT
    / "sample_data"
    / "sales_handoff"
)


def parse_arguments():
    parser = argparse.ArgumentParser(
        description=(
            "Run the Sales-to-CS Handoff Agent "
            "in mock or live mode."
        )
    )

    parser.add_argument(
        "--mode",
        choices=["mock", "live"],
        default="mock",
        help=(
            "Extraction mode. Defaults to mock "
            "to avoid unintended API charges."
        ),
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    input_path = SAMPLE_DATA_DIR / "deal_002.json"

    output_path = (
        SAMPLE_DATA_DIR
        / f"handoff_{args.mode}_002.json"
    )

    with input_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        deal_data = json.load(file)

    deal = Deal.model_validate(deal_data)

    base_handoff = generate_handoff_brief(deal)

    if args.mode == "mock":
        fixture_path = (
            SAMPLE_DATA_DIR
            / "mock_extraction_002.json"
        )

        extraction = load_mock_extraction(
            fixture_path
        )

    else:
        extraction = extract_sales_intelligence(
            deal.sales_notes
        )

    validated_extraction = validate_extraction_evidence(
        extraction,
        deal.sales_notes,
    )

    base_handoff["ai_extraction"] = (
        validated_extraction.model_dump()
    )

    base_handoff["execution_mode"] = args.mode

    base_handoff["requires_human_review"] = True

    base_handoff["status"] = "draft"

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            base_handoff,
            file,
            indent=2,
        )

    print("\nSales-to-CS Handoff Agent V0.2")
    print("-" * 40)

    print(f"Execution mode: {args.mode.upper()}")

    if args.mode == "mock":
        print("OpenAI API calls: NONE")
    else:
        print("OpenAI API calls: ENABLED")

    print(f"Output: {output_path}")

    print("\nExtracted Facts:")

    for fact in validated_extraction.extracted_facts:
        print(
            f"- {fact.category}: {fact.value} "
            f"[{fact.status}]"
        )

    print("\nHandoff status: DRAFT")
    print("Human review required: YES")


if __name__ == "__main__":
    main()