from dataclasses import dataclass, field
from typing import Any


@dataclass
class MigrationRequirement:
    """
    A migration-related requirement extracted from source information.

    A requirement is not considered confirmed merely because
    it appears in a handoff or AI-generated plan.
    """

    requirement_id: str
    description: str

    source_references: list[str] = field(default_factory=list)

    source_agent: str | None = None

    status: str = "proposed"

    verified: bool = False

    requires_human_review: bool = True


@dataclass
class SourceSystem:
    """
    A potential source system containing customer data.
    """

    system_id: str
    name: str

    system_type: str | None = None

    owner: str | None = None

    access_confirmed: bool = False

    verified: bool = False

    requires_human_review: bool = True


@dataclass
class DatasetInventory:
    """
    Describes a dataset that may need migration.
    """

    dataset_id: str
    name: str

    source_system_id: str | None = None

    record_count: int | None = None

    contains_sensitive_data: bool | None = None

    data_quality_assessed: bool = False

    verified: bool = False

    requires_human_review: bool = True


@dataclass
class FieldMapping:
    """
    Represents a proposed field mapping.

    No mapping is automatically approved.
    """

    mapping_id: str

    dataset_id: str

    source_field: str

    destination_field: str | None = None

    transformation_rule: str | None = None

    status: str = "proposed"

    verified: bool = False

    requires_human_review: bool = True


@dataclass
class MigrationRisk:
    """
    Represents a potential migration risk.

    Risk severity remains unassessed until reviewed.
    """

    risk_id: str

    description: str

    related_requirement_ids: list[str] = field(
        default_factory=list
    )

    related_dataset_ids: list[str] = field(
        default_factory=list
    )

    severity: str = "unassessed"

    status: str = "open"

    verified: bool = False

    requires_human_review: bool = True


@dataclass
class MigrationApproval:
    """
    Represents human review and approval information.

    This is a data structure, not an authenticated
    authorization mechanism.
    """

    reviewer_id: str | None = None

    reviewed_at: str | None = None

    decision: str = "pending"

    evidence_reference: str | None = None

    verified: bool = False


@dataclass
class MigrationAssessment:
    """
    Overall migration readiness assessment.

    This model does not authorize data movement.
    """

    deal_id: str

    customer_name: str | None = None

    requirements: list[MigrationRequirement] = field(
        default_factory=list
    )

    source_systems: list[SourceSystem] = field(
        default_factory=list
    )

    datasets: list[DatasetInventory] = field(
        default_factory=list
    )

    field_mappings: list[FieldMapping] = field(
        default_factory=list
    )

    risks: list[MigrationRisk] = field(
        default_factory=list
    )

    approval: MigrationApproval = field(
        default_factory=MigrationApproval
    )

    readiness_status: str = "not_assessed"

    requires_human_review: bool = True

    migration_authorized: bool = False

    metadata: dict[str, Any] = field(
        default_factory=dict
    )