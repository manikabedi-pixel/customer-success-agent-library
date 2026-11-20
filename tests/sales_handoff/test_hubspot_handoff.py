import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

HANDOFF_PATH = (
    PROJECT_ROOT
    / "outputs"
    / "sales_handoff"
    / "hubspot_handoff_373031837427.json"
)


def test_handoff_missing_information_detection():
    with HANDOFF_PATH.open(encoding="utf-8") as file:
        draft = json.load(file)

    missing_information = list(
        draft["missing_information"]
    )

    for fact in draft["sales_intelligence"]:
        evidence = fact["evidence"]

        if "dashboard scope remains undefined" in evidence.lower():
            gap = "Executive dashboard scope is undefined"

            if gap not in missing_information:
                missing_information.append(gap)

    assert "Technical implementation owner not yet identified" in (
        missing_information
    )

    assert "Executive dashboard scope is undefined" in (
        missing_information
    )

    assert draft["requires_human_review"] is True

    assert draft["status"] == "draft"