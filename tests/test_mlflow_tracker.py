"""Tests for the MLflow tracker wrapper.

These tests verify that the tracker can run without MLflow installed and
silently no-ops in that case; they also exercise the basic configure path.
"""

from __future__ import annotations

import pytest

from src.mlflow_tracker import (
    configure_tracking,
    log_artifact,
    log_metrics,
    log_params,
    start_run,
)


def test_start_run_returns_none_when_mlflow_absent(monkeypatch):
    monkeypatch.setattr("src.mlflow_tracker._import_mlflow", lambda: None)

    with start_run(experiment_name="test", run_name="test") as run:
        assert run is None


def test_log_helpers_silent_no_op_when_mlflow_absent(monkeypatch):
    monkeypatch.setattr("src.mlflow_tracker._import_mlflow", lambda: None)

    log_params({"x": 1})
    log_metrics({"y": 2.0})


def test_configure_tracking_returns_false_when_mlflow_absent(monkeypatch):
    monkeypatch.setattr("src.mlflow_tracker._import_mlflow", lambda: None)
    assert configure_tracking() is False


def test_log_artifact_skips_missing_file(monkeypatch, tmp_path):
    monkeypatch.setattr("src.mlflow_tracker._import_mlflow", lambda: None)
    log_artifact(tmp_path / "does_not_exist.json")


@pytest.mark.skipif("not __import__('importlib').util.find_spec('mlflow')")
def test_configure_tracking_returns_true_when_mlflow_present():
    assert configure_tracking() is True
