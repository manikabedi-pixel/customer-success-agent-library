from typing import Any


CATEGORY_PLANNING_RULES = {
    "business_objective": {
        "milestone": "Success Alignment",
        "task": "Validate customer objectives and success criteria",
    },
    "integration": {
        "milestone": "Technical Discovery",
        "task": "Confirm integration scope and dependencies",
    },
    "migration": {
        "milestone": "Data Readiness",
        "task": "Assess data migration requirements",
    },
    "stakeholder": {
        "milestone": "Stakeholder Alignment",
        "task": "Confirm stakeholder roles and responsibilities",
    },
    "timeline": {
        "milestone": "Implementation Planning",
        "task": "Validate implementation timeline and milestones",
    },
}


def get_planning_rule(category: str) -> dict[str, str]:
    """
    Return a deterministic planning rule.

    Unknown categories remain reviewable rather than
    being silently discarded.
    """

    if not isinstance(category, str):
        raise ValueError("category must be a string.")

    normalized = category.strip().lower()

    return CATEGORY_PLANNING_RULES.get(
        normalized,
        {
            "milestone": "Additional Discovery",
            "task": "Review additional onboarding requirement",
        },
    ).copy()


def validate_requirement_for_planning(
    requirement: dict[str, Any],
) -> None:
    """Validate the minimum information needed for planning."""

    if not isinstance(requirement, dict):
        raise ValueError("Requirement must be an object.")

    description = requirement.get("description")

    if not isinstance(description, str) or not description.strip():
        raise ValueError(
            "Requirement description is required."
        )

    source_note_ids = requirement.get(
        "source_note_ids", []
    )

    if not isinstance(source_note_ids, list):
        raise ValueError(
            "source_note_ids must be a list."
        )