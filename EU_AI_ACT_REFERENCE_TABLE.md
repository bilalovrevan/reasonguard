# EU AI Act factual reference table — for Chapter 6 (Discussion), §EU AI Act mapping

Prepared by Claude, 2 Sep 2026, per the offer in `REWRITE_GUIDE_ch2_3_6_7.md`. This
is factual legal material only (article text summaries + citation), not
interpretation — connecting each requirement to what ReasonGuard actually does
or doesn't satisfy is the argument you need to write yourself in Chapter 6.

Source: Regulation (EU) 2024/1689 ("the AI Act"), summarized via
artificialintelligenceact.eu (a widely-used AI Act reference maintained by the
Future of Life Institute) and cross-checked for title/date against the
official EUR-Lex record. **Before you finalize the chapter, verify the exact
paragraph wording against the Official Journal text on EUR-Lex
(CELEX:32024R1689)** — the consolidated version has been amended since 2024
(the current consolidated text on EUR-Lex is dated 27 July 2026), so double-check
you're citing anything you quote verbatim from the version in force. A ready-to-cite
BibTeX entry (`EUAIAct2024`) has already been added to `thesis/references.bib`.

## Article 6(2) + Annex III — does ReasonGuard fall in "high-risk" scope?

Annex III lists eight categories of high-risk AI systems. The one relevant to
ReasonGuard's ICS/smart-grid setting is:

> **Annex III, point 2 — Critical infrastructure.** AI systems intended to be
> used as a safety component in the management and operation of critical
> digital infrastructure, road traffic, or the supply of water, gas, heating,
> or electricity.

**Question for your own argument:** ReasonGuard is a *verification/explanation
layer* that checks whether an LLM's explanation of network traffic stays
within a formally verified bound — it does not itself manage or operate the
grid, and (per your own architecture in Chapter 3) it does not gate or block
actions. Does that put it outside Annex III point 2's "safety component"
language, or does flagging faithfulness violations in explanations *about*
critical-infrastructure traffic still count as a safety-relevant function once
a human analyst starts acting on ReasonGuard's verdicts? This is exactly the
kind of boundary case worth stating explicitly rather than assuming either way.

## Article 13 — Transparency and provision of information to deployers

Applies to providers of high-risk AI systems. Key obligations:

1. **§1 (design-level):** the system must be "designed and developed in such a
   way as to ensure that their operation is sufficiently transparent to enable
   deployers to interpret the system's output and use it appropriately."
2. **§2–3 (instructions for use):** accompanying documentation must be
   concise, complete, correct, and clear, and must include (among other
   items): intended purpose, accuracy/robustness/cybersecurity metrics and how
   they were measured, known limitations, human-oversight measures (Art. 14),
   and — closest to ReasonGuard's own subject matter — information "relevant
   to interpret the output" of the system.

**Where this maps onto your results (facts, not argument):** your own
per-class precision/recall table (`outputs/evaluation_metrics.md`) is exactly
the kind of "accuracy metrics" Article 13 asks a provider to disclose — a
detector with 0.90 precision / 0.09 recall on V1 and 0.48 precision / 0.92
recall on V4 is not equally reliable across classes, and Article 13 would
require that asymmetry to be disclosed to a deployer, not averaged away into a
single headline F1. Your own argument to make: does ReasonGuard's honest
per-class reporting in Chapter 5 model what Article 13 compliance would
actually look like for this kind of tool, or does it show how easy it would be
for a provider to under-disclose by reporting only macro-F1?

## Article 17 — Quality management system

Applies to providers of high-risk AI systems; requires a documented QMS
covering (among 13 listed elements, (a)–(m)): a regulatory-compliance
strategy, design/development/testing procedures with stated frequency,
technical specifications applied, a data-management system (acquisition,
labelling, storage, retention), integration of the Article 9 risk-management
system, post-market monitoring (Art. 72), serious-incident reporting (Art.
73), and record-keeping.

**Where this maps onto your own project (facts, not argument):**
- Your `AI_ADDENDUM.md` disclosure log and this repository's git history are,
  informally, the kind of "record-keeping of all relevant documentation" (Art.
  17(1)(k)) a QMS would require.
- Your manual annotation protocol (`src/annotate_cli.py`,
  `src/evaluation_metrics.py`) is a testing/validation procedure in the sense
  of Art. 17(1)(d), but it is a one-time academic evaluation, not the
  continuous "post-market monitoring" Art. 17(1)(h) requires of a deployed
  product — a real gap between a thesis prototype and a compliant product,
  worth naming plainly rather than implying ReasonGuard is production-ready.
- The known V4 over-triggering issue (documented in `AI_ADDENDUM.md` and
  Chapter 5) is precisely the kind of finding a real QMS's post-market
  monitoring loop (Art. 17(1)(h), Art. 72) would be designed to catch and feed
  back into a fix — you already have the raw material to argue this
  constructively rather than defensively.

## Suggested structure for your own §EU AI Act mapping subsection

This is a structural suggestion only — the actual sentences are yours:

1. State which Annex III category is arguably relevant and why (or why not).
2. Walk through Article 13's disclosure requirements against what your own
   Chapter 5 results table actually shows — is per-class transparency
   present or absent in how these systems are typically evaluated/reported?
3. Walk through Article 17's QMS elements against what a thesis-scale
   evaluation can and cannot demonstrate (be honest about the gap between
   "we tested this once" and "we monitor this continuously").
4. Close with your own claim: what would have to change about ReasonGuard
   (or about how it's evaluated) for it to plausibly support Article 13/17
   compliance for a deployer, versus what it can only gesture at today.
