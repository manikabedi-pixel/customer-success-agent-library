from agents.customer_data_migration.schemas import (
    DatasetInventory,
    FieldMapping,
)

from agents.customer_data_migration.mapping_rules import (
    assess_field_mappings,
)


def make_dataset():
    return DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
    )


def test_no_datasets_or_mappings():
    result = assess_field_mappings(
        datasets=[],
        mappings=[],
    )

    assert result.total_mappings == 0
    assert result.missing_information


def test_no_mappings_are_flagged():
    result = assess_field_mappings(
        datasets=[make_dataset()],
        mappings=[],
    )

    assert any(
        "No field mappings" in item
        for item in result.missing_information
    )


def test_mapping_counts():
    mappings = [
        FieldMapping(
            mapping_id="MAP-001",
            dataset_id="DATA-001",
            source_field="email",
        ),
        FieldMapping(
            mapping_id="MAP-002",
            dataset_id="DATA-001",
            source_field="name",
            verified=True,
        ),
    ]

    result = assess_field_mappings(
        datasets=[make_dataset()],
        mappings=mappings,
    )

    assert result.total_mappings == 2
    assert result.verified_mappings == 1
    assert result.unverified_mappings == 1


def test_unknown_dataset_is_flagged():
    mapping = FieldMapping(
        mapping_id="MAP-001",
        dataset_id="UNKNOWN",
        source_field="email",
    )

    result = assess_field_mappings(
        datasets=[make_dataset()],
        mappings=[mapping],
    )

    assert any(
        "unknown dataset" in item
        for item in result.missing_information
    )


def test_missing_destination_field_is_flagged():
    mapping = FieldMapping(
        mapping_id="MAP-001",
        dataset_id="DATA-001",
        source_field="email",
    )

    result = assess_field_mappings(
        datasets=[make_dataset()],
        mappings=[mapping],
    )

    assert any(
        "no destination field" in item
        for item in result.missing_information
    )


def test_unverified_mapping_is_flagged():
    mapping = FieldMapping(
        mapping_id="MAP-001",
        dataset_id="DATA-001",
        source_field="email",
        destination_field="contact_email",
    )

    result = assess_field_mappings(
        datasets=[make_dataset()],
        mappings=[mapping],
    )

    assert any(
        "requires verification" in item
        for item in result.missing_information
    )


def test_verified_mapping_is_counted():
    mapping = FieldMapping(
        mapping_id="MAP-001",
        dataset_id="DATA-001",
        source_field="email",
        destination_field="contact_email",
        verified=True,
    )

    result = assess_field_mappings(
        datasets=[make_dataset()],
        mappings=[mapping],
    )

    assert result.verified_mappings == 1
    assert result.unverified_mappings == 0


def test_mapping_assessment_requires_human_review():
    result = assess_field_mappings(
        datasets=[make_dataset()],
        mappings=[],
    )

    assert result.requires_human_review is True