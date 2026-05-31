# Week 11 Progress Report — ReasonGuard (forward plan)

Period: 31 May 2026 – 6 June 2026
Student: Ravan Bilalov
Phase: Phase 2 — LLM Explanation Pipeline (exposé weeks 5–12)

## 1. Planned for this week (per exposé)

The exposé week-11 block opens the W11–12 "Build" phase:

> Build bound comparison engine: for each extracted claim, compare against JSON
> formal bound — output SUPPORTED / UNSUPPORTED / CONTRADICTED per claim. Build
> V1–V5 violation classifier from claim patterns using rule-based logic.
> Internal test: manually verify 50 classifier outputs against own judgement.

## 2. What is already in place from week 10

- The three-state classifier (`src/claim_extraction/three_state_classifier.py`)
  is implemented and unit-tested.
- The V1–V5 rule-based classifier is mature; the W9 detector refinement reduced
  false positives on real local-LLM outputs.
- The 50-row manual annotation batch (`annotation/annotation_batch.csv`) is
  ready to be filled in.
- `src/evaluation_metrics.py` will compute the F1 and Cohen's Kappa numbers
  once the annotation batch is returned.

## 3. Concrete deliverables for this week

1. Complete the manual annotation of the 50 sampled responses.
2. Run `python -m src.evaluation_metrics` to produce
   `outputs/evaluation_metrics.json`, the markdown report, and the confusion
   matrix plot.
3. Regenerate the per-model per-event-type breakdown
   (`python -m src.event_analysis`).
4. If F1 < 0.80 for any V class, audit the failing rows and refine the
   classifier; otherwise hold the current detector and move on to volume.
5. Run the 25-per-event-type pilot (100 prompts × 2 local models = 200
   responses). Re-run the checker and refresh all figures.
6. If cloud API keys are available, run a matching 100-prompt pilot on
   GPT-4o-mini and Gemini-1.5-Flash.
7. Draft the Chapter 4 "Experimental Setup" sub-sections that describe the
   stratified sampling, the prompt design, and the evaluation protocol.

## 4. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Manual annotation takes longer than two days | Annotate in two passes: a first quick V1-V5/NONE pass and a slower severity pass; this front-loads the F1 numbers. |
| Multi-model batch slow on CPU (~30 minutes per 100 prompts × 2 models) | Run the batch overnight; stage the work so each evening fires the next batch. |
| F1 below 0.80 for some classes | Audit the failing pairs with the first supervisor; iterate the rule-based detector before scaling further. |

## 5. Definition of done for week 11

- `outputs/evaluation_metrics.json` exists with `sample_count >= 50` and
  `cohens_kappa >= 0.5` as a starting baseline.
- `outputs/event_type_analysis.json` covers at least two models and four event
  types.
- The week-11 meeting pack contains the per-class F1 and Kappa numbers.
