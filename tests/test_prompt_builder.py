from __future__ import annotations

from src.prompt_builder import bound_to_prompt_record, stratified_sample


def _bound(event_id: str, event_type: str) -> dict:
    return {
        "event_id": event_id,
        "dataset": "eon_iec",
        "event_granularity": "atomic_row",
        "timestamp_ms": 1,
        "formal_bound_version": "2.1",
        "schema_status": "proxy_until_official_automaton_schema",
        "protocol_hint": "iec104",
        "communication_direction": "client_to_server",
        "frame_type": "s_or_u_format_control",
        "observation_pattern": "iec104_control_frame_pattern",
        "formal_class": "IEC104_CONTROL_FRAME_OBSERVATION",
        "formal_class_status": "proxy_not_ground_truth_attack_label",
        "proxy_event_type": event_type,
        "features": {
            "source_id": 1,
            "destination_id": 2,
            "bytes": 46,
            "pkt_length": 4,
            "srcport": 57528,
            "dstport": 2404,
            "asdu_address": 0,
            "asdu_cot": 0,
            "asdu_items": 0,
            "asdu_type": 0,
            "frame_fmt": 1,
        },
        "allowed_facts": {},
        "allowed_claims": [],
        "required_claims": [],
        "forbidden_claims": [],
        "machine_constraints": {
            "attack_claim_allowed": False,
            "malicious_claim_allowed": False,
            "mitigation_claim_allowed": False,
            "causal_claim_allowed": False,
            "normality_claim_allowed": False,
            "scope_expansion_allowed": False,
        },
    }


def test_stratified_sample_returns_balanced_buckets():
    bounds = []

    for index in range(20):
        bounds.append(_bound(f"evt_a_{index}", "type_a"))

    for index in range(5):
        bounds.append(_bound(f"evt_b_{index}", "type_b"))

    selected = stratified_sample(bounds, per_event_type=3)

    type_a_count = sum(1 for bound in selected if bound["proxy_event_type"] == "type_a")
    type_b_count = sum(1 for bound in selected if bound["proxy_event_type"] == "type_b")

    assert type_a_count == 3
    assert type_b_count == 3
    assert len(selected) == 6


def test_stratified_sample_handles_small_buckets():
    bounds = [_bound("evt_a_0", "type_a"), _bound("evt_b_0", "type_b")]

    selected = stratified_sample(bounds, per_event_type=10)

    assert len(selected) == 2


def test_bound_to_prompt_record_includes_metadata():
    bound = _bound("evt_42", "type_a")
    record = bound_to_prompt_record(bound)

    assert record["event_id"] == "evt_42"
    assert record["formal_bound"] is bound
    assert record["metadata"]["dataset"] == "eon_iec"
