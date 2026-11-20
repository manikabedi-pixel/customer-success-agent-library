Execution Modes

The Sales-to-CS Handoff Agent supports two execution modes.

Mock mode (default)
python -m agents.sales_handoff.ai_main

Uses a predefined synthetic extraction fixture. No OpenAI API credentials or API calls are required.

Live mode
python -m agents.sales_handoff.ai_main --mode live

Uses the OpenAI API to extract structured information from sales notes.

Live mode requires an API key and may incur usage charges.

All outputs remain drafts requiring human review.

Mock responses are for development and demonstration purposes. They must not be represented as actual model-generated results.