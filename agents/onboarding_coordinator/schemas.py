from dataclasses import dataclass, field
from typing import Any


@dataclass
class CoordinationTask:
    task_id: str
    title: str
    description: str = ""

    owner: str | None = None
    due_date: str | None = None

    dependencies: list[str] = field(default_factory=list)
    source_references: list[str] = field(default_factory=list)

    status: str = "proposed"
    completion_percentage: int = 0

    requires_human_review: bool = True


@dataclass
class CoordinationMilestone:
    milestone_id: str
    title: str

    tasks: list[CoordinationTask] = field(default_factory=list)

    target_date: str | None = None
    status: str = "proposed"

    completion_percentage: int = 0


@dataclass
class CoordinationBlocker:
    blocker_id: str
    description: str

    related_task_ids: list[str] = field(default_factory=list)

    severity: str = "unassessed"
    status: str = "open"

    owner: str | None = None
    resolution_notes: str | None = None


@dataclass
class ApprovalRecord:
    """
    Records a claimed approval.

    An imported record is not independently verified.
    """

    reviewer_id: str | None = None
    reviewed_at: str | None = None
    decision: str = "pending"

    evidence_reference: str | None = None

    verified: bool = False


@dataclass
class CoordinationState:
    deal_id: str

    customer_name: str | None = None

    milestones: list[CoordinationMilestone] = field(
        default_factory=list
    )

    blockers: list[CoordinationBlocker] = field(
        default_factory=list
    )

    approval: ApprovalRecord = field(
        default_factory=ApprovalRecord
    )

    source_plan_status: str = "unverified"

    requires_human_review: bool = True

    execution_authorized: bool = False

    metadata: dict[str, Any] = field(
        default_factory=dict
    )