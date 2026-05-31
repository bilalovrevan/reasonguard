"""Tests for the spaCy dependency-parse-based negation scope detector.

These tests load the real spaCy model, so they are skipped when the model is
not installed. The CI environment is expected to install spacy and the
``en_core_web_lg`` model.
"""

from __future__ import annotations

import pytest

spacy = pytest.importorskip("spacy")

try:
    _NLP = spacy.load("en_core_web_lg")
except OSError:
    _NLP = None


pytestmark = pytest.mark.skipif(_NLP is None, reason="en_core_web_lg not installed")


from src.claim_extraction.negation_scope import (
    filter_unsafe_terms,
    is_term_negated_in_doc,
)


def test_attack_in_proxy_label_phrase_is_safe():
    doc = _NLP(
        "The current formal class is a proxy observation label, not a confirmed "
        "attack label."
    )
    verdict = is_term_negated_in_doc(doc, "attack")
    assert verdict.is_negated is True


def test_attack_in_descriptive_sentence_is_safe():
    doc = _NLP(
        "The proxy formal class indicates that no attack label is confirmed by this "
        "observation."
    )
    verdict = is_term_negated_in_doc(doc, "attack")
    assert verdict.is_negated is True


def test_attack_as_real_assertion_is_unsafe():
    doc = _NLP("The event shows a confirmed replay attack against destination 2.")
    verdict = is_term_negated_in_doc(doc, "attack")
    assert verdict.is_negated is False


def test_malicious_not_present_returns_term_absent():
    doc = _NLP("Source identifier 1 communicated with destination identifier 2.")
    verdict = is_term_negated_in_doc(doc, "malicious")
    assert verdict.reason == "term_absent"


def test_filter_unsafe_returns_only_unsafe_terms():
    doc = _NLP(
        "The proxy formal class is not a confirmed attack label. The traffic "
        "appears malicious based on the observation."
    )

    unsafe = filter_unsafe_terms(doc, ["attack", "malicious"])

    assert "attack" not in unsafe
    assert "malicious" in unsafe
