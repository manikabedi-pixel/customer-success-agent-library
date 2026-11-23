from agents.customer_data_migration.markdown_renderer import (
    render_migration_markdown,
    save_migration_markdown,
)


def make_report():
    return {
        "customer_name": "Synthetic Customer",
        "deal_id": "123",
        "readiness_status": "information_incomplete",
        "requirements": [
            {
                "requirement_id": "REQ-001",
                "description": "Assess historical CRM migration.",
            }
        ],
        "source_systems": [],
        "datasets": [],
        "field_mappings": [],
        "risks": [
            {
                "risk_id": "RISK-001",
                "description": "Source access is unconfirmed.",
                "severity": "unassessed",
            }
        ],
        "readiness_summary": {
            "total_raw_findings": 1,
            "total_unique_findings": 1,
            "unique_findings": [
                "Source access is unconfirmed."
            ],
        },
        "recommendations": [
            {
                "recommendation_id": "REC-001",
                "description": "Confirm source access.",
            }
        ],
        "approval": {
            "decision": "pending",
            "verified": False,
        },
    }


def test_markdown_title():
    markdown = render_migration_markdown(make_report())

    assert "# Customer Data Migration Assessment" in markdown


def test_markdown_customer():
    markdown = render_migration_markdown(make_report())

    assert "Synthetic Customer" in markdown


def test_markdown_requirements():
    markdown = render_migration_markdown(make_report())

    assert "REQ-001" in markdown


def test_markdown_risks():
    markdown = render_migration_markdown(make_report())

    assert "RISK-001" in markdown


def test_markdown_recommendations():
    markdown = render_migration_markdown(make_report())

    assert "REC-001" in markdown


def test_markdown_readiness():
    markdown = render_migration_markdown(make_report())

    assert "information_incomplete" in markdown


def test_markdown_human_review_notice():
    markdown = render_migration_markdown(make_report())

    assert "**Requires Human Review:** True" in markdown


def test_markdown_migration_not_authorized():
    markdown = render_migration_markdown(make_report())

    assert "**Migration Authorized:** False" in markdown


def test_markdown_missing_inventory():
    markdown = render_migration_markdown(make_report())

    assert "No source systems identified." in markdown
    assert "No datasets identified." in markdown


def test_markdown_saves_file(tmp_path):
    markdown = render_migration_markdown(make_report())

    path = tmp_path / "migration_report.md"

    save_migration_markdown(markdown, path)

    assert path.exists()
    assert "Customer Data Migration Assessment" in (
        path.read_text(encoding="utf-8")
    )


def test_markdown_escapes_pipe():
    report = make_report()

    report["customer_name"] = "Customer | Example"

    markdown = render_migration_markdown(report)

    assert "Customer \\| Example" in markdown


def test_markdown_escapes_html():
    report = make_report()

    report["customer_name"] = "<script>alert(1)</script>"

    markdown = render_migration_markdown(report)

    assert "<script>" not in markdown
    assert "&lt;script&gt;" in markdown