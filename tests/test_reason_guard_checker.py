from __future__ import annotations

from src.reason_guard_checker import (
    check_response,
    classify_severity,
    detect_v1_fabricated_reasoning,
    detect_v2_contradicted_reasoning,
    detect_v3_over_generalised_reasoning,
    detect_v4_under_specified_reasoning,
    detect_v5_incoherent_reasoning,
    extract_claims,
)


def _build_response_record(text: str, response_type: str = "test") -> dict:
    return {
        "response_id": f"evt_000001_{response_type}",
        "original_event_id": "evt_000001",
        "response_type": response_type,
        "model_name": "test_fixture",
        "response": text,
    }


def _build_prompt_record(bound: dict) -> dict:
    return {
        "event_id": bound["event_id"],
        "formal_bound": bound,
    }


def test_clean_response_has_no_violation(sample_bound, clean_response_text):
    prompt_record = _build_prompt_record(sample_bound)
    response_record = _build_response_record(clean_response_text, "clean")

    result = check_response(prompt_record, response_record)

    assert result["violation_codes"] == []
    assert result["severity"] == "none"


def test_v1_fabricated_response_is_high_severity(sample_bound, v1_fabricated_response_text):
    prompt_record = _build_prompt_record(sample_bound)
    response_record = _build_response_record(v1_fabricated_response_text, "v1")

    result = check_response(prompt_record, response_record)

    assert "V1" in result["violation_codes"]
    assert result["severity"] == "high"
    assert any("attack" in reason.lower() or "malicious" in reason.lower()
               for reason in result["reasons"]["V1"])


def test_v2_contradicted_direction_detected(sample_bound, v2_contradicted_response_text):
    prompt_record = _build_prompt_record(sample_bound)
    response_record = _build_response_record(v2_contradicted_response_text, "v2")

    result = check_response(prompt_record, response_record)

    assert "V2" in result["violation_codes"]


def test_v3_over_generalised_when_normality_without_specifics(
    sample_bound,
    v3_overgeneralised_response_text,
):
    prompt_record = _build_prompt_record(sample_bound)
    response_record = _build_response_record(v3_overgeneralised_response_text, "v3")

    result = check_response(prompt_record, response_record)

    assert "V3" in result["violation_codes"]


def test_v4_under_specified_when_required_fields_missing(
    sample_bound,
    v4_underspecified_response_text,
):
    prompt_record = _build_prompt_record(sample_bound)
    response_record = _build_response_record(v4_underspecified_response_text, "v4")

    result = check_response(prompt_record, response_record)

    assert "V4" in result["violation_codes"]


def test_v5_incoherent_response_flagged(sample_bound, v5_incoherent_response_text):
    prompt_record = _build_prompt_record(sample_bound)
    response_record = _build_response_record(v5_incoherent_response_text, "v5")

    result = check_response(prompt_record, response_record)

    assert "V5" in result["violation_codes"]


def test_extract_claims_recognises_negated_security_conclusion():
    claims = extract_claims("The bound does not confirm maliciousness or normality.")

    assert claims["mentions_not_confirmed"] is True
    assert claims["attack_terms"] == []


def test_severity_high_takes_priority():
    assert classify_severity(["V1", "V4"]) == "high"
    assert classify_severity(["V2"]) == "high"
    assert classify_severity(["V5"]) == "high"


def test_severity_medium_for_v3_v4_combo():
    assert classify_severity(["V3", "V4"]) == "medium"


def test_severity_low_for_single_v3_or_v4():
    assert classify_severity(["V3"]) == "low"
    assert classify_severity(["V4"]) == "low"


def test_severity_none_when_no_violations():
    assert classify_severity([]) == "none"


def test_individual_detector_returns_reason(sample_bound, v1_fabricated_response_text):
    claims = extract_claims(v1_fabricated_response_text)
    violation, reasons = detect_v1_fabricated_reasoning(sample_bound, claims)

    assert violation is True
    assert reasons
