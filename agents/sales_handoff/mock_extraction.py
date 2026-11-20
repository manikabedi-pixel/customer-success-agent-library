import json
from pathlib import Path

from agents.sales_handoff.ai_schemas import (
    SalesIntelligenceExtraction,
)


def load_mock_extraction(
    fixture_path: Path,
) -> SalesIntelligenceExtraction:
    """
    Load a predefined AI extraction fixture.

    This function makes no API calls.
    """

    if not fixture_path.is_file():
        raise FileNotFoundError(
            f"Mock extraction fixture not found: {fixture_path}"
        )

    with fixture_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        fixture_data = json.load(file)

    return SalesIntelligenceExtraction.model_validate(
        fixture_data
    )