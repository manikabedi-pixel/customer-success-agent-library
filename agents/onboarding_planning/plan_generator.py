from typing import Any

from agents.onboarding_planning.planning_rules import (
    get_planning_rule,
    validate_requirement_for_planning,
)

from agents.onboarding_planning.schemas import (
    OnboardingMilestone,
    OnboardingPlan,
    OnboardingTask,
)


def generate_draft_plan(
    extracted: dict[str, Any],
    customer_name: str | None = None,
) -> OnboardingPlan:
    """
    Generate a draft onboarding plan from extracted
    Agent #1 intelligence.

    No tasks are automatically approved, assigned,
    scheduled, or executed.
    """

    deal_id = extracted.get("deal_id")

    if not isinstance(deal_id, str) or not deal_id.strip():
        raise ValueError("Valid deal_id is required.")

    requirements = extracted.get("requirements", [])

    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list.")

    missing_information = extracted.get(
        "missing_information", []
    )

    if not isinstance(missing_information, list):
        raise ValueError(
            "missing_information must be a list."
        )

    milestones_by_title = {}

    objectives = []
    unresolved_questions = [
        "Confirm extracted handoff information with "
        "the responsible Sales and Customer Success reviewers."
    ]

    for index, requirement in enumerate(
        requirements, start=1
    ):
        validate_requirement_for_planning(requirement)

        category = requirement.get(
            "category", "uncategorized"
        )

        rule = get_planning_rule(category)

        milestone_title = rule["milestone"]

        if milestone_title not in milestones_by_title:
            milestone = OnboardingMilestone(
                milestone_id=(
                    f"MILESTONE-{len(milestones_by_title) + 1:03d}"
                ),
                title=milestone_title,
            )

            milestones_by_title[milestone_title] = milestone

        source_ids = requirement.get(
            "source_note_ids", []
        )

        task = OnboardingTask(
            task_id=f"TASK-{index:03d}",
            title=rule["task"],
            description=requirement["description"],
            owner=None,
            due_date=None,
            dependencies=[],
            source_references=[
                str(source_id)
                for source_id in source_ids
            ],
            status="proposed",
        )

        milestones_by_title[
            milestone_title
        ].tasks.append(task)

        if category == "business_objective":
            objectives.append(
                requirement["description"]
            )

        if requirement.get(
            "requires_verification", True
        ):
            unresolved_questions.append(
                f"Verify requirement {requirement.get('requirement_id', index)} "
                "against its original source."
            )

    if missing_information:
        unresolved_questions.append(
            "Resolve missing handoff information "
            "before confirming the onboarding plan."
        )

    return OnboardingPlan(
        deal_id=deal_id,
        customer_name=customer_name,
        objectives=objectives,
        milestones=list(
            milestones_by_title.values()
        ),
        missing_information=missing_information.copy(),
        unresolved_questions=unresolved_questions,
        source_handoff_status="unverified",
        requires_human_review=True,
        approved=False,
        metadata={
            "generated_from": "agent_1_handoff",
            "planning_mode": "draft",
            "requirements_processed": len(requirements),
        },
    )