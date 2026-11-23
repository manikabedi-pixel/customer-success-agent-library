from dataclasses import dataclass, field
from typing import Any


@dataclass
class OnboardingTask:
    task_id: str
    title: str
    description: str = ""
    owner: str | None = None
    due_date: str | None = None
    dependencies: list[str] = field(default_factory=list)
    source_references: list[str] = field(default_factory=list)
    status: str = "proposed"


@dataclass
class OnboardingMilestone:
    milestone_id: str
    title: str
    tasks: list[OnboardingTask] = field(default_factory=list)
    target_date: str | None = None
    status: str = "proposed"


@dataclass
class OnboardingPlan:
    deal_id: str
    customer_name: str | None = None
    objectives: list[str] = field(default_factory=list)
    milestones: list[OnboardingMilestone] = field(default_factory=list)
    missing_information: list[str] = field(default_factory=list)
    unresolved_questions: list[str] = field(default_factory=list)
    source_handoff_status: str = "unverified"
    requires_human_review: bool = True
    approved: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)