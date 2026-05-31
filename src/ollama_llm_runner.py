from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
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
    OLLAMA_BASE_URL,
    OLLAMA_MODELS,
    OLLAMA_PILOT_LIMIT,
    OLLAMA_RESPONSES_JSON,
    OLLAMA_RESPONSES_JSONL,
    OLLAMA_RESPONSES_PREVIEW,
    OLLAMA_TEMPERATURE,
    OLLAMA_TIMEOUT_SECONDS,
    OLLAMA_TOP_P,
    OUTPUT_DIR,
    ensure_project_directories,
)


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


def model_slug(model_name: str) -> str:
    return model_name.replace(":", "_").replace("/", "_").replace(".", "_")


def build_ollama_prompt(prompt_record: dict[str, Any]) -> str:
    return (
        f"{prompt_record['system_prompt']}\n\n"
        "FORMAL BOUND TASK:\n"
        f"{prompt_record['user_prompt']}\n\n"
        "Remember: do not use outside knowledge. Use only the formal bound."
    )


def call_ollama(prompt: str, model_name: str) -> dict[str, Any]:
    url = f"{OLLAMA_BASE_URL}/api/generate"

    payload = {
        "model": model_name,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": OLLAMA_TEMPERATURE,
            "top_p": OLLAMA_TOP_P,
        },
    }

    request_data = json.dumps(payload).encode("utf-8")

    request = urllib.request.Request(
        url=url,
        data=request_data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started_at = time.time()

    try:
        with urllib.request.urlopen(request, timeout=OLLAMA_TIMEOUT_SECONDS) as response:
            response_body = response.read().decode("utf-8")
            parsed = json.loads(response_body)

        elapsed_seconds = time.time() - started_at

        return {
            "ok": True,
            "response": parsed.get("response", "").strip(),
            "raw": parsed,
            "elapsed_seconds": elapsed_seconds,
        }

    except urllib.error.URLError as error:
        elapsed_seconds = time.time() - started_at

        return {
            "ok": False,
            "response": "",
            "error": str(error),
            "elapsed_seconds": elapsed_seconds,
        }


def build_response_record(
    prompt_record: dict[str, Any],
    model_name: str,
    model_result: dict[str, Any],
) -> dict[str, Any]:
    return {
        "response_id": f"{prompt_record['event_id']}_ollama_{model_slug(model_name)}",
        "original_event_id": prompt_record["event_id"],
        "response_type": "real_llm_output",
        "model_name": model_name,
        "model_backend": "ollama_local",
        "response": model_result.get("response", ""),
        "generation_ok": model_result.get("ok", False),
        "elapsed_seconds": model_result.get("elapsed_seconds"),
        "error": model_result.get("error"),
        "metadata": prompt_record.get("metadata", {}),
    }


def write_preview(records: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "=== OLLAMA LLM RESPONSE PREVIEW ===",
        f"Total responses: {len(records)}",
        "",
    ]

    for record in records[:5]:
        lines.append(f"Response ID: {record['response_id']}")
        lines.append(f"Model: {record['model_name']}")
        lines.append(f"Event ID: {record['original_event_id']}")
        lines.append(f"OK: {record['generation_ok']}")
        lines.append(f"Elapsed seconds: {record['elapsed_seconds']}")
        lines.append("Response:")
        lines.append(record["response"])
        lines.append("")
        lines.append("=" * 80)
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")


def run_one_model(
    prompts: list[dict[str, Any]],
    model_name: str,
) -> tuple[list[dict[str, Any]], dict[str, float]]:
    response_records: list[dict[str, Any]] = []
    ok_count = 0
    total_elapsed = 0.0

    for index, prompt_record in enumerate(prompts, start=1):
        print(f"[{model_name} {index}/{len(prompts)}] {prompt_record['event_id']}")

        full_prompt = build_ollama_prompt(prompt_record)
        model_result = call_ollama(full_prompt, model_name=model_name)
        record = build_response_record(prompt_record, model_name, model_result)
        response_records.append(record)

        if not model_result.get("ok"):
            print(f"  ERROR: {model_result.get('error')}")
        else:
            print(f"  OK in {model_result.get('elapsed_seconds'):.2f}s")
            ok_count += 1
            total_elapsed += float(model_result.get("elapsed_seconds") or 0.0)

    metrics = {
        "prompts": float(len(prompts)),
        "ok_count": float(ok_count),
        "ok_rate": float(ok_count) / float(len(prompts)) if prompts else 0.0,
        "total_elapsed_seconds": total_elapsed,
        "mean_elapsed_seconds": total_elapsed / ok_count if ok_count else 0.0,
    }

    return response_records, metrics


def per_model_output_paths(model_name: str) -> tuple[Path, Path, Path]:
    slug = model_slug(model_name)

    return (
        OUTPUT_DIR / f"ollama_responses_{slug}.json",
        OUTPUT_DIR / f"ollama_responses_{slug}.jsonl",
        OUTPUT_DIR / f"ollama_responses_{slug}_preview.txt",
    )


def resolve_models() -> list[str]:
    """Allow ad-hoc runs to override the configured model list via an env variable.

    Set ``REASONGUARD_OLLAMA_MODELS`` to a comma-separated model list to limit a run
    to a subset of models without editing the config. Empty or unset falls back to
    the full ``OLLAMA_MODELS`` list.
    """

    override = os.environ.get("REASONGUARD_OLLAMA_MODELS", "").strip()

    if override:
        return [name.strip() for name in override.split(",") if name.strip()]

    return list(OLLAMA_MODELS)


def resolve_pilot_limit() -> int:
    """Allow per-run override of the pilot-limit through an env variable.

    Set ``REASONGUARD_PILOT_LIMIT`` to an integer to take that many prompts from the
    head of the prompt file. Empty or unset falls back to ``OLLAMA_PILOT_LIMIT``.
    """

    override = os.environ.get("REASONGUARD_PILOT_LIMIT", "").strip()

    if override.isdigit():
        return int(override)

    return OLLAMA_PILOT_LIMIT


def main() -> None:
    ensure_project_directories()

    if not LLM_PROMPTS_JSONL.exists():
        raise FileNotFoundError(
            f"Prompt file not found: {LLM_PROMPTS_JSONL}\n"
            "Run: python -m src.prompt_builder"
        )

    prompt_records = load_jsonl(LLM_PROMPTS_JSONL)
    pilot_limit = resolve_pilot_limit()
    selected_prompts = prompt_records[:pilot_limit]

    all_responses: list[dict[str, Any]] = []
    models = resolve_models()

    for model_name in models:
        print("")
        print("=" * 80)
        print(f"Running Ollama model: {model_name}")
        print(f"Pilot prompts: {len(selected_prompts)}")
        print("=" * 80)

        with start_run(
            experiment_name=MLFLOW_EXPERIMENT_OLLAMA,
            run_name=f"ollama_{model_slug(model_name)}",
            tags={"stage": "ollama_llm_runner", "model": model_name},
        ):
            log_params({
                "model": model_name,
                "temperature": OLLAMA_TEMPERATURE,
                "top_p": OLLAMA_TOP_P,
                "pilot_limit": OLLAMA_PILOT_LIMIT,
            })

            responses, metrics = run_one_model(selected_prompts, model_name=model_name)
            log_metrics(metrics)

        all_responses.extend(responses)

        json_path, jsonl_path, preview_path = per_model_output_paths(model_name)

        with open(json_path, "w", encoding="utf-8") as file:
            json.dump(responses, file, indent=2, ensure_ascii=False)

        write_jsonl(responses, jsonl_path)
        write_preview(responses, preview_path)

    with open(OLLAMA_RESPONSES_JSON, "w", encoding="utf-8") as file:
        json.dump(all_responses, file, indent=2, ensure_ascii=False)

    write_jsonl(all_responses, OLLAMA_RESPONSES_JSONL)
    write_preview(all_responses, OLLAMA_RESPONSES_PREVIEW)

    ok_total = sum(1 for record in all_responses if record["generation_ok"])

    print("")
    print("Ollama multi-model batch completed.")
    print(f"Models executed: {len(models)}")
    print(f"Total responses: {len(all_responses)}")
    print(f"Successful responses: {ok_total}/{len(all_responses)}")
    print(f"Combined JSONL: {OLLAMA_RESPONSES_JSONL}")


if __name__ == "__main__":
    main()
