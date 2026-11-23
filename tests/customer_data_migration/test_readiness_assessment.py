from agents.customer_data_migration.schemas import (
    DatasetInventory,
    FieldMapping,
    MigrationAssessment,
    MigrationRequirement,
    SourceSystem,
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

from agents.customer_data_migration.readiness_assessment import (
    assess_migration_readiness,
    apply_readiness_to_assessment,
)


def make_requirement(verified=False):
    return MigrationRequirement(
        requirement_id="REQ-001",
        description="Assess historical CRM migration.",
        verified=verified,
    )


def make_inventory(verified=False):
    return SourceInventoryResult(
        source_systems=[
            SourceSystem(
                system_id="SYS-001",
                name="Legacy CRM",
                owner="Customer IT",
                access_confirmed=True,
                verified=verified,
            )
        ],
        datasets=[
            DatasetInventory(
                dataset_id="DATA-001",
                name="Customer Records",
                source_system_id="SYS-001",
                record_count=100,
                contains_sensitive_data=False,
                data_quality_assessed=True,
                verified=verified,
            )
        ],
    )


def make_mappings(verified=False):
    return MappingAssessmentResult(
        total_mappings=1,
        verified_mappings=1 if verified else 0,
        unverified_mappings=0 if verified else 1,
    )


def test_no_requirements():
    result = assess_migration_readiness(
        requirements=[],
        inventory=SourceInventoryResult(),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.readiness_status == (
        "scope_not_established"
    )

    assert result.migration_authorized is False


def test_missing_inventory():
    result = assess_migration_readiness(
        requirements=[make_requirement()],
        inventory=SourceInventoryResult(),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.readiness_status == (
        "information_incomplete"
    )


def test_missing_mappings():
    result = assess_migration_readiness(
        requirements=[make_requirement()],
        inventory=make_inventory(),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.readiness_status == (
        "information_incomplete"
    )


def test_missing_information():
    inventory = make_inventory()

    inventory.missing_information = [
        "Source system access is not confirmed."
    ]

    result = assess_migration_readiness(
        requirements=[make_requirement()],
        inventory=inventory,
        mappings=make_mappings(),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.readiness_status == (
        "information_incomplete"
    )


def test_unverified_requirement():
    result = assess_migration_readiness(
        requirements=[make_requirement(verified=False)],
        inventory=make_inventory(verified=True),
        mappings=make_mappings(verified=True),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.readiness_status == (
        "pending_human_review"
    )


def test_unverified_inventory():
    result = assess_migration_readiness(
        requirements=[make_requirement(verified=True)],
        inventory=make_inventory(verified=False),
        mappings=make_mappings(verified=True),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.readiness_status == (
        "pending_human_review"
    )


def test_unverified_mapping():
    result = assess_migration_readiness(
        requirements=[make_requirement(verified=True)],
        inventory=make_inventory(verified=True),
        mappings=make_mappings(verified=False),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.readiness_status == (
        "pending_human_review"
    )


def test_ready_for_review():
    result = assess_migration_readiness(
        requirements=[make_requirement(verified=True)],
        inventory=make_inventory(verified=True),
        mappings=make_mappings(verified=True),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.readiness_status == "ready_for_review"
    assert result.requires_human_review is True
    assert result.migration_authorized is False


def test_exact_duplicate_findings_removed():
    inventory = make_inventory()

    inventory.missing_information = [
        "Dataset count unknown.",
        " dataset count unknown. ",
    ]

    result = assess_migration_readiness(
        requirements=[make_requirement()],
        inventory=inventory,
        mappings=make_mappings(),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.total_raw_findings == 2
    assert result.total_unique_findings == 1


def test_distinct_wording_is_preserved():
    inventory = make_inventory()

    inventory.missing_information = [
        "Dataset count unknown.",
        "Dataset record count has not been established.",
    ]

    result = assess_migration_readiness(
        requirements=[make_requirement()],
        inventory=inventory,
        mappings=make_mappings(),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    assert result.total_unique_findings == 2


def test_apply_readiness_never_authorizes_migration():
    assessment = MigrationAssessment(
        deal_id="123",
        migration_authorized=True,
    )

    readiness = assess_migration_readiness(
        requirements=[make_requirement(verified=True)],
        inventory=make_inventory(verified=True),
        mappings=make_mappings(verified=True),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    updated = apply_readiness_to_assessment(
        assessment,
        readiness,
    )

    assert updated.readiness_status == "ready_for_review"
    assert updated.migration_authorized is False
    assert updated.requires_human_review is True


def test_readiness_summary_saved_to_metadata():
    assessment = MigrationAssessment(
        deal_id="123",
    )

    readiness = assess_migration_readiness(
        requirements=[],
        inventory=SourceInventoryResult(),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(),
        risks=MigrationRiskResult(),
    )

    updated = apply_readiness_to_assessment(
        assessment,
        readiness,
    )

    summary = updated.metadata["readiness_summary"]

    assert summary["total_raw_findings"] == 1
    assert summary["total_unique_findings"] == 1