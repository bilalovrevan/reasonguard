from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"

OUTPUT_DIR = PROJECT_ROOT / "outputs"
REPORTS_DIR = PROJECT_ROOT / "reports"
MEETING_PACK_DIR = PROJECT_ROOT / "meeting_pack"
THESIS_NOTES_DIR = PROJECT_ROOT / "thesis_notes"
THESIS_DIR = PROJECT_ROOT / "thesis"
ANNOTATION_DIR = PROJECT_ROOT / "annotation"

MLFLOW_TRACKING_DB = PROJECT_ROOT / "mlflow.db"
MLFLOW_TRACKING_URI = f"sqlite:///{MLFLOW_TRACKING_DB}"
MLFLOW_ARTIFACT_DIR = PROJECT_ROOT / "mlruns"

SAMPLE_INPUT_FILE = RAW_DATA_DIR / "sample_003.csv"

FORMAL_BOUNDS_JSON = OUTPUT_DIR / "formal_bounds_sample_003.json"
FORMAL_BOUNDS_JSONL = OUTPUT_DIR / "formal_bounds_sample_003.jsonl"
FORMAL_BOUNDS_PREVIEW = OUTPUT_DIR / "formal_bounds_preview.txt"
FORMAL_BOUNDS_SUMMARY = OUTPUT_DIR / "formal_bounds_summary.json"

LLM_PROMPTS_JSON = OUTPUT_DIR / "llm_prompts_sample_003.json"
LLM_PROMPTS_JSONL = OUTPUT_DIR / "llm_prompts_sample_003.jsonl"
LLM_PROMPTS_PREVIEW = OUTPUT_DIR / "llm_prompts_preview.txt"

SYNTHETIC_RESPONSES_JSON = OUTPUT_DIR / "synthetic_llm_responses_sample_003.json"
SYNTHETIC_RESPONSES_JSONL = OUTPUT_DIR / "synthetic_llm_responses_sample_003.jsonl"
SYNTHETIC_RESPONSES_PREVIEW = OUTPUT_DIR / "synthetic_llm_responses_preview.txt"

OLLAMA_RESPONSES_JSON = OUTPUT_DIR / "ollama_llm_responses_sample_003.json"
OLLAMA_RESPONSES_JSONL = OUTPUT_DIR / "ollama_llm_responses_sample_003.jsonl"
OLLAMA_RESPONSES_PREVIEW = OUTPUT_DIR / "ollama_llm_responses_preview.txt"

REASONGUARD_REPORT_JSON = OUTPUT_DIR / "reason_guard_report.json"
REASONGUARD_REPORT_JSONL = OUTPUT_DIR / "reason_guard_report.jsonl"
REASONGUARD_SUMMARY_JSON = OUTPUT_DIR / "reason_guard_summary.json"
REASONGUARD_SUMMARY_CSV = OUTPUT_DIR / "reason_guard_summary.csv"
REASONGUARD_PREVIEW = OUTPUT_DIR / "reason_guard_preview.txt"

MEETING_REPORT_MD = MEETING_PACK_DIR / "reason_guard_meeting_pack.md"
MEETING_TALKING_POINTS_MD = MEETING_PACK_DIR / "talking_points_3_min.md"
MEETING_SUMMARY_CSV = MEETING_PACK_DIR / "reason_guard_summary_for_meeting.csv"

ANNOTATION_INPUT_CSV = ANNOTATION_DIR / "annotation_batch.csv"
ANNOTATION_RESULTS_CSV = ANNOTATION_DIR / "annotation_results.csv"

DATASET_NAME = "eon_iec"
EVENT_GRANULARITY = "atomic_row"
FORMAL_BOUND_VERSION = "2.1"

MAX_PROMPT_EVENTS = 100
SYNTHETIC_RESPONSES_PER_PROMPT = 5

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_PILOT_LIMIT = 20
OLLAMA_TEMPERATURE = 0.1
OLLAMA_TOP_P = 0.9
OLLAMA_TIMEOUT_SECONDS = 180

OLLAMA_MODELS = [
    "llama3.1:8b-instruct-q4_0",
    "mistral:7b-instruct-v0.3-q4_0",
    "phi3:mini",
]
OLLAMA_MODEL = OLLAMA_MODELS[0]

EVENT_TYPES = [
    "normal_modbus_polling",
    "function_code_violation",
    "network_scan",
    "replay_attack",
    "topology_change",
]

RANDOM_SEED = 42

MLFLOW_EXPERIMENT_FORMAL_BOUNDS = "reasonguard_formal_bounds"
MLFLOW_EXPERIMENT_PROMPTS = "reasonguard_prompts"
MLFLOW_EXPERIMENT_SYNTHETIC = "reasonguard_synthetic_responses"
MLFLOW_EXPERIMENT_OLLAMA = "reasonguard_ollama_responses"
MLFLOW_EXPERIMENT_CHECKER = "reasonguard_violation_checker"


def ensure_project_directories() -> None:
    directories = [
        DATA_DIR,
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        OUTPUT_DIR,
        REPORTS_DIR,
        MEETING_PACK_DIR,
        THESIS_NOTES_DIR,
        THESIS_DIR,
        ANNOTATION_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
