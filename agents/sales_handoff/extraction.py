import os

from dotenv import load_dotenv
from openai import OpenAI

from agents.sales_handoff.ai_schemas import (
    SalesIntelligenceExtraction,
)


SYSTEM_PROMPT = """
You are a Sales-to-Customer-Success handoff analyst
for a B2B SaaS company.

Your job is to extract information from sales notes
without inventing facts or commitments.

Rules:

1. Extract only information supported by the notes.

2. Distinguish carefully between:
   - confirmed: explicitly presented as agreed or established
   - customer_requested: requested but not established as agreed
   - discussed_unconfirmed: discussed, proposed, or uncertain
   - missing: explicitly stated as unavailable or not identified

3. Never convert a proposed timeline into a commitment.

4. Never treat a customer request as an approved deliverable
   unless the notes explicitly establish that agreement.

5. For every extracted fact, include an exact supporting
   quotation copied from the provided notes.

6. If evidence is insufficient, do not invent it.

7. Treat "confirmed" as confirmed within the supplied notes,
   not independently verified against a contract.

8. Set requires_verification to true for requests,
   uncertain information, and missing details.

9. Identify relevant missing information and potential
   handoff risks.

10. Return information using the required structured schema.
"""


def extract_sales_intelligence(
    sales_notes: list[str],
) -> SalesIntelligenceExtraction:
    """
    Extract structured sales intelligence using OpenAI.
    """

    load_dotenv()

    if not sales_notes:
        raise ValueError(
            "Sales notes are required for AI extraction."
        )

    client = OpenAI(
        api_key=os.environ["OPENAI_API_KEY"]
    )

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-4.1-mini",
    )

    numbered_notes = "\n".join(
        f"Note {index}: {note}"
        for index, note in enumerate(sales_notes, start=1)
    )

    response = client.responses.parse(
        model=model,
        instructions=SYSTEM_PROMPT,
        input=numbered_notes,
        text_format=SalesIntelligenceExtraction,
    )

    result = response.output_parsed

    if result is None:
        raise RuntimeError(
            "The model did not return a parsed extraction."
        )

    return result


def validate_extraction_evidence(
    extraction: SalesIntelligenceExtraction,
    sales_notes: list[str],
) -> SalesIntelligenceExtraction:
    """
    Reject extracted facts whose evidence does not
    appear verbatim in the original sales notes.
    """

    source_text = "\n".join(sales_notes)

    validated_facts = []

    for fact in extraction.extracted_facts:

        if not fact.evidence:
            continue

        if fact.evidence not in source_text:
            continue

        validated_facts.append(fact)

    return extraction.model_copy(
        update={
            "extracted_facts": validated_facts
        }
    )