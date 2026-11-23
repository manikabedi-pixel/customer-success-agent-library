import json

import pytest

from agents.onboarding_planning.report_generator import (
    build_onboarding_report,
    save_json_report,
    save_markdown_report,
)
from agents.onboarding_planning.schemas import OnboardingPlan


def test_report_remains_unapproved():
    plan = OnboardingPlan(deal_id="DEAL-123")

    assessment = {
        "deal_id": "DEAL-123",
        "onboarding_risks": [],
    }

    ai_result = {
        "ai_status": "skipped",
        "suggestions": [],
    }

    report = build_onboarding_report(
        plan, assessment, ai_result
    )

    assert report["approved"] is False
    assert report["requires_human_review"] is True
    assert report["can_execute_onboarding"] is False


def test_report_rejects_mismatched_deal():
    plan = OnboardingPlan(deal_id="DEAL-123")

    with pytest.raises(ValueError, match="deal_id"):
        build_onboarding_report(
            plan,
            {"deal_id": "DEAL-999"},
            {
                "ai_status": "skipped",
                "suggestions": [],
            },
        )


def test_json_report_is_saved(tmp_path):
    path = tmp_path / "report.json"

    report = {
        "deal_id": "DEAL-123",
        "approved": False,
    }

    save_json_report(report, path)

    saved = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert saved["approved"] is False


def test_markdown_report_is_saved(tmp_path):
    path = tmp_path / "report.md"

    save_markdown_report(
        "# Draft Onboarding Plan",
        path,
    )

    assert path.read_text(
        encoding="utf-8"
    ) == "# Draft Onboarding Plan"