# Week 9 Progress Report — ReasonGuard

Period: 18 May 2026 – 23 May 2026
Student: Ravan Bilalov
Phase: Phase 2 — LLM Explanation Pipeline (exposé weeks 5–12)

## 1. Planned for this week (per exposé)

The exposé places week 9 inside the "Scale to full evaluation: 5 models × 5 event types
× 100 samples = 2 500 explanation pairs. All runs logged in MLflow. Begin claim
extraction pipeline: spaCy NER on LLM outputs" block.

## 2. Delivered this week

- Closed the end-to-end pipeline from raw IEC-104 rows to V1–V5 violation reports.
- Generated 20 000 formal bounds and 100 prompt records from `sample_003.csv`.
- Produced 500 adversarial synthetic responses covering clean output and the four
  primary violation patterns (V1, V2, V3, V4) plus the V5 incoherence case.
- Ran the first real local-LLM pilot via Ollama on `phi3:mini` (20 responses).
- Implemented the V1–V5 detector with severity classification (high / medium / low /
  none).
- Cleaned the repository: archived eight legacy v1/v2 prototypes and six root-level
  duplicates of `src/` modules into `archive/`.
- Added `requirements.txt`, `pyproject.toml`, and a project-level `README.md`.
- Wrote the week-9 meeting pack and the updated three-minute talking points.

## 3. Honest gap vs the exposé week-9 target

- Five ICS event types are not yet covered. Only IEC-104 is in the pipeline.
- Real-LLM volume is 20, not 2 000+.
- MLflow tracking is not wired.
- spaCy NER claim extraction is not implemented; the current detector uses curated
  keyword and regular-expression rules.
- The schema is still the proxy schema, not the official NES@FIT automaton schema.

## 4. Risks and mitigations

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Official automaton schema unavailable for several more weeks | Bound layer cannot move beyond proxy until then | Keep proxy schema clearly labelled; design the upgrade path during week 10 so swap is a refactor, not a rewrite |
| Local LLM inference too slow on CPU to reach 2 500 responses by week 12 | Schedule slip on M3 (week 10) | Stage the runs (500 in week 10, 1 000 in week 11, balance in week 12); enable response caching keyed on prompt hash |
| spaCy NER produces low recall on ICS-specific entities | F1 stays below 0.80 | Add a domain-tuned `EntityRuler` with explicit ICS entity patterns before relying on the statistical model |
| Cloud API budget overshoot | Cost > €25 | Track per-run token usage in MLflow from day one; cap per model per event type at 100 samples |

## 5. Plan for week 10 (24 May 2026 – 30 May 2026)

1. Build the multi-event dataset parser that maps raw rows to the five event types
   defined in the exposé.
2. Refactor `reason_guard_checker.py` so that the lexicon-based pre-filter is followed
   by a spaCy pipeline with a custom `EntityRuler` for ICS entities.
3. Wire MLflow tracking around `synthetic_response_generator`, `ollama_llm_runner`, and
   `reason_guard_checker` (one experiment per stage).
4. Extend `ollama_llm_runner` to iterate over three local models
   (`llama-3-8b-instruct`, `mistral-7b-v0.3-instruct`, `phi-4-mini-instruct`).
5. Generate the first 500 real-LLM responses (3 models × 5 event types × ~33 samples).
6. Begin the Overleaf thesis skeleton: Chapter 1 introduction and Chapter 2 related
   work outline.

## 6. Questions for the supervisor assistant on 21 May 2026

1. Is the proxy schema acceptable as the interim bound until the official automaton
   schema is documented?
2. Which mandatory fields should the official-schema upgrade introduce?
3. Which dataset path is recommended for the multi-event parser?
4. Is the three-model Ollama plan (Llama-3-8B, Mistral-7B, Phi-4-mini) acceptable for
   week 10, with the two cloud models added in week 11?
5. Is a custom `EntityRuler` with ICS entity patterns acceptable instead of training a
   bespoke NER model?
