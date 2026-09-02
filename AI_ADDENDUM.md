# AI Tool Disclosure Addendum — ReasonGuard Thesis

Per SRH "Generative AI in Research" policy: AI tools are disclosed here with what
they were used for and are NOT used to generate the final prose of the literature
review, theoretical framework, discussion, or conclusion chapters. Those chapters
are authored by Ravan Bilalov personally; AI involvement there is limited to
language/editing feedback, logged below.

Format per entry: date | tool | what was done | chapters/files touched | category
(permitted categories: code/pipeline engineering [explicitly endorsed by the
exposé itself], data processing, annotation tooling, factual table generation,
language/editing feedback on author-written text, project planning).

## Log

- 2026-08-31 | Claude (Cowork/claude-sonnet-5) | Audited repository state, read
  exposé and thesis guide, produced SEPT15_COMPLETION_PLAN.md, this addendum
  file. Category: project planning / documentation, no thesis prose generated.
- 2026-08-31 (later same day) | Claude (Cowork/claude-sonnet-5) | Discovered annotation_batch.csv
  was stale (50 rows, 49 synthetic, 0 labeled) and unrepresentative; regenerated to 200 rows via
  src/manual_annotation.py (patched to accept --size), now 86 real LLM / 114 synthetic. Wrote
  src/annotate_cli.py (fast terminal labeling tool). Wrote src/prepare_expert_review_package.py
  and ran it to build the VUT Brno M5 blind 50-sample package (sent by Ravan same day). Fixed
  retired gemini-1.5-flash default to gemini-2.5-flash-lite in src/cloud_llm_runner.py. Ran the
  existing pytest suite (90 tests) after installing pytest/streamlit in the local sandbox: all
  runnable tests pass, 10 skipped for optional heavy deps (spaCy model, mlflow) not available in
  this sandbox. Drafted factual table updates to thesis/chapters/04_experimental_setup.tex
  (preprocessing row counts, column dictionary, corrected stale gemini-1.5-flash reference,
  corrected manual-annotation section to describe the 200-row batch) -- numbers/tables only, no
  interpretive prose, for Ravan's review. Category: code/pipeline engineering, data processing,
  annotation tooling, factual table drafting -- all explicitly permitted categories.
- 2026-08-31 | Discovered that the device_bash sandbox is a separate network-restricted Linux VM,
  not Ravan's real macOS Terminal: cannot reach OpenAI/Gemini APIs (egress blocked), cannot reach
  Ollama (different machine/network namespace), cannot use the project's real .venv (macOS
  Homebrew Python 3.14, broken in this Linux sandbox). Cloud LLM run and any future
  Ollama/spaCy-model/Streamlit-runtime work must be run by Ravan in his own real Terminal.
- 2026-08-31 (evening) | Claude | Ravan attempted the first full 200-row annotation pass in one
  sitting, hit fatigue partway through and entered essentially random labels for the remainder
  (resulting Kappa ~0.03 confirmed this was noise, not a genuine detector problem). Reset
  annotation/annotation_results.csv to blank and marked outputs/evaluation_metrics.json/.md as
  RESET so the noisy numbers cannot be mistaken for real results later. Rebuilt
  src/annotate_cli.py with: auto-stop after a 25-row batch (re-run to continue), a 15-row stretch
  reminder, an 'u' undo key for mis-presses, and a one-time shortest-first sort on a fresh start
  so easy rows build momentum before harder ones. No annotation labels were entered by Claude at
  any point -- every human_label in the dataset must come from Ravan's own keypress.
- 2026-08-31 (night) | Claude | Ravan supplied his own worked-out decision procedure
  for applying V1-V5 (in Azerbaijani, his working language) -- a fixed check order
  (Forbidden claims first -> Required-to-mention omissions -> lost specificity ->
  self-contradiction -> else NONE) meant to replace gut-feel guessing with a
  repeatable rule, directly targeting the fatigue-driven noise from the earlier
  full-200 attempt. Embedded it verbatim in src/annotate_cli.py as RUBRIC_AZ: shown
  in full once at the start of every sprint batch (gated behind an Enter press so
  it's actually read, not skipped) and as a condensed one-line reminder on every
  row; added a `--rubric` flag to print it on demand. No annotation labels were
  entered by Claude -- every human_label still comes from Ravan's own keypress.
  Category: annotation tooling.
- 2026-08-31 (late night) | Claude | Ravan finished all 200/200 manual annotation
  rows in one sitting using the rubric-guided sprint tool (well ahead of the Day
  1-4 schedule in SEPT15_COMPLETION_PLAN.md). Ran src/evaluation_metrics.py for
  real: Accuracy 0.30, Macro F1 0.1871, Cohen's Kappa 0.1602 -- both below the
  expose's stated bar (F1>0.80, Kappa>0.70). Investigated the gap by inspecting
  src/reason_guard_checker.py: detect_v4_under_specified_reasoning() flags V4
  whenever ANY ONE of five separate fields (source/destination/port/ASDU/proxy-
  uncertainty phrasing) is missing, which fires on 110/200 rows (55%) vs Ravan's
  own 25/200 (12.5%) human V4 count -- a plausible, evidence-backed root cause
  for most of the score gap (his own decision rule treats V4 as specifically the
  proxy/uncertainty-caveat omission, not all four traffic fields). Asked Ravan
  whether to patch the rule and recompute, inspect examples first, or keep the
  current numbers as-is; he chose to leave the classifier untouched given the
  15 Sep deadline. outputs/evaluation_metrics.json/.md now hold these numbers as
  the final, honestly-reported result -- the V4-overtrigger pattern is a known,
  disclosed limitation for Chapter 5/6, not a bug hidden from the reader.
  Category: data processing / evaluation, project planning. No thesis prose
  written; interpretation of what this means is Ravan's own to draft.
- 2026-08-31 (late night, cont.) | Claude | Closed the 3 pipeline gaps flagged
  when Ravan asked for a % status: (1) the 200 cloud-model responses
  (gpt-4o-mini + gemini-2.5-flash-lite, generated earlier today) had never been
  run through src/reason_guard_checker.py -- re-ran it, reason_guard_report
  now covers all 1000 responses across 5 real models + synthetic (was 800,
  3 local models + synthetic only). (2) Added a chi-square test of
  independence (violation category vs. model, and vs. proxy event type) to
  src/event_analysis.py -- this did not exist in the codebase at all before
  today despite being named in the exposé/plan; added scipy>=1.11 to
  requirements.txt since the test needs it. Both tests reject H0 at p<0.001:
  violation category is statistically associated with which model produced
  the response and with the proxy event type. (3) Regenerated
  outputs/figures/ (violation/clean rate per model, confusion matrix) against
  the full 5-model report -- it already supported this, it just hadn't been
  re-run since the cloud merge. Manual annotation (200/200) and its
  evaluation_metrics were left untouched -- they were built and finished
  before the cloud responses existed, and re-sampling now would have wasted
  Ravan's annotation work for no real gain (the checker's generalisation is
  still validly tested against 3 local models + synthetic). Category:
  code/pipeline engineering, data processing -- explicitly permitted.
- 2026-08-31 (past midnight, Ravan asleep) | Claude | Ravan asked whether writing his
  own argument in Azerbaijani and having it translated to grammatical English would
  be detectable as AI -- answered honestly: yes, AI-detection tools score the
  produced English text's own statistics, not the provenance of the underlying idea,
  so translation is not a safe way to hide AI involvement; the safe/permitted path is
  Ravan composing his own paragraphs and Claude giving language-only feedback on text
  he already wrote, disclosed as such. He then authorised, before going to sleep,
  finding the 8 cited papers online and factually summarising them (an explicitly
  permitted "extract and summarise" use), since thesis_notes/01-08 turned out to
  still be empty templates despite SEPT15_COMPLETION_PLAN.md claiming this milestone
  was done -- that claim was wrong and is corrected here. Used WebSearch/WebFetch to
  find each paper's public abstract/listing and filled in the "Main argument" and
  "Methodology" sections of all 8 notes with factual, AI-assisted extraction only
  (flagged inline wherever the full text was paywalled/unverified so Ravan knows to
  double-check before citing) -- left sections 3-5 (relevance to ReasonGuard, gap
  addressed, quotations) untouched, since connecting these papers to his own thesis
  argument is exactly the interpretive step that has to be his. Also wrote
  REWRITE_GUIDE_ch2_3_6_7.md at the repo root: a structure-and-fact-pointer document
  (no chapter prose) flagging, section by section, what real result/number from
  today's work (F1/Kappa, chi-square, the V4-overtrigger finding, the dataset-
  sourcing gap for function_code_violation/replay_attack) should replace or ground
  the existing pre-results draft text in Chapters 2, 3 (interpretive parts), 6, and
  7. Category: extracting/summarising arguments, generating ideas for literature
  synthesis, project planning -- explicitly permitted; no thesis prose written.
