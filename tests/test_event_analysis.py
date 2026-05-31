from __future__ import annotations

from src.event_analysis import (
    compute_event_type_breakdown,
    render_markdown,
)


def _report_record(model: str, event_id: str, codes: list[str]) -> dict:
    return {
        "model_name": model,
        "event_id": event_id,
        "violation_codes": codes,
    }


def test_breakdown_groups_by_model_and_event_type():
    records = [
        _report_record("phi3:mini", "evt_000001", ["V1"]),
        _report_record("phi3:mini", "evt_000002", []),
        _report_record("phi3:mini", "evt_000003", ["V4"]),
        _report_record("llama3.1:8b", "evt_000001", []),
        _report_record("llama3.1:8b", "evt_000002", ["V1", "V4"]),
    ]

    event_type_lookup = {
        "evt_000001": "normal_polling",
        "evt_000002": "topology_change",
        "evt_000003": "normal_polling",
    }

    rows = compute_event_type_breakdown(records, event_type_lookup)

    by_key = {(row["model"], row["event_type"]): row for row in rows}

    assert by_key[("phi3:mini", "normal_polling")]["total"] == 2
    assert by_key[("phi3:mini", "normal_polling")]["V1"] == 1
    assert by_key[("phi3:mini", "normal_polling")]["V4"] == 1
    assert by_key[("phi3:mini", "topology_change")]["clean"] == 1

    assert by_key[("llama3.1:8b", "normal_polling")]["clean"] == 1
    assert by_key[("llama3.1:8b", "topology_change")]["V1"] == 1
    assert by_key[("llama3.1:8b", "topology_change")]["V4"] == 1


def test_breakdown_marks_unknown_event_type_when_missing():
    records = [_report_record("phi3:mini", "evt_999999", ["V1"])]
    rows = compute_event_type_breakdown(records, {})

    assert len(rows) == 1
    assert rows[0]["event_type"] == "unknown"
    assert rows[0]["V1"] == 1


def test_render_markdown_returns_table():
    rows = [
        {
            "model": "phi3:mini",
            "event_type": "topology_change",
            "total": 5,
            "clean": 2,
            "clean_rate": 0.4,
            "V1": 1,
            "V2": 0,
            "V3": 0,
            "V4": 2,
            "V5": 0,
        }
    ]

    markdown = render_markdown(rows)

    assert "| phi3:mini | topology_change |" in markdown
    assert "Clean rate" in markdown
