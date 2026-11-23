import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from agents.onboarding_planning.schemas import OnboardingPlan


REPORT_WARNING = "DRAFT — HUMAN REVIEW REQUIRED"


def build_onboarding_report(
    plan: OnboardingPlan,
    assessment: dict[str, Any],
    ai_result: dict[str, Any],
) -> dict[str, Any]:
    """
    Combine planning outputs into one reviewable report.

    Does not approve or execute onboarding.
    """

    if assessment.get("deal_id") != plan.deal_id:
        raise ValueError(
            "Assessment deal_id does not match plan."
        )

    if ai_result.get("ai_status") not in {
        "completed",
        "failed",
        "skipped",
    }:
        raise ValueError("Invalid AI planning status.")

    if ai_result.get("ai_status") == "completed":
        if not isinstance(ai_result.get("suggestions"), list):
            raise ValueError(
                "Completed AI result requires suggestions."
            )

    report = {
        "agent": "onboarding_planning",
        "version": "0.0.9",
        "status": REPORT_WARNING,
        "deal_id": plan.deal_id,
        "customer_name": plan.customer_name,
        "onboarding_plan": asdict(plan),
        "planning_assessment": assessment,
        "ai_planning": ai_result,
        "requires_human_review": True,
        "approved": False,
        "can_execute_onboarding": False,
    }

    return report


def save_json_report(
    report: dict[str, Any],
    output_path: str | Path,
) -> Path:
    """Save a structured JSON report."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    return path


def save_markdown_report(
    markdown: str,
    output_path: str | Path,
) -> Path:
    """Save a Markdown report."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    path.write_text(markdown, encoding="utf-8")

    return path