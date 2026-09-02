# Matoušek, Ryšavý & Grofčík (2022) — Smart Grid Dataset

BibTeX: `MatousekRysavyGrofcik2022SmartGrid`

Reference: Matoušek, P., Ryšavý, O. & Grofčík, R. (2022). ICS Dataset for Smart Grid
Anomaly Detection. *IEEE DataPort*, DOI: 10.21227/1trw-n685.

## 1. Main argument
[FACTUAL EXTRACTION -- AI-assisted, from the public IEEE DataPort listing. Cross-check
against the dataset's own README/documentation for the exact labelling methodology.]
A dataset supporting smart-grid ICS security monitoring and anomaly-detection
research, providing labeled network communication traces with both normal and
attack traffic, covering IEC 60870-104 and IEC 61850 (MMS) protocols -- this is the
dataset behind the thesis's working file data/raw/sample_003.csv (eon-iec subset).

## 2. Methodology
[Same caveat as above.]
Data collection combined real ICS device traffic with virtual/simulated ICS
application traffic. CSV traces were generated from PCAP captures via an IPFIX flow
probe or an extraction script, keeping timestamp, IP addresses, ports, and the
security-relevant IEC-104/MMS header fields (the same fields your
formal_bound_builder.py maps -- see Table~\ref{tab:column-dictionary} in Chapter 4).
Traffic includes normal operation captured over several days plus attack/anomaly
classes described as "scanning, switching, command blocking, etc." A public
commenter flagged possible duplicate rows across categories -- worth a spot-check
if you revisit preprocessing.

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
