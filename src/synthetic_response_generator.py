from __future__ import annotations

import json
import random
from typing import Any

from src.pipeline_config import (
    LLM_PROMPTS_JSONL,
    RANDOM_SEED,
    SYNTHETIC_RESPONSES_JSON,
    SYNTHETIC_RESPONSES_JSONL,
    SYNTHETIC_RESPONSES_PER_PROMPT,
    SYNTHETIC_RESPONSES_PREVIEW,
    ensure_project_directories,
)


def load_jsonl(path) -> list[dict[str, Any]]:
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))

    return records


def write_jsonl(records: list[dict[str, Any]], path) -> None:
    with open(path, "w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def build_clean_supported_response(bound: dict[str, Any]) -> str:
    f = bound["features"]

    return (
        f"The formal bound describes an {bound['protocol_hint']} observation from source identifier "
        f"{f['source_id']} to destination identifier {f['destination_id']}. "
        f"The observed source port is {f['srcport']} and the destination port is {f['dstport']}, "
        f"with communication direction classified as {bound['communication_direction']}. "
        f"The ASDU fields are type {f['asdu_type']}, COT {f['asdu_cot']}, item count {f['asdu_items']}, "
        f"and address {f['asdu_address']}. "
        f"The current formal class is a proxy observation label, so the bound does not confirm maliciousness or normality."
    )


def build_v1_fabricated_response(bound: dict[str, Any]) -> str:
    f = bound["features"]

    return (
        f"This event shows a confirmed replay attack against destination {f['destination_id']}. "
        f"The attacker is using malicious IEC-104 traffic to manipulate the control process. "
        f"The affected substation should be isolated immediately to prevent further compromise."
    )


def build_v2_contradicted_response(bound: dict[str, Any]) -> str:
    f = bound["features"]

    expected_direction = bound["communication_direction"]
    wrong_direction = (
        "server_to_client"
        if expected_direction == "client_to_server"
        else "client_to_server"
    )

    return (
        f"The event is best understood as {wrong_direction} communication from source identifier "
        f"{f['source_id']} to destination identifier {f['destination_id']}. "
        f"This direction should be used even though it differs from the formal observation. "
        f"The ASDU type is {f['asdu_type']} and the port information should be interpreted accordingly."
    )


def build_v3_over_generalised_response(bound: dict[str, Any]) -> str:
    return (
        "This appears to be routine IEC-104 traffic with standard communication behavior. "
        "The observation looks typical for an industrial control system exchange. "
        "No specific concern is visible from this event."
    )


def build_v4_under_specified_response(bound: dict[str, Any]) -> str:
    return (
        "The event is an IEC-104 observation with some ASDU-related information. "
        "It may be useful for understanding communication behavior. "
        "The bound does not provide enough information for a stronger conclusion."
    )


def build_v5_incoherent_response(bound: dict[str, Any]) -> str:
    f = bound["features"]

    return (
        f"The event is normal traffic and also a malicious attack at the same time. "
        f"It is isolated to source {f['source_id']} and destination {f['destination_id']}, "
        f"but it also affects the entire network segment. "
        f"The communication is both client-to-server and server-to-client."
    )


def get_response_templates():
    return [
        ("clean_supported", build_clean_supported_response),
        ("v1_fabricated", build_v1_fabricated_response),
        ("v2_contradicted", build_v2_contradicted_response),
        ("v3_over_generalised", build_v3_over_generalised_response),
        ("v4_under_specified", build_v4_under_specified_response),
        ("v5_incoherent", build_v5_incoherent_response),
    ]


def generate_responses_for_prompt(prompt_record: dict[str, Any]) -> list[dict[str, Any]]:
    bound = prompt_record["formal_bound"]
    templates = get_response_templates()
    selected_templates = templates[:SYNTHETIC_RESPONSES_PER_PROMPT]

    records = []

    for response_type, builder in selected_templates:
        records.append(
            {
                "response_id": f"{prompt_record['event_id']}_{response_type}",
                "original_event_id": prompt_record["event_id"],
                "response_type": response_type,
                "model_name": "synthetic_rule_based",
                "response": builder(bound),
                "expected_behavior": response_type,
                "source": "synthetic_validation",
            }
        )

    return records


def write_preview(records: list[dict[str, Any]]) -> None:
    lines = [
        "=== SYNTHETIC RESPONSE PREVIEW ===",
        f"Total synthetic responses: {len(records)}",
        "",
    ]

    for record in records[:10]:
        lines.append(f"Response ID: {record['response_id']}")
        lines.append(f"Type: {record['response_type']}")
        lines.append(record["response"])
        lines.append("")

    SYNTHETIC_RESPONSES_PREVIEW.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_project_directories()
    random.seed(RANDOM_SEED)

    if not LLM_PROMPTS_JSONL.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {LLM_PROMPTS_JSONL}\n"
            "Run: python -m src.prompt_builder"
        )

    prompt_records = load_jsonl(LLM_PROMPTS_JSONL)

    responses = []
    for prompt_record in prompt_records:
        responses.extend(generate_responses_for_prompt(prompt_record))

    with open(SYNTHETIC_RESPONSES_JSON, "w", encoding="utf-8") as file:
        json.dump(responses, file, indent=2, ensure_ascii=False)

    write_jsonl(responses, SYNTHETIC_RESPONSES_JSONL)
    write_preview(responses)

    print("Synthetic response generation completed successfully.")
    print(f"Prompt records: {len(prompt_records)}")
    print(f"Synthetic responses created: {len(responses)}")
    print(f"JSON: {SYNTHETIC_RESPONSES_JSON}")
    print(f"JSONL: {SYNTHETIC_RESPONSES_JSONL}")
    print(f"Preview: {SYNTHETIC_RESPONSES_PREVIEW}")


if __name__ == "__main__":
    main()