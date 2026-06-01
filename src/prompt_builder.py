"""Build strict LLM prompts from JSON formal bounds.

Each prompt comprises a fixed analyst system prompt and a user prompt that
embeds the formal bound, including the explicit allowed, required, and
forbidden claim lists. The user prompt is intentionally verbose so that any
deviation by the LLM is a deliberate model failure rather than a
prompt-engineering shortfall.

Stratified sampling
-------------------
When the environment variable ``REASONGUARD_STRATIFY`` is set, the builder
groups bounds by ``proxy_event_type`` and samples
``REASONGUARD_PER_EVENT_TYPE`` bounds from each bucket (default 20). The
sampler is seeded by :data:`src.pipeline_config.RANDOM_SEED` so the selection
is reproducible.
"""

from __future__ import annotations

import json
import os
import random
from typing import Any

from src.pipeline_config import (
    FORMAL_BOUNDS_JSONL,
    LLM_PROMPTS_JSON,
    LLM_PROMPTS_JSONL,
    LLM_PROMPTS_PREVIEW,
    MAX_PROMPT_EVENTS,
    RANDOM_SEED,
    ensure_project_directories,
)


SYSTEM_PROMPT = """You are an industrial control systems network security analyst.

Your task is to explain a formally bounded IEC-104 network observation in precise operational English.

Strict rules:
1. Use only facts explicitly provided in the formal bound.
2. Do not invent attack types, malicious intent, causality, timing patterns, affected assets, or mitigation actions.
3. Do not claim that the observation is confirmed normal or confirmed malicious unless the formal bound explicitly states that.
4. Treat proxy formal classes as observation labels, not as verified attack labels.
5. Stay consistent with the source identifier, destination identifier, ports, packet size, ASDU fields, protocol hint, and communication direction.
6. If evidence is insufficient for a security conclusion, explicitly say that the bound does not confirm a security conclusion.
7. Write 3 to 5 sentences.
8. Use professional analyst language.
"""


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


def build_user_prompt(bound: dict[str, Any]) -> str:
    allowed_claims = "\n".join(f"- {claim}" for claim in bound["allowed_claims"])
    required_claims = "\n".join(f"- {claim}" for claim in bound["required_claims"])
    forbidden_claims = "\n".join(f"- {claim}" for claim in bound["forbidden_claims"])

    features = bound["features"]

    return f"""Explain the following formally bounded ICS network event.

Event metadata:
- Event ID: {bound["event_id"]}
- Dataset: {bound["dataset"]}
- Event granularity: {bound["event_granularity"]}
- Timestamp ms: {bound["timestamp_ms"]}
- Formal bound version: {bound["formal_bound_version"]}
- Schema status: {bound["schema_status"]}

Formal observation:
- Protocol hint: {bound["protocol_hint"]}
- Communication direction: {bound["communication_direction"]}
- Frame type: {bound["frame_type"]}
- Observation pattern: {bound["observation_pattern"]}
- Formal class: {bound["formal_class"]}
- Formal class status: {bound["formal_class_status"]}

Observed features:
- source_id: {features["source_id"]}
- destination_id: {features["destination_id"]}
- bytes: {features["bytes"]}
- pkt_length: {features["pkt_length"]}
- srcport: {features["srcport"]}
- dstport: {features["dstport"]}
- asdu_address: {features["asdu_address"]}
- asdu_cot: {features["asdu_cot"]}
- asdu_items: {features["asdu_items"]}
- asdu_type: {features["asdu_type"]}
- frame_fmt: {features["frame_fmt"]}

Allowed claims:
{allowed_claims}

Required claims:
{required_claims}

Forbidden claims:
{forbidden_claims}

Write the explanation now.
"""


def bound_to_prompt_record(bound: dict[str, Any]) -> dict[str, Any]:
    return {
        "event_id": bound["event_id"],
        "prompt_version": "2.1",
        "system_prompt": SYSTEM_PROMPT,
        "user_prompt": build_user_prompt(bound),
        "formal_bound": bound,
        "metadata": {
            "dataset": bound["dataset"],
            "timestamp_ms": bound["timestamp_ms"],
            "protocol_hint": bound["protocol_hint"],
            "communication_direction": bound["communication_direction"],
            "formal_class": bound["formal_class"],
            "observation_pattern": bound["observation_pattern"],
        },
    }


def write_preview(prompt_records: list[dict[str, Any]]) -> None:
    lines = [
        "=== LLM PROMPT PREVIEW ===",
        f"Total prompts created: {len(prompt_records)}",
        "",
    ]

    for record in prompt_records[:2]:
        lines.append(f"Event ID: {record['event_id']}")
        lines.append("")
        lines.append("SYSTEM PROMPT:")
        lines.append(record["system_prompt"])
        lines.append("")
        lines.append("USER PROMPT:")
        lines.append(record["user_prompt"])
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

    LLM_PROMPTS_PREVIEW.write_text("\n".join(lines), encoding="utf-8")


def stratified_sample(
    bounds: list[dict[str, Any]],
    per_event_type: int,
) -> list[dict[str, Any]]:
    """Return up to ``per_event_type`` bounds for each distinct proxy_event_type.

    Empty event-type buckets are skipped silently. Sampling is seeded by
    ``RANDOM_SEED`` so the selection is reproducible across runs.
    """

    rng = random.Random(RANDOM_SEED)
    buckets: dict[str, list[dict[str, Any]]] = {}

    for bound in bounds:
        event_type = bound.get("proxy_event_type", "unknown")
        buckets.setdefault(event_type, []).append(bound)

    selected: list[dict[str, Any]] = []

    for event_type in sorted(buckets):
        available = buckets[event_type]
        sample_size = min(per_event_type, len(available))

        if sample_size == 0:
            continue

        sampled = rng.sample(available, k=sample_size)
        selected.extend(sampled)

    return selected


def main() -> None:
    ensure_project_directories()

    if not FORMAL_BOUNDS_JSONL.exists():
        raise FileNotFoundError(
            f"Formal bounds file not found: {FORMAL_BOUNDS_JSONL}\n"
            "Run: python -m src.formal_bound_builder"
        )

    bounds = load_jsonl(FORMAL_BOUNDS_JSONL)

    stratify_enabled = os.environ.get("REASONGUARD_STRATIFY", "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }

    if stratify_enabled:
        per_type = int(os.environ.get("REASONGUARD_PER_EVENT_TYPE", "20"))
        selected_bounds = stratified_sample(bounds, per_event_type=per_type)
        print(f"Stratified sampling enabled: {per_type} per event type")
    else:
        selected_bounds = bounds[:MAX_PROMPT_EVENTS]

    prompt_records = [bound_to_prompt_record(bound) for bound in selected_bounds]

    with open(LLM_PROMPTS_JSON, "w", encoding="utf-8") as file:
        json.dump(prompt_records, file, indent=2, ensure_ascii=False)

    write_jsonl(prompt_records, LLM_PROMPTS_JSONL)
    write_preview(prompt_records)

    print("Prompt generation completed successfully.")
    print(f"Available formal bounds: {len(bounds)}")
    print(f"Prompts created: {len(prompt_records)}")
    print(f"JSON: {LLM_PROMPTS_JSON}")
    print(f"JSONL: {LLM_PROMPTS_JSONL}")
    print(f"Preview: {LLM_PROMPTS_PREVIEW}")


if __name__ == "__main__":
    main()