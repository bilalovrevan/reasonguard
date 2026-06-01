from __future__ import annotations

import shutil

from src.pipeline_config import (
    OLLAMA_RESPONSES_JSONL,
    REASONGUARD_REPORT_JSON,
    REASONGUARD_SUMMARY_CSV,
    SYNTHETIC_RESPONSES_JSONL,
)


def main() -> None:
    if not OLLAMA_RESPONSES_JSONL.exists():
        raise FileNotFoundError(
            f"Ollama responses not found: {OLLAMA_RESPONSES_JSONL}\n"
            "Run: python -m src.ollama_llm_runner"
        )

    backup_file = SYNTHETIC_RESPONSES_JSONL.with_suffix(".synthetic_backup.jsonl")

    if SYNTHETIC_RESPONSES_JSONL.exists():
        shutil.copy2(SYNTHETIC_RESPONSES_JSONL, backup_file)

    shutil.copy2(OLLAMA_RESPONSES_JSONL, SYNTHETIC_RESPONSES_JSONL)

    print("Temporary response source switched to Ollama outputs.")
    print(f"Ollama file: {OLLAMA_RESPONSES_JSONL}")
    print(f"Checker input: {SYNTHETIC_RESPONSES_JSONL}")
    print("")
    print("Now run:")
    print("python -m src.reason_guard_checker")
    print("")
    print("After that, check:")
    print(f"- {REASONGUARD_REPORT_JSON}")
    print(f"- {REASONGUARD_SUMMARY_CSV}")


if __name__ == "__main__":
    main()
