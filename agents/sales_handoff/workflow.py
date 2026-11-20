import argparse
import json
from agents.sales_handoff.quality_scoring import calculate_handoff_quality
from agents.sales_handoff.handoff_rules import identify_missing_information

from agents.sales_handoff.hubspot_handoff import (
    OUTPUT_DIR,
    build_handoff_draft,
)

from agents.sales_handoff.report_generator import (
    generate_markdown_report,
)


def run_workflow(deal_id: str, mode: str = "report") -> dict:
    """
    Generate Sales-to-CS handoff outputs.

    report: Use existing JSON. No API calls.
    live: Retrieve HubSpot data and run OpenAI extraction.
    """

    json_path = OUTPUT_DIR / f"hubspot_handoff_{deal_id}.json"
    markdown_path = json_path.with_suffix(".md")
 
    if mode == "live":
        print("\nRetrieving HubSpot data and running AI extraction...")
        draft = build_handoff_draft(deal_id)

    elif mode == "report":
        if not json_path.exists():
            raise FileNotFoundError(
                f"No existing handoff JSON found: {json_path}"
            )

        with json_path.open(encoding="utf-8") as file:
            draft = json.load(file)

    else:
        raise ValueError(f"Unsupported mode: {mode}")

    # Safety: reject handoffs that are not drafts.
    if draft.get("status") != "draft":
        raise ValueError(
            "Only draft handoffs can be processed by this workflow."
        )

    if draft.get("requires_human_review") is not True:
        raise ValueError(
            "Handoff must require human review."
        )

    # Generate the report before writing any files.
    # If report generation fails, no new output is saved.

    # Recalculate missing information using the latest rules.
    draft["missing_information"] = identify_missing_information(
        draft.get("sales_intelligence", [])
    )

    # Calculate handoff quality.
    quality_result = calculate_handoff_quality(draft)
    # Add quality score to the handoff.
    draft["quality_score"] = quality_result
    # Generate the report before writing any files.
    report = generate_markdown_report(draft)
    
    # Save the validated live handoff.

    if mode == "live":
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        with json_path.open("w", encoding="utf-8") as file:
            json.dump(draft, file, indent=2)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    markdown_path.write_text(report, encoding="utf-8")

    print("\n=== SALES-TO-CS HANDOFF WORKFLOW ===")
    print("Deal:", draft["deal"]["deal_name"])
    print("Customer:", draft["customer"]["name"])
    print("Mode:", mode.upper())
    print("Status:", draft["status"])
    print("Human review required: YES")
    print("Quality score:", quality_result["score"], "/ 100")
    print("Quality rating:", quality_result["rating"])
    print("\nJSON:", json_path)
    print("Markdown:", markdown_path)

    return draft


def main():
    parser = argparse.ArgumentParser(
        description="Run the Sales-to-CS Handoff Workflow."
    )

    parser.add_argument(
        "--deal-id",
        required=True,
        help="HubSpot deal ID",
    )

    parser.add_argument(
        "--mode",
        choices=["report", "live"],
        default="report",
        help=(
            "report: regenerate Markdown from existing JSON; "
            "live: retrieve HubSpot data and run OpenAI."
        ),
    )

    args = parser.parse_args()

    run_workflow(
        deal_id=args.deal_id,
        mode=args.mode,
    )

if __name__ == "__main__":
    main()