"""Cross-check every \\cite{...}/\\autocite{...} key in the thesis LaTeX source
against the BibTeX keys defined in thesis/references.bib, in both directions.

Run: python3 scripts/check_citations.py
"""
from __future__ import annotations

import re
from pathlib import Path

THESIS_DIR = Path("thesis")
BIB_FILE = THESIS_DIR / "references.bib"

CITE_RE = re.compile(r"\\(?:auto)?cite[tp]?\*?(?:\[[^\]]*\])?\{([^}]+)\}")
BIB_KEY_RE = re.compile(r"^@\w+\{\s*([^,\s]+)\s*,", re.MULTILINE)


def find_cited_keys() -> dict[str, list[str]]:
    cited: dict[str, list[str]] = {}
    for tex_file in sorted(THESIS_DIR.rglob("*.tex")):
        text = tex_file.read_text(encoding="utf-8")
        for match in CITE_RE.finditer(text):
            for key in match.group(1).split(","):
                key = key.strip()
                if key:
                    cited.setdefault(key, []).append(str(tex_file))
    return cited


def find_bib_keys() -> set[str]:
    if not BIB_FILE.exists():
        raise SystemExit(f"Bib file not found: {BIB_FILE}")
    text = BIB_FILE.read_text(encoding="utf-8")
    return set(BIB_KEY_RE.findall(text))


def main() -> None:
    cited = find_cited_keys()
    bib_keys = find_bib_keys()
    cited_keys = set(cited)

    missing_from_bib = sorted(cited_keys - bib_keys)
    unused_in_bib = sorted(bib_keys - cited_keys)

    print(f"Cited keys found in thesis/**/*.tex: {len(cited_keys)}")
    print(f"Keys defined in {BIB_FILE}: {len(bib_keys)}")
    print()

    if missing_from_bib:
        print(f"MISSING FROM references.bib ({len(missing_from_bib)}) -- these will fail to compile / show as [?]:")
        for key in missing_from_bib:
            files = ", ".join(sorted(set(cited[key])))
            print(f"  - {key}  (cited in: {files})")
    else:
        print("OK: every \\cite/\\autocite key has a matching references.bib entry.")

    print()

    if unused_in_bib:
        print(f"DEFINED BUT NEVER CITED ({len(unused_in_bib)}) -- not an error, just unused entries:")
        for key in unused_in_bib:
            print(f"  - {key}")
    else:
        print("OK: every references.bib entry is cited at least once.")


if __name__ == "__main__":
    main()
