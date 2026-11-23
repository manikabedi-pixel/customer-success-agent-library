from typing import Any


def render_coordination_markdown(
    report: dict[str, Any],
) -> str:
    """Render a coordination report as Markdown."""

    lines = [
        "# Onboarding Coordination Report",
        "",
        f"**Customer:** {report.get('customer_name') or 'Unknown'}",
        f"**Deal ID:** {report['deal_id']}",
        f"**Status:** {report['status']}",
        f"**Generated:** {report['generated_at']}",
        "",
        "## Approval and Execution",
        "",
        f"- Source plan status: {report['source_plan_status']}",
        f"- Approval verified: {report['approval']['verified']}",
        (
            "- Internal coordination allowed: "
            f"{report['coordination']['can_begin_internal_coordination']}"
        ),
        "- External execution authorized: False",
        "- Human review required: True",
        "",
        "## Overall Progress",
        "",
    ]

    progress = report["progress"]

    lines.extend([
        f"- Total milestones: {progress['total_milestones']}",
        f"- Total tasks: {progress['total_tasks']}",
        f"- Reported completed tasks: {progress['completed_tasks']}",
        (
            "- Reported completion: "
            f"{progress['reported_completion_percentage']}%"
        ),
        "- Completion independently verified: False",
        "",
        "## Milestone Progress",
        "",
    ])

    for milestone in progress["milestones"]:
        lines.extend([
            f"### {milestone['title']}",
            "",
            f"- Total tasks: {milestone['total_tasks']}",
            f"- Reported completed: {milestone['completed_tasks']}",
            f"- Blocked: {milestone['blocked_tasks']}",
            (
                "- Reported completion: "
                f"{milestone['reported_completion_percentage']}%"
            ),
            "",
        ])

    lines.extend([
        "## Detected Planning and Task Issues",
        "",
    ])

    issue_summary = report["issue_summary"]

    lines.append(
        f"**Total detected issues:** {issue_summary['total_issues']}"
    )
    lines.append("")

    for issue_type, count in issue_summary["issue_counts"].items():
        lines.append(
            f"- {issue_type.replace('_', ' ').title()}: {count}"
        )

    lines.extend([
        "",
        "### Issue Details",
        "",
    ])

    for issue in report["issues"]:
        lines.append(
            f"- **{issue['task_id']}** "
            f"[{issue['issue_type']}]: "
            f"{issue['description']}"
        )

    lines.extend([
        "",
        "## Unassigned Tasks",
        "",
    ])

    for task in report["unassigned_tasks"]:
        lines.append(
            f"- **{task['task_id']}** — {task['title']}"
        )

    lines.extend([
        "",
        "## AI Coordination Recommendations",
        "",
    ])

    ai = report["ai"]

    lines.append(
        f"**AI status:** {ai['status']}"
    )
    lines.append("")

    if ai["recommendations"]:
        for recommendation in ai["recommendations"]:
            lines.extend([
                (
                    f"### {recommendation['task_id']} "
                    f"— {recommendation['issue_type']}"
                ),
                "",
                (
                    "**Suggested action:** "
                    f"{recommendation['recommended_action']}"
                ),
                "",
                (
                    "**Rationale:** "
                    f"{recommendation['rationale']}"
                ),
                "",
                "**Approval:** Pending human review",
                "",
            ])
    else:
        lines.extend([
            "No AI recommendations included.",
            "",
        ])

    lines.extend([
        "## Human Review Checklist",
        "",
        "- [ ] Confirm task owners.",
        "- [ ] Confirm task due dates.",
        "- [ ] Review blocked or overdue tasks.",
        "- [ ] Review dependency issues.",
        "- [ ] Review AI recommendations.",
        "- [ ] Verify reported task completion.",
        "- [ ] Obtain approval through an authenticated workflow.",
        "",
        "**This report does not authorize onboarding execution.**",
        "",
    ])

    return "\n".join(lines)