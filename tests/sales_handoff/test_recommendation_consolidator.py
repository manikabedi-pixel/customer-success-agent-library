from agents.sales_handoff.recommendation_consolidator import (
    consolidate_recommendations,
)
from agents.sales_handoff.recommendation_prioritizer import (
    prioritize_recommendations,
)


def test_exact_overlapping_recommendations_are_consolidated():
    recommendations = [
        "Confirm scope and feasibility: Salesforce integration requested",
        "Review onboarding risk: Salesforce integration requested",
    ]

    result = consolidate_recommendations(recommendations)

    assert result == [
        "Confirm scope, feasibility, and onboarding risks: "
        "Salesforce integration requested"
    ]


def test_unrelated_recommendations_are_preserved():
    recommendations = [
        "Resolve missing information: Implementation owner missing",
        "Review onboarding risk: Data migration complexity",
    ]

    result = consolidate_recommendations(recommendations)

    assert result == recommendations


def test_duplicate_recommendations_are_removed():
    recommendations = [
        "Resolve missing information: Implementation owner missing",
        "Resolve missing information: Implementation owner missing",
    ]

    result = consolidate_recommendations(recommendations)

    assert len(result) == 1


def test_consolidated_recommendations_receive_high_priority():
    recommendations = [
        "Confirm scope and feasibility: Salesforce integration requested",
        "Review onboarding risk: Salesforce integration requested",
    ]

    consolidated = consolidate_recommendations(recommendations)
    prioritized = prioritize_recommendations(consolidated)

    assert len(prioritized) == 1
    assert prioritized[0]["priority"] == "High"


def test_empty_recommendations():
    assert consolidate_recommendations([]) == []


def test_differently_worded_issues_are_not_automatically_merged():
    recommendations = [
        "Confirm scope and feasibility: Salesforce integration requested",
        "Review onboarding risk: Salesforce integration may require custom work",
    ]

    result = consolidate_recommendations(recommendations)

    assert result == recommendations