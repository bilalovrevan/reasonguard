"""Run pilot batches against cloud LLMs (OpenAI, Gemini) via their HTTP APIs.

The runner intentionally avoids the vendor SDKs and uses ``urllib`` directly
to keep the dependency footprint small. A provider is skipped automatically
when its API key environment variable is not set, so importing or executing
this module is always safe even in secret-less environments.

Environment variables consumed:

- ``OPENAI_API_KEY`` — bearer token for the OpenAI Chat Completions endpoint.
- ``GEMINI_API_KEY`` — API key for the Gemini generateContent endpoint.
- ``OPENAI_MODEL`` / ``GEMINI_MODEL`` — optional model name overrides.
- ``REASONGUARD_CLOUD_PILOT_LIMIT`` — integer prompt limit per provider.
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

from src.mlflow_tracker import (
    log_metrics,
    log_params,
    start_run,
)
from src.pipeline_config import (
    LLM_PROMPTS_JSONL,
    MLFLOW_EXPERIMENT_OLLAMA,
    OUTPUT_DIR,
    ensure_project_directories,
)


CLOUD_RESPONSES_JSON = OUTPUT_DIR / "cloud_llm_responses_sample_003.json"
CLOUD_RESPONSES_JSONL = OUTPUT_DIR / "cloud_llm_responses_sample_003.jsonl"
CLOUD_RESPONSES_PREVIEW = OUTPUT_DIR / "cloud_llm_responses_preview.txt"

CLOUD_PILOT_LIMIT_DEFAULT = 20
CLOUD_TEMPERATURE = 0.1
CLOUD_TOP_P = 0.9
CLOUD_MAX_TOKENS = 600

OPENAI_DEFAULT_MODEL = "gpt-4o-mini"
GEMINI_DEFAULT_MODEL = "gemini-1.5-flash"


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []

    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def write_jsonl(records: list[dict[str, Any]], path: Path) -> None:
    with open(path, "w", encoding="utf-8") as file:
        for record in records:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")


def resolve_pilot_limit() -> int:
    override = os.environ.get("REASONGUARD_CLOUD_PILOT_LIMIT", "").strip()

    if override.isdigit():
        return int(override)

    return CLOUD_PILOT_LIMIT_DEFAULT


def build_combined_prompt(prompt_record: dict[str, Any]) -> str:
    return (
        f"{prompt_record['system_prompt']}\n\n"
        "FORMAL BOUND TASK:\n"
        f"{prompt_record['user_prompt']}\n\n"
        "Remember: do not use outside knowledge. Use only the formal bound."
    )


def call_openai(
    prompt_record: dict[str, Any],
    model: str,
    api_key: str,
) -> dict[str, Any]:
    """Call the OpenAI Chat Completions endpoint without taking on a heavy dependency.

    The function uses urllib so the project does not require the openai SDK.
    """

    import urllib.error
    import urllib.request

    payload = {
        "model": model,
        "temperature": CLOUD_TEMPERATURE,
        "top_p": CLOUD_TOP_P,
        "max_tokens": CLOUD_MAX_TOKENS,
        "messages": [
            {"role": "system", "content": prompt_record["system_prompt"]},
            {"role": "user", "content": prompt_record["user_prompt"]},
        ],
    }

    request = urllib.request.Request(
        url="https://api.openai.com/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    started = time.time()

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            parsed = json.loads(response.read().decode("utf-8"))

        elapsed = time.time() - started
        message = parsed["choices"][0]["message"]["content"].strip()

        return {
            "ok": True,
            "response": message,
            "raw": parsed,
            "elapsed_seconds": elapsed,
        }

    except urllib.error.URLError as error:
        return {
            "ok": False,
            "response": "",
            "error": str(error),
            "elapsed_seconds": time.time() - started,
        }


def call_gemini(
    prompt_record: dict[str, Any],
    model: str,
    api_key: str,
) -> dict[str, Any]:
    """Call the Gemini text-generation endpoint."""

    import urllib.error
    import urllib.request

    combined = build_combined_prompt(prompt_record)

    payload = {
        "contents": [{"parts": [{"text": combined}]}],
        "generationConfig": {
            "temperature": CLOUD_TEMPERATURE,
            "topP": CLOUD_TOP_P,
            "maxOutputTokens": CLOUD_MAX_TOKENS,
        },
    }

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/"
        f"{model}:generateContent?key={api_key}"
    )

    request = urllib.request.Request(
        url=url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.time()

    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            parsed = json.loads(response.read().decode("utf-8"))

        elapsed = time.time() - started
        candidate = parsed["candidates"][0]
        text_parts = [part.get("text", "") for part in candidate["content"]["parts"]]
        message = "\n".join(part for part in text_parts if part).strip()

        return {
            "ok": True,
            "response": message,
            "raw": parsed,
            "elapsed_seconds": elapsed,
        }

    except urllib.error.URLError as error:
        return {
            "ok": False,
            "response": "",
            "error": str(error),
            "elapsed_seconds": time.time() - started,
        }


def build_response_record(
    prompt_record: dict[str, Any],
    model_name: str,
    provider: str,
    result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "response_id": f"{prompt_record['event_id']}_cloud_{provider}_{model_name.replace('/', '_')}",
        "original_event_id": prompt_record["event_id"],
        "response_type": "real_llm_output",
        "model_name": model_name,
        "model_backend": f"cloud_{provider}",
        "response": result.get("response", ""),
        "generation_ok": result.get("ok", False),
        "elapsed_seconds": result.get("elapsed_seconds"),
        "error": result.get("error"),
        "metadata": prompt_record.get("metadata", {}),
    }


def write_preview(records: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "=== CLOUD LLM RESPONSE PREVIEW ===",
        f"Total responses: {len(records)}",
        "",
    ]

    for record in records[:5]:
        lines.append(f"Response ID: {record['response_id']}")
        lines.append(f"Model: {record['model_name']}")
        lines.append(f"OK: {record['generation_ok']}")
        lines.append(f"Elapsed: {record['elapsed_seconds']}")
        lines.append("Response:")
        lines.append(record["response"])
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    ensure_project_directories()

    if not LLM_PROMPTS_JSONL.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {LLM_PROMPTS_JSONL}\n"
            "Run: python -m src.prompt_builder"
        )

    pilot_limit = resolve_pilot_limit()
    prompt_records = load_jsonl(LLM_PROMPTS_JSONL)[:pilot_limit]

    openai_api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    gemini_api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    openai_model = os.environ.get("OPENAI_MODEL", OPENAI_DEFAULT_MODEL)
    gemini_model = os.environ.get("GEMINI_MODEL", GEMINI_DEFAULT_MODEL)

    providers: list[tuple[str, str, str]] = []

    if openai_api_key:
        providers.append(("openai", openai_model, openai_api_key))
    else:
        print("OPENAI_API_KEY is not set; skipping OpenAI provider.")

    if gemini_api_key:
        providers.append(("gemini", gemini_model, gemini_api_key))
    else:
        print("GEMINI_API_KEY is not set; skipping Gemini provider.")

    if not providers:
        print(
            "\nNo cloud providers configured. Set OPENAI_API_KEY or GEMINI_API_KEY "
            "and re-run."
        )
        return

    all_responses: list[dict[str, Any]] = []

    for provider, model, api_key in providers:
        print("")
        print("=" * 80)
        print(f"Running cloud provider: {provider} | model: {model}")
        print(f"Pilot prompts: {len(prompt_records)}")
        print("=" * 80)

        with start_run(
            experiment_name=MLFLOW_EXPERIMENT_OLLAMA,
            run_name=f"cloud_{provider}_{model.replace('/', '_')}",
            tags={"stage": "cloud_llm_runner", "provider": provider, "model": model},
        ):
            log_params({
                "provider": provider,
                "model": model,
                "temperature": CLOUD_TEMPERATURE,
                "top_p": CLOUD_TOP_P,
                "max_tokens": CLOUD_MAX_TOKENS,
                "pilot_limit": pilot_limit,
            })

            responses: list[dict[str, Any]] = []
            ok_count = 0
            total_elapsed = 0.0

            for index, prompt_record in enumerate(prompt_records, start=1):
                print(f"[{provider}/{model} {index}/{len(prompt_records)}] {prompt_record['event_id']}")

                if provider == "openai":
                    result = call_openai(prompt_record, model=model, api_key=api_key)
                else:
                    result = call_gemini(prompt_record, model=model, api_key=api_key)

                record = build_response_record(prompt_record, model, provider, result)
                responses.append(record)

                if not result.get("ok"):
                    print(f"  ERROR: {result.get('error')}")
                else:
                    print(f"  OK in {result.get('elapsed_seconds'):.2f}s")
                    ok_count += 1
                    total_elapsed += float(result.get("elapsed_seconds") or 0.0)

            metrics = {
                "prompts": float(len(prompt_records)),
                "ok_count": float(ok_count),
                "ok_rate": float(ok_count) / float(len(prompt_records)) if prompt_records else 0.0,
                "total_elapsed_seconds": total_elapsed,
                "mean_elapsed_seconds": total_elapsed / ok_count if ok_count else 0.0,
            }
            log_metrics(metrics)

        all_responses.extend(responses)

    with open(CLOUD_RESPONSES_JSON, "w", encoding="utf-8") as file:
        json.dump(all_responses, file, indent=2, ensure_ascii=False)

    write_jsonl(all_responses, CLOUD_RESPONSES_JSONL)
    write_preview(all_responses, CLOUD_RESPONSES_PREVIEW)

    ok_total = sum(1 for record in all_responses if record["generation_ok"])

    print("")
    print("Cloud LLM batch completed.")
    print(f"Providers: {len(providers)}")
    print(f"Total responses: {len(all_responses)}")
    print(f"Successful: {ok_total}/{len(all_responses)}")
    print(f"Combined JSONL: {CLOUD_RESPONSES_JSONL}")


if __name__ == "__main__":
    main()
