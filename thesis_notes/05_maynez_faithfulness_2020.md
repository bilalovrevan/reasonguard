# Maynez et al. (2020) — Faithfulness

BibTeX: `Maynez2020Faithfulness`

Reference: Maynez, J. et al. (2020). On Faithfulness and Factuality in Abstractive
Summarization. *ACL 2020*.

## 1. Main argument
[FACTUAL EXTRACTION -- AI-assisted, from the arXiv abstract (2005.00661) only; the
precise faithfulness-vs-factuality definitions and the hallucination taxonomy could
not be retrieved from the accessible abstract text -- these need to come from your
own read of the full ACL paper, not from this note.]
Neural abstractive summarization models frequently hallucinate content unsupported
by the source document. Across the systems tested, pretrained models produced
summaries that were better not only by ROUGE but also more faithful/factual than
non-pretrained models.

## 2. Methodology
[Confirmed from the abstract: large-scale human evaluation was used to characterise
hallucinations across systems, and the paper reports that textual-entailment-based
metrics correlate better with human faithfulness judgments than standard overlap
metrics like ROUGE. The specific annotation protocol and taxonomy categories are
NOT filled in here -- read the full paper for those, since they matter for how you
frame ReasonGuard's own three-state claim classifier in Chapter 2/3.]

## 3. Direct relevance to ReasonGuard
This paper defines the faithfulness problem that ReasonGuard addresses in a different
domain. Note:
- The hallucination taxonomy, which informs the design of the V1–V5 taxonomy.
- The argument that faithfulness is a separate axis from factuality.

## 4. Gap addressed by this thesis
[Maynez et al. studies faithfulness against a free-text source document. ReasonGuard
studies faithfulness against a formally verified machine-readable bound, which makes
the verification deterministic and operationally actionable.]

## 5. Quotations and figures worth referencing
[Note the hallucination examples and the taxonomy diagram; cite these in
Chapter~\ref{ch:related-work}.]
