"""Tests for the Matousek IEC-104 HMI dataset parser."""

from __future__ import annotations

from src.hmi_dataset_parser import (
    _direction,
    _frame_type_from_fmt,
    _ip_to_id,
    _parse_int,
    row_to_hmi_bound,
)


def test_parse_int_handles_hex_and_decimal_and_empty():
    assert _parse_int("0x00000003") == 3
    assert _parse_int("42") == 42
    assert _parse_int("") == 0
    assert _parse_int(None) == 0
    assert _parse_int("not a number") == 0


def test_ip_to_id_takes_last_octet():
    assert _ip_to_id("192.168.1.100") == 100
    assert _ip_to_id("10.0.0.5") == 5
    assert _ip_to_id("") == 0


def test_direction_uses_iec104_port_convention():
    assert _direction(35344, 2404) == "client_to_server"
    assert _direction(2404, 35344) == "server_to_client"
    assert _direction(80, 443) == "unknown"


def test_frame_type_mapping():
    assert _frame_type_from_fmt(0) == "i_format_information_transfer"
    assert _frame_type_from_fmt(1) == "s_or_u_format_control"
    assert _frame_type_from_fmt(9) == "unknown_frame_format"


def test_row_to_hmi_bound_includes_ground_truth():
    row = {
        "TimeStamp": "14:00:44.61",
        "Relative Time": "0.077137916",
        "srcIP": "192.168.1.101",
        "dstIP": "192.168.1.100",
        "srcPort": "35344",
        "dstPort": "2404",
        "ipLen": "58",
        "len": "4",
        "fmt": "0x00000003",
        "uType": "0x00000001",
        "asduType": "",
        "numix": "",
        "cot": "",
        "oa": "",
        "addr": "",
    }

    bound = row_to_hmi_bound(row, ground_truth_class="masquerading_attack", event_index=1)

    assert bound["event_id"] == "hmi_000001"
    assert bound["ground_truth_class"] == "masquerading_attack"
    assert bound["schema_status"] == "ground_truth_hmi_dataset"
    assert bound["features"]["source_id"] == 101
    assert bound["features"]["destination_id"] == 100
    assert bound["features"]["srcport"] == 35344
    assert bound["features"]["dstport"] == 2404
    assert bound["communication_direction"] == "client_to_server"
    assert bound["machine_constraints"]["attack_claim_allowed"] is True
    assert bound["machine_constraints"]["normality_claim_allowed"] is False


def test_row_to_hmi_bound_normal_class_toggles_flags():
    row = {
        "TimeStamp": "13:20:51.36",
        "Relative Time": "2.473756145",
        "srcIP": "192.168.1.101",
        "dstIP": "192.168.1.100",
        "srcPort": "35342",
        "dstPort": "2404",
        "ipLen": "58",
        "len": "4",
        "fmt": "0",
        "uType": "0",
        "asduType": "0",
        "numix": "0",
        "cot": "0",
        "oa": "0",
        "addr": "0",
    }

    bound = row_to_hmi_bound(row, ground_truth_class="normal_hmi_traffic", event_index=42)

    assert bound["ground_truth_class"] == "normal_hmi_traffic"
    assert bound["machine_constraints"]["attack_claim_allowed"] is False
    assert bound["machine_constraints"]["normality_claim_allowed"] is True
