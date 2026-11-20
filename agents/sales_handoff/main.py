import json
from pathlib import Path

from agents.sales_handoff.schemas import Deal
from agents.sales_handoff.service import generate_handoff_brief


def main():

    project_root = Path(__file__).resolve().parents[2]

    input_path = (
        project_root
        / "sample_data"
        / "sales_handoff"
        / "deal_001.json"
    )

    output_path = (
        project_root
        / "sample_data"
        / "sales_handoff"
        / "handoff_001.json"
    )

    with open(input_path, "r", encoding="utf-8") as file:
        deal_data = json.load(file)

    deal = Deal.model_validate(deal_data)

    handoff_brief = generate_handoff_brief(deal)

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(handoff_brief, file, indent=2)

    print("Sales-to-CS Handoff Brief Generated")
    print(f"Output: {output_path}")

    print("\nMissing Information:")

    for item in handoff_brief["missing_information"]:
        print(f"- {item}")


if __name__ == "__main__":
    main()