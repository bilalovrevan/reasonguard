"""Streamlit dashboard for the ReasonGuard runtime verification framework.

Run with:

    streamlit run src/dashboard/app.py

The dashboard accepts a formal bound (pasted JSON or example selection) and an
LLM explanation (pasted text), runs the ReasonGuard checker, and shows the
V1-V5 verdict together with the per-claim three-state output produced by the
spaCy NER pipeline.

This is the W17-18 exposé deliverable. The skeleton is functional but minimal;
the polish pass happens once the violation taxonomy and the schema are frozen.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Streamlit Cloud (and `streamlit run src/dashboard/app.py` from an unusual cwd)
# only puts this file's own directory on sys.path, so the `src.*` package
# imports below fail with ModuleNotFoundError unless the repo root is added
# explicitly first.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st

from src.pipeline_config import FORMAL_BOUNDS_JSONL
from src.reason_guard_checker import check_response

EXAMPLE_RESPONSE_OPTIONS = {
    "Clean (well-bounded)": (
        "The formal bound describes an iec104 observation from source identifier "
        "1 to destination identifier 2. The observed source port is 57528 and the "
        "destination port is 2404, with communication direction classified as "
        "client_to_server. The ASDU fields are type 0, COT 0, item count 0, and "
        "address 0. The current formal class is a proxy observation label, so the "
        "bound does not confirm a security conclusion."
    ),
    "V1 fabricated (invents attack)": (
        "This event shows a confirmed replay attack against destination 2. The "
        "attacker is using malicious IEC-104 traffic to manipulate the control "
        "process. The affected substation should be isolated immediately to "
        "prevent further compromise."
    ),
    "V2 contradicted (wrong direction)": (
        "The event is best understood as server_to_client communication from source "
        "identifier 1 to destination identifier 2. The ASDU type is 0 and the port "
        "information should be interpreted accordingly."
    ),
    "V3 over-generalised (loses specifics)": (
        "This appears to be routine IEC-104 traffic with standard communication "
        "behavior. The observation looks typical for an industrial control system "
        "exchange. No specific concern is visible from this event."
    ),
    "V4 under-specified (missing fields)": (
        "The event is an IEC-104 observation. It may be useful for understanding "
        "communication behavior. The bound does not provide enough information for "
        "a stronger conclusion."
    ),
    "V5 incoherent (internal contradiction)": (
        "The event is normal traffic and also a malicious attack at the same time. "
        "It is isolated to source 1 and destination 2, but it also affects the "
        "entire network segment. The communication is both client-to-server and "
        "server-to-client."
    ),
}

SEVERITY_BADGES = {
    "high": ":red[HIGH]",
    "medium": ":orange[MEDIUM]",
    "low": ":blue[LOW]",
    "none": ":green[NONE]",
}


@st.cache_data
def load_first_bounds(path: Path, limit: int = 10) -> list[dict[str, Any]]:
    if not path.exists():
        return []

    records = []

    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

            if len(records) >= limit:
                break

    return records


def render_violation_panel(verdict: dict[str, Any]) -> None:
    severity = verdict["severity"]
    severity_badge = SEVERITY_BADGES.get(severity, severity)

    st.metric(label="Severity", value=severity.upper())
    st.markdown(f"**Severity classification:** {severity_badge}")

    if not verdict["violation_codes"]:
        st.success("No V1-V5 violations detected.")
        return

    st.error(f"Violations detected: {', '.join(verdict['violation_codes'])}")

    for code in verdict["violation_codes"]:
        reasons = verdict["reasons"].get(code, [])

        with st.expander(f"{code} reasons ({len(reasons)})"):
            for reason in reasons:
                st.write(f"- {reason}")


def render_per_claim_panel(verdict: dict[str, Any]) -> None:
    per_claim = verdict.get("per_claim_verdicts")

    if not per_claim:
        st.info(
            "Per-claim verdicts are not available. Make sure spaCy and the "
            "en_core_web_lg model are installed."
        )
        return

    st.subheader("Per-claim three-state verdicts")

    for entry in per_claim:
        verdict_label = entry["verdict"]
        evidence = ", ".join(entry["evidence"]) if entry["evidence"] else "—"

        if verdict_label == "SUPPORTED":
            st.success(f"**{entry['claim']}** — {verdict_label} (evidence: {evidence})")
        elif verdict_label == "CONTRADICTED":
            st.error(f"**{entry['claim']}** — {verdict_label} (evidence: {evidence})")
        else:
            st.warning(f"**{entry['claim']}** — {verdict_label} (evidence: {evidence})")


def render_main_panel() -> None:
    st.title("ReasonGuard — Runtime Verification Dashboard")
    st.caption(
        "Verify whether an LLM-generated ICS explanation stays within the bounds "
        "established by the formal automaton output."
    )

    bounds = load_first_bounds(FORMAL_BOUNDS_JSONL, limit=10)

    if not bounds:
        st.warning(
            "No formal bounds were found at `outputs/formal_bounds_sample_003.jsonl`. "
            "Run `python -m src.formal_bound_builder` first."
        )

    bound_labels = [f"{bound['event_id']} ({bound['formal_class']})" for bound in bounds]
    selected_label = st.selectbox("Choose a formal bound to verify against:", bound_labels)
    selected_bound = bounds[bound_labels.index(selected_label)] if bounds else None

    if selected_bound is not None:
        with st.expander("Show formal bound JSON"):
            st.json(selected_bound)

    response_choice = st.selectbox(
        "Pick an example explanation or write your own below:",
        ["(write my own)"] + list(EXAMPLE_RESPONSE_OPTIONS.keys()),
    )

    default_text = EXAMPLE_RESPONSE_OPTIONS.get(response_choice, "")
    explanation_text = st.text_area(
        "LLM explanation",
        value=default_text,
        height=180,
    )

    run_button = st.button("Verify with ReasonGuard")

    if run_button and selected_bound is not None and explanation_text.strip():
        prompt_record = {"event_id": selected_bound["event_id"], "formal_bound": selected_bound}
        response_record = {
            "response_id": f"{selected_bound['event_id']}_dashboard",
            "original_event_id": selected_bound["event_id"],
            "response_type": "dashboard_input",
            "model_name": "dashboard_user",
            "response": explanation_text.strip(),
        }

        verdict = check_response(prompt_record, response_record)

        st.divider()
        render_violation_panel(verdict)
        st.divider()
        render_per_claim_panel(verdict)


if __name__ == "__main__":
    render_main_panel()
