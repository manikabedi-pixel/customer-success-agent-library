from dataclasses import dataclass
from typing import Any

from agents.onboarding_coordinator.schemas import (
    CoordinationState,
    CoordinationTask,
)


@dataclass(frozen=True)
class OwnerAssignmentProposal:
    task_id: str
    proposed_owner: str
    rationale: str
    status: str = "proposed"
    requires_human_review: bool = True


def get_all_tasks(
    state: CoordinationState,
) -> list[CoordinationTask]:
    """Return all tasks across onboarding milestones."""

    return [
        task
        for milestone in state.milestones
        for task in milestone.tasks
    ]


def find_unassigned_tasks(
    state: CoordinationState,
) -> list[dict[str, Any]]:
    """Identify tasks without confirmed owners."""

    return [
        {
            "task_id": task.task_id,
            "title": task.title,
            "current_owner": task.owner,
            "status": task.status,
        }
        for task in get_all_tasks(state)
        if not isinstance(task.owner, str)
        or not task.owner.strip()
    ]


def propose_owner_assignment(
    state: CoordinationState,
    task_id: str,
    proposed_owner: str,
    rationale: str,
) -> OwnerAssignmentProposal:
    """
    Create an ownership proposal.

    Does not modify the task or assign its owner.
    """

    matching_tasks = [
        task
        for task in get_all_tasks(state)
        if task.task_id == task_id
    ]

    if len(matching_tasks) != 1:
        raise ValueError(
            "Task ID must identify exactly one task."
        )

    if not isinstance(proposed_owner, str) or not proposed_owner.strip():
        raise ValueError(
            "Proposed owner must be a nonempty string."
        )

    if not isinstance(rationale, str) or not rationale.strip():
        raise ValueError(
            "Assignment rationale must be a nonempty string."
        )

    return OwnerAssignmentProposal(
        task_id=task_id,
        proposed_owner=proposed_owner.strip(),
        rationale=rationale.strip(),
    )


def validate_owner_proposals(
    state: CoordinationState,
    proposals: list[OwnerAssignmentProposal],
) -> list[dict[str, Any]]:
    """
    Validate ownership proposals.

    Validated proposals remain unapproved.
    """

    if not isinstance(proposals, list):
        raise ValueError("Proposals must be a list.")

    task_ids = [
        task.task_id
        for task in get_all_tasks(state)
    ]

    seen_ids = set()
    validated = []

    for proposal in proposals:
        if not isinstance(proposal, OwnerAssignmentProposal):
            raise ValueError(
                "Each proposal must be an OwnerAssignmentProposal."
            )

        if task_ids.count(proposal.task_id) != 1:
            raise ValueError(
                f"Unknown or ambiguous task ID: {proposal.task_id}"
            )

        if proposal.task_id in seen_ids:
            raise ValueError(
                f"Duplicate ownership proposal: {proposal.task_id}"
            )

        if (
            not isinstance(proposal.proposed_owner, str)
            or not proposal.proposed_owner.strip()
        ):
            raise ValueError("Proposed owner is required.")

        if (
            not isinstance(proposal.rationale, str)
            or not proposal.rationale.strip()
        ):
            raise ValueError("Assignment rationale is required.")

        if (
            proposal.status != "proposed"
            or proposal.requires_human_review is not True
        ):
            raise ValueError(
                "Ownership proposals must remain unapproved."
            )

        validated.append({
            "task_id": proposal.task_id,
            "proposed_owner": proposal.proposed_owner.strip(),
            "rationale": proposal.rationale.strip(),
            "status": "proposed",
            "requires_human_review": True,
            "approved": False,
        })

        seen_ids.add(proposal.task_id)

    return validated