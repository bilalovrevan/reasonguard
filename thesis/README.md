# Thesis LaTeX Skeleton

This folder contains the Overleaf-ready LaTeX skeleton for the ReasonGuard MSc thesis.

## Structure

```
thesis/
  main.tex                     # Document root
  references.bib               # BibTeX references
  frontmatter/
    titlepage.tex
    declaration.tex
    abstract.tex
    acknowledgements.tex
  chapters/
    01_introduction.tex
    02_related_work.tex
    03_framework.tex
    04_experimental_setup.tex
    05_results.tex
    06_discussion.tex
    07_conclusion.tex
  appendices/
    A_violation_taxonomy.tex
    B_prompt_specifications.tex
    C_reproducibility.tex
```

## Uploading to Overleaf

1. Zip the contents of this folder (keeping the directory structure intact).
2. In Overleaf, create a new blank project, then upload the zip file via
   `Menu -> Upload Project`.
3. Set the main document to `main.tex` and select the `biber` BibTeX engine in
   `Menu -> Settings -> TeX Live version` and `BibTeX engine`.

## Author's notes

Square-bracketed `[Author's note: ...]` paragraphs are scaffolding for sections that
require empirical results, reading notes, or supervisor feedback before they can be
finalised. They are deliberately placed inline so that nothing is forgotten when
the chapter is filled in.

## Writing convention

- Plain academic English; passive voice where conventional, active voice where it adds
  clarity.
- No first-person plural except in the acknowledgements.
- Every quantitative claim must cite the section or table that contains the evidence.
- Every literature claim must cite the BibTeX entry that supports it.
