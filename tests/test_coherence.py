"""Tests for the sentence-level V5 coherence detector."""

from __future__ import annotations

import pytest

spacy = pytest.importorskip("spacy")

try:
    _NLP = spacy.load("en_core_web_lg")
except OSError:
    _NLP = None


pytestmark = pytest.mark.skipif(_NLP is None, reason="en_core_web_lg not installed")


from src.claim_extraction.coherence import find_incoherent_sentences  # noqa: E402


def test_conflicting_terms_in_same_sentence_are_flagged():
    doc = _NLP(
        "The event is normal traffic and also a malicious attack at the same time."
    )

    findings = find_incoherent_sentences(doc)

    assert len(findings) >= 1
    flagged_pairs = {(f.left_term, f.right_term) for f in findings}
    assert any(left == "normal" and right == "malicious" for left, right in flagged_pairs)


def test_conflict_under_negation_is_safe():
    doc = _NLP(
        "The bound does not confirm maliciousness or normality based on the available "
        "observation."
    )

    findings = find_incoherent_sentences(doc)

    assert findings == []


def test_terms_in_different_sentences_are_safe():
    doc = _NLP(
        "Source 1 communicated with destination 2 over the iec104 protocol. "
        "The proxy formal class does not assert that the traffic is malicious."
    )

    findings = find_incoherent_sentences(doc)

    assert findings == []


def test_direction_conflict_is_flagged():
    doc = _NLP(
        "The communication is both client-to-server and server-to-client at the same "
        "moment."
    )

    findings = find_incoherent_sentences(doc)

    assert any(
        f.left_term == "client-to-server" and f.right_term == "server-to-client"
        for f in findings
    )
