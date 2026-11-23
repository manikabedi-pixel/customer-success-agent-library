import argparse
import json
import sys
from pathlib import Path

from agents.onboarding_planning.handoff_loader import load_handoff
from agents.onboarding_planning.requirement_extractor import (
    extract_onboarding_requirements,
)
from agents.onboarding_planning.plan_generator import generate_draft_plan
from agents.onboarding_planning.planning_assessment import (
    assess_onboarding_plan,
)
from agents.onboarding_planning.ai_planning_workflow import (
    prepare_ai_planning_suggestions,
)
from agents.onboarding_planning.report_generator import (
    build_onboarding_report,
    save_json_report,
    save_markdown_report,
)
from agents.onboarding_planning.markdown_renderer import (
    render_onboarding_markdown,
)


def run_onboarding(
    handoff_path: str,
    mode: str = "report",
    output_dir: str = "outputs/onboarding_planning",
) -> dict:
    """Generate a draft onboarding plan from an Agent #1 handoff."""

    if mode not in {"report", "ai"}:
        raise ValueError("Mode must be 'report' or 'ai'.")

    handoff = load_handoff(handoff_path)
    extracted = extract_onboarding_requirements(handoff)

    customer = handoff.get("customer", {})

    if isinstance(customer, dict):
        customer_name = (
            customer.get("name")
            or customer.get("company_name")
        )
    else:
        customer_name = None

    customer_name = customer_name or handoff.get("customer_name")

    plan = generate_draft_plan(
        extracted,
        customer_name=customer_name,
    )

    assessment = assess_onboarding_plan(plan, handoff)

    if mode == "ai":
        from dotenv import load_dotenv

        load_dotenv(
            dotenv_path=Path(__file__).resolve().parent / ".env"
        )

        ai_result = prepare_ai_planning_suggestions(extracted)
    else:
        ai_result = {
            "ai_status": "skipped",
            "suggestions": [],
            "requires_human_review": True,
        }

    report = build_onboarding_report(
        plan,
        assessment,
        ai_result,
    )

    markdown = render_onboarding_markdown(report)

    destination = Path(output_dir)
    destination.mkdir(parents=True, exist_ok=True)

    # Avoid using an unvalidated deal ID as a filesystem path.
    safe_deal_id = "".join(
        character
        for character in plan.deal_id
        if character.isalnum() or character in "-_"
    )

    if not safe_deal_id:
        raise ValueError("Deal ID cannot be used as a filename.")

    json_path = destination / f"onboarding_plan_{safe_deal_id}.json"
    markdown_path = destination / f"onboarding_plan_{safe_deal_id}.md"

    save_json_report(report, json_path)
    save_markdown_report(markdown, markdown_path)

    return {
        "deal_id": plan.deal_id,
        "mode": mode,
        "milestones": len(plan.milestones),
        "tasks": sum(len(m.tasks) for m in plan.milestones),
        "risks": len(assessment["onboarding_risks"]),
        "ai_status": ai_result["ai_status"],
        "ai_suggestions": len(ai_result["suggestions"]),
        "requires_human_review": True,
        "approved": False,
        "can_execute_onboarding": False,
        "json_report": str(json_path),
        "markdown_report": str(markdown_path),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Customer Success Onboarding Planning Agent"
    )

    parser.add_argument(
        "--handoff",
        required=True,
        help="Path to a saved Agent #1 handoff JSON file",
    )

    parser.add_argument(
        "--mode",
        choices=["report", "ai"],
        default="report",
        help="report: deterministic only; ai: include AI suggestions",
    )

    parser.add_argument(
        "--output-dir",
        default="outputs/onboarding_planning",
    )

    args = parser.parse_args()

    try:
        result = run_onboarding(
            handoff_path=args.handoff,
            mode=args.mode,
            output_dir=args.output_dir,
        )
    except (FileNotFoundError, ValueError, OSError) as error:
        print(f"Onboarding planning failed: {error}", file=sys.stderr)
        return 1

    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())