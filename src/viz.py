"""Matplotlib figures consumed by the meeting pack and the thesis Results chapter.

All figures are written to ``outputs/figures/`` and are deliberately
self-contained: the script reads only from the persisted ReasonGuard report
and the evaluation_metrics JSON so the figures can be regenerated at any
point in the project life cycle.
"""

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

try:
    import numpy as np
except ImportError:
    np = None  # type: ignore


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

    with open(path, encoding="utf-8") as file:
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


SYNTHETIC_MODEL_NAME = "synthetic_rule_based"
SYNTHETIC_TICK_LABEL = "regression fixtures\n(not a model)"


def plot_per_model_violation_bars(
    counts: dict[str, dict[str, int]],
    output_path: Path,
) -> None:
    real_names = sorted(name for name in counts if name != SYNTHETIC_MODEL_NAME)
    model_names = real_names + ([SYNTHETIC_MODEL_NAME] if SYNTHETIC_MODEL_NAME in counts else [])
    n_models = len(model_names)
    n_codes = len(VIOLATION_CODES)

    # Leave a visual gap between the five real models and the synthetic regression
    # fixtures so the fixtures are not read as a sixth model (see thesis Sec. 4.1).
    has_synthetic = SYNTHETIC_MODEL_NAME in counts
    x_positions = list(range(len(real_names)))
    if has_synthetic:
        x_positions.append(len(real_names) + 1)

    figure, axes = plt.subplots(figsize=(9, 4.5))
    bar_width = 0.8 / n_codes

    for index, code in enumerate(VIOLATION_CODES):
        rates = [
            (counts[name][code] / counts[name]["total"]) * 100 if counts[name]["total"] else 0
            for name in model_names
        ]
        offsets = [position + (index - n_codes / 2 + 0.5) * bar_width for position in x_positions]
        bars = axes.bar(
            offsets,
            rates,
            width=bar_width,
            label=VIOLATION_LABELS[code],
            color=f"C{index}",
        )
        if has_synthetic:
            # Hatch only the last (synthetic) bar of this violation code so it reads
            # as visually distinct from the five real-model bars.
            bars[-1].set_hatch("//")
            bars[-1].set_edgecolor("black")
            bars[-1].set_linewidth(0.6)

    if has_synthetic:
        axes.axvline(len(real_names) + 0.5, color="grey", linestyle="--", linewidth=0.8)

    tick_labels = list(real_names)
    if has_synthetic:
        tick_labels.append(SYNTHETIC_TICK_LABEL)

    axes.set_xticks(x_positions)
    axes.set_xticklabels(tick_labels, rotation=15, ha="right")
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
    real_names = sorted(name for name in counts if name != SYNTHETIC_MODEL_NAME)
    has_synthetic = SYNTHETIC_MODEL_NAME in counts
    model_names = real_names + ([SYNTHETIC_MODEL_NAME] if has_synthetic else [])
    clean_rates = [
        (counts[name]["clean"] / counts[name]["total"]) * 100 if counts[name]["total"] else 0
        for name in model_names
    ]

    # Leave a visual gap before the synthetic regression-fixture bar (see thesis Sec. 4.1)
    # so it is not read as a sixth model alongside the five real ones.
    x_positions = list(range(len(real_names)))
    if has_synthetic:
        x_positions.append(len(real_names) + 1)

    figure, axes = plt.subplots(figsize=(8, 4))
    colors = ["#3a86ff"] * len(real_names) + (["#3a86ff"] if has_synthetic else [])
    bars = axes.bar(x_positions, clean_rates, color=colors, width=0.6)

    if has_synthetic:
        bars[-1].set_hatch("//")
        bars[-1].set_edgecolor("black")
        bars[-1].set_linewidth(0.6)
        axes.axvline(len(real_names) + 0.5, color="grey", linestyle="--", linewidth=0.8)

    for bar, rate in zip(bars, clean_rates, strict=False):
        axes.text(
            bar.get_x() + bar.get_width() / 2,
            rate + 1.5,
            f"{rate:.1f}%",
            ha="center",
            fontsize=9,
        )

    tick_labels = list(real_names)
    if has_synthetic:
        tick_labels.append(SYNTHETIC_TICK_LABEL)

    axes.set_xticks(x_positions)
    axes.set_ylabel("Clean response rate (%)")
    axes.set_ylim(0, 100)
    axes.set_title("Clean response rate per model (no V1-V5 fired)")
    axes.grid(axis="y", linestyle=":", alpha=0.4)
    axes.set_xticklabels(tick_labels, rotation=15, ha="right")
    figure.tight_layout()
    figure.savefig(output_path, dpi=160)
    plt.close(figure)


def plot_confusion_matrix(
    matrix: dict[str, dict[str, int]],
    output_path: Path,
    title: str = "Confusion matrix (rows = human, columns = machine)",
) -> None:
    """Render the confusion matrix produced by ``evaluation_metrics``."""

    labels = sorted(matrix.keys())
    n_labels = len(labels)

    if n_labels == 0:
        return

    values = [[matrix[true_label].get(pred_label, 0) for pred_label in labels] for true_label in labels]

    figure, axes = plt.subplots(figsize=(6, 5))
    image = axes.imshow(values, cmap="Blues", aspect="auto")

    axes.set_xticks(range(n_labels))
    axes.set_yticks(range(n_labels))
    axes.set_xticklabels(labels, rotation=30, ha="right")
    axes.set_yticklabels(labels)
    axes.set_xlabel("Machine label (predicted)")
    axes.set_ylabel("Human label (true)")
    axes.set_title(title)

    for i in range(n_labels):
        for j in range(n_labels):
            value = values[i][j]
            cell_text_color = "white" if value > max(max(row) for row in values) / 2 else "black"
            axes.text(j, i, str(value), ha="center", va="center", color=cell_text_color, fontsize=10)

    figure.colorbar(image, ax=axes, fraction=0.046, pad=0.04)
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

    confusion_matrix_path = FIGURES_DIR / "confusion_matrix.png"
    metrics_json_path = OUTPUT_DIR / "evaluation_metrics.json"

    if metrics_json_path.exists():
        with open(metrics_json_path, encoding="utf-8") as file:
            metrics = json.load(file)

        matrix = metrics.get("confusion_matrix")

        if matrix:
            plot_confusion_matrix(matrix, confusion_matrix_path)

    print("Visualisations written successfully.")
    print(f"Per-model violation rates: {per_model_path}")
    print(f"Clean rate per model: {clean_rate_path}")

    if confusion_matrix_path.exists():
        print(f"Confusion matrix: {confusion_matrix_path}")

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
