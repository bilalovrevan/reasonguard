# de Silva et al. (2014)

BibTeX: `DeSilva2014FormalReachability`

Reference: de Silva, G. et al. (2014). On Formal Reachability Analysis in Networks
with Dynamic Behavior. *Telecommunication Systems*, 57(4).

## 1. Main argument
[FACTUAL EXTRACTION -- AI-assisted, from the public Springer abstract only; the full
text is paywalled and was not accessible. Verify against the full PDF before citing
precise claims.]
Proposes a method to efficiently check reachability properties in networks whose
routing/topology changes dynamically over time, avoiding the exponential cost of
enumerating every possible concrete network state.

## 2. Methodology
[Same caveat -- abstract only, full soundness proof and case studies were not
accessible.]
Rather than enumerating states directly, the method enumerates available paths and,
for each path, searches for a "state aggregation" -- a group of concrete network
states, each defined by a combination of link-availability conditions, in which that
path is active. This aggregation is the abstraction that keeps the analysis
tractable. The soundness argument and the specific case-study results sit behind
the paywall; flag to the first supervisor if the exact experimental numbers are
needed for Chapter 2/3, or source the PDF through the university library.

## 3. Direct relevance to ReasonGuard
First-supervisor reference. Use to:
- Provide a precedent for the consumption of formal analysis output in a downstream
  decision.
- Motivate the structured-output viewpoint adopted by the bound schema.

## 4. Gap addressed by this thesis
[The paper outputs a formal analysis result. ReasonGuard adds an explanation
verification layer on top, which is not part of the original paper.]

## 5. Quotations and figures worth referencing
[Note quotations that frame the formal-methods tradition in which the supervisor
operates.]
