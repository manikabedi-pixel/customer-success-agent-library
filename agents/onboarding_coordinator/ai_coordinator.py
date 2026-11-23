import json
import os
from typing import Any

from openai import OpenAI


SYSTEM_PROMPT = """
You are an AI assistant supporting a Customer Success Manager.

Your task is to suggest safe coordination actions for onboarding issues.

Rules:
1. Use only the supplied issue information.
2. Do not invent customer facts, owners, deadlines, or approvals.
3. Do not claim that any action has been completed.
4. Do not assign tasks or change onboarding status.
5. Every recommendation must require human review.
6. Every recommendation must reference a supplied task ID.
7. Return JSON only.

Return this structure:

{
  "recommendations": [
    {
      "task_id": "TASK-001",
      "issue_type": "missing_owner",
      "recommended_action": "Confirm the responsible owner with the CSM.",
      "rationale": "The task has no confirmed owner.",
      "requires_human_review": true
    }
  ]
}
"""


def generate_coordination_recommendations(
    issues: list[dict[str, Any]],
    model: str = "gpt-4.1-mini",
    client: Any = None,
) -> dict[str, Any]:
    """
    Generate AI-assisted coordination suggestions.

    This function does not modify onboarding state.
    """

    if not issues:
        return {"recommendations": []}

    if client is None:
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not configured.")

        client = OpenAI()

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
                "content": json.dumps(
                    {"issues": issues},
                    ensure_ascii=False,
                ),
            },
        ],
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("AI returned an empty response.")

    result = json.loads(content)

    if not isinstance(result, dict):
        raise ValueError("AI response must be a JSON object.")

    return result