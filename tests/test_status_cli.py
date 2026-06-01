"""Tests for the status CLI helpers."""

from __future__ import annotations

from src.status_cli import (
    _format_int,
    render_status_lines,
)


def test_format_int_handles_none():
    assert _format_int(None) == "—"


def test_format_int_renders_value():
    assert _format_int(42) == "42"


def test_render_status_lines_runs_without_data(monkeypatch, tmp_path):
    monkeypatch.setattr("src.status_cli.FORMAL_BOUNDS_JSONL", tmp_path / "nope.jsonl")
    monkeypatch.setattr("src.status_cli.LLM_PROMPTS_JSONL", tmp_path / "nope.jsonl")
    monkeypatch.setattr("src.status_cli.SYNTHETIC_RESPONSES_JSONL", tmp_path / "nope.jsonl")
    monkeypatch.setattr("src.status_cli.OLLAMA_RESPONSES_JSONL", tmp_path / "nope.jsonl")
    monkeypatch.setattr("src.status_cli.REASONGUARD_REPORT_JSONL", tmp_path / "nope.jsonl")
    monkeypatch.setattr("src.status_cli.REASONGUARD_REPORT_JSON", tmp_path / "nope.json")
    monkeypatch.setattr("src.status_cli.FORMAL_BOUNDS_SUMMARY", tmp_path / "nope.json")
    monkeypatch.setattr("src.status_cli.ANNOTATION_INPUT_CSV", tmp_path / "nope.csv")
    monkeypatch.setattr("src.status_cli.ANNOTATION_RESULTS_CSV", tmp_path / "nope.csv")

    lines = render_status_lines()

    assert any("ReasonGuard — current status" in line for line in lines)
    assert any("—" in line for line in lines)


def test_render_status_lines_with_real_data():
    lines = render_status_lines()
    text = "\n".join(lines)

    assert "Artefact counts" in text
    assert "V1-V5 summary" in text
