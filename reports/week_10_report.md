# Week 10 Progress Report — ReasonGuard

Period: 24 May 2026 – 30 May 2026
Student: Ravan Bilalov
Phase: Phase 2 — LLM Explanation Pipeline (exposé weeks 5–12)

## 1. Planned for this week (per exposé)

The exposé week-10 block asks for "5 models × 5 event types × 100 samples = 2 500
explanation pairs, all runs logged in MLflow, and the beginning of the claim
extraction pipeline with spaCy NER plus a 50-sample extraction-accuracy check".

## 2. Delivered this week

- Added stratified sampling to `src/prompt_builder.py` via the
  `REASONGUARD_STRATIFY` environment variable, with `REASONGUARD_PER_EVENT_TYPE`
  controlling the bucket size. The sampler is reproducible (seeded by the
  pipeline `RANDOM_SEED`) and gracefully handles event types with fewer rows
  than requested.
- Added a configurable `REASONGUARD_PILOT_LIMIT` env var to
  `src/ollama_llm_runner.py` so longer pilot runs do not require a config edit.
- Generated a balanced 40-prompt batch covering all four observed proxy event
  types and ran it through both local Ollama models (llama3.1:8b-instruct-q4_0,
  phi3:mini) for 80 real-LLM responses.
- Built `src/event_analysis.py`, which computes a per-model × per-event-type
  violation breakdown and writes JSON, CSV, and markdown artefacts under
  `outputs/`.
- Built `src/evaluation_metrics.py` with per-class precision, recall, and F1, a
  confusion-matrix builder, and a Cohen's Kappa implementation, plus a unit
  test suite covering perfect agreement, no agreement, empty input, and
  per-class accounting.
- Extended `src/viz.py` with a confusion-matrix plotting helper that reads the
  evaluation_metrics JSON and writes `outputs/figures/confusion_matrix.png`.
- Built `src/cloud_llm_runner.py` as a thin urllib client for GPT-4o-mini and
  Gemini-1.5-Flash. The runner skips providers whose API keys are unset, so it
  is safe to import and run in the absence of secrets.
- Added a `test_prompt_builder.py` test suite covering stratified sampling and
  prompt-record construction, plus a `test_event_analysis.py` test suite for
  the per-event-type breakdown logic.
- Refreshed `meeting_pack/pipeline_stats.md` and the meeting CSV automatically
  via `src/prepare_meeting_pack.py`.

## 3. Honest gap vs the exposé week-10 target

- Target 2 500 explanation pairs; produced 80 real-LLM responses plus 200
  stratified synthetic responses. The remainder is a throughput problem on CPU
  inference, not an architectural one.
- spaCy `en_core_web_lg` download finished only after the Ollama batch
  completed; the per-claim three-state output is now exercised in the checker
  but the W10 report does not yet include the spaCy-only metrics.
- Cloud LLMs (GPT-4o-mini, Gemini-1.5-Flash) are wired but await API keys.
- Manual annotation of the 50-row batch is not yet filled in; the F1 and
  Kappa numbers in `outputs/evaluation_metrics.md` therefore depend on the
  annotator's pass.

## 4. Plan for week 11

1. Fill in the manual annotation batch (50 rows) and run
   `python -m src.evaluation_metrics` to produce the first F1 and Kappa
   numbers.
2. Extend the stratified pilot to 25 prompts per event type, producing 100
   prompts × 2 local models = 200 responses.
3. Add the cloud LLM run once API keys are available.
4. Begin writing the Chapter 4 "Experimental Setup" sections that reference the
   `event_type_analysis` and `evaluation_metrics` artefacts.
