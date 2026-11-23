from dataclasses import dataclass, field

from agents.customer_data_migration.schemas import (
    DatasetInventory,
    FieldMapping,
)


@dataclass
class MappingAssessmentResult:
    """
    Assessment of supplied field mappings.

    This does not approve or execute mappings.
    """

    total_mappings: int = 0

    verified_mappings: int = 0

    unverified_mappings: int = 0

    missing_information: list[str] = field(
        default_factory=list
    )

    requires_human_review: bool = True


def assess_field_mappings(
    datasets: list[DatasetInventory],
    mappings: list[FieldMapping],
) -> MappingAssessmentResult:
    """
    Check the completeness of supplied field mappings.

    Does not generate mappings or infer destination fields.
    """

    result = MappingAssessmentResult(
        total_mappings=len(mappings),
        verified_mappings=sum(
            mapping.verified
            for mapping in mappings
        ),
        unverified_mappings=sum(
            not mapping.verified
            for mapping in mappings
        ),
    )

    dataset_ids = {
        dataset.dataset_id
        for dataset in datasets
    }

    if not datasets:
        result.missing_information.append(
            "No datasets available for field mapping assessment."
        )

    if not mappings:
        result.missing_information.append(
            "No field mappings have been supplied."
        )

    for mapping in mappings:

        if mapping.dataset_id not in dataset_ids:
            result.missing_information.append(
                f"Mapping {mapping.mapping_id} references "
                f"unknown dataset {mapping.dataset_id}."
            )

        if not mapping.destination_field:
            result.missing_information.append(
                f"Mapping {mapping.mapping_id} "
                "has no destination field."
            )

        if not mapping.verified:
            result.missing_information.append(
                f"Mapping {mapping.mapping_id} "
                "requires verification."
            )

    return result