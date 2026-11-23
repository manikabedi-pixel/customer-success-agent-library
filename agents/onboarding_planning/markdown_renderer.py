from typing import Any


def render_onboarding_markdown(
    report: dict[str, Any],
) -> str:
    """Render a human-reviewable onboarding plan."""

    plan = report["onboarding_plan"]
    assessment = report["planning_assessment"]
    ai_planning = report["ai_planning"]

    lines = [
        "# Customer Onboarding Plan",
        "",
        "**DRAFT — HUMAN REVIEW REQUIRED**",
        "",
        f"**Deal ID:** {report['deal_id']}",
        f"**Customer:** {report.get('customer_name') or 'Not provided'}",
        "**Approval Status:** Not approved",
        "**Execution Status:** Not authorized",
        "",
        "## 1. Customer Objectives",
        "",
    ]

    objectives = plan.get("objectives", [])

    if objectives:
        for objective in objectives:
            lines.append(f"- {objective}")
    else:
        lines.append(
            "- No objectives available. Human review required."
        )

    lines.extend([
        "",
        "## 2. Proposed Onboarding Milestones",
        "",
    ])

    milestones = plan.get("milestones", [])

    if not milestones:
        lines.append(
            "No milestones generated. Human review required."
        )

    for milestone in milestones:
        lines.extend([
            f"### {milestone['title']}",
            "",
            "**Status:** Proposed",
            "",
        ])

        for task in milestone.get("tasks", []):
            lines.extend([
                f"#### {task['task_id']}: {task['title']}",
                "",
                f"**Requirement:** {task['description']}",
                f"**Owner:** {task.get('owner') or 'Not assigned'}",
                f"**Due date:** {task.get('due_date') or 'Not confirmed'}",
                f"**Status:** {task['status']}",
                "",
                "**Source references:** "
                + (
                    ", ".join(task.get("source_references", []))
                    or "Not available"
                ),
                "",
            ])

    lines.extend([
        "## 3. AI Planning Suggestions",
        "",
        f"**AI status:** {ai_planning.get('ai_status', 'unknown')}",
        "",
        "These suggestions are unverified and require human review.",
        "",
    ])

    suggestions = ai_planning.get("suggestions", [])

    if suggestions:
        for suggestion in suggestions:
            lines.extend([
                f"### {suggestion['requirement_id']}",
                "",
                f"**Suggested activity:** {suggestion['suggested_activity']}",
                f"**Rationale:** {suggestion['rationale']}",
                "**Status:** Proposed — requires human review",
                "",
            ])
    else:
        lines.append(
            "No validated AI suggestions available."
        )

    lines.extend([
        "",
        "## 4. Onboarding Risks",
        "",
    ])

    risks = assessment.get("onboarding_risks", [])

    if risks:
        for risk in risks:
            lines.extend([
                f"### {risk['risk_id']}",
                "",
                f"**Risk:** {risk['description']}",
                f"**Reason:** {risk.get('reason') or 'Not provided'}",
                "**Source references:** "
                + (
                    ", ".join(risk.get("source_note_ids", []))
                    or "Not available"
                ),
                "**Status:** Requires review",
                "",
            ])
    else:
        lines.append("No risks recorded in the handoff.")

    lines.extend([
        "",
        "## 5. Planning Gaps",
        "",
        f"- Tasks without owners: {len(assessment.get('tasks_without_owners', []))}",
        f"- Tasks without due dates: {len(assessment.get('tasks_without_due_dates', []))}",
        f"- Dependency issues detected: {assessment.get('dependency_assessment', {}).get('has_dependency_issues', False)}",
        "",
        "### Missing Information",
        "",
    ])

    missing_information = assessment.get(
        "missing_information", []
    )

    if missing_information:
        for item in missing_information:
            lines.append(f"- {item}")
    else:
        lines.append("- No missing information recorded.")

    lines.extend([
        "",
        "## 6. Human Review Checklist",
        "",
        "- [ ] Verify extracted requirements against original sources.",
        "- [ ] Confirm customer objectives and success criteria.",
        "- [ ] Validate implementation scope and dependencies.",
        "- [ ] Review onboarding risks.",
        "- [ ] Confirm task owners.",
        "- [ ] Confirm milestone dates and deadlines.",
        "- [ ] Review AI-generated planning suggestions.",
        "- [ ] Resolve missing information and open questions.",
        "- [ ] Obtain explicit human approval before execution.",
        "",
        "---",
        "",
        "**DRAFT — HUMAN REVIEW REQUIRED**",
        "",
        "This report is a planning aid, not an approved customer commitment.",
    ])

    return "\n".join(lines) + "\n"