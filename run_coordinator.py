import argparse
import json
from pathlib import Path
from typing import Any

from agents.onboarding_coordinator.ai_coordination_workflow import (
    run_ai_coordination,
)
from agents.onboarding_coordinator.blocker_detector import (
    detect_task_issues,
)
from agents.onboarding_coordinator.markdown_renderer import (
    render_coordination_markdown,
)
from agents.onboarding_coordinator.plan_loader import (
    build_coordination_state,
    load_onboarding_report,
)
from agents.onboarding_coordinator.report_generator import (
    generate_coordination_report,
)


def run_coordinator(
    plan_path: str | Path,
    mode: str = "report",
    output_dir: str | Path = "outputs/onboarding_coordinator",
    client: Any = None,
) -> dict[str, Any]:
    """
    Run Agent #3's read-only coordination workflow.

    Modes:
        report: deterministic analysis, no AI API call
        ai: AI-assisted recommendations

    Neither mode authorizes onboarding execution.
    """

    if mode not in {"report", "ai"}:
        raise ValueError(
            "Mode must be 'report' or 'ai'."
        )

    source_report = load_onboarding_report(plan_path)
    state = build_coordination_state(source_report)

    ai_result = {
        "status": "skipped",
        "recommendations": [],
        "requires_human_review": True,
        "approved": False,
    }

    if mode == "ai":
        issues = detect_task_issues(state)

        ai_result = run_ai_coordination(
            issues=issues,
            client=client,
        )

    report = generate_coordination_report(
        state=state,
        ai_result=ai_result,
    )

    markdown = render_coordination_markdown(report)

    destination = Path(output_dir)
    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Separate filenames prevent report mode from
    # overwriting AI mode output, and vice versa.
    json_path = (
        destination
        / f"coordination_report_{state.deal_id}_{mode}.json"
    )

    markdown_path = (
        destination
        / f"coordination_report_{state.deal_id}_{mode}.md"
    )

    json_path.write_text(
        json.dumps(
            report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    markdown_path.write_text(
        markdown,
        encoding="utf-8",
    )

    return {
        "deal_id": state.deal_id,
        "customer_name": state.customer_name,
        "mode": mode,
        "milestones": report["progress"]["total_milestones"],
        "tasks": report["progress"]["total_tasks"],
        "issues": report["issue_summary"]["total_issues"],
        "ai_status": report["ai"]["status"],
        "ai_recommendations": len(
            report["ai"]["recommendations"]
        ),
        "requires_human_review": report["requires_human_review"],
        "approved": report["approved"],
        "can_execute_onboarding": report["can_execute_onboarding"],
        "json_report": str(json_path),
        "markdown_report": str(markdown_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate read-only onboarding coordination reports."
        )
    )

    parser.add_argument(
        "--plan",
        required=True,
        help="Path to Agent #2's onboarding JSON report.",
    )

    parser.add_argument(
        "--mode",
        choices=["report", "ai"],
        default="report",
        help="Run deterministic or AI-assisted analysis.",
    )

    parser.add_argument(
        "--output-dir",
        default="outputs/onboarding_coordinator",
        help="Directory for generated reports.",
    )

    args = parser.parse_args()

    if args.mode == "ai":
        from dotenv import load_dotenv

        # Explicit path avoids python-dotenv issues
        # with Python 3.15 and stdin execution.
        load_dotenv(dotenv_path=".env")

    summary = run_coordinator(
        plan_path=args.plan,
        mode=args.mode,
        output_dir=args.output_dir,
    )

    print(
        json.dumps(
            summary,
            indent=2,
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()