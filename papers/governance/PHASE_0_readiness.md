# PHASE 0 Readiness — Gate 0 Verdict

Framework: `papers/PAPER_BUILD_PROMPT.md` (Evidence-Locked Q1 Publication
Production Framework). Date: 2026-07-10. Gate: **Gate 0 — P1 + P5 + P9 approve**
(P10 consulted on administrative gaps and journal template).

## 1. Anchor and repository state

- `project_root` = `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1`
  (contains `pyproject.toml`; framework path base).
- `git_root` = `D:/AI/PhD-Projects` (project paths prefixed
  `00-GSK-Family/02-GSK_Family_Python_v1.1/`).
- `anchor_commit` = `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`, branch `main`
  (reconciliation commit of the framework revision + generator fixes; decision
  D-0001). Confirmed unchanged at the gate by two independent commands
  (`git rev-parse HEAD` == `git rev-list -1 HEAD`; verbatim in
  `reproducibility_manifest.json` → `gate0_verification`). The same SHA appears
  in every governance artifact that records a commit; no conflicting anchor
  found.
- Dirty state at the gate: byte-identical to the preflight verification
  snapshot (`git status --porcelain -- .` SHA-256
  `14f3198460741a615804879bba7f91178e883ecebb1019f082615d66ab6dc224`):
  exactly `?? papers/governance/` (Phase 0's own sanctioned output) plus the
  live `results/_ablation/` staging churn. **No scientific source file changed
  during preflight or gate assembly.**
- Active-campaign note: the DT-GSK scaffold ablation
  (`scripts/run_ablation.py`) is RUNNING during Phase 0 (baseline mid-D100;
  `no_ace`, `no_psr` present; log stamps 2026-07-10). Non-blocking per
  Section 0.3 (staging-only); risk R-0001; decision D-0002; conflict C-09.

## 2. Boundaries

| Path | Boundary |
|---|---|
| `benchmarks/cec_reference_results/` | read-only immutable evidence (procedural enforcement; ACL limitation documented, R-0006) |
| `results/` | staging-only; Section 2.4 promotion required for any evidentiary use; Phase 12 is the sole ablation phase |
| `reference_papers/` (57 PDFs) + `papers/references.bib` (57 entries) | closed literature corpus; identity audit in Phase 1 |
| `papers/governance/` | governance writes (the only Phase 0 write target) |

All 14 expected source classes located `present`; none `missing`;
none `not_applicable` (`project_configuration.md` Section 7;
`preflight_inventory.csv`, 54 data rows).

## 3. Toolchain verdict

Verified present: Python 3.10.11, pip 26.1.2, Git 2.49.0, MiKTeX 26.5
(pdflatex 4.27, xelatex 4.18, latexmk 4.88, bibtex 4.2, biber 2.21),
pandoc 3.9.0.2, python-docx 1.2.0, tar, certutil/Get-FileHash. **Gaps**: `7z`
not on PATH (Phase 12 packaging; mitigated by tar — R-0002); `pypandoc` module
not importable (Phase 9 Word pipeline; mitigated by direct pandoc CLI +
python-docx — R-0003). Nothing installed during Phase 0 (D-0003). LaTeX chain:
no gap. Engineering preflight: 7/7 commands exit 0, including
`pytest` 324 passed and `ruff` clean (`engineering_preflight.md`; documented
pip-show deviation D-0004).

## 4. Traceability (merged at the gate)

- `source_line_traceability.csv`: **5,880 rows** (parts 0–5: 994 + 1,028 +
  946 + 969 + 1,004 + 939), single header. 0 duplicate `line_no`; coverage ==
  the master's 5,880 nonblank lines (0 missing, 0 extra); classifications all
  in the Section 3.2 allowed set (integrated 4,299; structural_heading 748;
  nonoperative 508; example_or_comment 307; duplicate 18); 0
  `unmapped`/`partial`/`unknown`.
- `requirements_traceability_matrix.csv`: **2,105 rows** (parts 0–5: 230 +
  203 + 494 + 514 + 407 + 257), single header. 0 duplicate requirement IDs;
  every row carries nonempty phase/artifact/validation/owner; 0 dangling
  references from source lines; 0 orphan requirements (every requirement is
  cited by at least one classified line).
- Condensed schemas accepted with rationale and reconstruction rule in
  decision **D-0005** (`source_document` constant per
  `project_configuration.md` Section 3; `line_text` recoverable byte-exactly
  from the master at the anchor commit).

## 5. Acceptance criteria (framework Phase 0)

| # | Criterion | Verdict | Evidence |
|---|---|---|---|
| 1 | repository root and anchor commit recorded | PASS | `project_configuration.md` §1; two-command anchor cross-check in `reproducibility_manifest.json` |
| 2 | every expected source class located or marked missing | PASS | `project_configuration.md` §7 (14 classes, all present); `preflight_inventory.csv` (54 rows, explicit status column) |
| 3 | empirical evidence and staging paths clearly separated | PASS | `project_configuration.md` §6 boundary table; R-0006 documents the procedural-enforcement limitation |
| 4 | no unresolved instruction conflict remains | PASS | `instruction_precedence.md` C-01…C-10 all carry explicit dispositions; sole OPEN row C-08 (cover-letter venue vs MDPI template) is resolved by framework-mandated deferral to the Phase 4 journal freeze (Section 1.4), with provisional target recorded and risk R-0004 owned |
| 5 | engineering preflight recorded | PASS | `engineering_preflight.md`: 7 commands, cwd, date, exit codes (all 0), output SHA-256 hashes; deviation documented (D-0004) |
| 6 | governance registers exist and are usable | PASS | all 13 governance files parse (csv/json/nonempty-md checks at the gate, 2026-07-10) |
| 7 | source-line and requirement traceability contain no unmapped or partial row | PASS | §4 above: 5,880/5,880 lines classified exactly once; 2,105 requirements fully mapped; 0 forbidden statuses |
| 8 | no scientific artifact was modified | PASS | gate git status byte-identical to preflight verification snapshot; only `papers/governance/` + live staging differ from the fingerprint snapshot; HEAD unchanged |

## 6. Critical risks carried forward

- **R-0004 (high impact)** — target-journal mismatch: MDPI template wired in
  repo vs cover letter addressing *Swarm and Evolutionary Computation*;
  Phase 4 must verify current official journal information and dispose (C-08).
- **R-0001** — live staging campaign keeps the dirty list time-varying;
  re-check scoped git status at every gate; Section 2.4 promotion required
  before any use (Phase 12 only).
- **R-0006** — read-only rule on `benchmarks/cec_reference_results/` is
  procedural until the Phase 2 SHA-256 ledger exists.
- **R-0002 / R-0003** — 7z and pypandoc absent (Phases 12 / 9); mitigations in
  place; no phase hard-blocked.

## 7. Quality-assurance sign-offs (Gate 0)

**P1 — Authority and scope.** The master framework is the sole project-wide
authority (rank 2, below only explicit human requirements); all 19 instruction
sources are inventoried and every conflict — including the R2 addendum's
authority-inversion banner, early/main-text ablation, `_run_all` fallback,
CEC2013 run count, and detector-evasion framing — carries an explicit
disposition per Section 0.2/0.3. Phase 12 is registered as the sole
implementation and ablation phase. Phase 0 wrote only under
`papers/governance/`, within its mandate. No authority conflict remains open
except C-08, which the framework itself assigns to Phase 4.
*Signed: P1 (research-integrity and scope authority), 2026-07-10 — APPROVE.*

**P5 — Audit reproducibility.** Every fingerprint and preflight command is
recorded with command, cwd, date, exit code, and output SHA-256; the anchor is
double-derived (`rev-parse`/`rev-list`) and identical across all seven
artifacts that record a commit. The gate-time status snapshot hashes
byte-identical to the preflight verification snapshot, so the no-scientific-
change claim is checkable, not asserted. Traceability merge numbers (5,880 /
2,105; zero defects on six checks each) were machine-validated and are
transcribed in `reproducibility_manifest.json` → `gate0_verification`. The
audit trail (D-0001…D-0005, R-0001…R-0006, A-0001…A-0006) satisfies
Section 3.9 for Phase 0.
*Signed: P5 (reproducibility auditor), 2026-07-10 — APPROVE.*

**P9 — Source boundaries.** Immutable evidence
(`benchmarks/cec_reference_results/`, 24 suite-by-optimizer cells inventoried)
is separated from staging (`results/`) and from the closed literature corpus
(57 PDFs = 57 BibTeX entries, identity audit deferred to Phase 1 as designed).
The ACL limitation is honestly documented (R-0006) with a Phase 2 checksum
backstop. The live campaign writes only under `results/_ablation/` (verified
by scoped git status at snapshot and gate), and no publishable path may
resolve through the `_run_all` fallback (C-05 superseded). Boundaries are
clear and enforced procedurally with detection controls.
*Signed: P9 (evidence-boundary steward), 2026-07-10 — APPROVE.*

**P10 — Administrative gaps and journal template.** Six administrative gaps
(AG-0001…AG-0006: author list, ORCIDs, funding, COI, corresponding-author
contact, journal administrative requirements) are registered as
author-input-only items with owning phases — none may be closed by
fabrication. The provisional target journal is recorded strictly from the
repository template (MDPI class, option `algorithms`) with no quartile or
page-limit claim, and the cover-letter venue mismatch is an owned Phase 4
conflict (C-08, R-0004). Template files are present and inventoried.
*Signed: P10 (administrative-compliance reviewer), 2026-07-10 — APPROVE
(advisory; not a Gate 0 blocking approver).*

## 8. Gate verdict and Phase 1 entry

- **Gate 0 verdict: FROZEN.** All eight acceptance criteria PASS; P1, P5, and
  P9 sign; no unexplained dirty scientific path, no unclear evidence boundary,
  no unresolved authority conflict.
- `phase_gate_register.csv` updated: Phase 0 → `FROZEN` (2026-07-10).
  Reopening now requires a change request row (Section 12.2).
- **Phase 1 entry status: READY.** Phase 1 inputs exist (closed corpus:
  `reference_papers/` 57 PDFs + `papers/references.bib` 57 entries;
  `reference_inventory.csv` schema fixed by Section 3.3); no Phase 0 blocker
  carries into Phase 1; open risks R-0001…R-0006 are owned and none blocks
  literature audit work.

## 9. Post-Gate-0 change-control rerun: CR-0001/CR-0002 traceability patch

Traceability patched for CR-0001/CR-0002 on 2026-07-10; 113 rows
added/reclassified (109 new source-line rows for the CR insertions + 4
replaced-line rows reclassified) and 21 operative requirements appended.

- Baseline: the frozen master at anchor `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`
  (7472 lines / 5880 nonblank). Current master after CR-0001/CR-0002:
  7585 lines / 5985 nonblank. Diff computed with
  `difflib.SequenceMatcher` (autojunk=False) over full lines.
- `source_line_traceability.csv`: line numbers of all unchanged lines
  shifted to current-master positions (4782 rows shifted); rows for the 4
  replaced frozen lines (1776, 1847-1849) dropped and re-classified at their
  current positions (1795-1798 -> new R-1795; 1882-1885 -> retained under
  R-1842, reworded by CR-0001); 109 rows added for the CR insertion ranges
  (Sections 6.7, 8.4, 8.5, 8.6, 8.7, 10.1, Phase 4 tasks 8/12 + outputs,
  Phase 7 task 3, Phase 10 task 4, 15.9.4) using the Section 3.2 vocabulary
  (108 `integrated`, 1 `nonoperative` lead-in at line 1944).
- `requirements_traceability_matrix.csv`: 21 new operative requirements
  appended (2105 -> 2126 rows). New ids follow `R-<current-line>`; where the
  bare number collides with a frozen-anchor id, the CR suffix disambiguates
  (`R-1386-CR0001`, `R-1389-CR0001`, `R-1391-CR0001`, `R-4340-CR0001`,
  `R-5136-CR0002`). Pre-CR requirement ids and their `line_no` fields keep
  their frozen-master anchors; current line positions for every id are
  resolved through `source_line_traceability.csv`.
- Mapping fix surfaced by the rerun validation: line 1094 (mandated
  contribution-matrix columns), the one `integrated` row without a
  requirement reference at Gate 0, is now noted as a continuation of R-1092.
- Validation (2026-07-10): rows_total 5985 == current-master nonblank 5985;
  duplicate line_no 0; missing/extra line_no 0/0; invalid classifications 0;
  unmapped integrated rows 0; dangling requirement refs 0; matrix duplicate
  ids 0. Full report: `cr_patch_report.json` (session scratchpad); pre-patch
  backups of both CSVs retained alongside it.
- Authority: Section 0.6 change control; CR-0001/CR-0002 rows in
  `change_request_register.csv` (APPROVED, P1); decision D-0005 condensed
  schemas unchanged.

## 10. Post-Gate-0 change-control rerun: CR-0003 traceability patch

Traceability patched for CR-0003 on 2026-07-10 (same method as Section 9);
177 new source-line rows classified for the CR-0003 insertions and 27
operative requirements appended.

- Baseline for diffing: the frozen master at anchor
  `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (7,472 lines / 5,880 nonblank;
  scratchpad copy SHA-256-verified byte-identical to `git show`,
  `4cea60c7fca0…`). Current master after CR-0003: 7,759 lines / 6,146
  nonblank (SHA-256 `067725d4a823…`). The intermediate CR-0001/2-era master
  (7,585 / 5,985) was never committed, so the full mapping was REBUILT in one
  pass: `difflib.SequenceMatcher` (autojunk=False) over frozen → current.
- `source_line_traceability.csv` (5,985 → **6,146 rows**):
  - 5,875 rows for lines unchanged since the frozen anchor carry the existing
    CSV's classification (5,691 shifted to current positions). The
    frozen→CR-era row alignment needed for the carry was reconstructed from
    the Gate 0 pre-patch backup vs the existing CSV and content-verified:
    all 5,876 carried pairs identical (sole difference: the Section 9
    line-1094 note fix, which is preserved, now at line 1123).
  - 94 CR-0001/2-inserted rows were repositioned via an explicit block map
    (e.g. family-overlay block CR-era 1375-1392 → current 1409-1433 around
    the CR-0003 aggregation-options insertion); notes updated where CR-0003
    reworded the text (three-exemplar retitles at 2011, 2028, 2048, 3763-3767,
    5283).
  - 177 rows added for the CR-0003 insertions (Sections 1.2, 2.3, 6.7, 6.9,
    7.4, 7.5, 7.7, 8.4, 8.6, 8.7, 8.10, 9.4, 10.1-adjacent, Phase 2 task 2,
    Phase 4 tasks 10/12, Phase 7 validation, 15.9 gate mapping + DoD):
    175 `integrated`, 2 `nonoperative` (gate-mapping table header/separator).
  - 5 frozen lines replaced overall: 1776 and 1847-1849 by CR-0001 (already
    handled in Section 9, carried forward), and 1422 extended in place by
    CR-0003 (reclassified at current 1482 under its original R-1421, with the
    new runtime-comparability guard as R-1483 at 1483-1485).
  - 15 CR-0001/2-era rows whose text CR-0003 replaced were re-expressed at
    their successors: the R-1946 single-register extraction wording (8 rows)
    → structured comparative review under `R-2030-CR0003` (2030-2047); three
    Phase 4 task-12 rows → expanded three-exemplar wording under
    `R-3768-CR0003` (3768-3783); four R-1842 supplement-bullet rows →
    1957-1964 with the CR-0003 extension under `R-1960-CR0003` (matrix rows
    R-1946/R-1842 retained; supersessions named in the row notes).
- `requirements_traceability_matrix.csv`: 27 new operative requirements
  appended (2,126 → **2,153 rows**). New ids follow `R-<current-line>`
  anchored to post-CR-0003 positions; the `-CR0003` suffix disambiguates the
  8 collisions with existing ids (`R-1601-CR0003`, `R-1620-CR0003`,
  `R-1960-CR0003`, `R-2030-CR0003`, `R-3227-CR0003`, `R-3768-CR0003`,
  `R-4578-CR0003`, `R-6740-CR0003`); the other 19 are bare (R-226, R-404,
  R-1401, R-1420, R-1483, R-1595, R-1644, R-1647, R-1865, R-1878, R-2022,
  R-2107, R-2461, R-3231, R-3755, R-4583, R-6806, R-6811, R-6851).
- Validation (2026-07-10): rows_total 6,146 == current-master nonblank 6,146;
  duplicate line_no 0; missing/extra line_no 0/0; invalid classifications 0;
  unmapped integrated rows 0; dangling requirement refs 0; matrix duplicate
  ids 0; orphan requirements 0. Classification histogram: integrated 4,563;
  structural_heading 748; nonoperative 510; example_or_comment 307;
  duplicate 18. Full report: `cr0003_patch_report.json` (session scratchpad);
  pre-patch backups of both CSVs retained alongside it
  (`*.pre_cr0003_backup.csv`).
- Authority: Section 0.6 change control; CR-0003 row in
  `change_request_register.csv` (APPROVED, P1); decision D-0005 condensed
  schemas unchanged; delta spec `cr0003_deltas.md` (session scratchpad).
