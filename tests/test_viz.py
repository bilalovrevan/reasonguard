"""Tests for the matplotlib figure helpers in src.viz.

The tests render figures to a tmp_path and assert that the files exist and
are larger than a small threshold; they do not assert pixel content.
"""

from __future__ import annotations

from src.viz import (
    per_model_violation_counts,
    plot_clean_rate_bar,
    plot_confusion_matrix,
    plot_per_model_violation_bars,
)


def test_per_model_violation_counts_aggregates_properly():
    records = [
        {"model_name": "phi3:mini", "violation_codes": ["V1"]},
        {"model_name": "phi3:mini", "violation_codes": []},
        {"model_name": "llama3.1:8b", "violation_codes": ["V1", "V4"]},
        {"model_name": "llama3.1:8b", "violation_codes": []},
        {"model_name": "llama3.1:8b", "violation_codes": []},
    ]

    counts = per_model_violation_counts(records)

    assert counts["phi3:mini"]["total"] == 2
    assert counts["phi3:mini"]["clean"] == 1
    assert counts["llama3.1:8b"]["total"] == 3
    assert counts["llama3.1:8b"]["clean"] == 2
    assert counts["llama3.1:8b"]["V1"] == 1
    assert counts["llama3.1:8b"]["V4"] == 1


def test_plot_per_model_violation_bars_writes_file(tmp_path):
    counts = {
        "phi3:mini": {"total": 10, "clean": 3, "V1": 6, "V2": 0, "V3": 0, "V4": 4, "V5": 0},
        "llama3.1:8b": {"total": 10, "clean": 7, "V1": 2, "V2": 0, "V3": 0, "V4": 1, "V5": 0},
    }
    output_path = tmp_path / "rates.png"
    plot_per_model_violation_bars(counts, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 1024


def test_plot_clean_rate_bar_writes_file(tmp_path):
    counts = {
        "phi3:mini": {"total": 10, "clean": 3, "V1": 6, "V2": 0, "V3": 0, "V4": 4, "V5": 0},
        "llama3.1:8b": {"total": 10, "clean": 7, "V1": 2, "V2": 0, "V3": 0, "V4": 1, "V5": 0},
    }
    output_path = tmp_path / "clean.png"
    plot_clean_rate_bar(counts, output_path)

    assert output_path.exists()


def test_plot_confusion_matrix_writes_file(tmp_path):
    matrix = {
        "NONE": {"NONE": 5, "V1": 1, "V4": 0},
        "V1": {"NONE": 0, "V1": 4, "V4": 1},
        "V4": {"NONE": 0, "V1": 0, "V4": 3},
    }
    output_path = tmp_path / "confusion.png"
    plot_confusion_matrix(matrix, output_path)

    assert output_path.exists()
    assert output_path.stat().st_size > 1024
