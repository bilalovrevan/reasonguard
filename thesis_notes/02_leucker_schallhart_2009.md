# Leucker & Schallhart (2009)

BibTeX: `LeuckerSchallhart2009RuntimeVerification`

Reference: Leucker, M. & Schallhart, C. (2009). A Brief Account of Runtime
Verification. *Journal of Logic and Algebraic Programming*, 78(5), 293–303.

## 1. Main argument
[FACTUAL EXTRACTION -- AI-assisted. I could not retrieve the full paywalled text
(ScienceDirect blocked automated fetch); this is based on the paper's well-established
public description as a foundational RV survey, not a direct read of the PDF. Verify
the exact wording against the actual paper before citing.]
Runtime verification (RV) is defined as a lightweight formal-methods discipline that
checks whether a single (typically finite) execution trace of a running system
satisfies a formal specification. This sits between two more extreme approaches:
exhaustive static verification / model checking (reasons over *all* possible
executions of a model, but does not scale to real deployed systems) and testing
(observes real executions, but without a formal specification or completeness
guarantee). A monitor, synthesized automatically from the specification, evaluates
the trace incrementally.

## 2. Methodology
[Same caveat as above.]
Surveys monitor-synthesis techniques from temporal-logic-style specifications and
discusses the safety/liveness distinction specifically in the finite-trace setting:
a safety violation can be conclusively detected from a finite prefix, but a liveness
property generally cannot be conclusively verified or falsified from a finite trace
alone. Reviews trace-based semantics and practical monitor-implementation
approaches.

## 3. Direct relevance to ReasonGuard
ReasonGuard treats the formal verdict as the runtime monitor specification and the AI
explanation as the execution to be checked. Use this paper to ground:
- The notion of a runtime monitor that is independent of the system under check.
- The definition of a violation as a finite witness against a property.
- The fact that runtime verification accepts that some properties are only checkable
  on the prefix observed so far.

## 4. Gap addressed by this thesis
[The paper considers properties of system executions in the formal-methods sense. The
thesis extends this viewpoint to AI reasoning faithfulness against a formal bound,
which is not considered in the original runtime-verification literature.]

## 5. Quotations and figures worth referencing
[Note the definitions and the running examples that translate cleanly to the
explanation-verification setting.]
