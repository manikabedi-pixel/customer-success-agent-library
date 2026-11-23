from agents.customer_data_migration.schemas import (
    DatasetInventory,
)

from agents.customer_data_migration.data_quality_rules import (
    assess_data_quality,
)


def test_no_datasets():
    result = assess_data_quality([])

    assert result.datasets_assessed == 0
    assert len(result.findings) == 1


def test_unknown_record_count():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
    )

    result = assess_data_quality([dataset])

    assert any(
        "record count has not been established"
        in finding
        for finding in result.findings
    )


def test_unknown_sensitive_data_classification():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
    )

    result = assess_data_quality([dataset])

    assert any(
        "sensitive-data classification is unknown"
        in finding
        for finding in result.findings
    )


def test_unassessed_data_quality():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
    )

    result = assess_data_quality([dataset])

    assert any(
        "data-quality assessment has not been confirmed"
        in finding
        for finding in result.findings
    )


def test_unverified_dataset():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
    )

    result = assess_data_quality([dataset])

    assert any(
        "dataset inventory has not been verified"
        in finding
        for finding in result.findings
    )


def test_complete_dataset_metadata():
    dataset = DatasetInventory(
        dataset_id="DATA-001",
        name="Customer Records",
        record_count=100,
        contains_sensitive_data=False,
        data_quality_assessed=True,
        verified=True,
    )

    result = assess_data_quality([dataset])

    assert result.findings == []


def test_multiple_datasets():
    datasets = [
        DatasetInventory(
            dataset_id="DATA-001",
            name="Customers",
        ),
        DatasetInventory(
            dataset_id="DATA-002",
            name="Contacts",
        ),
    ]

    result = assess_data_quality(datasets)

    assert result.datasets_assessed == 2
    assert len(result.findings) == 8


def test_data_quality_requires_human_review():
    result = assess_data_quality([])

    assert result.requires_human_review is True