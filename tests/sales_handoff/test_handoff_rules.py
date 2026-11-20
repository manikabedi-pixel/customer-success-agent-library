from agents.sales_handoff.handoff_rules import (
    identify_missing_information,
)


def test_identifies_missing_implementation_owner():
    facts = [
        {
            "status": "missing",
            "value": "Technical implementation owner not identified",
            "evidence": "The technical implementation owner has not yet been identified.",
        }
    ]

    result = identify_missing_information(facts)

    assert result == [
        "Technical implementation owner not identified"
    ]


def test_identifies_undefined_dashboard_scope():
    facts = [
        {
            "status": "customer_requested",
            "value": "Executive dashboards requested",
            "evidence": (
                "The customer asked for executive dashboards. "
                "The exact dashboard scope remains undefined."
            ),
        }
    ]

    result = identify_missing_information(facts)

    assert result == [
        "Executive dashboard scope is undefined"
    ]


def test_does_not_invent_missing_information():
    facts = [
        {
            "status": "confirmed",
            "value": "Consolidate customer reporting",
            "evidence": (
                "The customer wants to consolidate "
                "customer reporting across business units."
            ),
        }
    ]

    result = identify_missing_information(facts)

    assert result == []


def test_does_not_duplicate_missing_information():
    facts = [
        {
            "status": "missing",
            "value": "Technical implementation owner not identified",
            "evidence": "The technical implementation owner has not yet been identified.",
        },
        {
            "status": "missing",
            "value": "Technical implementation owner not identified",
            "evidence": "The technical implementation owner has not yet been identified.",
        },
    ]

    result = identify_missing_information(facts)

    assert result == [
        "Technical implementation owner not identified"
    ]