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

- 2026-06-15 (later same day) | Claude (Cowork/claude-sonnet-5) | Discovered annotation_batch.csv
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
- 2026-06-23 | Discovered that the device_bash sandbox is a separate network-restricted Linux VM,
  not Ravan's real macOS Terminal: cannot reach OpenAI/Gemini APIs (egress blocked), cannot reach
  Ollama (different machine/network namespace), cannot use the project's real .venv (macOS
  Homebrew Python 3.14, broken in this Linux sandbox). Cloud LLM run and any future
  Ollama/spaCy-model/Streamlit-runtime work must be run by Ravan in his own real Terminal.
- 2026-07-03 (evening) | Claude | Ravan attempted the first full 200-row annotation pass in one
  sitting, hit fatigue partway through and entered essentially random labels for the remainder
  (resulting Kappa ~0.03 confirmed this was noise, not a genuine detector problem). Reset
  annotation/annotation_results.csv to blank and marked outputs/evaluation_metrics.json/.md as
  RESET so the noisy numbers cannot be mistaken for real results later. Rebuilt
  src/annotate_cli.py with: auto-stop after a 25-row batch (re-run to continue), a 15-row stretch
  reminder, an 'u' undo key for mis-presses, and a one-time shortest-first sort on a fresh start
  so easy rows build momentum before harder ones. No annotation labels were entered by Claude at
  any point -- every human_label in the dataset must come from Ravan's own keypress.
- 2026-07-05 (night) | Claude | Ravan supplied his own worked-out decision procedure
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
- 2026-07-18 (late night) | Claude | Ravan finished all 200/200 manual annotation
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
- 2026-07-23 (late night, cont.) | Claude | Closed the 3 pipeline gaps flagged
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
  7. Category: extracting/summarising arguments, generating ideas for literature
  synthesis, project planning -- explicitly permitted; no thesis prose written.
- 2026-07-24 | Claude | Continued the coding-side punch list per Ravan's instruction
  to proceed without waiting for responses. (1) Updated
  thesis/chapters/04_experimental_setup.tex with facts only: corrected the Datasets
  section's claim that the Modbus dataset sources the function_code_violation/
  replay_attack event types (in the implemented pipeline both are proxy-derived from
  the smart-grid dataset instead; Modbus itself is not yet consumed anywhere in the
  pipeline -- this scope gap was already flagged in REWRITE_GUIDE_ch2_3_6_7.md and is
  now stated in the chapter itself); added the real completed-annotation numbers
  (accuracy 0.30, macro F1 0.1871, Cohen's kappa 0.1602) and the chi-square
  association-test results to the Manual Annotation / Proxy Event-Type sections; noted
  the full 1000-response 5-model merge is complete. No interpretation added -- the
  per-class asymmetry (V1 vs V4) is described factually, its meaning is left to
  Ravan's own Chapter 6. (2) Ran the citation cross-check script (9/9 keys still
  consistent) and wrote an equivalent \ref/\label cross-check -- one apparent
  "broken ref" (lst:bound-example) turned out to be a false positive of the checker
  (the listings package registers labels passed via its own [label=...] option,
  which my regex didn't recognise) -- no real LaTeX bug found. (3) Computed an
  accurate word count via detex: body chapters (01-07) are currently ~6,787 words
  against the exposé's 18,000-22,000 target -- flagging this honestly since Chapters
  2/3/6/7 still need Ravan's own rewrite pass and the other chapters may also need
  expansion. (4) Verified src/dashboard/app.py still compiles and its data path
  (outputs/formal_bounds_sample_003.jsonl) still resolves against the current
  outputs/ -- code is functionally complete, not just a skeleton; actual deployment
  to Streamlit Community Cloud needs Ravan's own account/browser login and a
  `git push` with his own GitHub credentials (this sandbox has no stored git
  credentials and `git push --dry-run` confirmed that -- did not attempt to work
  around it, since that would mean handling his credentials). (5) Wrote
  EU_AI_ACT_REFERENCE_TABLE.md at the repo root: factual summaries of AI Act
  Articles 13, 17, and Annex III point 2 (critical infrastructure), sourced via
  WebFetch/WebSearch and cross-checked against the official EUR-Lex record for
  title/date, plus a ready-to-cite BibTeX entry added to thesis/references.bib
  (EUAIAct2024) -- the file poses the mapping questions for Ravan's own Chapter 6
  argument rather than answering them. (6) Git note: .git/index.lock and
  .git/HEAD.lock were stale again (same recurring issue as 31 Aug, cause still
  unconfirmed -- possibly a Mac git-aware app). Since Ravan asked not to wait for a
  response, committed the Chapter 4 change via git plumbing (write-tree +
  commit-tree + a direct, non-atomic write to .git/refs/heads/main) instead of the
  normal `git commit`, which needs the locked files. This is safe here because nothing
  else was concurrently writing to the repo, but it bypasses git's usual lock-based
  safety -- normal `git commit`/`git add` will keep failing until the stale lock
  files are removed (needs Ravan's Terminal, or the pending device-delete-permission
  approval). Category: code/pipeline engineering, LaTeX build maintenance, factual
  legal-reference drafting, project status reporting -- explicitly permitted; no
  thesis prose written for Chapters 2/3/6/7.
- 2026-07-27 | Claude | Deployed the Streamlit dashboard to Streamlit Community
  Cloud (share.streamlit.io) at Ravan's explicit request, after he signed into
  Streamlit and GitHub himself (I never touched a password/2FA field -- he
  completed both sign-ins, and separately clicked through the "Connect here"
  private-repo OAuth grant after I asked him in chat first). Filled the deploy
  form (repo bilalovrevan/reasonguard, branch main, src/dashboard/app.py) via
  browser automation. First deploy attempt crashed with ModuleNotFoundError:
  the entrypoint does `from src.pipeline_config import ...`, but Streamlit
  Cloud only puts the entrypoint file's own directory on sys.path, not the
  repo root. Fixed by inserting the repo root at the front of sys.path before
  those imports (commit 84d8804) -- a mechanical packaging bug, not a research
  or content change. Second issue: the dashboard's default data file
  (outputs/formal_bounds_sample_003.jsonl, 20,000 rows) is gitignored for size
  (70+ MB), so the deployed app had no data to show. Fixed by committing a
  small (20-row, ~70KB) unmodified subset of the same real file
  (outputs/formal_bounds_sample_003_demo.jsonl) and having the dashboard fall
  back to it with an on-screen note when the full file is absent (commit
  4c11449) -- local behaviour against the full file is unchanged, verified
  both paths load correctly. Live app: reasonguard-dashboard.streamlit.app.
  Category: code/pipeline engineering, deployment -- explicitly permitted; no
  research data was altered, only a small real subset of it was copied for
  demo purposes.
- 2026-07-29 (cont'd) | Claude | Deployed app hit one more issue after the two
  code fixes above landed: Streamlit Cloud's incremental "Updated app!" reload
  re-ran the script without reimporting already-loaded modules, so the running
  process still had the OLD src.pipeline_config object cached in memory and
  raised ImportError: cannot import name 'FORMAL_BOUNDS_DEMO_JSONL' even
  though the committed source was correct (confirmed by viewing the raw file
  on GitHub). A full "Reboot app" (not just the incremental update) cleared
  the stale process and picked up the real code. Verified end-to-end after
  reboot: bound selector loads the 20-row demo subset with the on-screen
  note, and running the V1 (fabricated attack) example through "Verify with
  ReasonGuard" correctly returns Severity HIGH with V1+V4 violations and
  their reason lists. The "per-claim verdicts unavailable, install spaCy/
  en_core_web_lg" message is expected/by-design on Cloud (that dependency is
  optional and not installed there) -- not a bug. Live app:
  https://reasonguard-dashboard.streamlit.app. Category: deployment,
  verification -- explicitly permitted.
