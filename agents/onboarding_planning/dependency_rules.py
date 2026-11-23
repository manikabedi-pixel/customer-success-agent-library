from agents.onboarding_planning.schemas import OnboardingPlan


def assess_task_dependencies(plan: OnboardingPlan) -> dict:
    """Assess declared task dependencies without inventing them."""

    tasks = {
        task.task_id: task
        for milestone in plan.milestones
        for task in milestone.tasks
    }

    missing_dependencies = []
    self_dependencies = []
    valid_dependencies = []

    for task in tasks.values():
        for dependency_id in task.dependencies:
            if dependency_id == task.task_id:
                self_dependencies.append({
                    "task_id": task.task_id,
                    "dependency_id": dependency_id,
                })

            elif dependency_id not in tasks:
                missing_dependencies.append({
                    "task_id": task.task_id,
                    "dependency_id": dependency_id,
                })

            else:
                valid_dependencies.append({
                    "task_id": task.task_id,
                    "dependency_id": dependency_id,
                })

    return {
        "valid_dependencies": valid_dependencies,
        "missing_dependencies": missing_dependencies,
        "self_dependencies": self_dependencies,
        "has_dependency_issues": bool(
            missing_dependencies or self_dependencies
        ),
    }