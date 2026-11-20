from agents.sales_handoff.recommendation_prioritizer import (
    prioritize_recommendations,
)


def test_recommendations_sorted_by_priority():
    recommendations = [
        "Review onboarding risk: Salesforce integration",
        "Confirm scope and feasibility: Salesforce integration",
        "Resolve missing information: Implementation owner missing",
        "Verify before committing: Six-week timeline",
    ]

    result = prioritize_recommendations(recommendations)

    assert len(result) == 4

    assert [item["priority"] for item in result] == [
        "Critical",
        "Critical",
        "High",
        "Medium",
    ]


def test_prioritization_preserves_recommendation_text():
    recommendations = [
        "Confirm scope and feasibility: Historical data migration"
    ]

    result = prioritize_recommendations(recommendations)

    assert result[0]["recommendation"] == recommendations[0]
    assert result[0]["priority"] == "High"


def test_empty_recommendations():
    assert prioritize_recommendations([]) == []


def test_equal_priority_preserves_original_order():
    recommendations = [
        "Confirm scope: Salesforce integration",
        "Confirm feasibility: Historical data migration",
    ]

    result = prioritize_recommendations(recommendations)

    assert [item["recommendation"] for item in result] == recommendations