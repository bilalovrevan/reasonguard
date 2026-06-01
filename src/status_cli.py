"""Quick command-line snapshot of the ReasonGuard project state.

Run with ``python -m src.status_cli`` before a meeting or before recording a
weekly report. The output is a one-screen summary of artefact counts,
violation totals, and the per-model breakdown so the student does not need
to read three separate JSON files to find the headline numbers.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.pipeline_config import (
    ANNOTATION_INPUT_CSV,
    ANNOTATION_RESULTS_CSV,
    FORMAL_BOUNDS_JSONL,
    FORMAL_BOUNDS_SUMMARY,
    LLM_PROMPTS_JSONL,
    OLLAMA_RESPONSES_JSONL,
    REASONGUARD_REPORT_JSON,
    REASONGUARD_REPORT_JSONL,
    SYNTHETIC_RESPONSES_JSONL,
)


def _count_lines(path: Path) -> int | None:
    if not path.exists():
        return None

    return sum(1 for line in open(path, encoding="utf-8") if line.strip())


def _load_json(path: Path) -> dict | None:
    if not path.exists():
        return None

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def _format_int(value: int | None) -> str:
    return str(value) if value is not None else "—"


def render_status_lines() -> list[str]:
    lines: list[str] = []
    lines.append("ReasonGuard — current status")
    lines.append("=" * 50)

    lines.append("")
    lines.append("Artefact counts")
    lines.append("-" * 50)
    lines.append(f"  Formal bounds         : {_format_int(_count_lines(FORMAL_BOUNDS_JSONL))}")
    lines.append(f"  LLM prompts           : {_format_int(_count_lines(LLM_PROMPTS_JSONL))}")
    lines.append(f"  Synthetic responses   : {_format_int(_count_lines(SYNTHETIC_RESPONSES_JSONL))}")
    lines.append(f"  Real LLM responses    : {_format_int(_count_lines(OLLAMA_RESPONSES_JSONL))}")
    lines.append(f"  Verdicts (combined)   : {_format_int(_count_lines(REASONGUARD_REPORT_JSONL))}")

    bounds_summary = _load_json(FORMAL_BOUNDS_SUMMARY)

    if bounds_summary and "proxy_event_type_counts" in bounds_summary:
        lines.append("")
        lines.append("Proxy event-type distribution")
        lines.append("-" * 50)

        for event_type, count in sorted(
            bounds_summary["proxy_event_type_counts"].items(),
            key=lambda pair: -pair[1],
        ):
            short = event_type.replace("_proxy_until_official_schema", "")
            lines.append(f"  {short:30s}: {count}")

    report = _load_json(REASONGUARD_REPORT_JSON)

    if report and "summary" in report:
        summary = report["summary"]
        lines.append("")
        lines.append("V1-V5 summary")
        lines.append("-" * 50)

        for label, key in (
            ("Total responses", "total_responses"),
            ("No violation", "no_violation"),
            ("V1 fabricated", "V1_fabricated_reasoning"),
            ("V2 contradicted", "V2_contradicted_reasoning"),
            ("V3 over-generalised", "V3_over_generalised_reasoning"),
            ("V4 under-specified", "V4_under_specified_reasoning"),
            ("V5 incoherent", "V5_incoherent_reasoning"),
        ):
            lines.append(f"  {label:22s}: {summary.get(key, '—')}")

    if REASONGUARD_REPORT_JSONL.exists():
        lines.append("")
        lines.append("Per-model breakdown")
        lines.append("-" * 50)

        per_model = _per_model_counts()

        for model, counts in sorted(per_model.items()):
            total = counts["total"]
            clean = counts["clean"]
            clean_rate = (clean / total) * 100 if total else 0

            lines.append(
                f"  {model:35s}  total={total:4d}  clean={clean:4d} ({clean_rate:5.1f}%) "
                f"V1={counts['V1']:3d} V2={counts['V2']:3d} V3={counts['V3']:3d} "
                f"V4={counts['V4']:3d} V5={counts['V5']:3d}"
            )

    lines.append("")
    lines.append("Annotation status")
    lines.append("-" * 50)
    seed_count = _count_lines(ANNOTATION_INPUT_CSV)
    seed_count = (seed_count or 1) - 1 if seed_count else None
    results_count = _count_lines(ANNOTATION_RESULTS_CSV)
    results_count = (results_count or 1) - 1 if results_count else None
    lines.append(f"  Seed batch ready      : {_format_int(seed_count)} rows")
    lines.append(f"  Completed labels      : {_format_int(results_count)} rows")

    lines.append("")
    return lines


def _per_model_counts() -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}

    with open(REASONGUARD_REPORT_JSONL, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            record = json.loads(line)
            model = record.get("model_name") or "unknown"
            bucket = counts.setdefault(
                model,
                {"total": 0, "clean": 0, "V1": 0, "V2": 0, "V3": 0, "V4": 0, "V5": 0},
            )
            bucket["total"] += 1

            if not record.get("violation_codes"):
                bucket["clean"] += 1

            for code in record.get("violation_codes", []):
                if code in bucket:
                    bucket[code] += 1

    return counts


def main() -> None:
    for line in render_status_lines():
        print(line)


if __name__ == "__main__":
    main()
