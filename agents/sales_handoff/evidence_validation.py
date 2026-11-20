def assess_evidence_availability(draft: dict) -> dict:
    """
    Check whether extracted evidence is preserved in source notes.

    This checks internal evidence consistency, not whether
    a claim is factually correct or independently verified.
    """

    facts = draft.get("sales_intelligence", [])
    notes = draft.get("source_notes", [])

    source_lookup = {}

    for note in notes:
        if not isinstance(note, dict):
            continue

        source_id = (
            note.get("source_id")
            or note.get("note_id")
            or note.get("id")
        )

        if source_id is not None:
            source_lookup[str(source_id)] = note

    results = []

    for index, fact in enumerate(facts):
        evidence = fact.get("evidence")
        source_ids = fact.get("source_note_ids") or []

        evidence_present = (
            isinstance(evidence, str)
            and bool(evidence.strip())
        )

        excerpt_available = False
        evidence_match = False

        for source_id in source_ids:
            note = source_lookup.get(str(source_id))

            if note is None:
                continue

            excerpts = note.get("evidence_excerpts") or []

            if isinstance(excerpts, list):
                valid_excerpts = [
                    excerpt
                    for excerpt in excerpts
                    if isinstance(excerpt, str)
                    and excerpt.strip()
                ]
            else:
                valid_excerpts = []

            if valid_excerpts:
                excerpt_available = True

            if evidence_present and evidence in valid_excerpts:
                evidence_match = True

        if not evidence_present:
            status = "Extracted evidence missing"
        elif evidence_match:
            status = "Evidence excerpt matched"
        elif excerpt_available:
            status = "Evidence excerpt mismatch"
        else:
            status = "Evidence excerpt unavailable"

        results.append({
            "fact_index": index,
            "evidence_present": evidence_present,
            "source_text_available": False,
            "excerpt_available": excerpt_available,
            "evidence_match": evidence_match,
            "requires_verification": True,
            "verification_status": status,
        })

    return {
        "total_facts": len(facts),
        "facts_with_evidence": sum(
            item["evidence_present"]
            for item in results
        ),
        "facts_with_source_text": 0,
        "facts_with_excerpts": sum(
            item["excerpt_available"]
            for item in results
        ),
        "facts_with_matching_excerpts": sum(
            item["evidence_match"]
            for item in results
        ),
        "results": results,
        "requires_human_review": True,
    }