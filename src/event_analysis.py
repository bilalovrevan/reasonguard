"""Per-(model x event-type) breakdown of ReasonGuard verdicts.

The exposé requires a model-comparison and a condition-comparison analysis in
weeks 16-17. This module is the building block for both: it joins the
ReasonGuard report with the prompt-level proxy event type and produces a
breakdown that can be loaded into the thesis as a table or into matplotlib
as a heat map.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.pipeline_config import (
    LLM_PROMPTS_JSONL,
    OUTPUT_DIR,
    REASONGUARD_REPORT_JSONL,
    ensure_project_directories,
)


EVENT_TYPE_REPORT_JSON = OUTPUT_DIR / "event_type_analysis.json"
EVENT_TYPE_REPORT_CSV = OUTPUT_DIR / "event_type_analysis.csv"
EVENT_TYPE_REPORT_MD = OUTPUT_DIR / "event_type_analysis.md"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def build_event_type_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}

    if not LLM_PROMPTS_JSONL.exists():
        return lookup

    for record in load_jsonl(LLM_PROMPTS_JSONL):
        event_id = record["event_id"]
        proxy_event_type = record["formal_bound"].get("proxy_event_type", "unknown")
        lookup[event_id] = proxy_event_type

    return lookup


def compute_event_type_breakdown(
    report_records: list[dict[str, Any]],
    event_type_lookup: dict[str, str],
) -> list[dict[str, Any]]:
    """Produce a list of ``{model, event_type, ...counts}`` rows.

    Only responses whose event_id has a known event type are counted. Synthetic
    responses are included alongside real LLM responses so the same breakdown can
    be inspected for both populations.
    """

    bucket: dict[tuple[str, str], dict[str, int]] = {}

    for record in report_records:
        event_id = record.get("event_id") or ""
        model_name = record.get("model_name") or "unknown"
        event_type = event_type_lookup.get(event_id, "unknown")

        key = (model_name, event_type)
        counts = bucket.setdefault(
            key,
            {"total": 0, "clean": 0, "V1": 0, "V2": 0, "V3": 0, "V4": 0, "V5": 0},
        )

        counts["total"] += 1

        if not record.get("violation_codes"):
            counts["clean"] += 1

        for code in record.get("violation_codes", []):
            if code in counts:
                counts[code] += 1

    rows = []

    for (model_name, event_type), counts in sorted(bucket.items()):
        rate_clean = counts["clean"] / counts["total"] if counts["total"] else 0.0
        rates = {
            f"{code}_rate": counts[code] / counts["total"] if counts["total"] else 0.0
            for code in ("V1", "V2", "V3", "V4", "V5")
        }

        rows.append(
            {
                "model": model_name,
                "event_type": event_type,
                "total": counts["total"],
                "clean": counts["clean"],
                "clean_rate": round(rate_clean, 4),
                **{code: counts[code] for code in ("V1", "V2", "V3", "V4", "V5")},
                **{key: round(value, 4) for key, value in rates.items()},
            }
        )

    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())

    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Per-Event-Type Violation Breakdown",
        "",
        "Counts and rates of ReasonGuard verdicts grouped by model and proxy event type.",
        "",
        "| Model | Event type | Total | Clean | Clean rate | V1 | V2 | V3 | V4 | V5 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in rows:
        lines.append(
            f"| {row['model']} | {row['event_type']} | {row['total']} | {row['clean']} | "
            f"{row['clean_rate']:.2%} | {row['V1']} | {row['V2']} | {row['V3']} | "
            f"{row['V4']} | {row['V5']} |"
        )

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ensure_project_directories()

    if not REASONGUARD_REPORT_JSONL.exists():
        raise FileNotFoundError(
            f"ReasonGuard report not found: {REASONGUARD_REPORT_JSONL}\n"
            "Run: python -m src.reason_guard_checker"
        )

    report_records = load_jsonl(REASONGUARD_REPORT_JSONL)
    event_type_lookup = build_event_type_lookup()

    if not event_type_lookup:
        print(
            "No prompt-level event type information found. Run:\n"
            "  REASONGUARD_STRATIFY=1 python -m src.prompt_builder\n"
            "to populate proxy_event_type on the prompts."
        )

    rows = compute_event_type_breakdown(report_records, event_type_lookup)

    EVENT_TYPE_REPORT_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    write_csv(rows, EVENT_TYPE_REPORT_CSV)
    EVENT_TYPE_REPORT_MD.write_text(render_markdown(rows), encoding="utf-8")

    print("Per-event-type analysis completed successfully.")
    print(f"Rows: {len(rows)}")
    print(f"JSON: {EVENT_TYPE_REPORT_JSON}")
    print(f"CSV: {EVENT_TYPE_REPORT_CSV}")
    print(f"Markdown: {EVENT_TYPE_REPORT_MD}")


if __name__ == "__main__":
    main()
