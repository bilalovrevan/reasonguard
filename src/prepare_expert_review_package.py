"""Build the blind 50-sample package for the VUT Brno domain expert (M5 milestone).

Selects a stratified sample of REAL local-LLM explanation pairs (never synthetic
ones — the point is to validate ReasonGuard against genuine model behaviour) and
formats them for an independent human reviewer who has NOT seen ReasonGuard's own
verdict. This blindness is required for Cohen's Kappa between ReasonGuard and the
domain expert to be a valid inter-rater reliability measure rather than a biased
comparison.

Outputs:
    samples-for-expert-review/expert_review_batch_<date>.csv   -> send this
    samples-for-expert-review/v1_v5_taxonomy_reference.md      -> send this
    samples-for-expert-review/reviewer_instructions.md         -> send this
    samples-for-expert-review/expert_review_batch_<date>.zip   -> zip of the three above, send this
    samples-for-expert-review/INTERNAL_answer_key_<date>.csv   -> DO NOT SEND. Kept local
                                                                    to score Kappa once labels return.

Run:
    python -m src.prepare_expert_review_package
"""

from __future__ import annotations

import csv
import json
import random
import zipfile
from datetime import date
from pathlib import Path
from typing import Any

from src.pipeline_config import OUTPUT_DIR, PROJECT_ROOT, RANDOM_SEED

EXPERT_DIR = PROJECT_ROOT / "samples-for-expert-review"

REAL_RESPONSE_FILES = [
    OUTPUT_DIR / "ollama_responses_llama3_1_8b-instruct-q4_0.jsonl",
    OUTPUT_DIR / "ollama_responses_mistral_7b-instruct-v0_3-q4_0.jsonl",
    OUTPUT_DIR / "ollama_responses_phi3_mini.jsonl",
]
# Cloud responses are picked up automatically if/when they exist, so the sample
# widens to 5 models without needing to edit this script again.
OPTIONAL_CLOUD_FILE = OUTPUT_DIR / "cloud_llm_responses_sample_003.jsonl"

FORMAL_BOUNDS_FILE = OUTPUT_DIR / "formal_bounds_sample_003.jsonl"

SAMPLE_SIZE = 50


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records = []
    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_bounds_index() -> dict[str, dict[str, Any]]:
    return {b["event_id"]: b for b in load_jsonl(FORMAL_BOUNDS_FILE)}


def summarise_bound(bound: dict[str, Any] | None) -> str:
    if not bound:
        return "(formal bound not found for this event id — flag to first supervisor)"
    claims = bound.get("allowed_claims", [])
    version = bound.get("formal_bound_version", "unknown")
    status = bound.get("schema_status", "unknown")
    header = f"[Formal bound v{version}, schema status: {status}]"
    return header + "\n" + "\n".join(f"- {c}" for c in claims)


def stratified_sample(responses: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    rng = random.Random(RANDOM_SEED)
    by_model: dict[str, list[dict[str, Any]]] = {}
    for r in responses:
        by_model.setdefault(r["model_name"], []).append(r)

    for bucket in by_model.values():
        rng.shuffle(bucket)

    models = sorted(by_model.keys())
    per_model = n // len(models)
    remainder = n % len(models)

    selected: list[dict[str, Any]] = []
    for i, model in enumerate(models):
        take = per_model + (1 if i < remainder else 0)
        selected.extend(by_model[model][:take])

    rng.shuffle(selected)
    return selected[:n]


def main() -> None:
    EXPERT_DIR.mkdir(parents=True, exist_ok=True)

    responses: list[dict[str, Any]] = []
    for path in REAL_RESPONSE_FILES:
        responses.extend(load_jsonl(path))
    responses.extend(load_jsonl(OPTIONAL_CLOUD_FILE))

    only_real = [r for r in responses if r.get("response_type") == "real_llm_output" and r.get("generation_ok", True)]

    if len(only_real) < SAMPLE_SIZE:
        raise SystemExit(
            f"Only {len(only_real)} real LLM responses available, need {SAMPLE_SIZE}. "
            "Run the local/cloud LLM runners first."
        )

    bounds_index = load_bounds_index()
    sample = stratified_sample(only_real, SAMPLE_SIZE)

    today = date.today().isoformat()
    batch_csv = EXPERT_DIR / f"expert_review_batch_{today}.csv"
    answer_key_csv = EXPERT_DIR / f"INTERNAL_answer_key_{today}.csv"
    taxonomy_md = EXPERT_DIR / "v1_v5_taxonomy_reference.md"
    instructions_md = EXPERT_DIR / "reviewer_instructions.md"
    zip_path = EXPERT_DIR / f"expert_review_batch_{today}.zip"

    with open(batch_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            [
                "sample_id",
                "formal_bound_summary",
                "ai_explanation",
                "expert_violation_class",
                "expert_severity",
                "expert_confidence_1to5",
                "expert_notes",
            ]
        )
        for idx, r in enumerate(sample, start=1):
            sample_id = f"ER-{idx:03d}"
            bound = bounds_index.get(r.get("original_event_id"))
            writer.writerow(
                [
                    sample_id,
                    summarise_bound(bound),
                    r["response"],
                    "",
                    "",
                    "",
                    "",
                ]
            )

    with open(answer_key_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_id", "response_id", "original_event_id", "model_name"])
        for idx, r in enumerate(sample, start=1):
            writer.writerow([f"ER-{idx:03d}", r["response_id"], r.get("original_event_id", ""), r["model_name"]])

    taxonomy_md.write_text(
        "# ReasonGuard V1-V5 Reasoning Violation Taxonomy — Reviewer Reference\n\n"
        "For each sample, read the formal bound (the facts the system actually established) "
        "and the AI explanation, then judge which class (if any) applies.\n\n"
        "- **NONE** — the explanation stays within the formal bound; no violation.\n"
        "- **V1 Fabricated Reasoning** — the AI asserts facts, causes, or entities not present in "
        "or derivable from the formal bound.\n"
        "- **V2 Contradicted Reasoning** — the AI explicitly contradicts a fact established by the "
        "formal bound.\n"
        "- **V3 Over-Generalised Reasoning** — the AI produces a correct category but loses "
        "formally established specifics, reducing actionability.\n"
        "- **V4 Under-Specified Reasoning** — the AI omits formally established information that "
        "is operationally required for a correct response.\n"
        "- **V5 Incoherent Reasoning** — the AI explanation is internally self-contradictory, "
        "independent of the formal bound.\n\n"
        "Please assign exactly one class per sample (the single most severe violation present, "
        "or NONE), a severity (none/low/medium/high), your confidence (1-5), and any free-text "
        "notes. You are not shown ReasonGuard's own automated verdict — this is intentional, so "
        "your assessment is independent and can be compared against it (Cohen's Kappa).\n",
        encoding="utf-8",
    )

    instructions_md.write_text(
        "# Reviewer Instructions — ReasonGuard M5 Expert Validation Batch\n\n"
        f"Batch date: {today}. Sample size: {len(sample)} explanation pairs, drawn from real "
        "local-LLM outputs (not synthetic), stratified across models.\n\n"
        "1. Open `expert_review_batch_" + today + ".csv`.\n"
        "2. For each row, read `formal_bound_summary` (what is formally established) and "
        "`ai_explanation` (what the model said).\n"
        "3. Fill in `expert_violation_class` using the definitions in "
        "`v1_v5_taxonomy_reference.md`, plus `expert_severity`, `expert_confidence_1to5`, and "
        "optional `expert_notes`.\n"
        "4. Note: the formal bound schema is still the proxy schema (v2.1/v3.0-hmi), pending the "
        "official NES@FIT automaton output schema — please flag anything that reads as an "
        "artefact of the proxy schema rather than a genuine reasoning violation.\n"
        "5. Return the completed CSV by email. Target turnaround: as fast as feasible — the "
        "student is finishing under a confirmed 15 September 2026 submission deadline.\n\n"
        "Thank you for the independent review — it is what lets us report Cohen's Kappa between "
        "ReasonGuard and expert judgement in the thesis.\n",
        encoding="utf-8",
    )

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.write(batch_csv, batch_csv.name)
        zf.write(taxonomy_md, taxonomy_md.name)
        zf.write(instructions_md, instructions_md.name)

    print(f"Wrote {batch_csv}")
    print(f"Wrote {taxonomy_md}")
    print(f"Wrote {instructions_md}")
    print(f"Wrote {zip_path}  <-- SEND THIS ZIP TO VUT BRNO")
    print(f"Wrote {answer_key_csv}  <-- DO NOT SEND, keep local for scoring Kappa later")
    model_counts: dict[str, int] = {}
    for r in sample:
        model_counts[r["model_name"]] = model_counts.get(r["model_name"], 0) + 1
    print(f"Sample composition by model: {model_counts}")


if __name__ == "__main__":
    main()
