# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Check that every ``manuscript_label`` in artifact_binding.csv resolves (SE-022).

``papers/governance/artifact_binding.csv`` names, for each generated exhibit, the
``\\label{...}`` it appears under in the manuscript.  Nothing verified that column,
so it rotted silently: at the 2026-07-22 panel review **52 of 59 rows** pointed at
labels that no longer existed.  The drift was systematic, not random --

* supplement convergence grids were split into ``-a``/``-b``/``-c``/``-d`` panels
  while the bindings still named the un-suffixed parent;
* four per-dimension Nemenyi figures were merged into one multi-panel figure;
* four conceptual figures were converted to native tables (``fig:`` -> ``tab:``);
* three Phase-3 build inputs named labels that were never realised at all.

None of it was detectable from any gate, because ``validate_evidence_bindings.py``
checks the BIND comments in the sources, not this column.  This validator closes
that gap.

A label of the form ``n/a (...)`` is an explicit, accepted declaration that the
artifact has no one-to-one manuscript float; it is not treated as a failure.

Run::

    python papers/scripts/validate_artifact_labels.py

Exit code 0 = every label resolves; 1 = at least one dangling label.
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BINDING = REPO / "papers" / "governance" / "artifact_binding.csv"
ROOTS = ("main.tex", "supplementary.tex")

_LABEL = re.compile(re.escape(chr(92)) + r"label\{([^}]+)\}")


def defined_labels() -> dict[str, str]:
    """Every \label{...} reachable from the two document roots -> 'file:line'.

    Follows ``\input`` recursively.  The first version of this validator scanned
    only ``papers/sections/*.tex`` plus the two roots, and so reported the four
    Phase-3 method artifacts (notation tables, pseudocode, parameter table,
    equation registry) as having no manuscript label -- when in fact their labels
    are defined in the ``\input``-ed files under
    ``papers/build_prompt_phases/phase_03/``.  A partial scan produces confident
    false negatives, so the traversal must match what LaTeX actually reads.
    """
    _input = re.compile(re.escape(chr(92)) + r"input\{([^}]+)\}")
    seen: set[Path] = set()
    found: dict[str, str] = {}

    def walk(rel: str) -> None:
        base = REPO / "papers"
        for cand in (base / rel, base / (rel + ".tex")):
            if not cand.is_file():
                continue
            path = cand.resolve()
            if path in seen:
                return
            seen.add(path)
            text = path.read_text(encoding="utf-8", errors="ignore")
            for lineno, line in enumerate(text.splitlines(), 1):
                for label in _LABEL.findall(line):
                    found.setdefault(label, f"{path.name}:{lineno}")
            for nxt in _input.findall(text):
                walk(nxt)
            return
        raise SystemExit(f"HARD FAIL: \input target not found: {rel}")

    for root in ROOTS:
        if not (REPO / "papers" / root).is_file():
            raise SystemExit(f"HARD FAIL: manuscript root missing: {root}")
        walk(root)
    return found


def main() -> int:
    if not BINDING.exists():
        raise SystemExit(f"HARD FAIL: missing {BINDING}")
    labels = defined_labels()
    with BINDING.open("r", encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))

    dangling: list[tuple[str, str]] = []
    checked = declared_none = 0
    for row in rows:
        raw = (row.get("manuscript_label") or "").strip()
        if not raw:
            continue
        if raw.startswith("n/a"):
            declared_none += 1
            continue
        for label in (p.strip() for p in raw.split(";")):
            if not label:
                continue
            checked += 1
            if label not in labels:
                dangling.append((row["artifact_id"], label))

    print(f"artifact labels: {len(rows)} binding rows | {checked} labels checked | "
          f"{declared_none} rows declare no manuscript float | "
          f"{len(labels)} labels defined in sources")
    if dangling:
        print(f"\nFAIL ({len(dangling)} dangling label(s)):")
        for aid, label in dangling:
            print(f"  - {aid}: manuscript_label '{label}' is not defined in any source")
        return 1
    print("PASS: every manuscript_label resolves to a label in the shipped sources.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
