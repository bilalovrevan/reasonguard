# Min et al. (2023) — FActScore

BibTeX: `Min2023FActScore`

Reference: Min, S. et al. (2023). FActScore: Fine-Grained Atomic Evaluation of Factual
Precision in Long Form Text Generation. *EMNLP 2023*.

## 1. Main argument
[FACTUAL EXTRACTION -- AI-assisted, from the arXiv abstract (2305.14251) and public
project material. Verify against the full paper before citing exact figures.]
Long-form generations typically mix supported and unsupported claims, so judging an
entire passage as simply "factual" or "not factual" loses information; the paper
argues evaluation must happen at the level of individual atomic facts. Human
evaluation of biography generations from InstructGPT, ChatGPT, and PerplexityAI found
even a strong system like ChatGPT is only about 58% factually precise under this
finer-grained scoring.

## 2. Methodology
[Same caveat as above.]
A generated passage is decomposed into atomic facts; each atomic fact is then
verified for support against a reliable knowledge source. This was first done via
costly human annotation, then automated with a retrieval-plus-strong-LM pipeline
that reaches under 2% error relative to human judgment -- making it feasible to
score at scale (6,500 generations across 13 models; the paper estimates this would
have cost ~$26K if done entirely by human annotators). Released as an installable
package (`pip install factscore`).

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
