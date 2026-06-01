"""Manual annotation pipeline for the V1-V5 ground-truth set.

The exposé requires manually annotated explanation pairs (M4 milestone, week
14). This module:

1. Samples ``sample_size`` responses from the union of synthetic and Ollama
   outputs (seeded by :data:`src.pipeline_config.RANDOM_SEED`).
2. Writes the seed batch as a spreadsheet-friendly CSV with the machine
   verdict next to empty human-label columns.
3. Computes raw inter-rater agreement once the annotator returns the
   completed file.

The richer per-class precision, recall, F1, and Cohen's Kappa numbers are
produced by :mod:`src.evaluation_metrics`.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

from src.pipeline_config import (
    ANNOTATION_INPUT_CSV,
    ANNOTATION_RESULTS_CSV,
    OLLAMA_RESPONSES_JSONL,
    RANDOM_SEED,
    REASONGUARD_REPORT_JSONL,
    SYNTHETIC_RESPONSES_JSONL,
    ensure_project_directories,
)

VIOLATION_LABELS = ["NONE", "V1", "V2", "V3", "V4", "V5", "MIXED"]
SEVERITY_LABELS = ["none", "low", "medium", "high"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []

    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records


def collect_response_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    if SYNTHETIC_RESPONSES_JSONL.exists():
        records.extend(load_jsonl(SYNTHETIC_RESPONSES_JSONL))

    if OLLAMA_RESPONSES_JSONL.exists():
        records.extend(load_jsonl(OLLAMA_RESPONSES_JSONL))

    return records


def collect_machine_verdicts() -> dict[str, dict[str, Any]]:
    if not REASONGUARD_REPORT_JSONL.exists():
        return {}

    verdicts: dict[str, dict[str, Any]] = {}

    for entry in load_jsonl(REASONGUARD_REPORT_JSONL):
        verdicts[entry["response_id"]] = {
            "machine_violations": "|".join(entry.get("violation_codes", [])) or "NONE",
            "machine_severity": entry.get("severity", "none"),
        }

    return verdicts


def build_annotation_batch(sample_size: int = 50) -> list[dict[str, Any]]:
    response_records = collect_response_records()

    if not response_records:
        raise RuntimeError(
            "No response records were found. Run the synthetic and Ollama runners first."
        )

    machine_verdicts = collect_machine_verdicts()

    random.seed(RANDOM_SEED)
    sample_size = min(sample_size, len(response_records))
    sampled = random.sample(response_records, k=sample_size)

    batch = []

    for record in sampled:
        response_id = record["response_id"]
        verdict = machine_verdicts.get(response_id, {})

        batch.append(
            {
                "response_id": response_id,
                "event_id": record.get("original_event_id", ""),
                "model_name": record.get("model_name", ""),
                "response_type": record.get("response_type", ""),
                "machine_violations": verdict.get("machine_violations", ""),
                "machine_severity": verdict.get("machine_severity", ""),
                "human_label": "",
                "human_severity": "",
                "annotator_initials": "",
                "annotator_notes": "",
                "response_text": record.get("response", ""),
            }
        )

    return batch


def write_annotation_csv(batch: list[dict[str, Any]], path: Path) -> None:
    fieldnames = [
        "response_id",
        "event_id",
        "model_name",
        "response_type",
        "machine_violations",
        "machine_severity",
        "human_label",
        "human_severity",
        "annotator_initials",
        "annotator_notes",
        "response_text",
    ]

    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(batch)


def compute_inter_rater_metrics(results_path: Path) -> dict[str, Any]:
    if not results_path.exists():
        return {"status": "no_results", "path": str(results_path)}

    total = 0
    machine_codes: list[str] = []
    human_codes: list[str] = []
    matches = 0

    with open(results_path, encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            human_label = (row.get("human_label") or "").strip().upper()

            if not human_label or human_label not in VIOLATION_LABELS:
                continue

            machine_label = (row.get("machine_violations") or "NONE").strip().upper()

            if machine_label != "NONE" and "|" in machine_label:
                machine_label = "MIXED"

            machine_codes.append(machine_label)
            human_codes.append(human_label)

            if machine_label == human_label:
                matches += 1

            total += 1

    accuracy = matches / total if total else 0.0

    return {
        "status": "ok",
        "annotated_rows": total,
        "raw_agreement": accuracy,
        "machine_label_distribution": _label_counts(machine_codes),
        "human_label_distribution": _label_counts(human_codes),
    }


def _label_counts(labels: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}

    for label in labels:
        counts[label] = counts.get(label, 0) + 1

    return counts


def main() -> None:
    ensure_project_directories()

    batch = build_annotation_batch(sample_size=50)
    write_annotation_csv(batch, ANNOTATION_INPUT_CSV)

    print("Manual annotation batch generated successfully.")
    print(f"Rows: {len(batch)}")
    print(f"CSV: {ANNOTATION_INPUT_CSV}")
    print("")
    print("Annotation instructions:")
    print("  1. Open the CSV in your spreadsheet editor.")
    print("  2. For each row, fill in the human_label column with one of:")
    print(f"     {', '.join(VIOLATION_LABELS)}")
    print(f"  3. Fill in human_severity with one of: {', '.join(SEVERITY_LABELS)}.")
    print("  4. Initial the annotator_initials column and add notes if useful.")
    print(f"  5. Save the completed file as: {ANNOTATION_RESULTS_CSV.name}")
    print(
        "  6. Re-run with --report to compute inter-rater agreement against ReasonGuard."
    )


if __name__ == "__main__":
    import sys

    if "--report" in sys.argv:
        metrics = compute_inter_rater_metrics(ANNOTATION_RESULTS_CSV)
        print(json.dumps(metrics, indent=2))
    else:
        main()
