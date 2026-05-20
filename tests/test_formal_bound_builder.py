from __future__ import annotations

import pandas as pd

from src.formal_bound_builder import (
    infer_direction,
    infer_frame_type,
    infer_observation_pattern,
    infer_protocol,
    infer_proxy_formal_class,
    row_to_formal_bound,
    safe_int,
)


def _row(**kwargs) -> pd.Series:
    defaults = {
        "srcip": 1,
        "dstip": 2,
        "time": 1_654_646_400_041,
        "bytes": 46,
        "dstport": 2404,
        "asdu_address": 0,
        "srcport": 57528,
        "asdu_cot": 0,
        "asdu_items": 0,
        "asdu_type": 0,
        "frame_fmt": 1,
        "pkt_length": 4,
    }
    defaults.update(kwargs)
    return pd.Series(defaults)


def test_safe_int_handles_missing_value():
    series = pd.Series([1, None])
    assert safe_int(series[1]) == 0
    assert safe_int(series[0]) == 1


def test_infer_protocol_recognises_iec104_port():
    assert infer_protocol(_row(dstport=2404)) == "iec104"
    assert infer_protocol(_row(srcport=2404, dstport=8080)) == "iec104"


def test_infer_direction_for_iec104():
    assert infer_direction(_row(srcport=57528, dstport=2404)) == "client_to_server"
    assert infer_direction(_row(srcport=2404, dstport=57528)) == "server_to_client"


def test_infer_frame_type_uses_frame_format_field():
    assert infer_frame_type(_row(frame_fmt=0)) == "i_format_information_transfer"
    assert infer_frame_type(_row(frame_fmt=1)) == "s_or_u_format_control"


def test_dominant_measurement_pattern_detected():
    row = _row(asdu_type=36, asdu_cot=3, asdu_items=1, frame_fmt=0, pkt_length=25)
    assert infer_observation_pattern(row) == "dominant_iec104_measurement_pattern"


def test_proxy_formal_class_for_baseline_measurement():
    row = _row(asdu_type=36, asdu_cot=3, asdu_items=1, frame_fmt=0, pkt_length=25)
    assert infer_proxy_formal_class(row) == "IEC104_BASELINE_MEASUREMENT_OBSERVATION"


def test_row_to_formal_bound_returns_complete_structure():
    bound = row_to_formal_bound(_row(), event_index=1)

    assert bound["event_id"] == "evt_000001"
    assert bound["schema_status"] == "proxy_until_official_automaton_schema"
    assert "allowed_claims" in bound and len(bound["allowed_claims"]) == 10
    assert "required_claims" in bound and len(bound["required_claims"]) == 5
    assert "forbidden_claims" in bound and len(bound["forbidden_claims"]) == 8
    assert bound["machine_constraints"]["attack_claim_allowed"] is False


def test_row_to_formal_bound_event_id_zero_padded():
    bound = row_to_formal_bound(_row(), event_index=42)
    assert bound["event_id"] == "evt_000042"
