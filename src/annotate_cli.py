"""Fast one-row-at-a-time terminal annotation tool for the M4 manual evaluation set.

Reads/writes ``annotation/annotation_results.csv`` (seeded from
``annotation/annotation_batch.csv`` on first run) so progress is always saved
after every single row -- safe to quit any time (Ctrl+C or 'q') and resume
later. Never shows ReasonGuard's own machine_violations/machine_severity
columns while you are labeling a row, so your judgement stays independent.

Default mode is SPRINT MODE: press a single key (no Enter needed) for the
violation class and the row is saved immediately with severity/notes left
blank. Only the violation-class label is used by src/evaluation_metrics.py
for F1/Kappa -- severity and notes are optional supplementary detail, not
required for the core validation numbers, so skipping them under time
pressure costs nothing on the metrics that matter for M4/M5.

To keep quality up under time pressure, a session stops itself after
BATCH_SIZE rows (default 25) with an encouraging message -- just re-run the
same command to start the next batch. Press 'u' any time to undo the row you
just labeled (fixes a mis-press without needing to quit and lose the rest of
the session). On a fresh start (0 rows labeled yet) the queue is sorted by
response length, shortest first, so the fast/obvious rows build momentum
before the longer, more ambiguous ones.

Usage:
    python -m src.annotate_cli --initials RB              # sprint mode, batches of 25
    python -m src.annotate_cli --initials RB --batch=40    # custom batch size
    python -m src.annotate_cli --initials RB --batch=all   # no auto-stop
    python -m src.annotate_cli --initials RB --detailed    # old flow: severity+notes per row
    python -m src.annotate_cli --progress                  # just print how many rows are done
    python -m src.annotate_cli --rubric                    # print the AZ decision rubric and exit
"""

from __future__ import annotations

import csv
import json
import shutil
import sys
from pathlib import Path
from typing import Any

from src.pipeline_config import (
    ANNOTATION_INPUT_CSV,
    ANNOTATION_RESULTS_CSV,
    OUTPUT_DIR,
    ensure_project_directories,
)

FORMAL_BOUNDS_FILES = [
    OUTPUT_DIR / "formal_bounds_sample_003.jsonl",
    OUTPUT_DIR / "formal_bounds_hmi.jsonl",
]

VIOLATION_KEYS = {
    "0": "NONE",
    "1": "V1",
    "2": "V2",
    "3": "V3",
    "4": "V4",
    "5": "V5",
    "m": "MIXED",
}
SEVERITY_KEYS = {"0": "none", "1": "low", "2": "medium", "3": "high"}

# Ravan's own decision procedure (in Azerbaijani, his working language), written
# after the first full-200 annotation attempt produced near-random labels under
# fatigue (Kappa ~0.03, see AI_ADDENDUM.md). Shown once at the start of every
# sprint batch as a refresher, plus a condensed one-liner on every row, so the
# same systematic check order is applied under time pressure instead of a gut
# guess. Order matters: Forbidden -> Required -> specificity -> self-contradiction
# -> else NONE.
RUBRIC_AZ = """
QERAR QAYDASI (her setri etiketlemeden evvel bunu yadda saxla):

  0  = NONE     -- AI dediyi her sey bound-daki "Allowed" siyahisi ile ust-uste
                   dusur, hec ne uydurmayib, hec neyi eskik qoymayib. Sadece
                   faktlari duz tekrarlayib.
  V1 = Fabricated    -- AI, bound-da olmayan bir sey uydurub (mes. bound hec
                   bir hucumdan behs etmir, amma AI "bu skan hucumudur" ve ya
                   movcud olmayan bir cihaz/hadise adi cekir).
  V2 = Contradicted  -- AI, bound-un ACIQ dediyi bir faktin EKSINI deyib (mes.
                   bound "server_to_client" deyir, AI "client_to_server" yazir;
                   ya da bound "tesdiqlenmeyib" deyir, AI "tesdiqlenmis
                   normaldir/hucumdur" deyir).
  V3 = Over-generalised -- Kateqoriya/istiqamet duzgundur, AMMA bound-daki
                   konkret reqemleri (ID, port, ASDU saheleri) tamamile atib,
                   cox umumi yazib (mes. "qeyri-adi bir hadise bas verdi" --
                   hec bir reqem yoxdur).
  V4 = Under-specified  -- Detallarin coxu duzgundur, amma "Required to
                   mention" siyahisindaki vacib bir seyi (adeten "bu proxy
                   label-dir, tesdiqlenmis hucum deyil" ifadesini) tamamile
                   demeyib.
  V5 = Incoherent    -- Bound-dan asili olmayaraq, AI-nin oz cavabi oz-ozune
                   ziddir (mes. eyni cavabda hem "bir cihaza aiddir" deyir,
                   hem "butun sebekeye aiddir" deyir).
  MIXED = yuxaridakilardan aydin sekilde IKISI birden varsa (nadir hallarda
                   istifade et).

  SUERETLI QAYDA: evvel "Forbidden"-e bax (uydurma/zidd varmi? -> V1/V2),
  sonra "Required"-e bax (nese eskikdirmi? -> V4), sonra konkretliye bax
  (reqemler itibmi? -> V3), sonra oz-ozune ziddiyyete bax (-> V5).
  Hec biri yoxdursa -> 0.
"""

QUICK_RULE_AZ = (
    "Qayda: Forbidden var? -> V1/V2  |  Required eskikdir? -> V4  |  "
    "Reqemler itib? -> V3  |  Ozune zidd? -> V5  |  Hecne -> 0"
)


def print_rubric() -> None:
    print(RUBRIC_AZ)

FIELDNAMES = [
    "response_id",
    "event_id",
    "model_name",
    "response_type",
    "machine_violations",
    "machine_severity",
    "human_label",
    "human_severity",
    "annotator_initials",
    "annotator_notes",
    "response_text",
]


def load_rows(path: Path) -> list[dict[str, str]]:
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def save_rows(rows: list[dict[str, str]], path: Path) -> None:
    tmp_path = path.with_suffix(".tmp")
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
    tmp_path.replace(path)


def load_bounds_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for path in FORMAL_BOUNDS_FILES:
        if not path.exists():
            continue
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    d = json.loads(line)
                    index[d["event_id"]] = d
    return index


def format_bound(bound: dict[str, Any] | None) -> str:
    if not bound:
        return "(formal bound not found for this event id -- judge from the response text alone)"
    lines = [f"Formal class: {bound.get('formal_class', bound.get('ground_truth_class', 'unknown'))}"]
    claims = bound.get("allowed_claims", [])
    if claims:
        lines.append("Allowed:")
        lines.extend(f"  - {c}" for c in claims)
    forbidden = bound.get("forbidden_claims", [])
    if forbidden:
        lines.append("Forbidden:")
        lines.extend(f"  - {c}" for c in forbidden)
    required = bound.get("required_claims", [])
    if required:
        lines.append("Required to mention:")
        lines.extend(f"  - {c}" for c in required)
    return "\n".join(lines)


def ensure_results_file() -> Path:
    ensure_project_directories()

    if not ANNOTATION_RESULTS_CSV.exists():
        if not ANNOTATION_INPUT_CSV.exists():
            raise SystemExit(
                f"Neither {ANNOTATION_RESULTS_CSV} nor {ANNOTATION_INPUT_CSV} exist. "
                "Run `python -m src.manual_annotation --size=200` first."
            )
        shutil.copyfile(ANNOTATION_INPUT_CSV, ANNOTATION_RESULTS_CSV)
        print(f"Seeded {ANNOTATION_RESULTS_CSV} from {ANNOTATION_INPUT_CSV.name}.")

    return ANNOTATION_RESULTS_CSV


def prompt_choice(prompt: str, options: dict[str, str]) -> str | None:
    legend = "  ".join(f"[{k}]={v}" for k, v in options.items())
    while True:
        raw = input(f"{prompt}\n  {legend}\n  (q to quit, s to skip) > ").strip().lower()
        if raw == "q":
            return None
        if raw == "s":
            return ""
        if raw in options:
            return options[raw]
        print("  Not a valid option, try again.")


def get_single_key(valid: set[str]) -> str:
    """Read one keypress with no Enter required. Falls back to input() if not a real TTY."""
    try:
        import termios
        import tty

        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            while True:
                ch = sys.stdin.read(1)
                if ch in valid:
                    return ch
                if ch == "\x03":  # Ctrl+C
                    raise KeyboardInterrupt
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except (ImportError, AttributeError, OSError):
        while True:
            raw = input("> ").strip().lower()
            if raw in valid:
                return raw
            print("  Not a valid key, try again.")


def sprint_loop(rows, results_path, bounds_index, initials, done, total, batch_size) -> None:
    keys = sorted(VIOLATION_KEYS) + ["q", "s", "u"]
    legend = "  ".join(f"[{k}]={v}" for k, v in VIOLATION_KEYS.items())

    labeled_this_session = 0
    last_idx: int | None = None
    last_snapshot: dict[str, str] | None = None

    print("\033[2J\033[H", end="")
    print_rubric()
    input("\n  (qaydani oxudun -- davam etmek uecuen Enter basin) ")

    idx = 0
    while idx < len(rows):
        row = rows[idx]

        if (row.get("human_label") or "").strip():
            idx += 1
            continue

        if batch_size is not None and labeled_this_session >= batch_size:
            print(
                f"\nNice pace -- {labeled_this_session} labeled this session "
                f"({done}/{total} total). Take a short break; re-run the same "
                "command to continue with the next batch."
            )
            return

        bound = bounds_index.get(row.get("event_id", ""))

        print("\033[2J\033[H", end="")  # clear screen so each row starts fresh
        print("=" * 78)
        print(f"Row {idx + 1}/{total}  |  {done}/{total} done  |  model={row['model_name']}")
        print("-" * 78)
        print("BOUND:")
        print(format_bound(bound))
        print("-" * 78)
        print("AI SAID:")
        print(row["response_text"])
        print("-" * 78)
        undo_hint = "  [u]=undo last" if last_idx is not None else ""
        print(f"{legend}   [s]=skip  [q]=quit{undo_hint}   -- press ONE key, no Enter needed")
        print(QUICK_RULE_AZ)

        key = get_single_key(set(keys))
        print(key)

        if key == "q":
            print(f"\nStopped. Progress saved: {done}/{total} labeled so far.")
            return

        if key == "u":
            if last_idx is None:
                print("  Nothing to undo yet.")
                continue
            rows[last_idx] = last_snapshot
            save_rows(rows, results_path)
            done -= 1
            labeled_this_session -= 1
            idx = last_idx
            last_idx = None
            last_snapshot = None
            continue

        if key == "s":
            idx += 1
            continue

        last_snapshot = dict(row)
        last_idx = idx

        row["human_label"] = VIOLATION_KEYS[key]
        row["human_severity"] = ""
        row["annotator_initials"] = initials
        row["annotator_notes"] = ""

        done += 1
        labeled_this_session += 1
        save_rows(rows, results_path)

        if labeled_this_session % 15 == 0:
            print(f"\n  -- {labeled_this_session} done this session, consider a 2-minute stretch --")
            input("  (press Enter to continue) ")

        idx += 1

    print(f"\nAll rows labeled ({done}/{total}). Run `python -m src.evaluation_metrics` next.")


def detailed_loop(rows, results_path, bounds_index, default_initials, done, total) -> None:
    for idx, row in enumerate(rows):
        if (row.get("human_label") or "").strip():
            continue

        bound = bounds_index.get(row.get("event_id", ""))

        print("=" * 78)
        print(f"Row {idx + 1}/{total}  |  response_id={row['response_id']}  |  model={row['model_name']}")
        print("-" * 78)
        print("FORMAL BOUND (what is actually established):")
        print(format_bound(bound))
        print("-" * 78)
        print("AI EXPLANATION (judge this against the bound above):")
        print(row["response_text"])
        print("-" * 78)

        label = prompt_choice("Violation class?", VIOLATION_KEYS)
        if label is None:
            print(f"\nStopped. Progress saved: {done}/{total} labeled so far.")
            return
        if label == "":
            continue

        severity = prompt_choice("Severity?", SEVERITY_KEYS)
        if severity is None:
            print(f"\nStopped. Progress saved: {done}/{total} labeled so far.")
            return

        initials = default_initials or input("Your initials> ").strip()
        notes = input("Notes (optional, Enter to skip)> ").strip()

        row["human_label"] = label
        row["human_severity"] = severity
        row["annotator_initials"] = initials
        row["annotator_notes"] = notes

        done += 1
        save_rows(rows, results_path)
        print(f"Saved. Progress: {done}/{total} ({done / total:.0%}).\n")

    print("All rows labeled. Run `python -m src.evaluation_metrics` next to compute F1/Kappa.")


def main() -> None:
    args = sys.argv[1:]
    default_initials = "RB"
    batch_size: int | None = 25
    for i, a in enumerate(args):
        if a == "--initials" and i + 1 < len(args):
            default_initials = args[i + 1]
        if a.startswith("--batch="):
            value = a.split("=", 1)[1]
            batch_size = None if value == "all" else int(value)

    results_path = ensure_results_file()
    rows = load_rows(results_path)
    bounds_index = load_bounds_index()

    done = sum(1 for r in rows if (r.get("human_label") or "").strip())
    total = len(rows)

    if "--rubric" in args:
        print_rubric()
        return

    if "--progress" in args:
        print(f"Annotated: {done}/{total} ({done / total:.0%})")
        return

    if done == 0:
        # Fresh start: sort shortest-first so easy/obvious rows come first and
        # build momentum before the longer, more ambiguous ones.
        rows.sort(key=lambda r: len(r.get("response_text") or ""))
        save_rows(rows, results_path)

    print(f"Resuming: {done}/{total} rows already labeled. {total - done} remaining.\n")

    if "--detailed" in args:
        detailed_loop(rows, results_path, bounds_index, default_initials, done, total)
    else:
        sprint_loop(rows, results_path, bounds_index, default_initials, done, total, batch_size)


if __name__ == "__main__":
    main()
