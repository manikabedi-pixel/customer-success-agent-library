from agents.customer_data_migration.requirement_extractor import (
    extract_migration_requirements,
    extract_text,
    is_migration_related,
)


def test_detect_migration_keyword():
    assert is_migration_related(
        "Customer needs to migrate historical records."
    )


def test_detect_data_transfer():
    assert is_migration_related(
        "Data transfer from the existing CRM is required."
    )


def test_detect_legacy_data():
    assert is_migration_related(
        "Legacy data needs to be reviewed."
    )


def test_ignore_unrelated_statement():
    assert not is_migration_related(
        "Customer requires administrator training."
    )


def test_extract_plain_text():
    assert extract_text(
        "Migration assessment required"
    ) == "Migration assessment required"


def test_extract_description_from_dict():
    assert extract_text({
        "description": "Migrate historical data",
    }) == "Migrate historical data"


def test_ignore_unsupported_structure():
    assert extract_text({
        "unknown_field": "Migrate historical data",
    }) is None


def test_extract_agent_1_candidate():
    sources = {
        "agent_1": {
            "sales_intelligence": [
                {
                    "description":
                        "Customer discussed migrating historical CRM data."
                }
            ]
        }
    }

    requirements = extract_migration_requirements(sources)

    assert len(requirements) == 1

    requirement = requirements[0]

    assert requirement.source_agent == "agent_1"
    assert requirement.status == "proposed"
    assert requirement.verified is False
    assert requirement.requires_human_review is True


def test_extract_agent_2_objective():
    sources = {
        "agent_2": {
            "onboarding_plan": {
                "objectives": [
                    "Assess historical data migration requirements."
                ]
            }
        }
    }

    requirements = extract_migration_requirements(sources)

    assert len(requirements) == 1
    assert requirements[0].source_agent == "agent_2"


def test_ignore_unrelated_objectives():
    sources = {
        "agent_2": {
            "onboarding_plan": {
                "objectives": [
                    "Complete administrator training."
                ]
            }
        }
    }

    requirements = extract_migration_requirements(sources)

    assert requirements == []


def test_agent_3_issues_do_not_create_requirements():
    sources = {
        "agent_3": {
            "issues": [
                {
                    "description":
                        "Migration task has no assigned owner."
                }
            ]
        }
    }

    requirements = extract_migration_requirements(sources)

    assert requirements == []


def test_requirements_preserve_source_references():
    sources = {
        "agent_1": {
            "sales_intelligence": [
                "Customer discussed migrating legacy records."
            ]
        }
    }

    requirements = extract_migration_requirements(sources)

    assert requirements[0].source_references == [
        "agent_1.sales_intelligence[0]"
    ]


def test_no_migration_evidence_returns_empty_list():
    sources = {
        "agent_1": {
            "sales_intelligence": [
                "Customer requires user training."
            ]
        },
        "agent_2": {
            "onboarding_plan": {
                "objectives": [
                    "Configure the customer workspace."
                ]
            }
        },
    }

    requirements = extract_migration_requirements(sources)

    assert requirements == []


def test_multiple_candidates_remain_unverified():
    sources = {
        "agent_1": {
            "sales_intelligence": [
                "Customer discussed legacy data migration.",
                "Historical data may need to be imported.",
            ]
        }
    }

    requirements = extract_migration_requirements(sources)

    assert len(requirements) == 2

    assert all(
        requirement.verified is False
        for requirement in requirements
    )

    assert all(
        requirement.requires_human_review is True
        for requirement in requirements
    )