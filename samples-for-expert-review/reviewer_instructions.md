# Reviewer Instructions — ReasonGuard M5 Expert Validation Batch

Batch date: 2026-08-31. Sample size: 50 explanation pairs, drawn from real local-LLM outputs (not synthetic), stratified across models.

1. Open `expert_review_batch_2026-08-31.csv`.
2. For each row, read `formal_bound_summary` (what is formally established) and `ai_explanation` (what the model said).
3. Fill in `expert_violation_class` using the definitions in `v1_v5_taxonomy_reference.md`, plus `expert_severity`, `expert_confidence_1to5`, and optional `expert_notes`.
4. Note: the formal bound schema is still the proxy schema (v2.1/v3.0-hmi), pending the official NES@FIT automaton output schema — please flag anything that reads as an artefact of the proxy schema rather than a genuine reasoning violation.
5. Return the completed CSV by email. Target turnaround: as fast as feasible — the student is finishing under a confirmed 15 September 2026 submission deadline.

Thank you for the independent review — it is what lets us report Cohen's Kappa between ReasonGuard and expert judgement in the thesis.
