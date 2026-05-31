from __future__ import annotations

from src.evaluation_metrics import (
    compute_cohens_kappa,
    compute_confusion_matrix,
    compute_per_class_metrics,
    evaluate,
)


def test_perfect_agreement_gives_kappa_one():
    pairs = [("V1", "V1"), ("V2", "V2"), ("NONE", "NONE")]
    assert compute_cohens_kappa(pairs) == 1.0


def test_no_agreement_gives_low_kappa():
    pairs = [("V1", "V2"), ("V2", "V1"), ("NONE", "V1")]
    assert compute_cohens_kappa(pairs) < 0.5


def test_empty_pairs_returns_zero_kappa():
    assert compute_cohens_kappa([]) == 0.0


def test_per_class_metrics_basic_accounting():
    # (machine_label, human_label)
    pairs = [
        ("V1", "V1"),     # TP for V1
        ("V1", "V2"),     # FP for V1, FN for V2
        ("V2", "V2"),     # TP for V2
        ("NONE", "NONE"), # TP for NONE
        ("V1", "NONE"),   # FP for V1, FN for NONE
    ]

    metrics = compute_per_class_metrics(pairs, ["NONE", "V1", "V2"])
    metrics_by_label = {metric.label: metric for metric in metrics}

    v1 = metrics_by_label["V1"]
    assert v1.true_positive == 1
    assert v1.false_positive == 2
    assert v1.false_negative == 0

    v2 = metrics_by_label["V2"]
    assert v2.true_positive == 1
    assert v2.false_positive == 0
    assert v2.false_negative == 1

    none_metric = metrics_by_label["NONE"]
    assert none_metric.true_positive == 1
    assert none_metric.false_negative == 1


def test_confusion_matrix_includes_all_labels():
    pairs = [("V1", "V1"), ("V1", "V2"), ("V2", "V1")]
    matrix = compute_confusion_matrix(pairs, ["V1", "V2"])

    assert matrix["V1"]["V1"] == 1
    assert matrix["V2"]["V1"] == 1
    assert matrix["V1"]["V2"] == 1


def test_evaluate_returns_zero_when_empty():
    report = evaluate([])
    assert report.sample_count == 0
    assert report.accuracy == 0.0


def test_evaluate_on_simple_set():
    pairs = [
        ("V1", "V1"),
        ("V1", "V1"),
        ("NONE", "NONE"),
        ("V2", "V2"),
        ("V1", "NONE"),
    ]

    report = evaluate(pairs)

    assert report.sample_count == 5
    assert report.accuracy == 0.8
    assert 0.5 <= report.cohens_kappa <= 1.0
