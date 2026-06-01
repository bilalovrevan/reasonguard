"""Merge per-model Ollama response JSONL files into a single combined JSONL.

Long pilot runs occasionally crash mid-batch (transient network errors). The
runner writes each model's per-model JSONL only after all calls for that model
complete, so partial runs leave a mix of fully-written per-model files plus an
out-of-date combined file. This script regenerates the combined file from the
per-model files currently on disk, preserving the entire history without
re-running inference.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from src.pipeline_config import (
    OLLAMA_RESPONSES_JSON,
    OLLAMA_RESPONSES_JSONL,
    OLLAMA_RESPONSES_PREVIEW,
    OUTPUT_DIR,
    ensure_project_directories,
)

PER_MODEL_PATTERN = re.compile(r"ollama_responses_(?P<slug>.+?)\.jsonl$")
EXCLUDED_PATTERNS = ("SAVED", "preview", "v1")


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []

    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def discover_per_model_files() -> list[Path]:
    candidates = []

    for path in OUTPUT_DIR.glob("ollama_responses_*.jsonl"):
        name = path.name

        if any(pattern in name for pattern in EXCLUDED_PATTERNS):
            continue

        if not PER_MODEL_PATTERN.search(name):
            continue

        candidates.append(path)

    return sorted(candidates)


def write_preview(records: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "=== OLLAMA LLM RESPONSE PREVIEW (merged) ===",
        f"Total responses: {len(records)}",
        "",
    ]

    for record in records[:5]:
        lines.append(f"Response ID: {record['response_id']}")
        lines.append(f"Model: {record.get('model_name')}")
        lines.append(f"OK: {record.get('generation_ok')}")
        lines.append(f"Elapsed: {record.get('elapsed_seconds')}")
        lines.append("Response:")
        lines.append(record.get("response", ""))
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_project_directories()

    per_model_files = discover_per_model_files()

    if not per_model_files:
        print("No per-model Ollama JSONL files found under outputs/.")
        return

    merged: list[dict[str, Any]] = []
    summary: dict[str, int] = {}

    for path in per_model_files:
        records = load_jsonl(path)
        merged.extend(records)

        model = records[0].get("model_name", path.name) if records else path.name
        summary[model] = summary.get(model, 0) + len(records)

    write_jsonl(merged, OLLAMA_RESPONSES_JSONL)

    with open(OLLAMA_RESPONSES_JSON, "w", encoding="utf-8") as file:
        json.dump(merged, file, indent=2, ensure_ascii=False)

    write_preview(merged, OLLAMA_RESPONSES_PREVIEW)

    print("Merged Ollama responses written successfully.")
    print(f"Per-model files merged: {len(per_model_files)}")
    print(f"Total records: {len(merged)}")
    print("Per-model totals:")

    for model, count in sorted(summary.items()):
        print(f"  {model}: {count}")

    print(f"\nCombined JSONL: {OLLAMA_RESPONSES_JSONL}")
    print(f"Combined JSON:  {OLLAMA_RESPONSES_JSON}")
    print(f"Preview:        {OLLAMA_RESPONSES_PREVIEW}")


if __name__ == "__main__":
    main()
