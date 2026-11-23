from agents.customer_data_migration.schemas import (
    MigrationRequirement,
    SourceSystem,
    DatasetInventory,
    FieldMapping,
    MigrationRisk,
    MigrationApproval,
    MigrationAssessment,
)


def test_migration_requirement_defaults():
    requirement = MigrationRequirement(
        requirement_id="REQ-001",
        description="Assess historical customer data migration.",
    )

    assert requirement.status == "proposed"
    assert requirement.verified is False
    assert requirement.requires_human_review is True
    assert requirement.source_references == []


def test_source_system_defaults():
    system = SourceSystem(
        system_id="SYS-001",
        name="Existing CRM",
    )

    assert system.owner is None
    assert system.access_confirmed is False
    assert system.verified is False


def test_dataset_inventory_defaults():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
    )

    assert dataset.source_system_id is None
    assert dataset.record_count is None
    assert dataset.contains_sensitive_data is None
    assert dataset.data_quality_assessed is False


def test_field_mapping_defaults():
    mapping = FieldMapping(
        mapping_id="MAP-001",
        dataset_id="DATA-001",
        source_field="customer_id",
    )

    assert mapping.destination_field is None
    assert mapping.transformation_rule is None
    assert mapping.status == "proposed"
    assert mapping.verified is False


def test_migration_risk_defaults():
    risk = MigrationRisk(
        risk_id="RISK-001",
        description="Source data quality has not been assessed.",
    )

    assert risk.severity == "unassessed"
    assert risk.status == "open"
    assert risk.verified is False


def test_migration_approval_defaults():
    approval = MigrationApproval()

    assert approval.reviewer_id is None
    assert approval.decision == "pending"
    assert approval.verified is False


def test_migration_assessment_defaults():
    assessment = MigrationAssessment(
        deal_id="DEAL-123",
        customer_name="Example Customer",
    )

    assert assessment.requirements == []
    assert assessment.source_systems == []
    assert assessment.datasets == []
    assert assessment.field_mappings == []
    assert assessment.risks == []

    assert assessment.readiness_status == "not_assessed"
    assert assessment.requires_human_review is True
    assert assessment.migration_authorized is False


def test_assessment_lists_are_independent():
    first = MigrationAssessment(deal_id="DEAL-001")
    second = MigrationAssessment(deal_id="DEAL-002")

    first.requirements.append(
        MigrationRequirement(
            requirement_id="REQ-001",
            description="Review migration requirements.",
        )
    )

    assert len(first.requirements) == 1
    assert len(second.requirements) == 0


def test_dataset_unknown_is_not_assumed_safe():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
    )

    assert dataset.contains_sensitive_data is None
    assert dataset.verified is False


def test_mapping_cannot_be_assumed_approved():
    mapping = FieldMapping(
        mapping_id="MAP-001",
        dataset_id="DATA-001",
        source_field="email",
        destination_field="contact_email",
    )

    assert mapping.status == "proposed"
    assert mapping.verified is False
    assert mapping.requires_human_review is True