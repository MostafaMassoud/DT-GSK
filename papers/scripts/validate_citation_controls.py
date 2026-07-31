# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Cross-check the three citation-control files against each other (SE-025).

The semantic-role control is split across three registers that were maintained
by hand and drifted apart:

``papers/governance/citation_role_map.csv``
    the authority: which Appendix-B role each key may be cited in.
``papers/governance/citation_usage_map.csv``
    where each key is actually cited in the manuscript sources.
``papers/governance/word_citation_tag_map.csv``
    the DOCX source-generation map.

SE-025 was exactly this drift: ``awad2016problem`` -- the highest-traffic
suite-definition key -- was cited in the manuscript and mapped for Word, but
had no role-map row at all, because a Phase-1 finding that predated CR-0005 had
declared it inadmissible and nothing re-checked the registers after the key was
un-blocked.  A key can therefore be cited under no sanctioned role and no gate
notices.  This validator closes that hole.

Checks (all hard failures):

C1  every key cited in the usage map has a role-map row;
C2  every role-map key resolves to an evidence card that exists on disk;
C3  every key mapped for Word generation has a role-map row;
C4  no key is simultaneously role-mapped and marked BLOCKED for Word
    generation without an explicit override recorded in ``build_docx.py``;
C5  no duplicate ``citation_key`` in the role map or the Word map (the usage
    map is one row per citation *site*, so repeats there are expected).

Run::

    python papers/scripts/validate_citation_controls.py

Exit code 0 = all controls hold; 1 = at least one violation.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
GOV = REPO / "papers" / "governance"

ROLE_MAP = GOV / "citation_role_map.csv"
USAGE_MAP = GOV / "citation_usage_map.csv"
WORD_MAP = GOV / "word_citation_tag_map.csv"
BUILD_DOCX = REPO / "papers" / "scripts" / "build_docx.py"


def _rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SystemExit(f"HARD FAIL: missing citation-control file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _keys(rows: list[dict[str, str]], path: Path) -> list[str]:
    col = "citation_key"
    if rows and col not in rows[0]:
        raise SystemExit(f"HARD FAIL: {path.name} has no '{col}' column")
    return [(r.get(col) or "").strip() for r in rows if (r.get(col) or "").strip()]


def _overrides() -> set[str]:
    """Keys explicitly un-blocked for Word generation by a recorded decision."""
    if not BUILD_DOCX.exists():
        return set()
    text = BUILD_DOCX.read_text(encoding="utf-8")
    m = re.search(r"CITATION_BLOCK_OVERRIDES\s*=\s*\{(.*?)\}", text, re.S)
    return set(re.findall(r'"([^"]+)"\s*:', m.group(1))) if m else set()


def main() -> int:
    role_rows, usage_rows, word_rows = _rows(ROLE_MAP), _rows(USAGE_MAP), _rows(WORD_MAP)
    role_keys, usage_keys, word_keys = (
        _keys(role_rows, ROLE_MAP), _keys(usage_rows, USAGE_MAP), _keys(word_rows, WORD_MAP))
    role_set = set(role_keys)
    fails: list[str] = []

    # C5 -- duplicates.  The usage map is deliberately one row per citation
    # SITE (117 rows for 57 keys), so repeats there are correct; the role map
    # and the Word map are one row per key and must not repeat.
    for keys, path in ((role_keys, ROLE_MAP), (word_keys, WORD_MAP)):
        dupes = sorted({k for k in keys if keys.count(k) > 1})
        if dupes:
            fails.append(f"C5 {path.name}: duplicate citation_key rows: {', '.join(dupes)}")

    # C1 -- cited but unroled
    for key in sorted(set(usage_keys) - role_set):
        fails.append(
            f"C1 {key}: cited in {USAGE_MAP.name} but has no {ROLE_MAP.name} row "
            f"-- it is cited under no sanctioned role")

    # C2 -- role row points at a real evidence card
    for row in role_rows:
        key, card = (row.get("citation_key") or "").strip(), (row.get("evidence_card") or "").strip()
        if not key:
            continue
        if not card:
            fails.append(f"C2 {key}: {ROLE_MAP.name} row has an empty evidence_card")
        elif not (GOV / card).exists():
            fails.append(f"C2 {key}: evidence_card '{card}' does not exist on disk")

    # C3 -- Word-mapped but unroled
    for key in sorted(set(word_keys) - role_set):
        fails.append(f"C3 {key}: mapped in {WORD_MAP.name} but has no {ROLE_MAP.name} row")

    # C4 -- role-mapped yet still BLOCKED for Word generation
    overrides = _overrides()
    for row in word_rows:
        key = (row.get("citation_key") or "").strip()
        blob = " ".join(v or "" for v in row.values()).upper()
        if key in role_set and "BLOCKED" in blob and key not in overrides:
            fails.append(
                f"C4 {key}: has a {ROLE_MAP.name} row but is still BLOCKED in "
                f"{WORD_MAP.name} with no recorded CITATION_BLOCK_OVERRIDES entry")

    print(f"citation controls: role={len(role_keys)} usage={len(usage_keys)} "
          f"word={len(word_keys)} overrides={len(overrides)}")
    if fails:
        print(f"\nFAIL ({len(fails)} violation(s)):")
        for f in fails:
            print(f"  - {f}")
        return 1
    print("PASS: C1-C5 hold across all three citation-control files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
