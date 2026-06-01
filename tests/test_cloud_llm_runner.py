"""Tests for the cloud LLM runner that do not require a live API key."""

from __future__ import annotations

from src.cloud_llm_runner import (
    build_combined_prompt,
    build_response_record,
    resolve_pilot_limit,
)


def _sample_prompt() -> dict:
    return {
        "event_id": "evt_000001",
        "system_prompt": "You are an ICS analyst.",
        "user_prompt": "Explain event evt_000001.",
        "metadata": {"protocol_hint": "iec104"},
    }


def test_build_combined_prompt_concatenates_both_parts():
    combined = build_combined_prompt(_sample_prompt())

    assert "You are an ICS analyst." in combined
    assert "Explain event evt_000001." in combined
    assert "Remember: do not use outside knowledge." in combined


def test_build_response_record_has_expected_keys():
    result = {"ok": True, "response": "OK", "elapsed_seconds": 1.5}
    record = build_response_record(_sample_prompt(), "gpt-4o-mini", "openai", result)

    assert record["response_id"] == "evt_000001_cloud_openai_gpt-4o-mini"
    assert record["original_event_id"] == "evt_000001"
    assert record["model_backend"] == "cloud_openai"
    assert record["response_type"] == "real_llm_output"
    assert record["generation_ok"] is True
    assert record["metadata"]["protocol_hint"] == "iec104"


def test_build_response_record_carries_error_when_call_fails():
    result = {"ok": False, "response": "", "elapsed_seconds": 0.4, "error": "timeout"}
    record = build_response_record(_sample_prompt(), "gemini-1.5-flash", "gemini", result)

    assert record["generation_ok"] is False
    assert record["error"] == "timeout"


def test_resolve_pilot_limit_honours_environment(monkeypatch):
    monkeypatch.setenv("REASONGUARD_CLOUD_PILOT_LIMIT", "5")
    assert resolve_pilot_limit() == 5


def test_resolve_pilot_limit_defaults_when_env_unset(monkeypatch):
    monkeypatch.delenv("REASONGUARD_CLOUD_PILOT_LIMIT", raising=False)
    from src.cloud_llm_runner import CLOUD_PILOT_LIMIT_DEFAULT

    assert resolve_pilot_limit() == CLOUD_PILOT_LIMIT_DEFAULT
