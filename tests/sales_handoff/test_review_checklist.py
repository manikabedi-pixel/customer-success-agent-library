from agents.sales_handoff.review_checklist import (
    generate_review_checklist,
)


def test_checklist_uses_customer_specific_facts():
    draft = {
        "missing_information": [
            "Implementation owner not identified"
        ],
        "sales_intelligence": [
            {
                "status": "customer_requested",
                "value": "Salesforce integration requested",
            },
            {
                "status": "discussed_unconfirmed",
                "value": "Six-week implementation discussed",
            },
        ],
    }

    checklist = generate_review_checklist(draft)

    assert any(
        "Implementation owner not identified" in item
        for item in checklist
    )

    assert any(
        "Salesforce integration requested" in item
        for item in checklist
    )

    assert any(
        "Six-week implementation discussed" in item
        for item in checklist
    )


def test_checklist_does_not_invent_customer_requests():
    draft = {
        "missing_information": [],
        "sales_intelligence": [
            {
                "status": "confirmed",
                "value": "Improve customer reporting",
            }
        ],
    }

    checklist = generate_review_checklist(draft)

    assert not any(
        "Salesforce" in item
        for item in checklist
    )

    assert not any(
        "migration" in item.lower()
        for item in checklist
    )


def test_checklist_removes_duplicates():
    draft = {
        "missing_information": [
            "Implementation owner missing",
            "Implementation owner missing",
        ],
        "sales_intelligence": [],
    }

    checklist = generate_review_checklist(draft)

    assert checklist.count(
        "Resolve missing information: Implementation owner missing"
    ) == 1