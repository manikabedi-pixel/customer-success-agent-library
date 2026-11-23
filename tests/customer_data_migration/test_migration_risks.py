from agents.customer_data_migration.schemas import (
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
    detect_migration_risks,
)


def make_requirement():
    return MigrationRequirement(
        requirement_id="REQ-001",
        description="Assess historical CRM migration.",
    )


def test_no_requirements_produces_scope_warning():
    result = detect_migration_risks(
        requirements=[],
        inventory=SourceInventoryResult(),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(),
    )

    assert len(result.risks) == 1
    assert "scope has not been established" in (
        result.risks[0].description
    )


def test_inventory_gap_creates_risk():
    result = detect_migration_risks(
        requirements=[make_requirement()],
        inventory=SourceInventoryResult(
            missing_information=[
                "Source system owner is unknown."
            ]
        ),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(),
    )

    assert len(result.risks) == 1
    assert result.risks[0].description == (
        "Source system owner is unknown."
    )


def test_mapping_gap_creates_risk():
    result = detect_migration_risks(
        requirements=[make_requirement()],
        inventory=SourceInventoryResult(),
        mappings=MappingAssessmentResult(
            missing_information=[
                "Field mapping requires verification."
            ]
        ),
        data_quality=DataQualityResult(),
    )

    assert len(result.risks) == 1


def test_data_quality_gap_creates_risk():
    result = detect_migration_risks(
        requirements=[make_requirement()],
        inventory=SourceInventoryResult(),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(
            findings=[
                "Dataset quality has not been assessed."
            ]
        ),
    )

    assert len(result.risks) == 1


def test_risks_remain_unverified():
    result = detect_migration_risks(
        requirements=[make_requirement()],
        inventory=SourceInventoryResult(
            missing_information=[
                "Source access unconfirmed."
            ]
        ),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(),
    )

    risk = result.risks[0]

    assert risk.verified is False
    assert risk.severity == "unassessed"
    assert risk.requires_human_review is True


def test_risk_references_requirement():
    result = detect_migration_risks(
        requirements=[make_requirement()],
        inventory=SourceInventoryResult(
            missing_information=[
                "Source access unconfirmed."
            ]
        ),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(),
    )

    assert result.risks[0].related_requirement_ids == [
        "REQ-001"
    ]


def test_multiple_findings_create_multiple_risks():
    result = detect_migration_risks(
        requirements=[make_requirement()],
        inventory=SourceInventoryResult(
            missing_information=[
                "Missing owner.",
                "Missing access.",
            ]
        ),
        mappings=MappingAssessmentResult(
            missing_information=[
                "Missing mapping."
            ]
        ),
        data_quality=DataQualityResult(
            findings=[
                "Missing quality assessment."
            ]
        ),
    )

    assert len(result.risks) == 4


def test_no_findings_creates_no_risks():
    result = detect_migration_risks(
        requirements=[make_requirement()],
        inventory=SourceInventoryResult(),
        mappings=MappingAssessmentResult(),
        data_quality=DataQualityResult(),
    )

    assert result.risks == []