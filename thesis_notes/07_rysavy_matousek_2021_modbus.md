# Ryšavý & Matoušek (2021) — Modbus Dataset

BibTeX: `RysavyMatousek2021Modbus`

Reference: Ryšavý, O. & Matoušek, P. (2021). Modbus Dataset for ICS Anomaly Detection.
*IEEE DataPort*, DOI: 10.21227/e1bc-3w91.

## 1. Main argument
[FACTUAL EXTRACTION -- AI-assisted, from the public IEEE DataPort listing. Cross-check
against the dataset's own README once you re-download it, since label scheme and
preprocessing were not fully documented on the public page.]
A dataset supporting research and evaluation of ICS anomaly-detection methods,
providing both normal and anomalous Modbus/TCP traffic captured from a simulated
industrial testbed.

## 2. Methodology
[Same caveat as above.]
Captured from a Factory.IO industrial-process simulator, with a soft PLC/controller
communicating over Modbus with simulated Remote Terminal Units. Covers several
simulated process "scenes" -- Assembler, Assembler Analog, Separating Station,
Sorting Station -- each shipped as its own archive (four ZIPs, ~595MB total), with
normal-communication traces and traces described as containing anomalies per scene.
A public dataset comment notes that not every attack scenario was necessarily
populated at every release stage -- worth a sanity check against whatever subset
ReasonGuard actually draws function-code-violation and replay-attack events from
(Section 4.2 of the thesis notes this dataset is not yet the source for those two
event types).

## 3. Direct relevance to ReasonGuard
This is one of the two primary VUT Brno datasets used in the empirical evaluation.
Note:
- The Modbus event categories used as the five canonical event types in the thesis.
- The label semantics, especially the difference between normal polling and function
  code violation.
- The data dictionary and any provided processing scripts.

## 4. Gap addressed by this thesis
[The dataset descriptor does not address AI explanation systems. ReasonGuard uses the
dataset as the input to the formal-bound layer rather than as the input to a
machine-learning classifier.]

## 5. Reproducibility notes
[Document the exact file paths used from this dataset and the preprocessing steps
applied before bound construction.]
