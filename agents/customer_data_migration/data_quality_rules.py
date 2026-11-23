from dataclasses import dataclass, field

from agents.customer_data_migration.schemas import (
    DatasetInventory,
)


@dataclass
class DataQualityResult:
    """
    Records missing data-quality evidence.

    Does not inspect or modify customer records.
    """

    datasets_assessed: int = 0

    findings: list[str] = field(
        default_factory=list
    )

    requires_human_review: bool = True


def assess_data_quality(
    datasets: list[DatasetInventory],
) -> DataQualityResult:
    """
    Assess available dataset metadata.

    Missing evidence is reported as unknown,
    not as a confirmed data-quality defect.
    """

    result = DataQualityResult(
        datasets_assessed=len(datasets),
    )

    if not datasets:
        result.findings.append(
            "No datasets available for data-quality assessment."
        )

        return result

    for dataset in datasets:

        if dataset.record_count is None:
            result.findings.append(
                f"Dataset {dataset.dataset_id}: "
                "record count has not been established."
            )

        if dataset.contains_sensitive_data is None:
            result.findings.append(
                f"Dataset {dataset.dataset_id}: "
                "sensitive-data classification is unknown."
            )

        if not dataset.data_quality_assessed:
            result.findings.append(
                f"Dataset {dataset.dataset_id}: "
                "data-quality assessment has not been confirmed."
            )

        if not dataset.verified:
            result.findings.append(
                f"Dataset {dataset.dataset_id}: "
                "dataset inventory has not been verified."
            )

    return result