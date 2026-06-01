# ReasonGuard

Runtime verification of AI reasoning faithfulness against formally verified bounds.

This repository contains the implementation, evaluation, and supporting material for the
MSc Applied Data Science and Analytics thesis submitted at SRH University Hamburg in
collaboration with the Faculty of Information Technology, Brno University of Technology
(VUT). The thesis investigates whether the output of a formal automaton-based ICS
detection system can be reused as a machine-readable runtime bound against which AI
reasoning explanations are verified.

## Motivation

Large language models are increasingly used to translate the output of formally verified
detection systems into natural-language explanations for human operators. In
safety-critical environments such as industrial control systems, an explanation that
fabricates, contradicts, over-generalises, under-specifies, or is internally incoherent
can cause incorrect operational decisions. ReasonGuard treats the formal verdict as a
bound and classifies any reasoning that crosses that bound into the V1–V5 taxonomy.

## Repository layout

```
src/                                # Production source code
  pipeline_config.py                # Paths, model names, MLflow URIs, run parameters
  formal_bound_builder.py           # Raw IEC-104 rows -> JSON formal bounds
  event_type_classifier.py          # Proxy event-type assignment (5 ICS classes)
  prompt_builder.py                 # Bounds -> strict LLM prompts (stratified sampling)
  synthetic_response_generator.py   # Synthetic V1-V5 + clean responses (regression set)
  ollama_llm_runner.py              # Local LLM inference via Ollama
  cloud_llm_runner.py               # Cloud LLM inference (OpenAI, Gemini)
  reason_guard_checker.py           # V1-V5 detection + severity + per-claim verdicts
  claim_extraction/                 # spaCy NER, three-state classifier, negation, V5
  evaluation_metrics.py             # Precision, recall, F1, accuracy, Cohen's Kappa
  event_analysis.py                 # Per-model x event-type breakdown
  viz.py                            # Matplotlib figures (per-model rates, confusion)
  manual_annotation.py              # CSV annotation seed + inter-rater agreement
  mlflow_tracker.py                 # MLflow integration with safe no-op fallback
  prepare_meeting_pack.py           # Auto-generated pipeline stats markdown
  merge_ollama_responses.py         # Recover combined JSONL after partial runs
  status_cli.py                     # One-screen project status snapshot
  demo_walkthrough.py               # 5-minute meeting demo
  dashboard/                        # Streamlit verification dashboard skeleton

data/                              # Raw and processed dataset artefacts (gitignored)
outputs/                           # Generated artefacts; figures + reports
  figures/                         # PNG figures for the meeting and the thesis
annotation/                        # Manual annotation CSVs
meeting_pack/                      # Weekly meeting artefacts for the assistant
reports/                           # Weekly progress reports (W9-W14)
thesis_notes/                      # Reading notes for the eight required papers
thesis/                            # Overleaf-ready LaTeX manuscript
  chapters/                        # Chapters 1-7
  appendices/                      # Appendices A-C
  references.bib                   # BibTeX entries
tests/                             # pytest suite (80+ cases)
archive/                           # Legacy v1/v2 prototypes
```

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_lg
```

For the local-LLM runs, install Ollama and pull the configured models:

```bash
brew install ollama          # or platform equivalent
ollama serve &                # start the local server
ollama pull llama3.1:8b-instruct-q4_0
ollama pull mistral:7b-instruct-v0.3-q4_0
ollama pull phi3:mini
```

## End-to-end pipeline

```
data/raw/sample_003.csv
  -> python -m src.formal_bound_builder
  -> outputs/formal_bounds_sample_003.jsonl

outputs/formal_bounds_sample_003.jsonl
  -> REASONGUARD_STRATIFY=1 REASONGUARD_PER_EVENT_TYPE=25 python -m src.prompt_builder
  -> outputs/llm_prompts_sample_003.jsonl

outputs/llm_prompts_sample_003.jsonl
  -> python -m src.synthetic_response_generator
  -> python -m src.ollama_llm_runner
  -> outputs/*_responses_*.jsonl

outputs/*_responses_*.jsonl
  -> python -m src.reason_guard_checker
  -> outputs/reason_guard_report.json

outputs/reason_guard_report.json
  -> python -m src.event_analysis
  -> outputs/event_type_analysis.{json,csv,md}

  -> python -m src.viz
  -> outputs/figures/{violation_rate_per_model,clean_rate_per_model,confusion_matrix}.png

  -> python -m src.evaluation_metrics
  -> outputs/evaluation_metrics.{json,md}
```

## Useful commands

| Command | Purpose |
| --- | --- |
| `python -m src.status_cli` | One-screen project status snapshot |
| `python -m src.demo_walkthrough` | Five-minute meeting demo |
| `python -m src.prepare_meeting_pack` | Refresh the auto-generated pipeline stats |
| `python -m src.merge_ollama_responses` | Rebuild the combined JSONL after a partial run |
| `streamlit run src/dashboard/app.py` | Launch the Streamlit dashboard |
| `python -m pytest tests/` | Run the test suite |
| `ruff check src/ tests/` | Lint the codebase |

## Environment variables

| Variable | Purpose |
| --- | --- |
| `REASONGUARD_STRATIFY` | When set, prompt_builder samples bounds per event type |
| `REASONGUARD_PER_EVENT_TYPE` | Sample size per event type for stratified prompts |
| `REASONGUARD_OLLAMA_MODELS` | Comma-separated subset of local models to run |
| `REASONGUARD_PILOT_LIMIT` | Prompt limit per Ollama model |
| `REASONGUARD_CLOUD_PILOT_LIMIT` | Prompt limit per cloud provider |
| `OPENAI_API_KEY` | Bearer token for OpenAI Chat Completions |
| `GEMINI_API_KEY` | API key for Gemini generateContent |

## Status — schema caveat

The formal class field is currently generated by an internal proxy classifier and is
labelled `proxy_until_official_automaton_schema`. Once the official automaton output
schema from the NES@FIT group at VUT Brno is integrated, the proxy field will be
replaced and the classifier upgraded. Until then, no run claims a ground-truth attack
label.

## Licence

MIT (planned, pending supervisor confirmation).
