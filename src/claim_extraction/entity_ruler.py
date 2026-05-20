from __future__ import annotations

from typing import Any


ICS_ENTITY_PATTERNS: list[dict[str, Any]] = [
    {"label": "PROTOCOL", "pattern": [{"LOWER": "iec104"}]},
    {"label": "PROTOCOL", "pattern": [{"LOWER": "iec"}, {"TEXT": "-"}, {"LOWER": "104"}]},
    {"label": "PROTOCOL", "pattern": [{"LOWER": "modbus"}]},
    {"label": "PROTOCOL", "pattern": [{"LOWER": "dnp3"}]},
    {"label": "PROTOCOL", "pattern": [{"LOWER": "s7"}]},
    {"label": "PROTOCOL", "pattern": [{"LOWER": "mqtt"}]},
    {"label": "DIRECTION", "pattern": [{"LOWER": "client"}, {"LOWER": "to"}, {"LOWER": "server"}]},
    {"label": "DIRECTION", "pattern": [{"LOWER": "server"}, {"LOWER": "to"}, {"LOWER": "client"}]},
    {"label": "DIRECTION", "pattern": [{"LOWER": "client_to_server"}]},
    {"label": "DIRECTION", "pattern": [{"LOWER": "server_to_client"}]},
    {"label": "FRAME_TYPE", "pattern": [{"LOWER": "i"}, {"TEXT": "-"}, {"LOWER": "format"}]},
    {"label": "FRAME_TYPE", "pattern": [{"LOWER": "s"}, {"TEXT": "-"}, {"LOWER": "format"}]},
    {"label": "FRAME_TYPE", "pattern": [{"LOWER": "u"}, {"TEXT": "-"}, {"LOWER": "format"}]},
    {"label": "ASDU_FIELD", "pattern": [{"LOWER": "asdu"}]},
    {"label": "ASDU_FIELD", "pattern": [{"LOWER": "cot"}]},
    {"label": "ASDU_FIELD", "pattern": [{"LOWER": "asdu_type"}]},
    {"label": "ASDU_FIELD", "pattern": [{"LOWER": "asdu_address"}]},
    {"label": "ASDU_FIELD", "pattern": [{"LOWER": "asdu_items"}]},
    {"label": "NETWORK_ENDPOINT", "pattern": [{"LOWER": "source"}, {"LOWER": "identifier"}]},
    {"label": "NETWORK_ENDPOINT", "pattern": [{"LOWER": "destination"}, {"LOWER": "identifier"}]},
    {"label": "NETWORK_ENDPOINT", "pattern": [{"LOWER": "source"}, {"LOWER": "port"}]},
    {"label": "NETWORK_ENDPOINT", "pattern": [{"LOWER": "destination"}, {"LOWER": "port"}]},
    {"label": "ATTACK_CATEGORY", "pattern": [{"LOWER": "replay"}, {"LOWER": "attack"}]},
    {"label": "ATTACK_CATEGORY", "pattern": [{"LOWER": "network"}, {"LOWER": "scan"}]},
    {"label": "ATTACK_CATEGORY", "pattern": [{"LOWER": "denial"}, {"LOWER": "of"}, {"LOWER": "service"}]},
    {"label": "ATTACK_CATEGORY", "pattern": [{"LOWER": "command"}, {"LOWER": "injection"}]},
    {"label": "ATTACK_CATEGORY", "pattern": [{"LOWER": "man"}, {"LOWER": "in"}, {"LOWER": "the"}, {"LOWER": "middle"}]},
    {"label": "ATTACK_CATEGORY", "pattern": [{"LOWER": "mitm"}]},
    {"label": "ATTACK_CATEGORY", "pattern": [{"LOWER": "flooding"}]},
    {"label": "ATTACK_CATEGORY", "pattern": [{"LOWER": "topology"}, {"LOWER": "change"}]},
    {"label": "MITIGATION", "pattern": [{"LOWER": "isolate"}]},
    {"label": "MITIGATION", "pattern": [{"LOWER": "isolated"}]},
    {"label": "MITIGATION", "pattern": [{"LOWER": "shutdown"}]},
    {"label": "MITIGATION", "pattern": [{"LOWER": "blocked"}]},
    {"label": "MITIGATION", "pattern": [{"LOWER": "quarantine"}]},
    {"label": "MITIGATION", "pattern": [{"LOWER": "emergency"}, {"LOWER": "response"}]},
    {"label": "NORMALITY", "pattern": [{"LOWER": "normal"}, {"LOWER": "traffic"}]},
    {"label": "NORMALITY", "pattern": [{"LOWER": "benign"}]},
    {"label": "NORMALITY", "pattern": [{"LOWER": "routine"}]},
    {"label": "NORMALITY", "pattern": [{"LOWER": "typical"}]},
    {"label": "UNCERTAINTY", "pattern": [{"LOWER": "proxy"}]},
    {"label": "UNCERTAINTY", "pattern": [{"LOWER": "does"}, {"LOWER": "not"}, {"LOWER": "confirm"}]},
    {"label": "UNCERTAINTY", "pattern": [{"LOWER": "not"}, {"LOWER": "confirmed"}]},
    {"label": "UNCERTAINTY", "pattern": [{"LOWER": "insufficient"}]},
]


def build_entity_ruler_patterns() -> list[dict[str, Any]]:
    """Return a copy of the ICS entity ruler patterns.

    A copy is returned so that downstream code can extend the list without mutating the
    module-level pattern definitions.
    """

    return [dict(pattern) for pattern in ICS_ENTITY_PATTERNS]
