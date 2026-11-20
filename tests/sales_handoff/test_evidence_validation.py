from agents.sales_handoff.evidence_validation import (
    assess_evidence_availability,
)


def make_draft(evidence, source_ids, excerpts):
    return {
        "sales_intelligence": [
            {
                "evidence": evidence,
                "source_note_ids": source_ids,
            }
        ],
        "source_notes": [
            {
                "source_id": "NOTE-001",
                "evidence_excerpts": excerpts,
            }
        ],
    }


def test_matching_evidence_excerpt():
    draft = make_draft(
        "Customer requested Salesforce integration.",
        ["NOTE-001"],
        ["Customer requested Salesforce integration."],
    )

    result = assess_evidence_availability(draft)

    assert result["facts_with_matching_excerpts"] == 1
    assert result["results"][0]["evidence_match"] is True
    assert (
        result["results"][0]["verification_status"]
        == "Evidence excerpt matched"
    )
    assert result["requires_human_review"] is True


def test_mismatching_evidence_excerpt():
    draft = make_draft(
        "Customer requested Salesforce integration.",
        ["NOTE-001"],
        ["Customer requested executive dashboards."],
    )

    result = assess_evidence_availability(draft)

    assert result["facts_with_matching_excerpts"] == 0
    assert result["results"][0]["evidence_match"] is False
    assert (
        result["results"][0]["verification_status"]
        == "Evidence excerpt mismatch"
    )


def test_missing_evidence_excerpt():
    draft = make_draft(
        "Customer requested Salesforce integration.",
        ["NOTE-001"],
        [],
    )

    result = assess_evidence_availability(draft)

    assert result["facts_with_excerpts"] == 0
    assert result["facts_with_matching_excerpts"] == 0
    assert (
        result["results"][0]["verification_status"]
        == "Evidence excerpt unavailable"
    )


def test_missing_extracted_evidence():
    draft = make_draft(
        "",
        ["NOTE-001"],
        ["Customer requested Salesforce integration."],
    )

    result = assess_evidence_availability(draft)

    assert result["facts_with_evidence"] == 0
    assert (
        result["results"][0]["verification_status"]
        == "Extracted evidence missing"
    )


def test_invalid_source_id_cannot_match_evidence():
    draft = make_draft(
        "Customer requested Salesforce integration.",
        ["NOTE-999"],
        ["Customer requested Salesforce integration."],
    )

    result = assess_evidence_availability(draft)

    assert result["facts_with_matching_excerpts"] == 0
    assert result["results"][0]["evidence_match"] is False
    assert (
        result["results"][0]["verification_status"]
        == "Evidence excerpt unavailable"
    )


def test_multiple_facts_with_one_matching_excerpt():
    draft = {
        "sales_intelligence": [
            {
                "evidence": "Customer requested Salesforce integration.",
                "source_note_ids": ["NOTE-001"],
            },
            {
                "evidence": "Customer requested executive dashboards.",
                "source_note_ids": ["NOTE-001"],
            },
        ],
        "source_notes": [
            {
                "source_id": "NOTE-001",
                "evidence_excerpts": [
                    "Customer requested Salesforce integration.",
                ],
            }
        ],
    }

    result = assess_evidence_availability(draft)

    assert result["total_facts"] == 2
    assert result["facts_with_excerpts"] == 2
    assert result["facts_with_matching_excerpts"] == 1
    assert (
        result["results"][0]["verification_status"]
        == "Evidence excerpt matched"
    )
    assert (
        result["results"][1]["verification_status"]
        == "Evidence excerpt mismatch"
    )


def test_numeric_source_id_matches_string_reference():
    draft = {
        "sales_intelligence": [
            {
                "evidence": "Customer requested Salesforce integration.",
                "source_note_ids": ["427498006250"],
            }
        ],
        "source_notes": [
            {
                "source_id": 427498006250,
                "evidence_excerpts": [
                    "Customer requested Salesforce integration.",
                ],
            }
        ],
    }

    result = assess_evidence_availability(draft)

    assert result["facts_with_matching_excerpts"] == 1


def test_empty_handoff():
    draft = {
        "sales_intelligence": [],
        "source_notes": [],
    }

    result = assess_evidence_availability(draft)

    assert result["total_facts"] == 0
    assert result["results"] == []
    assert result["requires_human_review"] is True