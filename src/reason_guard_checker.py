from __future__ import annotations

import json
import re
from typing import Any

from src.mlflow_tracker import (
    log_artifact,
    log_metrics,
    log_params,
    start_run,
)
from src.pipeline_config import (
    LLM_PROMPTS_JSONL,
    MLFLOW_EXPERIMENT_CHECKER,
    REASONGUARD_PREVIEW,
    REASONGUARD_REPORT_JSON,
    REASONGUARD_REPORT_JSONL,
    REASONGUARD_SUMMARY_CSV,
    REASONGUARD_SUMMARY_JSON,
    SYNTHETIC_RESPONSES_JSONL,
    ensure_project_directories,
)


def _try_extract_spacy_claims(response: str, bound: dict[str, Any]):
    try:
        from src.claim_extraction import (
            classify_claims_against_bound,
            extract_claims_with_spacy,
        )
    except Exception:
        return None, None

    try:
        extracted = extract_claims_with_spacy(response)
    except RuntimeError:
        return None, None

    per_claim = classify_claims_against_bound(extracted, bound)

    return (
        extracted.to_dict(),
        [
            {
                "claim": entry.claim,
                "verdict": entry.verdict.value,
                "evidence": entry.evidence,
            }
            for entry in per_claim
        ],
    )


ATTACK_TERMS = [
    "attack",
    "malicious",
    "replay",
    "flooding",
    "mitm",
    "man in the middle",
    "scan",
    "scanning",
    "dos",
    "denial of service",
    "command injection",
    "intrusion",
    "compromise",
    "attacker",
    "exploit",
]

MITIGATION_TERMS = [
    "isolate",
    "isolated",
    "shutdown",
    "block",
    "blocked",
    "quarantine",
    "disconnect",
    "emergency response",
    "immediate response",
    "prevent further",
]

CAUSAL_TERMS = [
    "because",
    "caused by",
    "due to",
    "therefore",
    "suggests that",
    "indicates that",
    "appears to be using",
    "is using",
    "in order to",
]

NORMALITY_TERMS = [
    "normal traffic",
    "benign",
    "routine",
    "typical",
    "standard communication",
    "no specific concern",
    "normality",
]

DIRECTION_TERMS = {
    "client_to_server": [
        "client-to-server",
        "client to server",
        "client_to_server",
    ],
    "server_to_client": [
        "server-to-client",
        "server to client",
        "server_to_client",
    ],
}

INCOHERENT_PAIRS = [
    ("normal", "malicious"),
    ("normal", "attack"),
    ("benign", "malicious"),
    ("routine", "attack"),
    ("isolated", "entire network"),
    ("single device", "entire network"),
    ("client-to-server", "server-to-client"),
    ("client to server", "server to client"),
    ("client_to_server", "server_to_client"),
]


SAFE_NEGATION_PATTERNS = [
    "does not confirm maliciousness",
    "does not confirm a security conclusion",
    "not confirmed malicious",
    "not confirm malicious",
    "not malicious",
    "does not confirm attack",
    "no confirmed attack",
    "does not provide enough information",
]


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


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains_any(text: str, terms: list[str]) -> list[str]:
    text_lower = normalize_text(text)
    return [term for term in terms if term in text_lower]


def extract_numbers(text: str) -> list[int]:
    return [int(match) for match in re.findall(r"\b\d+\b", text)]


def is_safe_negated_usage(response: str, term: str) -> bool:
    response_lower = normalize_text(response)

    for pattern in SAFE_NEGATION_PATTERNS:
        if pattern in response_lower and term in pattern:
            return True

    return False


def extract_attack_terms(response: str) -> list[str]:
    found_terms = []

    for term in ATTACK_TERMS:
        if term in normalize_text(response):
            if not is_safe_negated_usage(response, term):
                found_terms.append(term)

    return found_terms


def extract_claims(response: str) -> dict[str, Any]:
    response_lower = normalize_text(response)

    claims = {
        "attack_terms": extract_attack_terms(response),
        "mitigation_terms": contains_any(response, MITIGATION_TERMS),
        "causal_terms": contains_any(response, CAUSAL_TERMS),
        "normality_terms": contains_any(response, NORMALITY_TERMS),
        "numbers": extract_numbers(response),
        "direction_terms": [],
        "mentions_source": "source" in response_lower,
        "mentions_destination": "destination" in response_lower,
        "mentions_port": "port" in response_lower,
        "mentions_asdu": "asdu" in response_lower,
        "mentions_proxy": "proxy" in response_lower,
        "mentions_not_confirmed": (
            "does not confirm" in response_lower
            or "not confirm" in response_lower
            or "not confirmed" in response_lower
            or "insufficient" in response_lower
            or "does not provide enough information" in response_lower
        ),
    }

    for direction, terms in DIRECTION_TERMS.items():
        for term in terms:
            if term in response_lower:
                claims["direction_terms"].append(direction)

    claims["direction_terms"] = sorted(set(claims["direction_terms"]))

    return claims


def detect_v1_fabricated_reasoning(
    bound: dict[str, Any],
    claims: dict[str, Any],
) -> tuple[bool, list[str]]:
    reasons = []
    constraints = bound["machine_constraints"]

    if claims["attack_terms"] and not constraints["attack_claim_allowed"]:
        reasons.append(
            f"Unsupported attack or maliciousness terms: {claims['attack_terms']}"
        )

    if claims["mitigation_terms"] and not constraints["mitigation_claim_allowed"]:
        reasons.append(
            f"Unsupported mitigation terms: {claims['mitigation_terms']}"
        )

    if claims["causal_terms"] and not constraints["causal_claim_allowed"]:
        reasons.append(
            f"Unsupported causal language: {claims['causal_terms']}"
        )

    response_numbers = set(claims["numbers"])

    allowed_numbers = {
        int(bound["features"]["source_id"]),
        int(bound["features"]["destination_id"]),
        int(bound["features"]["srcport"]),
        int(bound["features"]["dstport"]),
        int(bound["features"]["bytes"]),
        int(bound["features"]["pkt_length"]),
        int(bound["features"]["asdu_address"]),
        int(bound["features"]["asdu_cot"]),
        int(bound["features"]["asdu_items"]),
        int(bound["features"]["asdu_type"]),
        int(bound["features"]["frame_fmt"]),
        104,
        2404,
    }

    unsupported_numbers = sorted(response_numbers - allowed_numbers)

    suspicious_numbers = [
        number for number in unsupported_numbers
        if number > 1000
    ]

    if suspicious_numbers:
        reasons.append(
            f"Unsupported numeric identifiers or values: {suspicious_numbers}"
        )

    return bool(reasons), reasons


def detect_v2_contradicted_reasoning(
    bound: dict[str, Any],
    claims: dict[str, Any],
    response: str,
) -> tuple[bool, list[str]]:
    reasons = []

    expected_direction = bound["communication_direction"]
    observed_directions = claims["direction_terms"]

    if expected_direction in ["client_to_server", "server_to_client"]:
        opposite_direction = (
            "server_to_client"
            if expected_direction == "client_to_server"
            else "client_to_server"
        )

        if (
            opposite_direction in observed_directions
            and expected_direction not in observed_directions
        ):
            reasons.append(
                f"Response states {opposite_direction}, but the formal bound states {expected_direction}."
            )

    response_lower = normalize_text(response)

    source_id = str(bound["features"]["source_id"])
    destination_id = str(bound["features"]["destination_id"])

    if (
        "source" in response_lower
        and destination_id in response_lower
        and source_id not in response_lower
    ):
        reasons.append(
            "Response appears to confuse source and destination identifiers."
        )

    return bool(reasons), reasons


def detect_v3_over_generalised_reasoning(
    bound: dict[str, Any],
    claims: dict[str, Any],
    response: str,
) -> tuple[bool, list[str]]:
    reasons = []

    response_lower = normalize_text(response)

    specific_values = {
        str(bound["features"]["source_id"]),
        str(bound["features"]["destination_id"]),
        str(bound["features"]["srcport"]),
        str(bound["features"]["dstport"]),
        str(bound["features"]["asdu_type"]),
        str(bound["features"]["asdu_cot"]),
    }

    mentioned_specific_values = {
        value for value in specific_values
        if value in response_lower
    }

    if (
        claims["normality_terms"]
        and len(mentioned_specific_values) < 3
    ):
        reasons.append(
            "Response uses broad normality language while omitting key formal specifics."
        )

    return bool(reasons), reasons


def detect_v4_under_specified_reasoning(
    claims: dict[str, Any],
) -> tuple[bool, list[str]]:
    reasons = []

    if not claims["mentions_source"]:
        reasons.append("Missing source reference.")

    if not claims["mentions_destination"]:
        reasons.append("Missing destination reference.")

    if not claims["mentions_port"]:
        reasons.append("Missing port reference.")

    if not claims["mentions_asdu"]:
        reasons.append("Missing ASDU reference.")

    if (
        not claims["mentions_proxy"]
        and not claims["mentions_not_confirmed"]
    ):
        reasons.append(
            "Missing uncertainty or proxy clarification."
        )

    return bool(reasons), reasons


def detect_v5_incoherent_reasoning(
    response: str,
) -> tuple[bool, list[str]]:
    response_lower = normalize_text(response)

    safe_negated_incoherence_patterns = [
        "does not confirm maliciousness or normality",
        "does not confirm normality or maliciousness",
        "does not confirm maliciousness",
        "does not confirm normality",
        "not confirmed as malicious",
        "not confirmed as normal",
        "does not confirm a security conclusion",
    ]

    for pattern in safe_negated_incoherence_patterns:
        if pattern in response_lower:
            return False, []

    reasons = []

    for left, right in INCOHERENT_PAIRS:
        if left in response_lower and right in response_lower:
            reasons.append(
                f"Conflicting terms detected: '{left}' and '{right}'."
            )

    return bool(reasons), reasons


def classify_severity(violation_codes: list[str]) -> str:
    if any(code in violation_codes for code in ["V1", "V2", "V5"]):
        return "high"

    if "V3" in violation_codes and "V4" in violation_codes:
        return "medium"

    if any(code in violation_codes for code in ["V3", "V4"]):
        return "low"

    return "none"


def check_response(
    prompt_record: dict[str, Any],
    response_record: dict[str, Any],
) -> dict[str, Any]:
    bound = prompt_record["formal_bound"]
    response = response_record["response"]

    claims = extract_claims(response)

    v1, v1_reasons = detect_v1_fabricated_reasoning(bound, claims)
    v2, v2_reasons = detect_v2_contradicted_reasoning(
        bound,
        claims,
        response,
    )
    v3, v3_reasons = detect_v3_over_generalised_reasoning(
        bound,
        claims,
        response,
    )
    v4, v4_reasons = detect_v4_under_specified_reasoning(claims)
    v5, v5_reasons = detect_v5_incoherent_reasoning(response)

    violations = {
        "V1_fabricated_reasoning": v1,
        "V2_contradicted_reasoning": v2,
        "V3_over_generalised_reasoning": v3,
        "V4_under_specified_reasoning": v4,
        "V5_incoherent_reasoning": v5,
    }

    violation_codes = []

    if v1:
        violation_codes.append("V1")

    if v2:
        violation_codes.append("V2")

    if v3:
        violation_codes.append("V3")

    if v4:
        violation_codes.append("V4")

    if v5:
        violation_codes.append("V5")

    spacy_claims, per_claim_verdicts = _try_extract_spacy_claims(response, bound)

    return {
        "response_id": response_record["response_id"],
        "event_id": response_record["original_event_id"],
        "response_type": response_record["response_type"],
        "model_name": response_record.get("model_name", "unknown"),
        "response": response,
        "violation_codes": violation_codes,
        "severity": classify_severity(violation_codes),
        "violations": violations,
        "reasons": {
            "V1": v1_reasons,
            "V2": v2_reasons,
            "V3": v3_reasons,
            "V4": v4_reasons,
            "V5": v5_reasons,
        },
        "lexicon_claims": claims,
        "spacy_claims": spacy_claims,
        "per_claim_verdicts": per_claim_verdicts,
    }


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    summary = {
        "total_responses": len(results),
        "no_violation": 0,
        "V1_fabricated_reasoning": 0,
        "V2_contradicted_reasoning": 0,
        "V3_over_generalised_reasoning": 0,
        "V4_under_specified_reasoning": 0,
        "V5_incoherent_reasoning": 0,
    }

    for result in results:
        if not result["violation_codes"]:
            summary["no_violation"] += 1

        for key, value in result["violations"].items():
            if value:
                summary[key] += 1

    return summary


def write_csv_summary(results: list[dict[str, Any]]) -> None:
    lines = [
        "response_id,event_id,response_type,severity,violations"
    ]

    for result in results:
        lines.append(
            ",".join(
                [
                    result["response_id"],
                    result["event_id"],
                    result["response_type"],
                    result["severity"],
                    "|".join(result["violation_codes"])
                    if result["violation_codes"]
                    else "NONE",
                ]
            )
        )

    REASONGUARD_SUMMARY_CSV.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def write_preview(
    results: list[dict[str, Any]],
    summary: dict[str, Any],
) -> None:
    lines = [
        "=== REASONGUARD REPORT PREVIEW ===",
        "",
        "SUMMARY:",
        json.dumps(summary, indent=2),
        "",
    ]

    for result in results[:5]:
        lines.append(json.dumps(result, indent=2))
        lines.append("")

    REASONGUARD_PREVIEW.write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def main() -> None:
    ensure_project_directories()

    prompt_records = load_jsonl(LLM_PROMPTS_JSONL)
    response_records = load_jsonl(SYNTHETIC_RESPONSES_JSONL)

    prompts_by_event = {
        record["event_id"]: record
        for record in prompt_records
    }

    results = []

    for response_record in response_records:
        event_id = response_record["original_event_id"]

        if event_id not in prompts_by_event:
            continue

        result = check_response(
            prompts_by_event[event_id],
            response_record,
        )

        results.append(result)

    summary = summarize(results)

    with open(REASONGUARD_REPORT_JSON, "w", encoding="utf-8") as file:
        json.dump(
            {
                "summary": summary,
                "results": results,
            },
            file,
            indent=2,
            ensure_ascii=False,
        )

    write_jsonl(results, REASONGUARD_REPORT_JSONL)

    with open(REASONGUARD_SUMMARY_JSON, "w", encoding="utf-8") as file:
        json.dump(summary, file, indent=2)

    write_csv_summary(results)
    write_preview(results, summary)

    with start_run(
        experiment_name=MLFLOW_EXPERIMENT_CHECKER,
        run_name="checker_run",
        tags={"stage": "reason_guard_checker"},
    ):
        log_params({
            "prompt_records": len(prompt_records),
            "response_records": len(response_records),
        })
        log_metrics({float_key: float(value) for float_key, value in summary.items()})
        log_artifact(REASONGUARD_SUMMARY_JSON)
        log_artifact(REASONGUARD_SUMMARY_CSV)
        log_artifact(REASONGUARD_PREVIEW)

    print("ReasonGuard analysis completed successfully.")
    print("")
    print(json.dumps(summary, indent=2))
    print("")
    print(f"Report JSON: {REASONGUARD_REPORT_JSON}")
    print(f"Summary CSV: {REASONGUARD_SUMMARY_CSV}")


if __name__ == "__main__":
    main()