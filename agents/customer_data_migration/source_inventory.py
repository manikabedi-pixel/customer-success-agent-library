from dataclasses import dataclass, field

from agents.customer_data_migration.schemas import (
    DatasetInventory,
    MigrationRequirement,
    SourceSystem,
)


@dataclass
class SourceInventoryResult:
    """
    Inventory of explicitly supplied source systems and datasets.

    This component does not infer system identities from
    migration-related text.
    """

    source_systems: list[SourceSystem] = field(
        default_factory=list
    )

    datasets: list[DatasetInventory] = field(
        default_factory=list
    )

    missing_information: list[str] = field(
        default_factory=list
    )

    requires_human_review: bool = True


def build_source_inventory(
    requirements: list[MigrationRequirement],
    source_systems: list[SourceSystem] | None = None,
    datasets: list[DatasetInventory] | None = None,
) -> SourceInventoryResult:
    """
    Build an inventory from explicitly supplied records.

    Migration candidates do not automatically establish
    the existence of a source system or dataset.
    """

    result = SourceInventoryResult(
        source_systems=list(source_systems or []),
        datasets=list(datasets or []),
    )

    if not requirements:
        result.missing_information.append(
            "No migration-related requirement identified "
            "by the current extractor; migration scope "
            "requires clarification."
        )

        return result

    if not result.source_systems:
        result.missing_information.append(
            "Source systems have not been identified."
        )

    if not result.datasets:
        result.missing_information.append(
            "Datasets have not been identified."
        )

    known_system_ids = {
        system.system_id
        for system in result.source_systems
    }

    for system in result.source_systems:
        if not system.owner:
            result.missing_information.append(
                f"Source system {system.system_id} "
                "has no confirmed owner."
            )

        if not system.access_confirmed:
            result.missing_information.append(
                f"Source system {system.system_id} "
                "access is not confirmed."
            )

    for dataset in result.datasets:
        if not dataset.source_system_id:
            result.missing_information.append(
                f"Dataset {dataset.dataset_id} "
                "has no source system assigned."
            )

        elif dataset.source_system_id not in known_system_ids:
            result.missing_information.append(
                f"Dataset {dataset.dataset_id} references "
                f"unknown source system "
                f"{dataset.source_system_id}."
            )

        if dataset.record_count is None:
            result.missing_information.append(
                f"Dataset {dataset.dataset_id} "
                "record count is unknown."
            )

        if dataset.contains_sensitive_data is None:
            result.missing_information.append(
                f"Dataset {dataset.dataset_id} "
                "sensitive-data classification is unknown."
            )

    return result