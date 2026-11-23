import argparse
from dataclasses import dataclass
from pathlib import Path

from agents.customer_data_migration.schemas import (
    MigrationAssessment,
)
from agents.customer_data_migration.source_loader import (
    load_agent_sources,
)
from agents.customer_data_migration.requirement_extractor import (
    extract_migration_requirements,
)
from agents.customer_data_migration.source_inventory import (
    build_source_inventory,
)
from agents.customer_data_migration.mapping_rules import (
    assess_field_mappings,
)
from agents.customer_data_migration.data_quality_rules import (
    assess_data_quality,
)
from agents.customer_data_migration.migration_risks import (
    detect_migration_risks,
)
from agents.customer_data_migration.readiness_assessment import (
    assess_migration_readiness,
    apply_readiness_to_assessment,
)
from agents.customer_data_migration.ai_migration_advisor import (
    generate_migration_recommendations,
)
from agents.customer_data_migration.report_generator import (
    build_migration_report,
    save_migration_report,
)
from agents.customer_data_migration.markdown_renderer import (
    render_migration_markdown,
    save_migration_markdown,
)


@dataclass
class MigrationWorkflowResult:
    report: dict
    json_path: Path
    markdown_path: Path


def run_migration_workflow(
    deal_id: str,
    customer_name: str | None = None,
    output_dir: str | Path = "outputs/customer_data_migration",
    source_paths: dict | None = None,
) -> MigrationWorkflowResult:
    """
    Run a read-only migration assessment.

    This workflow does not execute or authorize migration.
    """

    if not deal_id or not deal_id.strip():
        raise ValueError("A deal ID is required.")

    deal_id = deal_id.strip()

    if source_paths is None:
        source_paths = {
            "agent_1": Path(
                f"outputs/sales_handoff/"
                f"hubspot_handoff_{deal_id}.json"
            ),
            "agent_2": Path(
                f"outputs/onboarding_planning/"
                f"onboarding_plan_{deal_id}.json"
            ),
            "agent_3": Path(
                f"outputs/onboarding_coordinator/"
                f"coordination_report_{deal_id}_report.json"
            ),
        }

    loaded = load_agent_sources(
        deal_id=deal_id,
        source_paths=source_paths,
    )

    requirements = extract_migration_requirements(
        loaded.sources
    )

    # No inventory or mappings are invented.
    # Future versions can accept explicitly verified inputs.
    inventory = build_source_inventory(
        requirements
    )

    mappings = assess_field_mappings(
        datasets=inventory.datasets,
        mappings=[],
    )

    quality = assess_data_quality(
        datasets=inventory.datasets
    )

    risks = detect_migration_risks(
        requirements,
        inventory,
        mappings,
        quality,
    )

    readiness = assess_migration_readiness(
        requirements,
        inventory,
        mappings,
        quality,
        risks,
    )

    advisor = generate_migration_recommendations(
        readiness,
        risks,
    )

    assessment = MigrationAssessment(
        deal_id=deal_id,
        customer_name=customer_name,
        requirements=requirements,
        source_systems=inventory.source_systems,
        datasets=inventory.datasets,
        field_mappings=[],
        risks=risks.risks,
    )

    assessment = apply_readiness_to_assessment(
        assessment,
        readiness,
    )

    assessment.metadata["source_loading"] = {
        "loaded_sources": sorted(loaded.sources.keys()),
        "missing_sources": list(loaded.missing_sources),
        "warnings": list(loaded.warnings),
    }

    report = build_migration_report(
        assessment,
        readiness,
        advisor,
    )

    output_dir = Path(output_dir)

    json_path = output_dir / (
        f"migration_assessment_{deal_id}.json"
    )

    markdown_path = output_dir / (
        f"migration_assessment_{deal_id}.md"
    )

    save_migration_report(
        report,
        json_path,
    )

    markdown = render_migration_markdown(
        report
    )

    save_migration_markdown(
        markdown,
        markdown_path,
    )

    return MigrationWorkflowResult(
        report=report,
        json_path=json_path,
        markdown_path=markdown_path,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Generate a read-only customer data "
            "migration assessment."
        )
    )

    parser.add_argument(
        "--deal-id",
        required=True,
        help="Deal ID to assess.",
    )

    parser.add_argument(
        "--customer-name",
        default=None,
        help="Optional customer name.",
    )

    parser.add_argument(
        "--output-dir",
        default="outputs/customer_data_migration",
        help="Directory for assessment reports.",
    )

    args = parser.parse_args()

    result = run_migration_workflow(
        deal_id=args.deal_id,
        customer_name=args.customer_name,
        output_dir=args.output_dir,
    )

    report = result.report

    print("\nCUSTOMER DATA MIGRATION ASSESSMENT")
    print("----------------------------------")
    print("Deal ID:", report["deal_id"])
    print("Customer:", report["customer_name"])
    print("Readiness:", report["readiness_status"])
    print("Requirements:", len(report["requirements"]))
    print("Risks:", len(report["risks"]))
    print("Recommendations:", len(report["recommendations"]))
    print("Human review required:", report["requires_human_review"])
    print("Migration authorized:", report["migration_authorized"])

    print("\nReports generated:")
    print("-", result.json_path)
    print("-", result.markdown_path)


if __name__ == "__main__":
    main()