"""Smoke tests for the Streamlit dashboard module.

These tests only exercise the pure-Python helpers; they do not start a
Streamlit server. The intent is to catch import errors and ensure the
example dictionaries stay consistent with the V1-V5 taxonomy.
"""

from __future__ import annotations

from src.dashboard import app


def test_example_response_options_cover_all_violation_types():
    expected_keywords = ["Clean", "V1", "V2", "V3", "V4", "V5"]

    for keyword in expected_keywords:
        matched = any(keyword in key for key in app.EXAMPLE_RESPONSE_OPTIONS)
        assert matched, f"No example covers {keyword}"


def test_severity_badges_cover_all_levels():
    for level in ("high", "medium", "low", "none"):
        assert level in app.SEVERITY_BADGES


def test_example_responses_are_non_empty_strings():
    for _label, text in app.EXAMPLE_RESPONSE_OPTIONS.items():
        assert isinstance(text, str)
        assert len(text) > 50
