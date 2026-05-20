from __future__ import annotations

from typing import Any


PROXY_LABEL_SUFFIX = "_proxy_until_official_schema"


def classify_event_type(bound: dict[str, Any]) -> str:
    """Return the proxy event type for one formal bound.

    The thesis exposé identifies five canonical event types: normal Modbus polling,
    function code violation, network scan, replay attack, and topology change. Until
    the official NES@FIT automaton output schema is integrated, the type is derived
    from observable proxy features. Each returned label carries the proxy suffix to
    make the provenance explicit in downstream artefacts.
    """

    protocol = bound.get("protocol_hint", "unknown")
    pattern = bound.get("observation_pattern", "")
    features = bound.get("features", {})
    asdu_type = int(features.get("asdu_type", 0))
    asdu_cot = int(features.get("asdu_cot", 0))
    bytes_observed = int(features.get("bytes", 0))

    if protocol == "iec104" and pattern == "dominant_iec104_measurement_pattern":
        return f"normal_modbus_polling{PROXY_LABEL_SUFFIX}"

    if protocol == "iec104" and pattern == "iec104_information_transfer_pattern":
        if asdu_cot in (6, 7):
            return f"function_code_violation{PROXY_LABEL_SUFFIX}"

        if asdu_cot in (44, 45, 46, 47):
            return f"function_code_violation{PROXY_LABEL_SUFFIX}"

        return f"normal_modbus_polling{PROXY_LABEL_SUFFIX}"

    if protocol == "iec104" and pattern == "iec104_control_frame_pattern":
        if bytes_observed < 40:
            return f"network_scan{PROXY_LABEL_SUFFIX}"

        return f"topology_change{PROXY_LABEL_SUFFIX}"

    if protocol == "iec104" and pattern == "iec104_non_dominant_pattern":
        if asdu_type in (100, 101, 102, 103, 104, 105):
            return f"function_code_violation{PROXY_LABEL_SUFFIX}"

        return f"replay_attack{PROXY_LABEL_SUFFIX}"

    return f"network_scan{PROXY_LABEL_SUFFIX}"


def annotate_bounds_with_event_type(bounds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    annotated = []

    for bound in bounds:
        event_type = classify_event_type(bound)
        bound_copy = dict(bound)
        bound_copy["proxy_event_type"] = event_type
        annotated.append(bound_copy)

    return annotated


def count_event_types(bounds: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}

    for bound in bounds:
        event_type = bound.get("proxy_event_type") or classify_event_type(bound)
        counts[event_type] = counts.get(event_type, 0) + 1

    return counts
