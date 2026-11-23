import re
from typing import Any

from agents.customer_data_migration.schemas import (
    MigrationRequirement,
)


MIGRATION_PATTERNS = [
    r"\bmigrat(?:e|es|ed|ing|ion)\b",
    r"\bdata\s+transfer\b",
    r"\bimport(?:ing)?\s+(?:historical\s+)?data\b",
    r"\bhistorical\s+data\b",
    r"\blegacy\s+(?:system|data|records)\b",
    r"\bdata\s+conversion\b",
]


def is_migration_related(text: str) -> bool:
    """
    Detect language potentially related to data migration.

    A keyword match is a candidate signal, not proof
    of a contractual migration requirement.
    """

    normalized = text.lower()

    return any(
        re.search(pattern, normalized)
        for pattern in MIGRATION_PATTERNS
    )


def extract_text(value: Any) -> str | None:
    """
    Extract explicit text from supported source structures.

    Arbitrary nested objects are not converted into
    invented or concatenated requirements.
    """

    if isinstance(value, str):
        text = value.strip()

        return text or None

    if isinstance(value, dict):
        for key in (
            "description",
            "text",
            "statement",
            "content",
            "objective",
        ):
            candidate = value.get(key)

            if isinstance(candidate, str):
                text = candidate.strip()

                if text:
                    return text

    return None


def extract_migration_requirements(
    sources: dict[str, dict[str, Any]],
) -> list[MigrationRequirement]:
    """
    Extract migration-related candidate statements.

    Input must be a trusted source bundle from
    load_agent_sources(), not arbitrary unverified JSON.

    Every extracted statement remains proposed,
    unverified, and subject to human review.
    """

    requirements = []

    candidate_sources = []

    agent_1 = sources.get("agent_1", {})

    sales_intelligence = agent_1.get(
        "sales_intelligence",
        [],
    )

    if isinstance(sales_intelligence, list):
        for index, item in enumerate(sales_intelligence):
            candidate_sources.append((
                "agent_1",
                f"sales_intelligence[{index}]",
                item,
            ))

    agent_2 = sources.get("agent_2", {})

    onboarding_plan = agent_2.get(
        "onboarding_plan",
        {},
    )

    if isinstance(onboarding_plan, dict):
        objectives = onboarding_plan.get(
            "objectives",
            [],
        )

        if isinstance(objectives, list):
            for index, item in enumerate(objectives):
                candidate_sources.append((
                    "agent_2",
                    f"onboarding_plan.objectives[{index}]",
                    item,
                ))

    for agent_name, source_path, item in candidate_sources:

        text = extract_text(item)

        if not text:
            continue

        if not is_migration_related(text):
            continue

        requirement = MigrationRequirement(
            requirement_id=f"REQ-{len(requirements) + 1:03d}",
            description=text,
            source_references=[
                f"{agent_name}.{source_path}"
            ],
            source_agent=agent_name,
            status="proposed",
            verified=False,
            requires_human_review=True,
        )

        requirements.append(requirement)

    return requirements