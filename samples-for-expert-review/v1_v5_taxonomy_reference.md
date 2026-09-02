# ReasonGuard V1-V5 Reasoning Violation Taxonomy — Reviewer Reference

For each sample, read the formal bound (the facts the system actually established) and the AI explanation, then judge which class (if any) applies.

- **NONE** — the explanation stays within the formal bound; no violation.
- **V1 Fabricated Reasoning** — the AI asserts facts, causes, or entities not present in or derivable from the formal bound.
- **V2 Contradicted Reasoning** — the AI explicitly contradicts a fact established by the formal bound.
- **V3 Over-Generalised Reasoning** — the AI produces a correct category but loses formally established specifics, reducing actionability.
- **V4 Under-Specified Reasoning** — the AI omits formally established information that is operationally required for a correct response.
- **V5 Incoherent Reasoning** — the AI explanation is internally self-contradictory, independent of the formal bound.

Please assign exactly one class per sample (the single most severe violation present, or NONE), a severity (none/low/medium/high), your confidence (1-5), and any free-text notes. You are not shown ReasonGuard's own automated verdict — this is intentional, so your assessment is independent and can be compared against it (Cohen's Kappa).
