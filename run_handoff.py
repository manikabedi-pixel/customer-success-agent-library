import argparse
import sys

from agents.sales_handoff.workflow import run_workflow


def main():
    parser = argparse.ArgumentParser(
        description="Sales-to-Customer-Success Handoff Agent"
    )

    parser.add_argument(
        "--deal-id",
        required=True,
        help="HubSpot deal ID",
    )

    parser.add_argument(
        "--mode",
        choices=["report", "live"],
        default="report",
        help="report: use saved JSON; live: retrieve CRM data and run AI",
    )

    args = parser.parse_args()

    try:
        run_workflow(
            deal_id=args.deal_id,
            mode=args.mode,
        )

    except (FileNotFoundError, ValueError) as error:
        print(f"\nERROR: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())