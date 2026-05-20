# Leucker & Schallhart (2009)

BibTeX: `LeuckerSchallhart2009RuntimeVerification`

Reference: Leucker, M. & Schallhart, C. (2009). A Brief Account of Runtime
Verification. *Journal of Logic and Algebraic Programming*, 78(5), 293–303.

## 1. Main argument
[State the formal definition of runtime verification and the distinction it draws
from static verification and from testing.]

## 2. Methodology
[Describe the monitor specification formalism, the safety/liveness distinction, and
the categories of properties that can be checked at run time.]

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
