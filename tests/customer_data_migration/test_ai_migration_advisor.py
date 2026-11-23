from agents.customer_data_migration.ai_migration_advisor import (
    generate_migration_recommendations,
)

from agents.customer_data_migration.migration_risks import (
    MigrationRiskResult,
)

from agents.customer_data_migration.readiness_assessment import (
    MigrationReadinessResult,
)

from agents.customer_data_migration.schemas import MigrationRisk


def make_readiness(status):
    return MigrationReadinessResult(
        readiness_status=status,
    )


def make_risk():
    return MigrationRisk(
        risk_id="RISK-001",
        description="Source system access is not confirmed.",
    )


def test_scope_not_established():
    result = generate_migration_recommendations(
        readiness=make_readiness("scope_not_established"),
        risks=MigrationRiskResult(),
    )

    assert len(result.recommendations) == 1
    assert "Confirm whether" in (
        result.recommendations[0].description
    )


def test_scope_recommendation_references_risk():
    result = generate_migration_recommendations(
        readiness=make_readiness("scope_not_established"),
        risks=MigrationRiskResult(risks=[make_risk()]),
    )

    assert result.recommendations[0].related_risk_ids == [
        "RISK-001"
    ]


def test_risk_generates_recommendation():
    result = generate_migration_recommendations(
        readiness=make_readiness("information_incomplete"),
        risks=MigrationRiskResult(risks=[make_risk()]),
    )

    assert len(result.recommendations) == 2

    assert result.recommendations[0].related_risk_ids == [
        "RISK-001"
    ]


def test_information_incomplete():
    result = generate_migration_recommendations(
        readiness=make_readiness("information_incomplete"),
        risks=MigrationRiskResult(),
    )

    assert len(result.recommendations) == 1

    assert "Complete the missing" in (
        result.recommendations[0].description
    )


def test_pending_human_review():
    result = generate_migration_recommendations(
        readiness=make_readiness("pending_human_review"),
        risks=MigrationRiskResult(),
    )

    assert "human verification" in (
        result.recommendations[0].description
    )


def test_ready_for_review():
    result = generate_migration_recommendations(
        readiness=make_readiness("ready_for_review"),
        risks=MigrationRiskResult(),
    )

    assert "human review" in (
        result.recommendations[0].description
    )


def test_unknown_readiness_status():
    result = generate_migration_recommendations(
        readiness=make_readiness("unexpected_status"),
        risks=MigrationRiskResult(),
    )

    assert result.advisory_status == "requires_clarification"
    assert len(result.recommendations) == 1


def test_recommendations_are_unverified():
    result = generate_migration_recommendations(
        readiness=make_readiness("information_incomplete"),
        risks=MigrationRiskResult(risks=[make_risk()]),
    )

    assert all(
        recommendation.verified is False
        for recommendation in result.recommendations
    )


def test_recommendations_require_human_review():
    result = generate_migration_recommendations(
        readiness=make_readiness("ready_for_review"),
        risks=MigrationRiskResult(),
    )

    assert result.requires_human_review is True

    assert all(
        recommendation.requires_human_review
        for recommendation in result.recommendations
    )


def test_advisor_never_authorizes_migration():
    result = generate_migration_recommendations(
        readiness=make_readiness("ready_for_review"),
        risks=MigrationRiskResult(),
    )

    assert result.migration_authorized is False


def test_recommendation_ids_are_unique():
    risks = MigrationRiskResult(
        risks=[
            MigrationRisk(
                risk_id="RISK-001",
                description="Missing source owner.",
            ),
            MigrationRisk(
                risk_id="RISK-002",
                description="Unverified field mapping.",
            ),
        ]
    )

    result = generate_migration_recommendations(
        readiness=make_readiness("information_incomplete"),
        risks=risks,
    )

    ids = [
        recommendation.recommendation_id
        for recommendation in result.recommendations
    ]

    assert len(ids) == len(set(ids))


def test_recommendations_remain_proposed():
    result = generate_migration_recommendations(
        readiness=make_readiness("ready_for_review"),
        risks=MigrationRiskResult(),
    )

    assert all(
        recommendation.status == "proposed"
        for recommendation in result.recommendations
    )