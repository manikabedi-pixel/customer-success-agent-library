from dataclasses import dataclass, field
import re

from agents.customer_data_migration.schemas import (
    MigrationAssessment,
    MigrationRequirement,
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

from agents.customer_data_migration.migration_risks import (
    MigrationRiskResult,
)


@dataclass
class MigrationReadinessResult:
    readiness_status: str = "not_assessed"

    unique_findings: list[str] = field(
        default_factory=list
    )

    total_raw_findings: int = 0

    total_unique_findings: int = 0

    requires_human_review: bool = True

    migration_authorized: bool = False


def _normalize_finding(finding: str) -> str:
    """
    Normalize a finding for conservative duplicate detection.

    This is not semantic deduplication.
    """

    normalized = finding.strip().lower()

    normalized = re.sub(
        r"\s+",
        " ",
        normalized,
    )

    return normalized


def _deduplicate_findings(
    findings: list[str],
) -> list[str]:
    """
    Remove exact duplicates after normalization.

    Preserve original wording and order.
    """

    seen = set()
    unique = []

    for finding in findings:
        normalized = _normalize_finding(finding)

        if normalized in seen:
            continue

        seen.add(normalized)
        unique.append(finding)

    return unique


def assess_migration_readiness(
    requirements: list[MigrationRequirement],
    inventory: SourceInventoryResult,
    mappings: MappingAssessmentResult,
    data_quality: DataQualityResult,
    risks: MigrationRiskResult,
) -> MigrationReadinessResult:
    """
    Assess migration readiness without authorizing execution.

    The assessment is conservative:
    missing information and unverified evidence prevent
    readiness from being treated as established.
    """

    result = MigrationReadinessResult()

    if not requirements:
        result.readiness_status = "scope_not_established"

        result.unique_findings = [
            "Migration scope has not been established."
        ]

        result.total_raw_findings = 1
        result.total_unique_findings = 1

        return result

    raw_findings = (
        inventory.missing_information
        + mappings.missing_information
        + data_quality.findings
    )

    result.total_raw_findings = len(raw_findings)

    result.unique_findings = _deduplicate_findings(
        raw_findings
    )

    result.total_unique_findings = len(
        result.unique_findings
    )

    if (
        not inventory.source_systems
        or not inventory.datasets
        or mappings.total_mappings == 0
    ):
        result.readiness_status = "information_incomplete"
        return result

    if result.unique_findings:
        result.readiness_status = "information_incomplete"
        return result

    if any(
        not requirement.verified
        for requirement in requirements
    ):
        result.readiness_status = "pending_human_review"
        return result

    if any(
        not system.verified
        for system in inventory.source_systems
    ):
        result.readiness_status = "pending_human_review"
        return result

    if any(
        not dataset.verified
        for dataset in inventory.datasets
    ):
        result.readiness_status = "pending_human_review"
        return result

    if mappings.unverified_mappings > 0:
        result.readiness_status = "pending_human_review"
        return result

    if risks.risks:
        result.readiness_status = "pending_human_review"
        return result

    result.readiness_status = "ready_for_review"

    return result


def apply_readiness_to_assessment(
    assessment: MigrationAssessment,
    readiness: MigrationReadinessResult,
) -> MigrationAssessment:
    """
    Update readiness fields on a migration assessment.

    This function never grants migration authorization.
    """

    assessment.readiness_status = (
        readiness.readiness_status
    )

    assessment.requires_human_review = True

    assessment.migration_authorized = False

    assessment.metadata["readiness_summary"] = {
        "total_raw_findings": (
            readiness.total_raw_findings
        ),
        "total_unique_findings": (
            readiness.total_unique_findings
        ),
        "unique_findings": list(
            readiness.unique_findings
        ),
    }

    return assessment