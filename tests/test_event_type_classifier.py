from __future__ import annotations

from src.event_type_classifier import (
    PROXY_LABEL_SUFFIX,
    annotate_bounds_with_event_type,
    classify_event_type,
    count_event_types,
)


def _bound(pattern: str, asdu_cot: int = 0, bytes_value: int = 50, asdu_type: int = 0) -> dict:
    return {
        "protocol_hint": "iec104",
        "observation_pattern": pattern,
        "features": {
            "asdu_type": asdu_type,
            "asdu_cot": asdu_cot,
            "bytes": bytes_value,
        },
    }


def test_dominant_measurement_pattern_maps_to_normal_polling():
    label = classify_event_type(_bound("dominant_iec104_measurement_pattern"))
    assert label == f"normal_modbus_polling{PROXY_LABEL_SUFFIX}"


def test_information_transfer_with_management_cot_maps_to_function_code_violation():
    label = classify_event_type(_bound("iec104_information_transfer_pattern", asdu_cot=44))
    assert label == f"function_code_violation{PROXY_LABEL_SUFFIX}"


def test_control_frame_small_packet_maps_to_scan():
    label = classify_event_type(_bound("iec104_control_frame_pattern", bytes_value=20))
    assert label == f"network_scan{PROXY_LABEL_SUFFIX}"


def test_control_frame_normal_packet_maps_to_topology_change():
    label = classify_event_type(_bound("iec104_control_frame_pattern", bytes_value=100))
    assert label == f"topology_change{PROXY_LABEL_SUFFIX}"


def test_annotate_bounds_attaches_event_type_field():
    bounds = [
        _bound("dominant_iec104_measurement_pattern"),
        _bound("iec104_control_frame_pattern", bytes_value=20),
    ]
    annotated = annotate_bounds_with_event_type(bounds)

    assert all("proxy_event_type" in record for record in annotated)
    assert annotated[0]["proxy_event_type"].startswith("normal_modbus_polling")
    assert annotated[1]["proxy_event_type"].startswith("network_scan")


def test_count_event_types_aggregates_counts():
    bounds = [
        _bound("dominant_iec104_measurement_pattern"),
        _bound("dominant_iec104_measurement_pattern"),
        _bound("iec104_control_frame_pattern", bytes_value=20),
    ]
    counts = count_event_types(bounds)

    assert sum(counts.values()) == 3
