import json
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from agents.customer_data_migration.schemas import (
    MigrationAssessment,
)

from agents.customer_data_migration.ai_migration_advisor import (
    MigrationAdvisorResult,
)

from agents.customer_data_migration.readiness_assessment import (
    MigrationReadinessResult,
)


def build_migration_report(
    assessment: MigrationAssessment,
    readiness: MigrationReadinessResult,
    advisor: MigrationAdvisorResult,
) -> dict:
    """
    Build a structured migration assessment report.

    This function does not authorize or execute migration.
    """

    return {
        "agent": "customer_data_migration",
        "version": "0.0.9",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "deal_id": assessment.deal_id,
        "customer_name": assessment.customer_name,
        "status": "assessment_generated",
        "readiness_status": readiness.readiness_status,
        "requires_human_review": True,
        "migration_authorized": False,
        "approval": asdict(assessment.approval),
        "requirements": [
            asdict(item)
            for item in assessment.requirements
        ],
        "source_systems": [
            asdict(item)
            for item in assessment.source_systems
        ],
        "datasets": [
            asdict(item)
            for item in assessment.datasets
        ],
        "field_mappings": [
            asdict(item)
            for item in assessment.field_mappings
        ],
        "risks": [
            asdict(item)
            for item in assessment.risks
        ],
        "readiness_summary": {
            "total_raw_findings": readiness.total_raw_findings,
            "total_unique_findings": readiness.total_unique_findings,
            "unique_findings": list(
                readiness.unique_findings
            ),
        },
        "recommendations": [
            asdict(item)
            for item in advisor.recommendations
        ],
        "advisory_status": advisor.advisory_status,
        "metadata": dict(assessment.metadata),
    }


def save_migration_report(
    report: dict,
    output_path: str | Path,
) -> Path:
    """
    Save a JSON report to disk.

    This writes only the report artifact.
    It does not modify customer data.
    """

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            report,
            file,
            indent=2,
            ensure_ascii=False,
        )

    return path