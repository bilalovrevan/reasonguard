# Week 13 Progress Report — ReasonGuard (forward plan)

Period: 14 June 2026 – 20 June 2026
Student: Ravan Bilalov
Phase: Phase 2 close-out → Phase 3 open
Milestone window: leading into M4 (week 14)

## 1. Planned for this week (per exposé)

The exposé week-13 block opens the M4 milestone preparation:

> Manually annotate 200 explanation pairs for ground truth violation class
> (V1–V5 or NONE). Calculate ReasonGuard F1 per violation class on annotated
> set. Iterate extraction and classification logic until F1 > 0.80.
> Send 50 samples to VUT Brno domain expert at M5.

## 2. Concrete deliverables for this week

1. Complete the annotation of the 50-row pilot batch
   (`annotation/annotation_batch.csv`).
2. Run `python -m src.evaluation_metrics` and inspect the per-class F1 numbers.
3. If F1 < 0.80 for any V class, iterate the rule-based detector. Each
   iteration is tracked as an MLflow run under
   `MLFLOW_EXPERIMENT_CHECKER` and committed under its own tag.
4. Expand the annotation set to 200 rows by sampling additional stratified
   responses (50 per model where possible).
5. Package 50 explanation pairs for the VUT Brno domain expert at M4. The
   package includes: prompts, formal bounds, machine verdicts, and a short
   instruction document.
6. Begin filling in the thesis Section~\ref{sec:results-detector} (per-class
   precision, recall, F1, confusion matrix) with the actual numbers.

## 3. Definition of done for week 13

- 200 manually annotated rows in `annotation/annotation_results.csv`.
- `outputs/evaluation_metrics.json` exists with at least 200 sample count
  and macro F1 reported.
- A `samples-for-expert-review/` directory exists with the 50-row package
  prepared for VUT Brno.
- The W13 meeting pack includes the F1 numbers and the package summary.
