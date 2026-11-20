def identify_missing_information(extracted_facts: list[dict]) -> list[str]:
    """
    Identify missing information from evidence-backed AI facts.

    Does not call OpenAI or HubSpot.
    """

    missing_information = []

    for fact in extracted_facts:
        status = fact["status"]
        value = fact["value"]
        evidence = fact["evidence"]

        if status == "missing":
            if value not in missing_information:
                missing_information.append(value)

        if "dashboard scope remains undefined" in evidence.lower():
            gap = "Executive dashboard scope is undefined"

            if gap not in missing_information:
                missing_information.append(gap)

    return missing_information