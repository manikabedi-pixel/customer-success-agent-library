import json
from typing import Any

from openai import OpenAI


SYSTEM_PROMPT = """
You are an AI assistant supporting a Customer Success
Onboarding Planning Agent.

Your role is to suggest onboarding planning activities
based on unverified sales handoff information.

Rules:
1. Treat all input as unverified.
2. Do not invent customer commitments.
3. Do not invent implementation dates or task owners.
4. Do not claim that integrations or migrations are supported.
5. Do not represent suggested activities as approved.
6. Do not treat source evidence as independent verification.
7. Return valid JSON only.

For each input requirement, return one planning suggestion.

Required JSON structure:
{
  "suggestions": [
    {
      "requirement_id": "REQ-001",
      "suggested_activity": "Confirm integration requirements",
      "rationale": "The handoff mentions an integration need",
      "requires_human_review": true
    }
  ]
}
"""


def generate_ai_planning_suggestions(
    requirements: list[dict[str, Any]],
    client: Any = None,
    model: str = "gpt-4.1-mini",
) -> list[dict[str, Any]]:
    """
    Generate proposed onboarding activities.

    The returned suggestions are untrusted until validated.
    """

    if not isinstance(requirements, list):
        raise ValueError("requirements must be a list.")

    if not requirements:
        return []

    if client is None:
        client = OpenAI()

    safe_requirements = [
        {
            "requirement_id": item["requirement_id"],
            "category": item.get("category"),
            "description": item["description"],
        }
        for item in requirements
    ]

    response = client.chat.completions.create(
        model=model,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": json.dumps({
                    "requirements": safe_requirements
                }),
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned an empty response.")

    result = json.loads(content)

    if not isinstance(result, dict):
        raise ValueError("AI response must be an object.")

    suggestions = result.get("suggestions")

    if not isinstance(suggestions, list):
        raise ValueError(
            "AI response must contain a suggestions list."
        )

    return suggestions