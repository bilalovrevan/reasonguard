from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_bound() -> dict:
    return {
        "event_id": "evt_000001",
        "dataset": "eon_iec",
        "event_granularity": "atomic_row",
        "timestamp_ms": 1_654_646_400_041,
        "formal_bound_version": "2.1",
        "schema_status": "proxy_until_official_automaton_schema",
        "protocol_hint": "iec104",
        "communication_direction": "client_to_server",
        "frame_type": "s_or_u_format_control",
        "observation_pattern": "iec104_control_frame_pattern",
        "formal_class": "IEC104_CONTROL_FRAME_OBSERVATION",
        "formal_class_status": "proxy_not_ground_truth_attack_label",
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
        "machine_constraints": {
            "must_match": {
                "source_id": 1,
                "destination_id": 2,
                "srcport": 57528,
                "dstport": 2404,
                "asdu_type": 0,
                "asdu_cot": 0,
                "asdu_items": 0,
                "frame_fmt": 1,
                "protocol_hint": "iec104",
                "communication_direction": "client_to_server",
            },
            "attack_claim_allowed": False,
            "malicious_claim_allowed": False,
            "mitigation_claim_allowed": False,
            "causal_claim_allowed": False,
            "normality_claim_allowed": False,
            "scope_expansion_allowed": False,
        },
    }


@pytest.fixture
def clean_response_text() -> str:
    return (
        "The formal bound describes an iec104 observation from source identifier 1 to "
        "destination identifier 2. The observed source port is 57528 and the destination "
        "port is 2404, with communication direction classified as client_to_server. "
        "The ASDU fields are type 0, COT 0, item count 0, and address 0. The current "
        "formal class is a proxy observation label, so the bound does not confirm "
        "a security conclusion."
    )


@pytest.fixture
def v1_fabricated_response_text() -> str:
    return (
        "This event shows a confirmed replay attack against destination 2. The attacker "
        "is using malicious IEC-104 traffic to manipulate the control process. The "
        "affected substation should be isolated immediately to prevent further compromise."
    )


@pytest.fixture
def v2_contradicted_response_text() -> str:
    return (
        "The event is best understood as server_to_client communication from source "
        "identifier 1 to destination identifier 2. The ASDU type is 0 and the port "
        "information should be interpreted accordingly."
    )


@pytest.fixture
def v3_overgeneralised_response_text() -> str:
    return (
        "This appears to be routine IEC-104 traffic with standard communication "
        "behavior. The observation looks typical for an industrial control system "
        "exchange. No specific concern is visible from this event."
    )


@pytest.fixture
def v4_underspecified_response_text() -> str:
    return (
        "The event is an IEC-104 observation. It may be useful for understanding "
        "communication behavior. The bound does not provide enough information for a "
        "stronger conclusion."
    )


@pytest.fixture
def v5_incoherent_response_text() -> str:
    return (
        "The event is normal traffic and also a malicious attack at the same time. "
        "It is isolated to source 1 and destination 2, but it also affects the entire "
        "network segment. The communication is both client-to-server and "
        "server-to-client."
    )
