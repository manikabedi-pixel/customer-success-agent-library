import pytest

from agents.onboarding_planning.plan_generator import (
    generate_draft_plan,
)


def test_generate_plan_from_requirements():
    extracted = {
        "deal_id": "DEAL-123",
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "category": "integration",
                "description": "CRM integration required",
                "source_note_ids": ["NOTE-001"],
                "requires_verification": True,
            }
        ],
        "missing_information": [],
    }

    plan = generate_draft_plan(
        extracted,
        customer_name="Example Customer",
    )

    assert plan.deal_id == "DEAL-123"
    assert plan.customer_name == "Example Customer"
    assert len(plan.milestones) == 1
    assert plan.milestones[0].title == "Technical Discovery"


def test_generated_tasks_remain_proposed():
    extracted = {
        "deal_id": "DEAL-123",
        "requirements": [
            {
                "category": "migration",
                "description": "Historical data migration",
                "source_note_ids": ["NOTE-001"],
            }
        ],
    }

    plan = generate_draft_plan(extracted)

    task = plan.milestones[0].tasks[0]

    assert task.status == "proposed"
    assert task.owner is None
    assert task.due_date is None
    assert task.dependencies == []


def test_source_references_are_preserved():
    extracted = {
        "deal_id": "DEAL-123",
        "requirements": [
            {
                "category": "integration",
                "description": "CRM integration",
                "source_note_ids": ["NOTE-123"],
            }
        ],
    }

    plan = generate_draft_plan(extracted)

    assert (
        plan.milestones[0].tasks[0].source_references
        == ["NOTE-123"]
    )


def test_multiple_requirements_share_milestone():
    extracted = {
        "deal_id": "DEAL-123",
        "requirements": [
            {
                "category": "integration",
                "description": "CRM integration",
                "source_note_ids": [],
            },
            {
                "category": "integration",
                "description": "ERP integration",
                "source_note_ids": [],
            },
        ],
    }

    plan = generate_draft_plan(extracted)

    assert len(plan.milestones) == 1
    assert len(plan.milestones[0].tasks) == 2


def test_business_objectives_are_preserved():
    extracted = {
        "deal_id": "DEAL-123",
        "requirements": [
            {
                "category": "business_objective",
                "description": "Reduce time to value",
                "source_note_ids": [],
            }
        ],
    }

    plan = generate_draft_plan(extracted)

    assert plan.objectives == ["Reduce time to value"]


def test_plan_is_never_automatically_approved():
    extracted = {
        "deal_id": "DEAL-123",
        "approved": True,
        "requirements": [],
    }

    plan = generate_draft_plan(extracted)

    assert plan.approved is False
    assert plan.requires_human_review is True
    assert plan.source_handoff_status == "unverified"


def test_missing_information_is_preserved():
    extracted = {
        "deal_id": "DEAL-123",
        "requirements": [],
        "missing_information": [
            "Implementation owner unknown"
        ],
    }

    plan = generate_draft_plan(extracted)

    assert plan.missing_information == [
        "Implementation owner unknown"
    ]


def test_invalid_deal_id_rejected():
    with pytest.raises(ValueError, match="deal_id"):
        generate_draft_plan({
            "deal_id": "",
            "requirements": [],
        })


def test_unknown_category_creates_discovery_task():
    extracted = {
        "deal_id": "DEAL-123",
        "requirements": [
            {
                "category": "custom_requirement",
                "description": "Special implementation request",
                "source_note_ids": [],
            }
        ],
    }

    plan = generate_draft_plan(extracted)

    assert plan.milestones[0].title == (
        "Additional Discovery"
    )


def test_empty_requirements_create_reviewable_draft():
    extracted = {
        "deal_id": "DEAL-123",
        "requirements": [],
    }

    plan = generate_draft_plan(extracted)

    assert plan.milestones == []
    assert plan.requires_human_review is True
    assert plan.approved is False