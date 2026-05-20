# Matoušek, Ryšavý & Grofčík (2022) — Smart Grid Dataset

BibTeX: `MatousekRysavyGrofcik2022SmartGrid`

Reference: Matoušek, P., Ryšavý, O. & Grofčík, R. (2022). ICS Dataset for Smart Grid
Anomaly Detection. *IEEE DataPort*, DOI: 10.21227/1trw-n685.

## 1. Main argument
[Dataset descriptor: state the purpose of the dataset, the testbed used to capture
the data, and the event categories represented.]

## 2. Methodology
[Describe the dataset capture protocol, the IEC-104 specific labelling decisions, the
size of the dataset, and any preprocessing applied before release.]

## 3. Direct relevance to ReasonGuard
This is the IEC-104 dataset used in the current evaluation block. The Eon-IEC subset
provides the rows that are converted into formal bounds by the pipeline. Note:
- The event categories specific to IEC-104.
- The data dictionary and the column semantics used by `formal_bound_builder.py`.
- The relationship between this dataset and the Holík et al. (2023) automaton paper.

## 4. Gap addressed by this thesis
[The dataset descriptor does not address AI explanation systems. ReasonGuard uses the
dataset as the input to the formal-bound layer.]

## 5. Reproducibility notes
[Document the exact subsets used (Datasets 004/eon-iec and the
`dedup_eon_iec_vut_processed-002.csv` file), the row sampling strategy, and the
preprocessing steps applied before bound construction.]
