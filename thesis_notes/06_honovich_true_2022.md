# Honovich et al. (2022) — TRUE

BibTeX: `Honovich2022True`

Reference: Honovich, O. et al. (2022). TRUE: Re-Evaluating Factual Consistency
Evaluation. *NAACL 2022*.

## 1. Main argument
[FACTUAL EXTRACTION -- AI-assisted, from the arXiv abstract (2204.04991). Verify
against the full NAACL paper before citing.]
Prior factual-consistency metrics were developed and evaluated in isolation, one
task/dataset at a time, fragmenting progress; existing meta-evaluation also only
measured system-level correlation with human judgment, leaving example-level
accuracy of these metrics unclear. TRUE unifies evaluation across 11 existing
datasets that carry manual factual-consistency annotations.

## 2. Methodology
[Same caveat as above.]
Consolidates 11 benchmarks under one evaluation protocol and introduces an
example-level (not just system-level) meta-evaluation approach. Benchmarking a range
of metric families found that large-scale NLI-based metrics and question-generation-
and-answering-based metrics achieve the strongest and mutually complementary results,
recommended as the starting point for anyone building a new factual-consistency
metric -- directly relevant to how ReasonGuard's own claim-verification approach
should be framed and compared in Chapter 2.

## 3. Direct relevance to ReasonGuard
This is the evaluation methodology reference. Use to:
- Justify the evaluation protocol in Chapter~\ref{ch:experimental-setup}.
- Frame the precision-recall-$F_1$ reporting in Section~\ref{sec:results-detector}.

## 4. Gap addressed by this thesis
[TRUE evaluates how well a factual-consistency model scores a passage. ReasonGuard
adds the explicit violation classification that goes beyond a single consistency
score.]

## 5. Quotations and figures worth referencing
[Note the consolidated benchmark table and the per-metric performance plots.]
