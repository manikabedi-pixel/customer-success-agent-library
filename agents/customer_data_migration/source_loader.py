import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SourceLoadResult:
    deal_id: str

    sources: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )

    missing_sources: list[str] = field(
        default_factory=list
    )

    warnings: list[str] = field(
        default_factory=list
    )

    requires_human_review: bool = True


def load_json_file(path: Path) -> dict[str, Any]:
    """
    Load a JSON object from disk.

    Invalid JSON and non-object JSON are rejected.
    """

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, dict):
        raise ValueError(
            f"Expected JSON object in {path}"
        )

    return data


def extract_deal_id(data: dict[str, Any]) -> str | None:
    """
    Extract a deal identifier from known upstream schemas.

    Supported:
    - Agent #1: deal.deal_id
    - Agent #2: deal_id
    - Agent #3: deal_id
    - Metadata-based identifiers
    """

    candidates = [
        data.get("deal_id"),
        data.get("hubspot_deal_id"),
    ]

    deal = data.get("deal")

    if isinstance(deal, dict):
        candidates.extend([
            deal.get("deal_id"),
            deal.get("hubspot_deal_id"),
        ])

    metadata = data.get("metadata")

    if isinstance(metadata, dict):
        candidates.extend([
            metadata.get("deal_id"),
            metadata.get("hubspot_deal_id"),
        ])

    for candidate in candidates:
        if isinstance(candidate, (str, int)):
            value = str(candidate).strip()

            if value:
                return value

    return None


def load_agent_sources(
    deal_id: str,
    source_paths: dict[str, Path],
) -> SourceLoadResult:
    """
    Load upstream agent outputs for a single deal.

    Sources with mismatched deal IDs are rejected.

    Sources without a discoverable deal ID are retained
    with a warning, not treated as verified matches.
    """

    result = SourceLoadResult(deal_id=deal_id)

    for agent_name, path in source_paths.items():

        if not path.exists():
            result.missing_sources.append(agent_name)

            result.warnings.append(
                f"{agent_name}: source file missing: {path}"
            )

            continue

        try:
            data = load_json_file(path)

        except (OSError, ValueError) as exc:
            result.warnings.append(
                f"{agent_name}: could not load source: {exc}"
            )

            continue

        source_deal_id = extract_deal_id(data)

        if source_deal_id is None:
            result.warnings.append(
                f"{agent_name}: deal ID could not be verified; "
                "source excluded from trusted inputs"
            )
            continue

        elif source_deal_id != deal_id:
            result.warnings.append(
                f"{agent_name}: deal ID mismatch "
                f"(expected {deal_id}, found {source_deal_id})"
            )

            continue

        result.sources[agent_name] = data

    return result