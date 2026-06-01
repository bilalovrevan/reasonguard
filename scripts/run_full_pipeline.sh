#!/usr/bin/env bash
# Run the ReasonGuard pipeline end to end.
#
# Usage:
#   scripts/run_full_pipeline.sh [PER_EVENT_TYPE]
#
# PER_EVENT_TYPE defaults to 25 (100 prompts across the 4 observed proxy
# event types). Override the local-model list with:
#   REASONGUARD_OLLAMA_MODELS="llama3.1:8b-instruct-q4_0,phi3:mini" ./scripts/run_full_pipeline.sh
#
# The script is idempotent: each stage writes to a fixed path under outputs/
# and re-running overwrites the previous artefact. The script does not run
# the cloud LLM stage unless OPENAI_API_KEY or GEMINI_API_KEY is set.

set -euo pipefail

PER_EVENT_TYPE="${1:-25}"

REASONGUARD_STRATIFY=1 REASONGUARD_PER_EVENT_TYPE="$PER_EVENT_TYPE" \
  python -m src.formal_bound_builder

REASONGUARD_STRATIFY=1 REASONGUARD_PER_EVENT_TYPE="$PER_EVENT_TYPE" \
  python -m src.prompt_builder

python -m src.synthetic_response_generator

python -m src.ollama_llm_runner

if [[ -n "${OPENAI_API_KEY:-}" || -n "${GEMINI_API_KEY:-}" ]]; then
    python -m src.cloud_llm_runner
fi

python -m src.merge_ollama_responses

python -m src.reason_guard_checker

python -m src.event_analysis

python -m src.viz

if [[ -f annotation/annotation_results.csv ]]; then
    python -m src.evaluation_metrics
fi

python -m src.prepare_meeting_pack
python -m src.status_cli
