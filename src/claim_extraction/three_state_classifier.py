from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any

from src.claim_extraction.extractor import ExtractedClaims


class ClaimVerdict(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    CONTRADICTED = "CONTRADICTED"


@dataclass
class PerClaimVerdict:
    claim: str
    verdict: ClaimVerdict
    evidence: list[str]


def _direction_matches(extracted: ExtractedClaims, expected: str) -> bool:
    expected_tokens = expected.lower().replace("_", " ")

    return any(
        expected_tokens in direction.lower().replace("_", " ")
        for direction in extracted.directions
    )


def _direction_contradicts(extracted: ExtractedClaims, expected: str) -> bool:
    opposite = (
        "server_to_client"
        if expected == "client_to_server"
        else "client_to_server"
    )
    opposite_tokens = opposite.replace("_", " ")

    direction_texts = [direction.lower().replace("_", " ") for direction in extracted.directions]

    return any(opposite_tokens in text for text in direction_texts) and not _direction_matches(
        extracted,
        expected,
    )


def classify_claims_against_bound(
    extracted: ExtractedClaims,
    bound: dict[str, Any],
) -> list[PerClaimVerdict]:
    """Map the bound's required and forbidden claims to a per-claim three-state verdict."""

    verdicts: list[PerClaimVerdict] = []
    constraints = bound["machine_constraints"]
    features = bound["features"]
    expected_direction = bound["communication_direction"]

    if _direction_contradicts(extracted, expected_direction):
        verdicts.append(
            PerClaimVerdict(
                claim="communication_direction",
                verdict=ClaimVerdict.CONTRADICTED,
                evidence=extracted.directions,
            )
        )
    elif _direction_matches(extracted, expected_direction):
        verdicts.append(
            PerClaimVerdict(
                claim="communication_direction",
                verdict=ClaimVerdict.SUPPORTED,
                evidence=extracted.directions,
            )
        )
    else:
        verdicts.append(
            PerClaimVerdict(
                claim="communication_direction",
                verdict=ClaimVerdict.UNSUPPORTED,
                evidence=extracted.directions,
            )
        )

    if extracted.source_mentions > 0:
        verdicts.append(
            PerClaimVerdict(
                claim="source_identifier_present",
                verdict=ClaimVerdict.SUPPORTED,
                evidence=[f"source_mentions={extracted.source_mentions}"],
            )
        )
    else:
        verdicts.append(
            PerClaimVerdict(
                claim="source_identifier_present",
                verdict=ClaimVerdict.UNSUPPORTED,
                evidence=[],
            )
        )

    if extracted.destination_mentions > 0:
        verdicts.append(
            PerClaimVerdict(
                claim="destination_identifier_present",
                verdict=ClaimVerdict.SUPPORTED,
                evidence=[f"destination_mentions={extracted.destination_mentions}"],
            )
        )
    else:
        verdicts.append(
            PerClaimVerdict(
                claim="destination_identifier_present",
                verdict=ClaimVerdict.UNSUPPORTED,
                evidence=[],
            )
        )

    if extracted.port_mentions > 0:
        verdicts.append(
            PerClaimVerdict(
                claim="port_information_present",
                verdict=ClaimVerdict.SUPPORTED,
                evidence=[f"port_mentions={extracted.port_mentions}"],
            )
        )
    else:
        verdicts.append(
            PerClaimVerdict(
                claim="port_information_present",
                verdict=ClaimVerdict.UNSUPPORTED,
                evidence=[],
            )
        )

    if extracted.asdu_mentions > 0:
        verdicts.append(
            PerClaimVerdict(
                claim="asdu_fields_present",
                verdict=ClaimVerdict.SUPPORTED,
                evidence=[f"asdu_mentions={extracted.asdu_mentions}"],
            )
        )
    else:
        verdicts.append(
            PerClaimVerdict(
                claim="asdu_fields_present",
                verdict=ClaimVerdict.UNSUPPORTED,
                evidence=[],
            )
        )

    if extracted.attack_categories and not constraints["attack_claim_allowed"]:
        verdicts.append(
            PerClaimVerdict(
                claim="attack_category_claim",
                verdict=ClaimVerdict.UNSUPPORTED,
                evidence=extracted.attack_categories,
            )
        )

    if extracted.mitigation_terms and not constraints["mitigation_claim_allowed"]:
        verdicts.append(
            PerClaimVerdict(
                claim="mitigation_claim",
                verdict=ClaimVerdict.UNSUPPORTED,
                evidence=extracted.mitigation_terms,
            )
        )

    if extracted.normality_terms and not constraints["normality_claim_allowed"]:
        verdicts.append(
            PerClaimVerdict(
                claim="normality_claim",
                verdict=ClaimVerdict.UNSUPPORTED,
                evidence=extracted.normality_terms,
            )
        )

    allowed_numbers = {
        int(features[key])
        for key in (
            "source_id",
            "destination_id",
            "srcport",
            "dstport",
            "bytes",
            "pkt_length",
            "asdu_address",
            "asdu_cot",
            "asdu_items",
            "asdu_type",
            "frame_fmt",
        )
    }

    if "timestamp_ms" in bound:
        allowed_numbers.add(int(bound["timestamp_ms"]))

    allowed_numbers |= {104, 2404}

    unsupported_numbers = sorted(
        number for number in set(extracted.numbers) if number > 1_000 and number not in allowed_numbers
    )

    if unsupported_numbers:
        verdicts.append(
            PerClaimVerdict(
                claim="numeric_identifier_consistency",
                verdict=ClaimVerdict.UNSUPPORTED,
                evidence=[str(number) for number in unsupported_numbers],
            )
        )

    return verdicts
