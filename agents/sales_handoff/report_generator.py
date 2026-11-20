import argparse
import json
from pathlib import Path

from agents.sales_handoff.handoff_rules import identify_missing_information
from agents.sales_handoff.quality_scoring import calculate_handoff_quality
from agents.sales_handoff.review_checklist import generate_review_checklist

from agents.sales_handoff.quality_recommendations import (
    generate_quality_recommendations,
)

from agents.sales_handoff.recommendation_prioritizer import (
    prioritize_recommendations,
)
from agents.sales_handoff.recommendation_consolidator import (
    consolidate_recommendations,
)
from agents.sales_handoff.readiness_assessment import (
    assess_onboarding_readiness,
)
from agents.sales_handoff.evidence_validation import (
    assess_evidence_availability,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "outputs" / "sales_handoff"


def generate_markdown_report(draft: dict) -> str:
    """
    Generate a human-readable Sales-to-CS handoff report.

    Uses existing handoff data.
    Does not call HubSpot or OpenAI.
    """

    # --------------------------------------------------
    # 1. Extract handoff information
    # --------------------------------------------------

    customer = draft.get("customer", {})
    deal = draft.get("deal", {})
    stakeholders = draft.get("stakeholders", [])
    facts = draft.get("sales_intelligence", [])
    risks = draft.get("onboarding_risks", [])
    source_notes = draft.get("source_notes", [])

    # Recalculate missing information using current rules.
    missing_information = identify_missing_information(facts)

    # --------------------------------------------------
    # 2. Calculate handoff quality
    # --------------------------------------------------

    quality_draft = {
        **draft,
        "missing_information": missing_information,
    }

    quality = calculate_handoff_quality(quality_draft)

    readiness_draft = {
    **draft,
    "missing_information": missing_information,
}
    readiness = assess_onboarding_readiness(readiness_draft)

    # --------------------------------------------------
    # 3. Start Markdown report
    # --------------------------------------------------

    lines = [
        "# Sales-to-Customer-Success Handoff",
        "",
        "> **DRAFT — HUMAN REVIEW REQUIRED**",
        "",
        "### Handoff Quality Assessment",
        "",
        f"**Quality Score:** {quality['score']}/100",
        "",
        f"**Quality Rating:** {quality['rating']}",
        "",
        "| Quality Dimension | Score | Maximum |",
        "|---|---:|---:|",
        (
            f"| Evidence Coverage | "
            f"{quality['breakdown']['evidence_coverage']} | 30 |"
        ),
        (
            f"| Missing Information | "
            f"{quality['breakdown']['missing_information']} | 25 |"
        ),
        (
            f"| Unconfirmed Commitments | "
            f"{quality['breakdown']['unconfirmed_commitments']} | 20 |"
        ),
        (
            f"| Onboarding Risks | "
            f"{quality['breakdown']['onboarding_risks']} | 15 |"
        ),
        (
            f"| Human Review Safeguards | "
            f"{quality['breakdown']['human_review_safeguards']} | 10 |"
        ),
        "",
        (
            "**Important:** This score is for review prioritization only. "
            "It does not constitute handoff approval."
        ),
        "",
    ]

    lines.extend([

        "### Onboarding Readiness Assessment",
        "",
        f"**Readiness:** {readiness['readiness']}",
        f"**Supported Facts:** {readiness['supported_facts']}/{readiness['total_facts']}",
        "**Human Review Required:** YES",
        "",
        "**Assessment Reasons:**",
        "",
    ])

    if readiness["reasons"]:
        for reason in readiness["reasons"]:
            lines.append(f"- {reason}")
    else:
        lines.append(
            "- No clarification issues identified by current readiness rules."
        )
    lines.append("")

    # --------------------------------------------------
    # Source Reference Validation
    # --------------------------------------------------

    source_validation = readiness["source_validation"]
    lines.extend([
        "### Source Reference Validation",
        "",
        (
            "**Validation Status:** "
            + (
                "Passed"
                if source_validation["valid"]
                else "Requires clarification"
            )
        ),

        (
            "**Available Source Notes:** "
            f"{source_validation['known_note_count']}"
        ),

        (
            "**Invalid References:** "
            f"{len(source_validation['invalid_references'])}"
        ),
        (
            "**Facts Without Sources:** "
            f"{len(source_validation['facts_without_sources'])}"
        ),
        "",
    ])

    if source_validation["invalid_references"]:
        lines.append("**Invalid Source References:**")
        lines.append("")
        for item in source_validation["invalid_references"]:
            lines.append(
                f"- Fact {item['fact_index'] + 1}: "
                f"Source note {item['source_note_id']} not found"
            )
        lines.append("")
    if source_validation["facts_without_sources"]:
        lines.append("**Facts Missing Source References:**")
        lines.append("")
        for index in source_validation["facts_without_sources"]:
            lines.append(f"- Fact {index + 1}")
        lines.append("")
    lines.extend([
        (
            "**Note:** Validation checks whether referenced notes "
            "exist in the handoff. It does not independently verify "
            "the CRM records or whether the notes support each claim."
        ),
        "",
    ])

    # --------------------------------------------------
    # Evidence Validation
    # --------------------------------------------------

    evidence_validation = assess_evidence_availability(draft)

    # --------------------------------------------------
    # Evidence Review Summary
    # --------------------------------------------------
    
    evidence_results = evidence_validation["results"]

    matching_count = sum(
        item["verification_status"] == "Evidence excerpt matched"
        for item in evidence_results
    )

    mismatch_count = sum(
        item["verification_status"] == "Evidence excerpt mismatch"
        for item in evidence_results
    )

    unavailable_count = sum(
        item["verification_status"] == "Evidence excerpt unavailable"
        for item in evidence_results
    )

    missing_evidence_count = sum(
        item["verification_status"] == "Extracted evidence missing"
        for item in evidence_results
    )

    attention_count = (
        mismatch_count
        + unavailable_count
        + missing_evidence_count
    )

    lines.extend([
        "### Evidence Review Summary",
        "",
        f"**Total Facts:** {len(evidence_results)}",
        f"**Matching Evidence Excerpts:** {matching_count}",
        f"**Evidence Mismatches:** {mismatch_count}",
        f"**Unavailable Evidence Excerpts:** {unavailable_count}",
        f"**Facts Missing Extracted Evidence:** {missing_evidence_count}",
        f"**Facts Requiring Evidence Investigation:** {attention_count}",
        "",
        "**Human Review Required:** YES",
        "",
    ])    

    lines.extend([
        "### Evidence Validation Assessment",
        "",
        (
            "**Total Extracted Facts:** "
            f"{evidence_validation['total_facts']}"
        ),
        (
            "**Facts With Evidence:** "
            f"{evidence_validation['facts_with_evidence']}"
        ),
        (
            "**Facts With Preserved Excerpts:** "
            f"{evidence_validation['facts_with_excerpts']}"
        ),
        (
            "**Facts With Matching Excerpts:** "
            f"{evidence_validation['facts_with_matching_excerpts']}"
        ),
        "",
        "**Fact-Level Evidence Status:**",
        "",
    ])

    for item in evidence_validation["results"]:
        lines.append(
            f"- Fact {item['fact_index'] + 1}: "
            f"{item['verification_status']}"
        )

    # --------------------------------------------------

    # Evidence Review Recommendations

    # --------------------------------------------------

    evidence_review_actions = []

    for item in evidence_validation["results"]:
        fact_number = item["fact_index"] + 1
        status = item["verification_status"]

        if status == "Extracted evidence missing":
            evidence_review_actions.append(
                f"- Fact {fact_number}: Obtain supporting evidence "
                "before relying on this claim."
            )
        elif status == "Evidence excerpt mismatch":
            evidence_review_actions.append(
                f"- Fact {fact_number}: Compare the extracted evidence "
                "with the original CRM note and resolve the mismatch."
            )
        elif status == "Evidence excerpt unavailable":
            evidence_review_actions.append(
                f"- Fact {fact_number}: Retrieve the original CRM note "
                "and verify the supporting evidence."
            )
        elif status == "Evidence excerpt matched":
            evidence_review_actions.append(
                f"- Fact {fact_number}: Review the original CRM note "
                "to confirm the excerpt supports the claim."
            )
    lines.extend([
        "",
        "**Recommended Evidence Review Actions:**",
        "",
    ])

    if evidence_review_actions:
        lines.extend(evidence_review_actions)
    else:
        lines.append(
            "- No extracted facts available for evidence review."
        )

    lines.extend([
        "",
        (
            "**Verification Note:** Matching excerpts confirm "
            "internal consistency within the saved handoff. "
            "They do not independently establish that the "
            "original CRM note supports the extracted claim."
        ),
        "",
        "**Human Review Required:** YES",
        "",
    ])

    # --------------------------------------------------
    # 4. Customer Overview
    # --------------------------------------------------

    lines.extend([
        "## 1. Customer Overview",
        "",
        f"**Customer:** {customer.get('name', 'Not specified')}",
        f"**Deal:** {deal.get('deal_name', 'Not specified')}",
        f"**Deal ID:** {deal.get('deal_id', 'Not specified')}",
        f"**Deal Amount:** {deal.get('amount', 'Not specified')}",
        f"**Deal Stage:** {deal.get('stage', 'Not specified')}",
        "",
    ])

    # --------------------------------------------------
    # 5. Key Stakeholders
    # --------------------------------------------------

    lines.extend([
        "## 2. Key Stakeholders",
        "",
    ])

    if stakeholders:
        for stakeholder in stakeholders:
            lines.append(
                f"- **{stakeholder.get('name', 'Unknown')}** — "
                f"{stakeholder.get('job_title', 'Role not specified')}"
            )
    else:
        lines.append("- No stakeholders identified.")

    lines.append("")

    # --------------------------------------------------
    # 6. Business Objectives
    # --------------------------------------------------

    lines.extend([
        "## 3. Business Objectives",
        "",
    ])

    objectives = [
        fact
        for fact in facts
        if fact.get("category") == "business_objective"
        and fact.get("status") == "confirmed"
    ]

    if objectives:
        for fact in objectives:
            lines.append(f"- {fact.get('value', 'Not specified')}")
    else:
        lines.append("- No confirmed business objectives identified.")

    lines.append("")

    # --------------------------------------------------
    # 7. Customer Requests
    # --------------------------------------------------

    lines.extend([
        "## 4. Customer Requests",
        "",
    ])

    requests = [
        fact
        for fact in facts
        if fact.get("status") == "customer_requested"
    ]

    if requests:
        for fact in requests:
            lines.append(f"- {fact.get('value', 'Not specified')}")
    else:
        lines.append("- No customer requests identified.")

    lines.append("")

    # --------------------------------------------------
    # 8. Unconfirmed Commitments and Timelines
    # --------------------------------------------------

    lines.extend([
        "## 5. Unconfirmed Commitments and Timelines",
        "",
    ])

    unconfirmed = [
        fact
        for fact in facts
        if fact.get("status") == "discussed_unconfirmed"
    ]

    if unconfirmed:
        for fact in unconfirmed:
            lines.append(
                f"- {fact.get('value', 'Not specified')} "
                "**(Not confirmed)**"
            )
    else:
        lines.append("- No unconfirmed commitments identified.")

    lines.append("")

    # --------------------------------------------------
    # 9. Missing Information
    # --------------------------------------------------

    lines.extend([
        "## 6. Missing Information",
        "",
    ])

    if missing_information:
        for item in missing_information:
            lines.append(f"- {item}")
    else:
        lines.append("- No missing information identified by current rules.")

    lines.append("")

    # --------------------------------------------------
    # 10. Onboarding Risks
    # --------------------------------------------------

    lines.extend([
        "## 7. Onboarding Risks",
        "",
    ])

    if risks:
        for risk in risks:
            if isinstance(risk, dict):
                description = risk.get(
                    "description",
                    risk.get("risk", "Unspecified risk"),
                )
                reason = risk.get("reason")

                lines.append(f"- **Risk:** {description}")

                if reason:
                    lines.append(f"  - Reason: {reason}")

                note_ids = risk.get("source_note_ids", [])

                if note_ids:
                    lines.append(
                        f"  - Source notes: {', '.join(map(str, note_ids))}"
                    )
            else:
                lines.append(f"- {risk}")
    else:
        lines.append("- No onboarding risks identified.")

    lines.append("")

    # --------------------------------------------------
    # 11. Source Evidence
    # --------------------------------------------------

    lines.extend([
        "## 8. Source Evidence",
        "",
    ])

    if facts:
        for fact in facts:
            value = fact.get("value", "Not specified")
            evidence = fact.get("evidence", "No evidence provided")
            source_ids = fact.get("source_note_ids", [])

            lines.append(f"**Fact:** {value}")
            lines.append("")
            lines.append(f"- Status: {fact.get('status', 'Not specified')}")
            lines.append(f"- Evidence: {evidence}")

            if source_ids:
                lines.append(
                    f"- Source note IDs: {', '.join(map(str, source_ids))}"
                )
            else:
                lines.append("- Source note IDs: Not available")

            lines.append("")
    else:
        lines.append("- No extracted sales intelligence available.")
        lines.append("")

    # Include original source-note references when available.
    if source_notes:
        lines.extend([
            "### Original CRM Source Notes",
            "",
        ])

        for note in source_notes:
            if isinstance(note, dict):
                note_id = (
                    note.get("note_id")
                    or note.get("id")
                    or "Unknown"
                )

                lines.append(f"- CRM Note ID: {note_id}")
            else:
                lines.append(f"- Source note: {note}")

        lines.append("")

    # --------------------------------------------------
    # Quality Improvement Recommendations
    # --------------------------------------------------

    recommendations_draft = {
        **draft,
        "missing_information": missing_information,
    }

    recommendations = generate_quality_recommendations(
        recommendations_draft
    )

    consolidated_recommendations = consolidate_recommendations(
        recommendations
    )

    prioritized_recommendations = prioritize_recommendations(
        consolidated_recommendations
    )

    lines.extend([
        "### Quality Improvement Recommendations",
        "",
    ])

    if prioritized_recommendations:
        for number, item in enumerate(
            prioritized_recommendations,
            start=1,
        ):
            lines.append(
                f"{number}. **[{item['priority']}]** "
                f"{item['recommendation']}"
            )
    else:
        lines.append(
            "No additional recommendations identified by current rules."
        )
    lines.append("")

    # --------------------------------------------------
    # 12. Dynamic Human Review Checklist
    # --------------------------------------------------

    lines.extend([
        "## 9. Human Review Checklist",
        "",
        "Complete these checks before approving the handoff:",
        "",
    ])

    review_draft = {
        **draft,
        "missing_information": missing_information,
    }

    checklist = generate_review_checklist(review_draft)

    for item in checklist:
        lines.append(f"- [ ] {item}")

    lines.append("")

    # --------------------------------------------------
    # 13. Handoff Approval
    # --------------------------------------------------

    lines.extend([
        "## 10. Handoff Approval",
        "",
        "**Reviewed by:** ____________________",
        "",
        "**Review date:** ____________________",
        "",
        "**Decision:** Pending review",
        "",
        "**Comments:** ____________________",
        "",
        "---",
        "",
        "**Status:** DRAFT",
        "",
        "**Human Review Required:** YES",
        "",
    ])

    return "\n".join(lines)


def main():
    """
    Generate Markdown from an existing handoff JSON file.

    This command does not call HubSpot or OpenAI.
    """

    parser = argparse.ArgumentParser(
        description="Generate a Sales-to-CS Markdown handoff report."
    )

    parser.add_argument(
        "--deal-id",
        required=True,
        help="HubSpot deal ID",
    )

    args = parser.parse_args()

    json_path = (
        OUTPUT_DIR / f"hubspot_handoff_{args.deal_id}.json"
    )

    markdown_path = (
        OUTPUT_DIR / f"hubspot_handoff_{args.deal_id}.md"
    )

    if not json_path.exists():
        raise FileNotFoundError(
            f"Handoff JSON not found: {json_path}"
        )

    with json_path.open("r", encoding="utf-8") as file:
        draft = json.load(file)

    if draft.get("status") != "draft":
        raise ValueError(
            "Only draft handoffs can be converted into reports."
        )

    if draft.get("requires_human_review") is not True:
        raise ValueError(
            "Handoff must require human review."
        )

    report = generate_markdown_report(draft)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    markdown_path.write_text(
        report,
        encoding="utf-8",
    )

    print("\n=== SALES-TO-CS MARKDOWN REPORT ===")
    print("Deal ID:", args.deal_id)
    print("Markdown:", markdown_path)
    print("Status: DRAFT")
    print("Human review required: YES")


if __name__ == "__main__":
    main()