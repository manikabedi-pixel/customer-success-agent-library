def validate_source_references(draft: dict) -> dict:
    """
    Validate fact source references against notes in the handoff.

    Supports source_id, note_id, and id.

    This checks internal consistency only.
    It does not verify records directly with HubSpot.
    """

    facts = draft.get("sales_intelligence", [])
    notes = draft.get("source_notes", [])

    known_note_ids = set()

    for note in notes:
        if not isinstance(note, dict):
            continue

        note_id = (
            note.get("source_id")
            or note.get("note_id")
            or note.get("id")
        )

        if note_id is not None:
            known_note_ids.add(str(note_id))

    invalid_references = []
    facts_without_sources = []

    for index, fact in enumerate(facts):
        source_ids = fact.get("source_note_ids") or []

        if not source_ids:
            facts_without_sources.append(index)
            continue

        for source_id in source_ids:
            if str(source_id) not in known_note_ids:
                invalid_references.append({
                    "fact_index": index,
                    "source_note_id": str(source_id),
                })

    return {
        "valid": (
            not invalid_references
            and not facts_without_sources
        ),
        "invalid_references": invalid_references,
        "facts_without_sources": facts_without_sources,
        "known_note_count": len(known_note_ids),
    }