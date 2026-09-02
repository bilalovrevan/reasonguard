# Holík, Matoušek, Ryšavý & Vojnar (2023)

BibTeX: `HolikMatousekRysavyVojnar2023`

Reference: Holík, L., Matoušek, P., Ryšavý, O., & Vojnar, T. (2023). Accurate
Automata-Based Detection of Cyber Threats in Smart Grid Communication. *IEEE
Transactions on Smart Grid*, 15(1).

## 1. Main argument
[FACTUAL EXTRACTION -- AI-assisted, from the public abstract (fit.vut.cz), not yet
verified by Ravan against the full IEEE Xplore text. Verify before citing, then
replace this note with your own reading.]
The paper proposes a new ICS anomaly-detection approach based on Deterministic
Probabilistic Automata (DPAs) that capture the intended *semantics* of ICS message
exchange, rather than surface-level packet attributes. It improves an earlier
automata-based method's detection performance and reduces its false-positive rate,
and adds a technique for producing detailed, human-readable explanations of each
detected anomaly -- explicitly motivated by real-world deployment needs. Demonstrated
on IEC 104 and MMS traffic from several ICS systems.

## 2. Methodology
[Same caveat as above -- abstract-level extraction only.]
A set of DPAs models the expected/legitimate message-sequence patterns per protocol
(normal traffic). Detection reasons about deviation from these automata: an
"unexpected ICS message" relative to the learned model is flagged as anomalous.
Evaluation used real IEC 104 / MMS communication captured from different ICS
systems, measured on detection performance and false-positive rate; the paper's
added contribution is the explanation-generation technique layered on top of the
automaton verdict.

## 3. Direct relevance to ReasonGuard
This is the paper whose formal automaton output ReasonGuard directly uses as the
verified bound. Note specifically:
- The output fields that should appear in the bound schema (after the proxy phase).
- The event classes that are formally distinguished.
- The confidence or scoring mechanism, if any, attached to the verdict.

## 4. Gap addressed by this thesis
[Describe what the paper does not address: the consumption of the formal output by an
AI explanation layer. ReasonGuard addresses the verification of an explanation against
the formal output, which is outside the scope of this paper.]

## 5. Quotations and figures worth referencing
[Note specific quotations and figures that may be reproduced in
Chapter~\ref{ch:related-work} or Chapter~\ref{ch:framework}.]
