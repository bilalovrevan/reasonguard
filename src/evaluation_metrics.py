"""Per-class precision, recall, F1, accuracy, and Cohen's Kappa.

This module compares the machine label produced by ReasonGuard with the
human label in :data:`src.pipeline_config.ANNOTATION_RESULTS_CSV` and
writes:

- a JSON report with per-class numbers and the confusion matrix,
- a markdown report rendering the same numbers as readable tables.

The M5 milestone in the exposé requires Cohen's $\\kappa$ between
ReasonGuard and a VUT Brno domain expert; that is computed by
:func:`compute_cohens_kappa` using the linear (categorical) definition.
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from src.pipeline_config import (
    ANNOTATION_RESULTS_CSV,
    OUTPUT_DIR,
    ensure_project_directories,
)


VIOLATION_CLASSES = ["NONE", "V1", "V2", "V3", "V4", "V5", "MIXED"]
PRIMARY_CLASSES = ["NONE", "V1", "V2", "V3", "V4", "V5"]

METRICS_REPORT_JSON = OUTPUT_DIR / "evaluation_metrics.json"
METRICS_REPORT_MD = OUTPUT_DIR / "evaluation_metrics.md"


@dataclass
class ClassMetrics:
    label: str
    true_positive: int = 0
    false_positive: int = 0
    false_negative: int = 0
    true_negative: int = 0

    @property
    def precision(self) -> float:
        denom = self.true_positive + self.false_positive
        return self.true_positive / denom if denom else 0.0

    @property
    def recall(self) -> float:
        denom = self.true_positive + self.false_negative
        return self.true_positive / denom if denom else 0.0

    @property
    def f1(self) -> float:
        denom = self.precision + self.recall
        return 2 * self.precision * self.recall / denom if denom else 0.0

    @property
    def support(self) -> int:
        return self.true_positive + self.false_negative

    def as_dict(self) -> dict[str, Any]:
        return {
            "label": self.label,
            "precision": round(self.precision, 4),
            "recall": round(self.recall, 4),
            "f1": round(self.f1, 4),
            "support": self.support,
            "true_positive": self.true_positive,
            "false_positive": self.false_positive,
            "false_negative": self.false_negative,
            "true_negative": self.true_negative,
        }


@dataclass
class EvaluationReport:
    per_class: list[ClassMetrics] = field(default_factory=list)
    macro_precision: float = 0.0
    macro_recall: float = 0.0
    macro_f1: float = 0.0
    accuracy: float = 0.0
    sample_count: int = 0
    cohens_kappa: float = 0.0
    confusion_matrix: dict[str, dict[str, int]] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {
            "sample_count": self.sample_count,
            "accuracy": round(self.accuracy, 4),
            "macro_precision": round(self.macro_precision, 4),
            "macro_recall": round(self.macro_recall, 4),
            "macro_f1": round(self.macro_f1, 4),
            "cohens_kappa": round(self.cohens_kappa, 4),
            "per_class": [metric.as_dict() for metric in self.per_class],
            "confusion_matrix": self.confusion_matrix,
        }


def _normalise_label(label: str) -> str:
    cleaned = (label or "").strip().upper()

    if not cleaned:
        return ""

    if "|" in cleaned:
        return "MIXED"

    if cleaned in VIOLATION_CLASSES:
        return cleaned

    return ""


def _machine_label_for_row(row: dict[str, str]) -> str:
    raw = (row.get("machine_violations") or "").strip().upper()

    if not raw or raw == "NONE":
        return "NONE"

    if "|" in raw:
        return "MIXED"

    if raw in VIOLATION_CLASSES:
        return raw

    return ""


def load_annotation_pairs(results_path: Path) -> list[tuple[str, str]]:
    """Return ``(machine_label, human_label)`` pairs for rows that have a human label."""

    pairs: list[tuple[str, str]] = []

    with open(results_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            human = _normalise_label(row.get("human_label") or "")

            if not human:
                continue

            machine = _machine_label_for_row(row)

            if not machine:
                continue

            pairs.append((machine, human))

    return pairs


def compute_confusion_matrix(
    pairs: list[tuple[str, str]],
    labels: list[str] | None = None,
) -> dict[str, dict[str, int]]:
    """Rows are the true (human) label; columns are the machine prediction."""

    label_set = labels or sorted({label for pair in pairs for label in pair})
    matrix = {true_label: {pred_label: 0 for pred_label in label_set} for true_label in label_set}

    for machine, human in pairs:
        if human not in matrix:
            matrix[human] = {pred_label: 0 for pred_label in label_set}

        if machine not in matrix[human]:
            matrix[human][machine] = 0

        matrix[human][machine] += 1

    return matrix


def compute_per_class_metrics(
    pairs: list[tuple[str, str]],
    labels: list[str],
) -> list[ClassMetrics]:
    metrics_by_label = {label: ClassMetrics(label=label) for label in labels}

    for machine, human in pairs:
        for label in labels:
            machine_is_label = machine == label
            human_is_label = human == label

            if machine_is_label and human_is_label:
                metrics_by_label[label].true_positive += 1
            elif machine_is_label and not human_is_label:
                metrics_by_label[label].false_positive += 1
            elif not machine_is_label and human_is_label:
                metrics_by_label[label].false_negative += 1
            else:
                metrics_by_label[label].true_negative += 1

    return [metrics_by_label[label] for label in labels]


def compute_cohens_kappa(pairs: list[tuple[str, str]]) -> float:
    """Cohen's Kappa with linear (categorical) agreement.

    Returns 0.0 when fewer than two classes are present or when the expected
    agreement equals the observed agreement (avoiding division by zero).
    """

    if not pairs:
        return 0.0

    labels = sorted({label for pair in pairs for label in pair})
    total = len(pairs)

    machine_distribution = {label: 0 for label in labels}
    human_distribution = {label: 0 for label in labels}
    agreements = 0

    for machine, human in pairs:
        machine_distribution[machine] += 1
        human_distribution[human] += 1

        if machine == human:
            agreements += 1

    observed_agreement = agreements / total
    expected_agreement = sum(
        (machine_distribution[label] * human_distribution[label]) / (total * total)
        for label in labels
    )

    if expected_agreement >= 1.0:
        return 0.0

    return (observed_agreement - expected_agreement) / (1.0 - expected_agreement)


def evaluate(pairs: list[tuple[str, str]], labels: list[str] | None = None) -> EvaluationReport:
    if not pairs:
        return EvaluationReport()

    active_labels = labels or PRIMARY_CLASSES
    per_class = compute_per_class_metrics(pairs, active_labels)

    macro_precision = sum(metric.precision for metric in per_class) / len(per_class)
    macro_recall = sum(metric.recall for metric in per_class) / len(per_class)
    macro_f1 = sum(metric.f1 for metric in per_class) / len(per_class)
    accuracy = sum(1 for machine, human in pairs if machine == human) / len(pairs)
    kappa = compute_cohens_kappa(pairs)
    matrix = compute_confusion_matrix(pairs, active_labels)

    return EvaluationReport(
        per_class=per_class,
        macro_precision=macro_precision,
        macro_recall=macro_recall,
        macro_f1=macro_f1,
        accuracy=accuracy,
        sample_count=len(pairs),
        cohens_kappa=kappa,
        confusion_matrix=matrix,
    )


def render_markdown(report: EvaluationReport) -> str:
    lines = [
        "# ReasonGuard Evaluation Metrics",
        "",
        f"- Sample count: {report.sample_count}",
        f"- Accuracy: {report.accuracy:.4f}",
        f"- Macro precision: {report.macro_precision:.4f}",
        f"- Macro recall: {report.macro_recall:.4f}",
        f"- Macro F1: {report.macro_f1:.4f}",
        f"- Cohen's Kappa: {report.cohens_kappa:.4f}",
        "",
        "## Per-class metrics",
        "",
        "| Class | Precision | Recall | F1 | Support | TP | FP | FN |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for metric in report.per_class:
        lines.append(
            f"| {metric.label} | {metric.precision:.4f} | {metric.recall:.4f} | "
            f"{metric.f1:.4f} | {metric.support} | {metric.true_positive} | "
            f"{metric.false_positive} | {metric.false_negative} |"
        )

    lines.append("")
    lines.append("## Confusion matrix (rows = human label, columns = machine label)")
    lines.append("")

    if report.confusion_matrix:
        labels = sorted(report.confusion_matrix.keys())
        header = ["true \\ predicted"] + labels
        lines.append("| " + " | ".join(header) + " |")
        lines.append("| " + " | ".join("---" for _ in header) + " |")

        for true_label in labels:
            row = [true_label] + [
                str(report.confusion_matrix[true_label].get(pred_label, 0))
                for pred_label in labels
            ]
            lines.append("| " + " | ".join(row) + " |")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    ensure_project_directories()

    if not ANNOTATION_RESULTS_CSV.exists():
        print(
            f"Annotation results not found at {ANNOTATION_RESULTS_CSV}.\n"
            "Fill annotation/annotation_batch.csv first and save the completed file "
            "under that name."
        )
        return

    pairs = load_annotation_pairs(ANNOTATION_RESULTS_CSV)

    if not pairs:
        print(
            "No annotated rows were found. Make sure the human_label column is "
            "filled in for at least some rows."
        )
        return

    report = evaluate(pairs)

    METRICS_REPORT_JSON.write_text(
        json.dumps(report.as_dict(), indent=2),
        encoding="utf-8",
    )
    METRICS_REPORT_MD.write_text(render_markdown(report), encoding="utf-8")

    print("Evaluation metrics computed successfully.")
    print(json.dumps(report.as_dict(), indent=2))
    print(f"JSON: {METRICS_REPORT_JSON}")
    print(f"Markdown: {METRICS_REPORT_MD}")


if __name__ == "__main__":
    main()
