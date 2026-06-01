"""Five-minute walkthrough demo of the ReasonGuard pipeline.

Run with ``python -m src.demo_walkthrough`` during a supervisor meeting or
when explaining the framework to a new reader. The script prints a single
formal bound, generates a synthetic clean response and a synthetic V1
response, runs both through ReasonGuard, and shows the verdicts side by
side. Nothing is written to disk so the demo can be replayed safely.
"""

from __future__ import annotations

import json

from src.pipeline_config import LLM_PROMPTS_JSONL
from src.reason_guard_checker import check_response
from src.synthetic_response_generator import (
    build_clean_supported_response,
    build_v1_fabricated_response,
)


def _load_first_prompt() -> dict:
    with open(LLM_PROMPTS_JSONL, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                return json.loads(line)

    raise RuntimeError(
        f"No prompts found in {LLM_PROMPTS_JSONL}. "
        "Run python -m src.prompt_builder first."
    )


def _show_header(title: str) -> None:
    bar = "=" * 70
    print()
    print(bar)
    print(title)
    print(bar)


def _show_bound(bound: dict) -> None:
    _show_header("1. FORMAL BOUND (proxy schema v2.1)")
    print(f"event_id          : {bound['event_id']}")
    print(f"protocol_hint     : {bound['protocol_hint']}")
    print(f"direction         : {bound['communication_direction']}")
    print(f"observation       : {bound['observation_pattern']}")
    print(f"formal_class      : {bound['formal_class']}")
    print(f"schema_status     : {bound['schema_status']}")
    print(f"proxy_event_type  : {bound.get('proxy_event_type', '—')}")
    print()
    print("machine_constraints (all default false under proxy):")

    for key, value in bound["machine_constraints"].items():
        if key == "must_match":
            continue

        print(f"  {key:30s} : {value}")


def _show_response(label: str, text: str) -> None:
    _show_header(f"2. {label.upper()} RESPONSE")
    print(text)


def _show_verdict(label: str, prompt: dict, response_text: str) -> None:
    record = {
        "response_id": f"{prompt['event_id']}_demo_{label}",
        "original_event_id": prompt["event_id"],
        "response_type": f"demo_{label}",
        "model_name": "demo_synthetic",
        "response": response_text,
    }

    verdict = check_response(prompt, record)

    _show_header(f"3. REASONGUARD VERDICT FOR {label.upper()}")
    print(f"violation_codes : {verdict['violation_codes'] or 'NONE'}")
    print(f"severity        : {verdict['severity']}")

    if verdict["violation_codes"]:
        print()
        print("Reasons:")

        for code in verdict["violation_codes"]:
            reasons = verdict["reasons"][code]
            for reason in reasons:
                print(f"  [{code}] {reason}")

    per_claim = verdict.get("per_claim_verdicts")

    if per_claim:
        print()
        print("Per-claim three-state verdicts (spaCy):")

        for entry in per_claim:
            print(f"  [{entry['verdict']:13s}] {entry['claim']}")


def main() -> None:
    prompt = _load_first_prompt()
    bound = prompt["formal_bound"]

    _show_bound(bound)

    clean_text = build_clean_supported_response(bound)
    v1_text = build_v1_fabricated_response(bound)

    _show_response("clean", clean_text)
    _show_verdict("clean", prompt, clean_text)

    _show_response("V1 fabricated", v1_text)
    _show_verdict("v1_fabricated", prompt, v1_text)

    print()
    print("=" * 70)
    print(
        "Two responses, same bound: ReasonGuard accepts the clean one and "
        "rejects the V1-fabricated one with the specific reasons that "
        "triggered the verdict."
    )
    print("=" * 70)


if __name__ == "__main__":
    main()
