from dataclasses import dataclass, field

from agents.customer_data_migration.readiness_assessment import (
    MigrationReadinessResult,
)
from agents.customer_data_migration.migration_risks import (
    MigrationRiskResult,
)


@dataclass
class MigrationRecommendation:
    recommendation_id: str
    description: str
    rationale: str
    related_risk_ids: list[str] = field(default_factory=list)
    status: str = "proposed"
    verified: bool = False
    requires_human_review: bool = True


@dataclass
class MigrationAdvisorResult:
    recommendations: list[MigrationRecommendation] = field(
        default_factory=list
    )
    advisory_status: str = "not_assessed"
    requires_human_review: bool = True
    migration_authorized: bool = False


def generate_migration_recommendations(
    readiness: MigrationReadinessResult,
    risks: MigrationRiskResult,
) -> MigrationAdvisorResult:
    """
    Generate deterministic, evidence-grounded recommendations.

    No AI model or external service is called.
    No migration execution is authorized.
    """

    result = MigrationAdvisorResult(
        advisory_status="completed",
    )

    if readiness.readiness_status == "scope_not_established":
        result.recommendations.append(
            MigrationRecommendation(
                recommendation_id="REC-001",
                description=(
                    "Confirm whether the customer requires "
                    "historical data migration."
                ),
                rationale=(
                    "The current assessment has not identified "
                    "an established migration scope."
                ),
                related_risk_ids=[
                    risk.risk_id for risk in risks.risks
                ],
            )
        )
        return result

    for risk in risks.risks:
        result.recommendations.append(
            MigrationRecommendation(
                recommendation_id=(
                    f"REC-{len(result.recommendations) + 1:03d}"
                ),
                description=(
                    "Investigate and resolve the following "
                    f"migration assessment finding: "
                    f"{risk.description}"
                ),
                rationale=(
                    "The finding remains unresolved in the "
                    "migration assessment."
                ),
                related_risk_ids=[risk.risk_id],
            )
        )

    if readiness.readiness_status == "information_incomplete":
        result.recommendations.append(
            MigrationRecommendation(
                recommendation_id=(
                    f"REC-{len(result.recommendations) + 1:03d}"
                ),
                description=(
                    "Complete the missing migration inventory, "
                    "mapping, and data-quality information "
                    "before reassessing readiness."
                ),
                rationale=(
                    "The readiness assessment indicates that "
                    "required information is incomplete."
                ),
            )
        )

    elif readiness.readiness_status == "pending_human_review":
        result.recommendations.append(
            MigrationRecommendation(
                recommendation_id=(
                    f"REC-{len(result.recommendations) + 1:03d}"
                ),
                description=(
                    "Request human verification of migration "
                    "requirements, inventory, and mappings."
                ),
                rationale=(
                    "The current assessment contains evidence "
                    "that has not completed verification."
                ),
            )
        )

    elif readiness.readiness_status == "ready_for_review":
        result.recommendations.append(
            MigrationRecommendation(
                recommendation_id=(
                    f"REC-{len(result.recommendations) + 1:03d}"
                ),
                description=(
                    "Submit the migration assessment for "
                    "human review and confirm any outstanding "
                    "destination-schema, security, and "
                    "migration-testing requirements."
                ),
                rationale=(
                    "The implemented automated readiness "
                    "checks are satisfied, but this does not "
                    "constitute migration approval."
                ),
            )
        )

    else:
        result.advisory_status = "requires_clarification"
        result.recommendations.append(
            MigrationRecommendation(
                recommendation_id=(
                    f"REC-{len(result.recommendations) + 1:03d}"
                ),
                description=(
                    "Clarify the migration readiness status "
                    "before determining next steps."
                ),
                rationale=(
                    "The supplied readiness status is not "
                    "recognized by the advisory rules."
                ),
            )
        )

    return result