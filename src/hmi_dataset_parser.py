"""Parse the Matousek IEC-104 HMI dataset into ground-truth-labeled formal bounds.

Unlike the eon-iec sample used by ``formal_bound_builder``, this dataset carries
real ground-truth class labels (normal HMI traffic, masquerading attack, replay
attack) derived from the file name each row was captured in. Bounds produced by
this module drop the ``proxy_until_official_automaton_schema`` suffix in
favour of a ``ground_truth_class`` field, and their ``schema_status`` is set to
``ground_truth_hmi_dataset``.

The three source CSVs live under
``datasets/Datasets 001/matousek/iec104-hmi/`` and use semicolon separators
plus a mixed hex/decimal encoding for the ASDU-related fields.
"""

from __future__ import annotations

import csv
import json
import random
from pathlib import Path
from typing import Any

from src.pipeline_config import (
    OUTPUT_DIR,
    PROJECT_ROOT,
    RANDOM_SEED,
    ensure_project_directories,
)


HMI_ROOT = PROJECT_ROOT / "datasets" / "Datasets 001" / "matousek" / "iec104-hmi"

HMI_SOURCES: dict[str, Path] = {
    "normal_hmi_traffic": HMI_ROOT / "report_block_HMI.csv",
    "masquerading_attack": HMI_ROOT / "masquerating_HMI.csv",
    "replay_attack": HMI_ROOT / "replay_HMI.csv",
}

HMI_BOUNDS_JSONL = OUTPUT_DIR / "formal_bounds_hmi.jsonl"
HMI_BOUNDS_SUMMARY = OUTPUT_DIR / "formal_bounds_hmi_summary.json"

HMI_SCHEMA_STATUS = "ground_truth_hmi_dataset"
HMI_BOUND_VERSION = "3.0-hmi"


def _parse_int(value: str) -> int:
    """Convert HMI cell value (decimal or hex like ``0x00000003``) into an integer.

    Empty cells and values that cannot be parsed become 0 so the resulting bound
    remains well-typed. This mirrors the ``safe_int`` helper in
    ``formal_bound_builder`` and keeps the two schemas comparable.
    """

    if value is None:
        return 0

    stripped = value.strip()

    if not stripped:
        return 0

    try:
        if stripped.lower().startswith("0x"):
            return int(stripped, 16)
        return int(stripped)
    except ValueError:
        return 0


def _ip_to_id(ip: str) -> int:
    """Map dotted-quad IPv4 into a small integer id (last octet).

    The HMI dataset uses real IPs (192.168.1.100, 192.168.1.101). Reducing to
    the last octet is sufficient for downstream V1-V5 checks and matches the
    integer-id convention used by the eon-iec sample.
    """

    if not ip:
        return 0

    try:
        return int(ip.strip().split(".")[-1])
    except (ValueError, IndexError):
        return 0


def _read_hmi_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []

    with open(path, encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file, delimiter=";")
        return list(reader)


def _frame_type_from_fmt(fmt_int: int) -> str:
    if fmt_int == 0:
        return "i_format_information_transfer"

    if fmt_int == 1:
        return "s_or_u_format_control"

    if fmt_int == 2:
        return "u_format_control"

    return "unknown_frame_format"


def _direction(src_port: int, dst_port: int) -> str:
    if src_port == 2404 and dst_port != 2404:
        return "server_to_client"

    if dst_port == 2404 and src_port != 2404:
        return "client_to_server"

    return "unknown"


def row_to_hmi_bound(
    row: dict[str, str],
    ground_truth_class: str,
    event_index: int,
) -> dict[str, Any]:
    src_id = _ip_to_id(row.get("srcIP", ""))
    dst_id = _ip_to_id(row.get("dstIP", ""))
    src_port = _parse_int(row.get("srcPort", ""))
    dst_port = _parse_int(row.get("dstPort", ""))
    ip_len = _parse_int(row.get("ipLen", ""))
    pkt_len = _parse_int(row.get("len", ""))
    fmt_int = _parse_int(row.get("fmt", ""))
    asdu_type = _parse_int(row.get("asduType", ""))
    numix = _parse_int(row.get("numix", ""))
    cot = _parse_int(row.get("cot", ""))
    addr = _parse_int(row.get("addr", ""))

    features = {
        "source_id": src_id,
        "destination_id": dst_id,
        "bytes": ip_len,
        "pkt_length": pkt_len,
        "srcport": src_port,
        "dstport": dst_port,
        "asdu_address": addr,
        "asdu_cot": cot,
        "asdu_items": numix,
        "asdu_type": asdu_type,
        "frame_fmt": fmt_int,
    }

    frame_type = _frame_type_from_fmt(fmt_int)
    direction = _direction(src_port, dst_port)

    allowed_facts = {
        "protocol_hint": "iec104",
        "communication_direction": direction,
        "frame_type": frame_type,
        **features,
    }

    return {
        "event_id": f"hmi_{event_index:06d}",
        "dataset": "matousek_iec104_hmi",
        "event_granularity": "atomic_row",
        "timestamp_string": row.get("TimeStamp", ""),
        "relative_time_seconds": row.get("Relative Time", ""),
        "formal_bound_version": HMI_BOUND_VERSION,
        "schema_status": HMI_SCHEMA_STATUS,
        "ground_truth_class": ground_truth_class,
        "protocol_hint": "iec104",
        "communication_direction": direction,
        "frame_type": frame_type,
        "features": features,
        "allowed_facts": allowed_facts,
        "allowed_claims": [
            f"The observed communication direction is {direction}.",
            f"The observed frame type is {frame_type}.",
            f"Source identifier {src_id} communicated with destination identifier {dst_id}.",
            f"The observed source port is {src_port} and the observed destination port is {dst_port}.",
            f"The observed packet size is {ip_len} bytes and the packet length field is {pkt_len}.",
            f"The observed ASDU address is {addr}.",
            f"The observed ASDU type is {asdu_type}, COT is {cot}, and ASDU item count is {numix}.",
            f"The ground-truth event class is {ground_truth_class}.",
        ],
        "required_claims": [
            "The explanation must mention the observed source and destination identifiers.",
            "The explanation must mention the observed source and destination ports.",
            "The explanation must remain consistent with the observed IEC-104 protocol hint when present.",
            "The explanation must remain consistent with the observed ASDU fields.",
            f"The explanation must reflect the ground-truth event class ({ground_truth_class}).",
        ],
        "forbidden_claims": [
            "Do not claim an attack class that contradicts the ground-truth class.",
            "Do not invent additional devices, network segments, operators, substations, or assets.",
            "Do not invent causal explanations beyond the observed ground-truth class.",
            "Do not invent timing patterns beyond the single observed timestamp.",
            "Do not invent mitigation requirements such as isolation, shutdown, blocking, or emergency response.",
        ],
        "machine_constraints": {
            "must_match": {
                "source_id": src_id,
                "destination_id": dst_id,
                "srcport": src_port,
                "dstport": dst_port,
                "asdu_type": asdu_type,
                "asdu_cot": cot,
                "asdu_items": numix,
                "frame_fmt": fmt_int,
                "protocol_hint": "iec104",
                "communication_direction": direction,
            },
            "ground_truth_class": ground_truth_class,
            "attack_claim_allowed": ground_truth_class in {"masquerading_attack", "replay_attack"},
            "malicious_claim_allowed": ground_truth_class in {"masquerading_attack", "replay_attack"},
            "mitigation_claim_allowed": False,
            "causal_claim_allowed": False,
            "normality_claim_allowed": ground_truth_class == "normal_hmi_traffic",
            "scope_expansion_allowed": False,
        },
        "thesis_note": (
            "This formal bound is generated from an atomic IEC-104 HMI row from the "
            "Matousek dataset. The ground-truth class is derived from the source "
            "file (report_block, masquerating, or replay HMI capture)."
        ),
    }


def build_balanced_sample(
    per_class: int,
    seed: int = RANDOM_SEED,
) -> list[dict[str, Any]]:
    """Return a balanced sample of ``per_class`` bounds for each HMI class."""

    rng = random.Random(seed)
    bounds: list[dict[str, Any]] = []
    global_index = 1

    for ground_truth_class, source_path in HMI_SOURCES.items():
        rows = _read_hmi_csv(source_path)

        if not rows:
            print(f"Warning: no rows found in {source_path}")
            continue

        take = min(per_class, len(rows))
        sampled = rng.sample(rows, k=take)

        for row in sampled:
            bounds.append(
                row_to_hmi_bound(
                    row,
                    ground_truth_class=ground_truth_class,
                    event_index=global_index,
                )
            )
            global_index += 1

    return bounds


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_summary(bounds: list[dict[str, Any]]) -> dict[str, Any]:
    class_counts: dict[str, int] = {}
    direction_counts: dict[str, int] = {}

    for bound in bounds:
        class_counts[bound["ground_truth_class"]] = (
            class_counts.get(bound["ground_truth_class"], 0) + 1
        )
        direction_counts[bound["communication_direction"]] = (
            direction_counts.get(bound["communication_direction"], 0) + 1
        )

    return {
        "dataset": "matousek_iec104_hmi",
        "schema_status": HMI_SCHEMA_STATUS,
        "formal_bound_version": HMI_BOUND_VERSION,
        "total_bounds": len(bounds),
        "ground_truth_class_counts": class_counts,
        "communication_direction_counts": direction_counts,
    }


def main() -> None:
    ensure_project_directories()

    bounds = build_balanced_sample(per_class=100)

    if not bounds:
        raise RuntimeError(
            f"No HMI bounds were built. Check that the source CSVs exist under "
            f"{HMI_ROOT}"
        )

    write_jsonl(bounds, HMI_BOUNDS_JSONL)

    summary = build_summary(bounds)

    with open(HMI_BOUNDS_SUMMARY, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2, ensure_ascii=False)

    print("HMI ground-truth formal bounds generated successfully.")
    print(f"Total bounds: {len(bounds)}")
    print("Per-class:")

    for class_name, count in summary["ground_truth_class_counts"].items():
        print(f"  {class_name}: {count}")

    print("")
    print(f"JSONL: {HMI_BOUNDS_JSONL}")
    print(f"Summary: {HMI_BOUNDS_SUMMARY}")


if __name__ == "__main__":
    main()
