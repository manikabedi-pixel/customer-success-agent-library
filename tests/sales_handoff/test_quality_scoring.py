from agents.sales_handoff.quality_scoring import (
    calculate_handoff_quality,
)


def test_quality_score_with_complete_evidence():
    draft = {
        "sales_intelligence": [
            {
                "status": "confirmed",
                "evidence": "Customer requested consolidated reporting.",
                "source_note_ids": ["NOTE-001"],
            }
        ],
        "missing_information": [],
        "onboarding_risks": [],
        "status": "draft",
        "requires_human_review": True,
    }

    result = calculate_handoff_quality(draft)

    assert result["score"] == 100
    assert result["breakdown"]["evidence_coverage"] == 30
    assert result["requires_human_review"] is True


def test_quality_score_penalizes_missing_information():
    draft = {
        "sales_intelligence": [
            {
                "status": "confirmed",
                "evidence": "Customer wants better reporting.",
                "source_note_ids": ["NOTE-002"],
            }
        ],
        "missing_information": [
            "Implementation owner missing",
            "Timeline not confirmed",
        ],
        "onboarding_risks": [],
        "status": "draft",
        "requires_human_review": True,
    }

    result = calculate_handoff_quality(draft)

    assert result["score"] == 90
    assert result["breakdown"]["missing_information"] == 15


def test_quality_score_without_evidence():
    draft = {
        "sales_intelligence": [
            {
                "status": "confirmed",
                "evidence": "",
                "source_note_ids": [],
            }
        ],
        "missing_information": [],
        "onboarding_risks": [],
        "status": "draft",
        "requires_human_review": True,
    }

    result = calculate_handoff_quality(draft)

    assert result["breakdown"]["evidence_coverage"] == 0
    assert result["score"] == 70


def test_quality_score_never_approves_handoff():
    draft = {
        "sales_intelligence": [],
        "missing_information": [],
        "onboarding_risks": [],
        "status": "approved",
        "requires_human_review": False,
    }

    result = calculate_handoff_quality(draft)

    assert result["breakdown"]["human_review_safeguards"] == 0
    assert result["requires_human_review"] is True

def test_empty_handoff_has_low_quality_score():
    draft = {
        "sales_intelligence": [],
        "missing_information": [],
        "onboarding_risks": [],
        "status": "draft",
        "requires_human_review": True,
    }

    result = calculate_handoff_quality(draft)

    assert result["score"] == 40
    assert result["rating"] == (
        "Low quality — significant clarification needed"
    )
    assert result["requires_human_review"] is True