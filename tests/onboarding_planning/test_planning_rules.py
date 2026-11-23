import pytest

from agents.onboarding_planning.planning_rules import (
    get_planning_rule,
    validate_requirement_for_planning,
)


def test_business_objective_rule():
    rule = get_planning_rule("business_objective")

    assert rule["milestone"] == "Success Alignment"


def test_integration_rule():
    rule = get_planning_rule("integration")

    assert rule["milestone"] == "Technical Discovery"


def test_migration_rule():
    rule = get_planning_rule("migration")

    assert rule["milestone"] == "Data Readiness"


def test_stakeholder_rule():
    rule = get_planning_rule("stakeholder")

    assert rule["milestone"] == "Stakeholder Alignment"


def test_timeline_rule():
    rule = get_planning_rule("timeline")

    assert rule["milestone"] == "Implementation Planning"


def test_unknown_category_is_not_discarded():
    rule = get_planning_rule("unknown_category")

    assert rule["milestone"] == "Additional Discovery"


def test_category_normalization():
    rule = get_planning_rule(" INTEGRATION ")

    assert rule["milestone"] == "Technical Discovery"


def test_requirement_requires_description():
    with pytest.raises(ValueError, match="description"):
        validate_requirement_for_planning({})


def test_valid_requirement_passes():
    validate_requirement_for_planning({
        "description": "Confirm CRM integration",
        "source_note_ids": ["NOTE-001"],
    })


def test_invalid_source_references_rejected():
    with pytest.raises(ValueError, match="source_note_ids"):
        validate_requirement_for_planning({
            "description": "Confirm integration",
            "source_note_ids": "NOTE-001",
        })