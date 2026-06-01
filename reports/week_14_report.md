# Week 14 Progress Report — ReasonGuard (forward plan, M4 milestone)

Period: 21 June 2026 – 27 June 2026
Student: Ravan Bilalov
Milestone: M4 — Classifier
Required deliverables: ReasonGuard classifier F1 scores on the 200 annotated
pairs and the 50-sample package sent to VUT Brno.

## 1. Planned for this week (per exposé)

> M4 — Classifier (week 14)
> Student submits: ReasonGuard classifier F1 scores on 200 annotated pairs
> + 50-sample package sent to VUT Brno.
> First supervisor: review F1 results. If < 0.80: redesign session.
> VUT Brno: receive and independently assess 50 explanation pairs. Return
> violation class labels within 10 working days.

## 2. Concrete deliverables

1. Finalise the 200-pair annotation. Confirm inter-annotator consistency by
   double-labelling 20 rows and running
   `python -m src.evaluation_metrics --report` to inspect the agreement.
2. Submit `outputs/evaluation_metrics.json` and the markdown report to the
   first supervisor at the M4 milestone.
3. Send the 50-sample package to VUT Brno. The package is reproducible from
   `samples-for-expert-review/`; it is uploaded as a single zip to the shared
   drive together with the bound schema version that was active when the
   pairs were produced.
4. Tag the M4 freeze in git as `m4-classifier-w14` so the F1 numbers in the
   thesis can be reproduced from a specific commit.
5. Continue extending the Chapter~\ref{ch:results} draft.

## 3. Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| F1 < 0.80 on any V class | Hold the M4 submission; iterate on the rule-based detector; resubmit before the M5 deadline at week 15. |
| VUT Brno cannot return labels within 10 working days | Use the M4 labelled subset for the first $\kappa$ estimate; carry the remaining labels into a follow-up batch. |
| Annotator fatigue at 200 rows | Split into 4 sessions of 50 rows each; alternate with thesis-writing days. |

## 4. Outputs at the end of week 14

| Artefact | Path |
| --- | --- |
| 200-row annotation | `annotation/annotation_results.csv` |
| Evaluation metrics report | `outputs/evaluation_metrics.json` + `.md` |
| Confusion matrix figure | `outputs/figures/confusion_matrix.png` |
| Sample package for VUT | `samples-for-expert-review/m4_batch_2026-06-26.zip` |
| Git tag | `m4-classifier-w14` |

## 5. Definition of done

- M4 submission acknowledged by the first supervisor.
- VUT Brno confirms receipt of the 50-sample package and the start of the
  10-working-day window.
- The W14 meeting pack contains the per-class F1 numbers and links to the
  artefacts above.
