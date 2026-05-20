from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any, Iterator

from src.pipeline_config import (
    MLFLOW_ARTIFACT_DIR,
    MLFLOW_TRACKING_URI,
)


def _import_mlflow():
    try:
        import mlflow

        return mlflow
    except ImportError:
        return None


def configure_tracking() -> bool:
    """Point MLflow at the project-local SQLite store. Returns True if MLflow is usable."""

    mlflow = _import_mlflow()

    if mlflow is None:
        return False

    MLFLOW_ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    return True


@contextlib.contextmanager
def start_run(
    experiment_name: str,
    run_name: str | None = None,
    tags: dict[str, str] | None = None,
) -> Iterator[Any]:
    """Context manager that wraps ``mlflow.start_run`` and silently no-ops when MLflow
    is not installed. Downstream pipeline stages can therefore call into the tracker
    without conditional imports."""

    mlflow = _import_mlflow()

    if mlflow is None:
        yield None
        return

    if not configure_tracking():
        yield None
        return

    mlflow.set_experiment(experiment_name)

    with mlflow.start_run(run_name=run_name, tags=tags or {}) as active_run:
        yield active_run


def log_params(params: dict[str, Any]) -> None:
    mlflow = _import_mlflow()

    if mlflow is None or mlflow.active_run() is None:
        return

    mlflow.log_params({key: str(value) for key, value in params.items()})


def log_metrics(metrics: dict[str, float]) -> None:
    mlflow = _import_mlflow()

    if mlflow is None or mlflow.active_run() is None:
        return

    mlflow.log_metrics(metrics)


def log_artifact(artifact_path: Path) -> None:
    mlflow = _import_mlflow()

    if mlflow is None or mlflow.active_run() is None:
        return

    if artifact_path.exists():
        mlflow.log_artifact(str(artifact_path))
