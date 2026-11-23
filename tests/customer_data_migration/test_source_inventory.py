from agents.customer_data_migration.schemas import (
    DatasetInventory,
    MigrationRequirement,
    SourceSystem,
)

from agents.customer_data_migration.source_inventory import (
    build_source_inventory,
)


def make_requirement():
    return MigrationRequirement(
        requirement_id="REQ-001",
        description="Assess historical CRM data migration.",
    )


def test_no_requirements_does_not_invent_inventory():
    result = build_source_inventory(
        requirements=[],
    )

    assert result.source_systems == []
    assert result.datasets == []
    assert result.missing_information
    assert result.requires_human_review is True


def test_requirement_does_not_create_source_system():
    result = build_source_inventory(
        requirements=[make_requirement()],
    )

    assert result.source_systems == []
    assert result.datasets == []


def test_missing_source_system_is_flagged():
    result = build_source_inventory(
        requirements=[make_requirement()],
    )

    assert any(
        "Source systems have not been identified"
        in item
        for item in result.missing_information
    )


def test_missing_dataset_is_flagged():
    result = build_source_inventory(
        requirements=[make_requirement()],
    )

    assert any(
        "Datasets have not been identified"
        in item
        for item in result.missing_information
    )


def test_explicit_source_system_is_preserved():
    system = SourceSystem(
        system_id="SYS-001",
        name="Legacy CRM",
    )

    result = build_source_inventory(
        requirements=[make_requirement()],
        source_systems=[system],
    )

    assert len(result.source_systems) == 1
    assert result.source_systems[0].name == "Legacy CRM"


def test_missing_system_owner_is_flagged():
    system = SourceSystem(
        system_id="SYS-001",
        name="Legacy CRM",
    )

    result = build_source_inventory(
        requirements=[make_requirement()],
        source_systems=[system],
    )

    assert any(
        "no confirmed owner" in item
        for item in result.missing_information
    )


def test_unconfirmed_access_is_flagged():
    system = SourceSystem(
        system_id="SYS-001",
        name="Legacy CRM",
    )

    result = build_source_inventory(
        requirements=[make_requirement()],
        source_systems=[system],
    )

    assert any(
        "access is not confirmed" in item
        for item in result.missing_information
    )


def test_unknown_dataset_source_system_is_flagged():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
        source_system_id="UNKNOWN",
    )

    result = build_source_inventory(
        requirements=[make_requirement()],
        datasets=[dataset],
    )

    assert any(
        "unknown source system" in item
        for item in result.missing_information
    )


def test_unknown_record_count_is_flagged():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
    )

    result = build_source_inventory(
        requirements=[make_requirement()],
        datasets=[dataset],
    )

    assert any(
        "record count is unknown" in item
        for item in result.missing_information
    )


def test_unknown_sensitive_data_classification_is_flagged():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
    )

    result = build_source_inventory(
        requirements=[make_requirement()],
        datasets=[dataset],
    )

    assert any(
        "sensitive-data classification is unknown" in item
        for item in result.missing_information
    )