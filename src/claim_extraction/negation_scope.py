"""Detect whether forbidden terms appear inside a negation scope.

The lexicon-based V1 detector flags any forbidden term unless the surrounding
text matches a hand-curated safe-negation pattern. Multi-clause negation
(e.g. ``"is a proxy observation label, not a confirmed attack label"``)
is hard to cover with substring patterns, so this module uses spaCy's
dependency parser to walk the token tree and determine whether each
occurrence of a forbidden term is governed by a negation marker.

The check is intentionally conservative: it only marks a term as safe when
the parser can connect it to a negation token or to a descriptive marker
("proxy", "label", "schema", "observation") within the same sentence.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


NEGATION_TOKENS = {"not", "no", "never", "neither", "nor", "without"}
DESCRIPTIVE_MARKERS = {"proxy", "schema"}


@dataclass
class NegationVerdict:
    term: str
    is_negated: bool
    reason: str


def _sentence_contains_marker(sentence_tokens, markers: Iterable[str]) -> bool:
    sentence_text_lower = {token.text.lower() for token in sentence_tokens}
    return any(marker in sentence_text_lower for marker in markers)


def _token_has_negation_in_path(token) -> bool:
    """Check if any ancestor of the token has a child with a ``neg`` dependency."""

    visited = set()
    current = token

    while current is not None and current.i not in visited:
        visited.add(current.i)

        for child in current.children:
            if child.dep_ == "neg":
                return True

            if child.text.lower() in NEGATION_TOKENS:
                return True

        if current.head is current:
            break

        current = current.head

    return False


def is_term_negated_in_doc(doc, term: str) -> NegationVerdict:
    """Return a verdict for whether the given term is negated in the spaCy doc.

    The term is matched case-insensitively against full tokens. The first match
    that is not negated triggers an unsafe verdict; otherwise the term is safe.
    """

    term_lower = term.lower()
    any_match = False

    for token in doc:
        if token.text.lower() != term_lower:
            continue

        any_match = True

        if _token_has_negation_in_path(token):
            continue

        sentence = token.sent

        if _sentence_contains_marker(sentence, DESCRIPTIVE_MARKERS):
            continue

        return NegationVerdict(term=term, is_negated=False, reason="unsafe_usage")

    if not any_match:
        return NegationVerdict(term=term, is_negated=False, reason="term_absent")

    return NegationVerdict(term=term, is_negated=True, reason="all_occurrences_negated")


def filter_unsafe_terms(doc, terms: Iterable[str]) -> list[str]:
    """Return only the subset of terms that are NOT safely negated in the document."""

    unsafe = []

    for term in terms:
        verdict = is_term_negated_in_doc(doc, term)

        if verdict.reason == "unsafe_usage":
            unsafe.append(term)

    return unsafe
