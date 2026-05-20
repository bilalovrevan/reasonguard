from pathlib import Path
import json
import pandas as pd


OUTPUT_DIR = Path("outputs")
MEETING_DIR = Path("meeting_pack")
MEETING_DIR.mkdir(exist_ok=True)

REQUIRED_FILES = {
    "formal_bounds": OUTPUT_DIR / "formal_bounds_sample_003.jsonl",
    "prompts": OUTPUT_DIR / "llm_prompts_sample_003.jsonl",
    "synthetic_responses": OUTPUT_DIR / "synthetic_llm_responses_sample_003.jsonl",
    "reason_guard_report": OUTPUT_DIR / "reason_guard_report.json",
    "reason_guard_summary": OUTPUT_DIR / "reason_guard_summary.json",
    "reason_guard_summary_csv": OUTPUT_DIR / "reason_guard_summary.csv",
}


def load_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def load_jsonl(path: Path) -> list[dict]:
    records = []
    with open(path, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def check_required_files() -> None:
    missing = []

    for name, path in REQUIRED_FILES.items():
        if not path.exists():
            missing.append(f"{name}: {path}")

    if missing:
        raise FileNotFoundError(
            "The following required output files are missing:\n"
            + "\n".join(missing)
            + "\nRun python run_pipeline.py first."
        )


def build_markdown_report() -> str:
    bounds = load_jsonl(REQUIRED_FILES["formal_bounds"])
    prompts = load_jsonl(REQUIRED_FILES["prompts"])
    responses = load_jsonl(REQUIRED_FILES["synthetic_responses"])
    report = load_json(REQUIRED_FILES["reason_guard_report"])
    summary = report["summary"]
    results = report["results"]

    first_bound = bounds[0]
    first_prompt = prompts[0]
    first_result = next(item for item in results if "error" not in item)

    lines = []

    lines.append("# ReasonGuard Meeting Pack")
    lines.append("")
    lines.append("## 1. Current project status")
    lines.append("")
    lines.append("I have implemented a first end-to-end vertical prototype of the ReasonGuard pipeline.")
    lines.append("")
    lines.append("Current working pipeline:")
    lines.append("")
    lines.append("```text")
    lines.append("sample_003.csv")
    lines.append("  -> formal_bound_builder.py")
    lines.append("  -> formal_bounds_sample_003.jsonl")
    lines.append("  -> prompt_builder.py")
    lines.append("  -> llm_prompts_sample_003.jsonl")
    lines.append("  -> synthetic_response_generator.py")
    lines.append("  -> synthetic_llm_responses_sample_003.jsonl")
    lines.append("  -> reason_guard_checker.py")
    lines.append("  -> reason_guard_report.json / reason_guard_summary.csv")
    lines.append("```")
    lines.append("")

    lines.append("## 2. What has been completed")
    lines.append("")
    lines.append(f"- Formal bounds generated: {len(bounds)}")
    lines.append(f"- LLM prompts generated: {len(prompts)}")
    lines.append(f"- Synthetic LLM responses generated: {len(responses)}")
    lines.append(f"- ReasonGuard responses analysed: {summary['total_responses']}")
    lines.append(f"- No violation: {summary['no_violation']}")
    lines.append(f"- V1 fabricated reasoning: {summary['V1_fabricated_reasoning']}")
    lines.append(f"- V2 contradicted reasoning: {summary['V2_contradicted_reasoning']}")
    lines.append(f"- V3 over-generalised reasoning: {summary['V3_over_generalised_reasoning']}")
    lines.append(f"- V4 under-specified reasoning: {summary['V4_under_specified_reasoning']}")
    lines.append(f"- V5 incoherent reasoning: {summary['V5_incoherent_reasoning']}")
    lines.append("")

    lines.append("## 3. Formal bound example")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(first_bound, indent=2))
    lines.append("```")
    lines.append("")

    lines.append("## 4. Prompt example")
    lines.append("")
    lines.append("### System prompt")
    lines.append("")
    lines.append("```text")
    lines.append(first_prompt["system_prompt"])
    lines.append("```")
    lines.append("")
    lines.append("### User prompt")
    lines.append("")
    lines.append("```text")
    lines.append(first_prompt["user_prompt"])
    lines.append("```")
    lines.append("")

    lines.append("## 5. ReasonGuard output example")
    lines.append("")
    lines.append("```json")
    lines.append(json.dumps(first_result, indent=2))
    lines.append("```")
    lines.append("")

    lines.append("## 6. Important limitation")
    lines.append("")
    lines.append(
        "The current formal class is still a proxy observation label, because the official automaton output schema has not yet been integrated. "
        "Therefore, the current prototype demonstrates the verification architecture and V1-V5 checking logic, but it does not yet claim final domain-ground-truth attack labels."
    )
    lines.append("")

    lines.append("## 7. Immediate next steps")
    lines.append("")
    lines.append("1. Confirm whether the proxy formal bound schema is acceptable until the official automaton schema is available.")
    lines.append("2. Replace synthetic responses with real local LLM outputs from Ollama.")
    lines.append("3. Run a 100-event pilot with one local model.")
    lines.append("4. Save each model response in the same JSONL format.")
    lines.append("5. Run ReasonGuard on real LLM responses.")
    lines.append("6. Start manual annotation of 50-100 outputs.")
    lines.append("7. Prepare methodology text for the thesis in Overleaf.")
    lines.append("")

    lines.append("## 8. Questions for supervisor assistant")
    lines.append("")
    lines.append("1. Is the current JSON formal bound structure acceptable as an interim schema?")
    lines.append("2. Which fields from the official automaton output should be mandatory in the final bound?")
    lines.append("3. Should the evaluation start with IEC-104 only, or should Modbus be integrated immediately?")
    lines.append("4. Is synthetic response testing acceptable as a software validation step before real LLM inference?")
    lines.append("5. For the first pilot, is 100 events x 1 model sufficient?")
    lines.append("")

    return "\n".join(lines)


def build_short_talking_points() -> str:
    return """# 3-Minute Meeting Talking Points

## What I built
I built a first end-to-end vertical prototype of ReasonGuard. It takes a sample IEC-104 dataset, converts each row into a machine-readable formal bound, builds LLM prompts from those bounds, generates test explanations, and checks those explanations against the V1-V5 violation taxonomy.

## What works now
The current pipeline produces:
- formal JSON bounds,
- LLM-ready prompts,
- synthetic explanation responses,
- ReasonGuard violation reports,
- summary CSV and JSON results.

## Why synthetic responses are used now
I used synthetic responses first to test whether the violation checker correctly detects fabricated reasoning, contradicted reasoning, over-generalisation, under-specification, and incoherence before running real LLMs.

## Current limitation
The formal class is currently a proxy observation label because the official automaton output schema is not yet integrated. I am not treating it as a final attack label.

## What I need feedback on
I need feedback on whether my current formal bound schema is acceptable as an interim structure and which fields should be mandatory once the official automaton schema is available.

## Next step
My next technical step is to replace synthetic responses with real local LLM responses and run a 100-event pilot.
"""


def main() -> None:
    check_required_files()

    meeting_report = build_markdown_report()
    talking_points = build_short_talking_points()

    report_path = MEETING_DIR / "reason_guard_meeting_pack.md"
    talking_points_path = MEETING_DIR / "talking_points_3_min.md"

    report_path.write_text(meeting_report, encoding="utf-8")
    talking_points_path.write_text(talking_points, encoding="utf-8")

    if REQUIRED_FILES["reason_guard_summary_csv"].exists():
        df = pd.read_csv(REQUIRED_FILES["reason_guard_summary_csv"])
        df.to_csv(MEETING_DIR / "reason_guard_summary_for_meeting.csv", index=False)

    print("Meeting pack created successfully.")
    print(f"Main report: {report_path}")
    print(f"Talking points: {talking_points_path}")
    print(f"CSV summary: {MEETING_DIR / 'reason_guard_summary_for_meeting.csv'}")


if __name__ == "__main__":
    main()