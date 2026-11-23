from dataclasses import dataclass, field

from agents.customer_data_migration.schemas import (
    MigrationRequirement,
    MigrationRisk,
)

from agents.customer_data_migration.source_inventory import (
    SourceInventoryResult,
)

from agents.customer_data_migration.mapping_rules import (
    MappingAssessmentResult,
)

from agents.customer_data_migration.data_quality_rules import (
    DataQualityResult,
)


@dataclass
class MigrationRiskResult:
    risks: list[MigrationRisk] = field(
        default_factory=list
    )

    requires_human_review: bool = True


def detect_migration_risks(
    requirements: list[MigrationRequirement],
    inventory: SourceInventoryResult,
    mappings: MappingAssessmentResult,
    data_quality: DataQualityResult,
) -> MigrationRiskResult:
    """
    Generate reviewable risks from assessment findings.

    No risk is automatically verified or assigned
    a severity level.
    """

    result = MigrationRiskResult()

    # No confirmed migration scope:
    # avoid treating missing migration details as
    # evidence of an active migration project.

    if not requirements:
        result.risks.append(
            MigrationRisk(
                risk_id="RISK-001",
                description=(
                    "Migration scope has not been established. "
                    "Clarification is required before a migration "
                    "readiness assessment can proceed."
                ),
            )
        )

        return result

    findings = (
        inventory.missing_information
        + mappings.missing_information
        + data_quality.findings
    )

    requirement_ids = [
        requirement.requirement_id
        for requirement in requirements
    ]

    for index, finding in enumerate(findings, start=1):

        result.risks.append(
            MigrationRisk(
                risk_id=f"RISK-{index:03d}",
                description=finding,
                related_requirement_ids=requirement_ids,
                severity="unassessed",
                status="open",
                verified=False,
                requires_human_review=True,
            )
        )

    return result