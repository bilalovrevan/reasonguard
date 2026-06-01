from __future__ import annotations

from src.claim_extraction.entity_ruler import (
    ICS_ENTITY_PATTERNS,
    build_entity_ruler_patterns,
)
from src.claim_extraction.extractor import ExtractedClaims
from src.claim_extraction.three_state_classifier import (
    ClaimVerdict,
    PerClaimVerdict,
    classify_claims_against_bound,
)


def _sample_bound() -> dict:
    return {
        "communication_direction": "client_to_server",
        "features": {
            "source_id": 1,
            "destination_id": 2,
            "bytes": 46,
            "pkt_length": 4,
            "srcport": 57528,
            "dstport": 2404,
            "asdu_address": 0,
            "asdu_cot": 0,
            "asdu_items": 0,
            "asdu_type": 0,
            "frame_fmt": 1,
        },
        "machine_constraints": {
            "attack_claim_allowed": False,
            "mitigation_claim_allowed": False,
            "normality_claim_allowed": False,
        },
    }


def test_entity_ruler_patterns_returns_copy():
    patterns = build_entity_ruler_patterns()
    patterns.append({"label": "TEST", "pattern": []})

    assert len(ICS_ENTITY_PATTERNS) != len(patterns)


def test_three_state_classifier_marks_direction_supported_when_matches():
    extracted = ExtractedClaims(
        raw_text="client to server",
        directions=["client to server"],
        source_mentions=1,
        destination_mentions=1,
        port_mentions=1,
        asdu_mentions=1,
    )

    verdicts = classify_claims_against_bound(extracted, _sample_bound())
    direction_verdict = next(v for v in verdicts if v.claim == "communication_direction")

    assert direction_verdict.verdict == ClaimVerdict.SUPPORTED


def test_three_state_classifier_marks_direction_contradicted_when_opposite():
    extracted = ExtractedClaims(
        raw_text="server to client",
        directions=["server to client"],
        source_mentions=1,
        destination_mentions=1,
        port_mentions=1,
        asdu_mentions=1,
    )

    verdicts = classify_claims_against_bound(extracted, _sample_bound())
    direction_verdict = next(v for v in verdicts if v.claim == "communication_direction")

    assert direction_verdict.verdict == ClaimVerdict.CONTRADICTED


def test_unsupported_attack_category_flagged_when_constraints_forbid_it():
    extracted = ExtractedClaims(
        raw_text="replay attack happened",
        attack_categories=["replay attack"],
        source_mentions=1,
        destination_mentions=1,
        port_mentions=1,
        asdu_mentions=1,
    )

    verdicts = classify_claims_against_bound(extracted, _sample_bound())
    attack_verdicts = [v for v in verdicts if v.claim == "attack_category_claim"]

    assert len(attack_verdicts) == 1
    assert attack_verdicts[0].verdict == ClaimVerdict.UNSUPPORTED


def test_per_claim_verdict_dataclass_is_immutable_like():
    verdict = PerClaimVerdict(
        claim="communication_direction",
        verdict=ClaimVerdict.SUPPORTED,
        evidence=["client to server"],
    )

    assert verdict.claim == "communication_direction"
    assert verdict.evidence == ["client to server"]
