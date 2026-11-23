import json

from agents.customer_data_migration.schemas import (
    MigrationAssessment,
    MigrationRequirement,
    MigrationRisk,
)

from agents.customer_data_migration.readiness_assessment import (
    MigrationReadinessResult,
)

from agents.customer_data_migration.ai_migration_advisor import (
    MigrationAdvisorResult,
    MigrationRecommendation,
)

from agents.customer_data_migration.report_generator import (
    build_migration_report,
    save_migration_report,
)


def make_report():
    assessment = MigrationAssessment(
        deal_id="123",
        customer_name="Synthetic Customer",
        requirements=[
            MigrationRequirement(
                requirement_id="REQ-001",
                description="Assess historical CRM migration.",
            )
        ],
        risks=[
            MigrationRisk(
                risk_id="RISK-001",
                description="Source access is unconfirmed.",
            )
        ],
    )

    readiness = MigrationReadinessResult(
        readiness_status="information_incomplete",
        total_raw_findings=1,
        total_unique_findings=1,
        unique_findings=[
            "Source access is unconfirmed."
        ],
    )

    advisor = MigrationAdvisorResult(
        advisory_status="completed",
        recommendations=[
            MigrationRecommendation(
                recommendation_id="REC-001",
                description="Confirm source access.",
                rationale=(
                    "Source-system access has not been confirmed. "
                    "Human verification is required before "
                    "migration readiness can be reassessed."
                ),
                related_risk_ids=["RISK-001"],
            )
        ],

    )

    return build_migration_report(
        assessment,
        readiness,
        advisor,
    )


def test_report_identity():
    report = make_report()

    assert report["deal_id"] == "123"
    assert report["customer_name"] == "Synthetic Customer"


def test_report_version():
    report = make_report()

    assert report["version"] == "0.0.9"


def test_report_contains_requirements():
    report = make_report()

    assert len(report["requirements"]) == 1


def test_report_contains_risks():
    report = make_report()

    assert len(report["risks"]) == 1


def test_report_contains_recommendations():
    report = make_report()

    assert len(report["recommendations"]) == 1


def test_report_contains_readiness():
    report = make_report()

    assert report["readiness_status"] == (
        "information_incomplete"
    )


def test_report_never_authorizes_migration():
    report = make_report()

    assert report["migration_authorized"] is False
    assert report["requires_human_review"] is True


def test_report_preserves_approval():
    report = make_report()

    assert report["approval"]["decision"] == "pending"


def test_report_saves_valid_json(tmp_path):
    report = make_report()

    path = tmp_path / "migration_report.json"

    save_migration_report(report, path)

    loaded = json.loads(
        path.read_text(encoding="utf-8")
    )

    assert loaded["deal_id"] == "123"


def test_report_preserves_risk_references():
    report = make_report()

    recommendation = report["recommendations"][0]

    assert recommendation["related_risk_ids"] == [
        "RISK-001"
    ]