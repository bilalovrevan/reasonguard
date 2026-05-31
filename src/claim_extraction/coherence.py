"""Sentence-level coherence checks for V5 (incoherent reasoning) detection.

The substring-based V5 detector flags conflicting term pairs anywhere in the
text. That produces false positives whenever an LLM uses both members of a
canonical opposite pair in clearly separate, well-scoped clauses
(for example *"the bound does not confirm maliciousness or normality"*).

This module uses spaCy's sentence segmentation to constrain the contradiction
check to within a single sentence, so opposites are flagged only when they
appear together in an assertion that the model itself is making.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from src.claim_extraction.negation_scope import NEGATION_TOKENS


CONFLICTING_PAIRS: list[tuple[str, str]] = [
    ("normal", "malicious"),
    ("normal", "attack"),
    ("benign", "malicious"),
    ("routine", "attack"),
    ("isolated", "entire network"),
    ("single device", "entire network"),
    ("client-to-server", "server-to-client"),
    ("client to server", "server to client"),
    ("client_to_server", "server_to_client"),
]


@dataclass
class IncoherenceFinding:
    sentence: str
    left_term: str
    right_term: str


def _sentence_text(sentence) -> str:
    return sentence.text.strip().lower()


def _sentence_has_negation(sentence) -> bool:
    tokens = {token.text.lower() for token in sentence}
    return bool(tokens & NEGATION_TOKENS)


def find_incoherent_sentences(
    doc,
    pairs: Iterable[tuple[str, str]] | None = None,
) -> list[IncoherenceFinding]:
    """Return findings where both members of a conflicting pair appear in the same
    sentence and that sentence does not contain a negation marker.

    Negated sentences (for example *"the bound does not confirm normality or
    maliciousness"*) are deliberately skipped because the apparent contradiction
    is framed under negation and therefore does not represent a model claim.
    """

    findings: list[IncoherenceFinding] = []
    target_pairs = list(pairs) if pairs is not None else CONFLICTING_PAIRS

    for sentence in doc.sents:
        if _sentence_has_negation(sentence):
            continue

        text = _sentence_text(sentence)

        for left, right in target_pairs:
            if left in text and right in text:
                findings.append(
                    IncoherenceFinding(
                        sentence=sentence.text.strip(),
                        left_term=left,
                        right_term=right,
                    )
                )

    return findings
