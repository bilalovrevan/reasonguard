"""Per-(model x event-type) breakdown of ReasonGuard verdicts.

The exposé requires a model-comparison and a condition-comparison analysis in
weeks 16-17. This module is the building block for both: it joins the
ReasonGuard report with the prompt-level proxy event type and produces a
breakdown that can be loaded into the thesis as a table or into matplotlib
as a heat map.
"""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from src.pipeline_config import (
    LLM_PROMPTS_JSONL,
    OUTPUT_DIR,
    REASONGUARD_REPORT_JSONL,
    ensure_project_directories,
)

EVENT_TYPE_REPORT_JSON = OUTPUT_DIR / "event_type_analysis.json"
EVENT_TYPE_REPORT_CSV = OUTPUT_DIR / "event_type_analysis.csv"
EVENT_TYPE_REPORT_MD = OUTPUT_DIR / "event_type_analysis.md"

CHI_SQUARE_REPORT_JSON = OUTPUT_DIR / "chi_square_tests.json"
CHI_SQUARE_REPORT_MD = OUTPUT_DIR / "chi_square_tests.md"

# Single-label collapse used for the chi-square contingency tables (mirrors the
# NONE/MIXED collapse in src/evaluation_metrics.py, so the categorical unit is
# consistent across both analyses).
CHI_SQUARE_LABELS = ["NONE", "V1", "V2", "V3", "V4", "V5", "MIXED"]


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    records = []

    with open(path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if line:
                records.append(json.loads(line))

    return records


def build_event_type_lookup() -> dict[str, str]:
    lookup: dict[str, str] = {}

    if not LLM_PROMPTS_JSONL.exists():
        return lookup

    for record in load_jsonl(LLM_PROMPTS_JSONL):
        event_id = record["event_id"]
        proxy_event_type = record["formal_bound"].get("proxy_event_type", "unknown")
        lookup[event_id] = proxy_event_type

    return lookup


def compute_event_type_breakdown(
    report_records: list[dict[str, Any]],
    event_type_lookup: dict[str, str],
) -> list[dict[str, Any]]:
    """Produce a list of ``{model, event_type, ...counts}`` rows.

    Only responses whose event_id has a known event type are counted. Synthetic
    responses are included alongside real LLM responses so the same breakdown can
    be inspected for both populations.
    """

    bucket: dict[tuple[str, str], dict[str, int]] = {}

    for record in report_records:
        event_id = record.get("event_id") or ""
        model_name = record.get("model_name") or "unknown"
        event_type = event_type_lookup.get(event_id, "unknown")

        key = (model_name, event_type)
        counts = bucket.setdefault(
            key,
            {"total": 0, "clean": 0, "V1": 0, "V2": 0, "V3": 0, "V4": 0, "V5": 0},
        )

        counts["total"] += 1

        if not record.get("violation_codes"):
            counts["clean"] += 1

        for code in record.get("violation_codes", []):
            if code in counts:
                counts[code] += 1

    rows = []

    for (model_name, event_type), counts in sorted(bucket.items()):
        rate_clean = counts["clean"] / counts["total"] if counts["total"] else 0.0
        rates = {
            f"{code}_rate": counts[code] / counts["total"] if counts["total"] else 0.0
            for code in ("V1", "V2", "V3", "V4", "V5")
        }

        rows.append(
            {
                "model": model_name,
                "event_type": event_type,
                "total": counts["total"],
                "clean": counts["clean"],
                "clean_rate": round(rate_clean, 4),
                **{code: counts[code] for code in ("V1", "V2", "V3", "V4", "V5")},
                **{key: round(value, 4) for key, value in rates.items()},
            }
        )

    return rows


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    fieldnames = list(rows[0].keys())

    with open(path, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Per-Event-Type Violation Breakdown",
        "",
        "Counts and rates of ReasonGuard verdicts grouped by model and proxy event type.",
        "",
        "| Model | Event type | Total | Clean | Clean rate | V1 | V2 | V3 | V4 | V5 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]

    for row in rows:
        lines.append(
            f"| {row['model']} | {row['event_type']} | {row['total']} | {row['clean']} | "
            f"{row['clean_rate']:.2%} | {row['V1']} | {row['V2']} | {row['V3']} | "
            f"{row['V4']} | {row['V5']} |"
        )

    lines.append("")
    return "\n".join(lines)


def collapse_label(violation_codes: list[str] | None) -> str:
    """Collapse a response's violation-code list to one categorical label.

    Mirrors the NONE/MIXED collapse used for the human-vs-machine comparison in
    src/evaluation_metrics.py, so "is violation category independent of X"
    tests operate on the same categorical unit as the F1/Kappa analysis.
    """

    codes = violation_codes or []

    if not codes:
        return "NONE"

    if len(codes) > 1:
        return "MIXED"

    return codes[0] if codes[0] in CHI_SQUARE_LABELS else "NONE"


def build_contingency_table(
    report_records: list[dict[str, Any]],
    group_key_fn: Any,
) -> tuple[list[str], list[str], list[list[int]]]:
    """Build a (group x violation-label) contingency table.

    ``group_key_fn`` maps a report record to its group (e.g. model_name, or
    proxy event type via a lookup closure). Returns (group_names, label_names,
    matrix) with matrix[i][j] = count of group_names[i] responses labeled
    label_names[j].
    """

    groups: dict[str, dict[str, int]] = {}

    for record in report_records:
        group = group_key_fn(record)

        if group is None:
            continue

        label = collapse_label(record.get("violation_codes"))
        counts = groups.setdefault(group, dict.fromkeys(CHI_SQUARE_LABELS, 0))
        counts[label] += 1

    group_names = sorted(groups)
    matrix = [[groups[g][label] for label in CHI_SQUARE_LABELS] for g in group_names]

    return group_names, CHI_SQUARE_LABELS, matrix


def compute_chi_square(
    group_names: list[str],
    label_names: list[str],
    matrix: list[list[int]],
) -> dict[str, Any]:
    """Chi-square test of independence between group (rows) and violation label
    (columns). Drops all-zero columns first (chi2_contingency rejects a
    zero-sum column/row), since a violation class absent from the whole sample
    (e.g. no V5 responses at all) is not evidence of dependence, just of an
    empty category, and would otherwise crash the test.
    """

    import numpy as np
    from scipy.stats import chi2_contingency

    array = np.array(matrix, dtype=float)
    kept_cols = [j for j in range(array.shape[1]) if array[:, j].sum() > 0]
    kept_rows = [i for i in range(array.shape[0]) if array[i, :].sum() > 0]

    dropped_labels = [label_names[j] for j in range(len(label_names)) if j not in kept_cols]

    reduced = array[np.ix_(kept_rows, kept_cols)]
    reduced_groups = [group_names[i] for i in kept_rows]
    reduced_labels = [label_names[j] for j in kept_cols]

    if reduced.shape[0] < 2 or reduced.shape[1] < 2:
        return {
            "groups": reduced_groups,
            "labels": reduced_labels,
            "dropped_labels_all_zero": dropped_labels,
            "chi2": None,
            "p_value": None,
            "dof": None,
            "significant_at_0_05": None,
            "note": "Not enough non-empty rows/columns to run a chi-square test.",
        }

    chi2, p_value, dof, _expected = chi2_contingency(reduced)

    return {
        "groups": reduced_groups,
        "labels": reduced_labels,
        "dropped_labels_all_zero": dropped_labels,
        "chi2": round(float(chi2), 4),
        "p_value": round(float(p_value), 6),
        "dof": int(dof),
        "significant_at_0_05": bool(p_value < 0.05),
    }


def render_chi_square_markdown(tests: dict[str, Any]) -> str:
    lines = [
        "# Chi-Square Tests of Independence: Violation Category vs. Grouping",
        "",
        "H0: the distribution of ReasonGuard violation categories (NONE/V1-V5/MIXED, ",
        "collapsed to a single label per response as in the F1/Kappa analysis) is ",
        "independent of the grouping variable. p < 0.05 rejects H0 -- i.e. violation ",
        "category is associated with that grouping variable.",
        "",
    ]

    for name, result in tests.items():
        lines.append(f"## {name}")
        lines.append("")

        if result["chi2"] is None:
            lines.append(f"Not computed: {result['note']}")
            lines.append("")
            continue

        lines.append(f"- Groups: {', '.join(result['groups'])}")
        lines.append(f"- Violation labels tested: {', '.join(result['labels'])}")

        if result["dropped_labels_all_zero"]:
            lines.append(
                f"- Labels dropped (zero count across all groups): "
                f"{', '.join(result['dropped_labels_all_zero'])}"
            )

        lines.append(f"- Chi-square statistic: {result['chi2']}")
        lines.append(f"- Degrees of freedom: {result['dof']}")
        lines.append(f"- p-value: {result['p_value']}")

        if result["significant_at_0_05"]:
            verdict = "yes -- reject H0, violation category is associated with this grouping variable"
        else:
            verdict = "no -- fail to reject H0"

        lines.append(f"- Significant at alpha=0.05: {verdict}")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    ensure_project_directories()

    if not REASONGUARD_REPORT_JSONL.exists():
        raise FileNotFoundError(
            f"ReasonGuard report not found: {REASONGUARD_REPORT_JSONL}\n"
            "Run: python -m src.reason_guard_checker"
        )

    report_records = load_jsonl(REASONGUARD_REPORT_JSONL)
    event_type_lookup = build_event_type_lookup()

    if not event_type_lookup:
        print(
            "No prompt-level event type information found. Run:\n"
            "  REASONGUARD_STRATIFY=1 python -m src.prompt_builder\n"
            "to populate proxy_event_type on the prompts."
        )

    rows = compute_event_type_breakdown(report_records, event_type_lookup)

    EVENT_TYPE_REPORT_JSON.write_text(json.dumps(rows, indent=2), encoding="utf-8")
    write_csv(rows, EVENT_TYPE_REPORT_CSV)
    EVENT_TYPE_REPORT_MD.write_text(render_markdown(rows), encoding="utf-8")

    print("Per-event-type analysis completed successfully.")
    print(f"Rows: {len(rows)}")
    print(f"JSON: {EVENT_TYPE_REPORT_JSON}")
    print(f"CSV: {EVENT_TYPE_REPORT_CSV}")
    print(f"Markdown: {EVENT_TYPE_REPORT_MD}")

    # Chi-square: is violation category independent of (a) model, (b) proxy event type?
    # Synthetic responses are a rule-based baseline, not a language model, so they are
    # excluded from the model association test (thesis Sec. 3.10); they stay in the
    # event-type test below.
    model_groups, labels, model_matrix = build_contingency_table(
        report_records,
        lambda r: None
        if (r.get("model_name") or "unknown") == "synthetic_rule_based"
        else (r.get("model_name") or "unknown"),
    )
    event_groups, _labels, event_matrix = build_contingency_table(
        report_records, lambda r: event_type_lookup.get(r.get("event_id") or "")
    )

    chi_square_tests = {
        "violation_category_vs_model": compute_chi_square(model_groups, labels, model_matrix),
        "violation_category_vs_proxy_event_type": compute_chi_square(
            event_groups, labels, event_matrix
        ),
    }

    CHI_SQUARE_REPORT_JSON.write_text(json.dumps(chi_square_tests, indent=2), encoding="utf-8")
    CHI_SQUARE_REPORT_MD.write_text(render_chi_square_markdown(chi_square_tests), encoding="utf-8")

    print("Chi-square tests completed successfully.")
    print(f"JSON: {CHI_SQUARE_REPORT_JSON}")
    print(f"Markdown: {CHI_SQUARE_REPORT_MD}")


if __name__ == "__main__":
    main()
