"""Tests for the per-model JSONL merger."""

from __future__ import annotations

from src.merge_ollama_responses import (
    discover_per_model_files,
    load_jsonl,
    write_jsonl,
)


def test_load_and_write_jsonl_roundtrip(tmp_path):
    records = [{"response_id": "evt_1", "model_name": "phi3:mini"}]
    path = tmp_path / "sample.jsonl"

    write_jsonl(records, path)
    loaded = load_jsonl(path)

    assert loaded == records


def test_load_jsonl_skips_blank_lines(tmp_path):
    path = tmp_path / "sample.jsonl"
    path.write_text(
        '{"a": 1}\n\n{"b": 2}\n   \n',
        encoding="utf-8",
    )

    loaded = load_jsonl(path)

    assert loaded == [{"a": 1}, {"b": 2}]


def test_discover_per_model_files_filters_excluded(tmp_path, monkeypatch):
    monkeypatch.setattr("src.merge_ollama_responses.OUTPUT_DIR", tmp_path)

    (tmp_path / "ollama_responses_phi3_mini.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "ollama_responses_phi3_mini_preview.txt").write_text("preview\n", encoding="utf-8")
    (tmp_path / "ollama_responses_phi3_mini.SAVED.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "ollama_responses_llama3_1_8b.jsonl").write_text("{}\n", encoding="utf-8")
    (tmp_path / "synthetic_llm_responses_v1.jsonl").write_text("{}\n", encoding="utf-8")

    discovered = discover_per_model_files()
    discovered_names = {path.name for path in discovered}

    assert "ollama_responses_phi3_mini.jsonl" in discovered_names
    assert "ollama_responses_llama3_1_8b.jsonl" in discovered_names
    assert "ollama_responses_phi3_mini.SAVED.jsonl" not in discovered_names
    assert all("preview" not in name for name in discovered_names)
    assert all("synthetic" not in name for name in discovered_names)
