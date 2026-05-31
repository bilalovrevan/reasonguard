from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt

from src.pipeline_config import (
    OUTPUT_DIR,
    REASONGUARD_REPORT_JSONL,
    ensure_project_directories,
)


FIGURES_DIR = OUTPUT_DIR / "figures"

VIOLATION_CODES = ["V1", "V2", "V3", "V4", "V5"]
VIOLATION_LABELS = {
    "V1": "V1 fabricated",
    "V2": "V2 contradicted",
    "V3": "V3 over-general.",
    "V4": "V4 under-spec.",
    "V5": "V5 incoherent",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records


def per_model_violation_counts(records: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    counts: dict[str, dict[str, int]] = {}

    for record in records:
        model_name = record.get("model_name") or "unknown"
        bucket = counts.setdefault(
            model_name,
            {"total": 0, "clean": 0, "V1": 0, "V2": 0, "V3": 0, "V4": 0, "V5": 0},
        )

        bucket["total"] += 1

        if not record.get("violation_codes"):
            bucket["clean"] += 1

        for code in record.get("violation_codes", []):
            if code in bucket:
                bucket[code] += 1

    return counts


def plot_per_model_violation_bars(
    counts: dict[str, dict[str, int]],
    output_path: Path,
) -> None:
    model_names = sorted(counts)
    n_models = len(model_names)
    n_codes = len(VIOLATION_CODES)

    figure, axes = plt.subplots(figsize=(8.5, 4.5))
    bar_width = 0.8 / n_codes
    x_positions = list(range(n_models))

    for index, code in enumerate(VIOLATION_CODES):
        rates = [
            (counts[name][code] / counts[name]["total"]) * 100 if counts[name]["total"] else 0
            for name in model_names
        ]
        offsets = [position + (index - n_codes / 2 + 0.5) * bar_width for position in x_positions]
        axes.bar(offsets, rates, width=bar_width, label=VIOLATION_LABELS[code])

    axes.set_xticks(x_positions)
    axes.set_xticklabels(model_names, rotation=15, ha="right")
    axes.set_ylabel("Violation rate (%)")
    axes.set_ylim(0, 100)
    axes.set_title("ReasonGuard V1-V5 violation rate per model")
    axes.legend(loc="upper right", fontsize="small")
    axes.grid(axis="y", linestyle=":", alpha=0.4)
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def plot_clean_rate_bar(
    counts: dict[str, dict[str, int]],
    output_path: Path,
) -> None:
    model_names = sorted(counts)
    clean_rates = [
        (counts[name]["clean"] / counts[name]["total"]) * 100 if counts[name]["total"] else 0
        for name in model_names
    ]

    figure, axes = plt.subplots(figsize=(7.5, 4))
    bars = axes.bar(model_names, clean_rates, color="#3a86ff")

    for bar, rate in zip(bars, clean_rates):
        axes.text(
            bar.get_x() + bar.get_width() / 2,
            rate + 1.5,
            f"{rate:.1f}%",
            ha="center",
            fontsize=9,
        )

    axes.set_ylabel("Clean response rate (%)")
    axes.set_ylim(0, 100)
    axes.set_title("Clean response rate per model (no V1-V5 fired)")
    axes.grid(axis="y", linestyle=":", alpha=0.4)
    plt.setp(axes.get_xticklabels(), rotation=15, ha="right")
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def main() -> None:
    ensure_project_directories()
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)

    if not REASONGUARD_REPORT_JSONL.exists():
        raise FileNotFoundError(
            f"ReasonGuard report not found: {REASONGUARD_REPORT_JSONL}\n"
            "Run: python -m src.reason_guard_checker"
        )

    records = load_jsonl(REASONGUARD_REPORT_JSONL)
    counts = per_model_violation_counts(records)

    if not counts:
        raise RuntimeError("No per-model counts could be computed from the report.")

    per_model_path = FIGURES_DIR / "violation_rate_per_model.png"
    clean_rate_path = FIGURES_DIR / "clean_rate_per_model.png"

    plot_per_model_violation_bars(counts, per_model_path)
    plot_clean_rate_bar(counts, clean_rate_path)

    print("Visualisations written successfully.")
    print(f"Per-model violation rates: {per_model_path}")
    print(f"Clean rate per model: {clean_rate_path}")
    print("")
    print("Per-model raw counts:")

    for name in sorted(counts):
        row = counts[name]
        print(
            f"  {name:35s} total={row['total']:4d} clean={row['clean']:4d} "
            f"V1={row['V1']:3d} V2={row['V2']:3d} V3={row['V3']:3d} V4={row['V4']:3d} V5={row['V5']:3d}"
        )


if __name__ == "__main__":
    main()
