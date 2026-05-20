from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from src.claim_extraction.entity_ruler import build_entity_ruler_patterns


@dataclass
class ExtractedClaims:
    raw_text: str
    entities: list[tuple[str, str]] = field(default_factory=list)
    numbers: list[int] = field(default_factory=list)
    protocols: list[str] = field(default_factory=list)
    directions: list[str] = field(default_factory=list)
    attack_categories: list[str] = field(default_factory=list)
    mitigation_terms: list[str] = field(default_factory=list)
    normality_terms: list[str] = field(default_factory=list)
    uncertainty_terms: list[str] = field(default_factory=list)
    asdu_mentions: int = 0
    source_mentions: int = 0
    destination_mentions: int = 0
    port_mentions: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "entities": self.entities,
            "numbers": self.numbers,
            "protocols": self.protocols,
            "directions": self.directions,
            "attack_categories": self.attack_categories,
            "mitigation_terms": self.mitigation_terms,
            "normality_terms": self.normality_terms,
            "uncertainty_terms": self.uncertainty_terms,
            "asdu_mentions": self.asdu_mentions,
            "source_mentions": self.source_mentions,
            "destination_mentions": self.destination_mentions,
            "port_mentions": self.port_mentions,
        }


class SpacyClaimExtractor:
    """Wraps a spaCy pipeline configured with an ICS-domain EntityRuler.

    The class loads the model lazily so unit tests that only import the module do not
    trigger a model download.
    """

    def __init__(self, base_model: str = "en_core_web_lg") -> None:
        self.base_model = base_model
        self._nlp = None

    def _load_pipeline(self):
        try:
            import spacy
        except ImportError as error:
            raise RuntimeError(
                "spaCy is not installed. Install it with: pip install spacy "
                "and download the model with: python -m spacy download en_core_web_lg"
            ) from error

        try:
            nlp = spacy.load(self.base_model)
        except OSError as error:
            raise RuntimeError(
                f"spaCy model '{self.base_model}' is not available. "
                "Download it with: python -m spacy download " + self.base_model
            ) from error

        ruler_name = "ics_entity_ruler"

        if ruler_name not in nlp.pipe_names:
            ruler = nlp.add_pipe("entity_ruler", name=ruler_name, before="ner")
            ruler.add_patterns(build_entity_ruler_patterns())

        return nlp

    def extract(self, text: str) -> ExtractedClaims:
        if self._nlp is None:
            self._nlp = self._load_pipeline()

        doc = self._nlp(text)
        lowered_text = text.lower()

        entities = [(entity.text, entity.label_) for entity in doc.ents]
        numbers = [int(match.group()) for match in re.finditer(r"\b\d+\b", text)]

        protocols = [text_value for text_value, label in entities if label == "PROTOCOL"]
        directions = [text_value for text_value, label in entities if label == "DIRECTION"]
        attack_categories = [text_value for text_value, label in entities if label == "ATTACK_CATEGORY"]
        mitigation_terms = [text_value for text_value, label in entities if label == "MITIGATION"]
        normality_terms = [text_value for text_value, label in entities if label == "NORMALITY"]
        uncertainty_terms = [text_value for text_value, label in entities if label == "UNCERTAINTY"]

        return ExtractedClaims(
            raw_text=text,
            entities=entities,
            numbers=numbers,
            protocols=protocols,
            directions=directions,
            attack_categories=attack_categories,
            mitigation_terms=mitigation_terms,
            normality_terms=normality_terms,
            uncertainty_terms=uncertainty_terms,
            asdu_mentions=lowered_text.count("asdu"),
            source_mentions=lowered_text.count("source"),
            destination_mentions=lowered_text.count("destination"),
            port_mentions=lowered_text.count("port"),
        )


_DEFAULT_EXTRACTOR: SpacyClaimExtractor | None = None


def extract_claims_with_spacy(text: str) -> ExtractedClaims:
    """Convenience function that reuses one extractor instance across calls."""

    global _DEFAULT_EXTRACTOR

    if _DEFAULT_EXTRACTOR is None:
        _DEFAULT_EXTRACTOR = SpacyClaimExtractor()

    return _DEFAULT_EXTRACTOR.extract(text)
