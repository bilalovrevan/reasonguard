# Min et al. (2023) — FActScore

BibTeX: `Min2023FActScore`

Reference: Min, S. et al. (2023). FActScore: Fine-Grained Atomic Evaluation of Factual
Precision in Long Form Text Generation. *EMNLP 2023*.

## 1. Main argument
[State that long-form text generation requires evaluation at the level of atomic
facts and not at the level of entire passages.]

## 2. Methodology
[Describe the atomic-fact decomposition pipeline, the verification step against a
knowledge base, and the human-evaluation methodology used to validate the metric.]

## 3. Direct relevance to ReasonGuard
This is the closest methodology to the claim-extraction step in ReasonGuard. Note:
- The decomposition of an explanation into atomic claims.
- The per-claim verification against a reference.
- The aggregation of per-claim verdicts into a passage-level score.

The crucial methodological adaptation in ReasonGuard is that the reference is a
formally verified detector output (a bound) rather than a knowledge base, and the
verification is performed at runtime rather than as offline scoring.

## 4. Gap addressed by this thesis
[FActScore evaluates the offline quality of an output. ReasonGuard adds the runtime
monitoring viewpoint and the V1–V5 taxonomy that allows the reporting of why an
explanation is unfaithful, not just how unfaithful it is.]

## 5. Quotations and figures worth referencing
[Note the figures that show the claim-decomposition pipeline; these can be cited in
Chapter~\ref{ch:framework}.]
