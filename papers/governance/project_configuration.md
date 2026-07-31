# Project Configuration — Evidence-Locked Q1 Publication Production Framework

> **SUPERSEDED BINDINGS — read this first (SE-022, 2026-07-22).** This file is the
> dated **Phase-0/2 configuration snapshot**. Two bindings below are no longer current:
>
> 1. **Evidence release.** Section 5 and Section 10 bind `rel-2026-07-10-262fc16c9`.
>    The **shipped** release is **`rel-2026-07-20-67d9345f9`** (anchor
>    `67d9345f9502a9a584e645fa8948f60a61d70e29`); the controlled analysis area is
>    `papers/analysis/rel-2026-07-20-67d9345f9/`. The 2026-07-10 release was superseded
>    after CR-0007 (post-freeze code audit) forced regeneration.
> 2. **Cover-letter venue.** Section 4 records R-0004 as DEFERRED with the cover letter
>    still addressing *Swarm and Evolutionary Computation*. **R-0004 was CLEARED on
>    2026-07-11 (Phase 9):** `papers/cover_letter.md`/`.tex` were rewritten for the
>    frozen venue, **MDPI *Algorithms***. See `claims_evidence_matrix.csv` row CL-01 and
>    `decision_log.md` D-0015.
>
> The frozen target journal (MDPI *Algorithms*, decision D-0010) is unchanged and correct.
> Everything else below is retained unedited as the dated snapshot.


Phase 0 authoritative project configuration (framework: `papers/PAPER_BUILD_PROMPT.md`).
Created: 2026-07-10 (Phase 0, Task Group A). All relative paths resolve against
the **project root** unless stated otherwise.

## 1. Roots and repository identity

| Field | Value |
|---|---|
| `project_root` | `D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1` (contains `pyproject.toml`; parent of `papers/`; framework path base) |
| `git_root` | `D:/AI/PhD-Projects` (enclosing Git repository, per `git rev-parse --show-toplevel`; project paths are prefixed `00-GSK-Family/02-GSK_Family_Python_v1.1/` in Git output) |
| `anchor_commit` | `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` |
| Anchor cross-check | `git rev-parse HEAD` == `git rev-list -1 HEAD` == anchor commit (two independent commands, 2026-07-10; verbatim records in `reproducibility_manifest.json`) |
| Anchor provenance | Reconciliation commit of the framework revision + generator fixes, made immediately before Phase 0 (see `decision_log.md` D-0001) |
| Branch | `main` |
| Remotes | `origin  https://github.com/MostafaMassoud/PhD-Projects.git` (fetch + push) |
| Submodules | none (`git submodule status` empty) |
| Governance root | `papers/governance/` (canonical home of all Section 3 governance artifacts; Section 3 preamble, Section 12.4) |
| Phase-snapshot root | `papers/build_prompt_phases/phase_<NN>/` (copies for gate evidence, never the master; Section 12.4). Legacy flat `papers/build_prompt_phases/PHASE_<n>_*.md` files are examples only, never authoritative outputs. |

## 2. Dirty-path list at Phase 0 snapshot (live staging campaign)

`git status --porcelain -- .` scoped to the project root (2026-07-10; verbatim
output and SHA-256 `c2ade2e3e8be39dfed48ea7f3cd64b7ceadd8e6deb92dfb3b2ef094fd3240e69`
in `reproducibility_manifest.json`) reports dirty paths **exclusively** under
`results/_ablation/`:

- `M  results/_ablation/baseline/dt-gsk/cec2017/summary/dt-gsk_cec2017_D100.csv`
- `M  results/_ablation/baseline/dt-gsk/cec2017/summary/per_run.csv`
- `?? results/_ablation/baseline/dt-gsk/cec2017/curves/Figure_F25_D100_Run#5.csv`
- `?? results/_ablation/baseline/dt-gsk/cec2017/curves/Figure_F26_D100_Run#22.csv`
- `?? results/_ablation/baseline/dt-gsk/cec2017/curves/Figure_F27_D100_Run#15.csv`
- `?? results/_ablation/baseline/dt-gsk/cec2017/curves/Figure_F28_D100_Run#25.csv`
- `?? results/_ablation/baseline/dt-gsk/cec2017/curves/Figure_F29_D100_Run#2.csv`
- `?? results/_ablation/baseline/dt-gsk/cec2017/curves/Figure_F30_D100_Run#21.csv`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/environment.json`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/dt-gsk_D100_log_2026-07-10_15.00.23.txt`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/dt-gsk_D100_runs_log_2026-07-10_15.00.23.txt`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/dt-gsk_D10_log_2026-07-10_15.00.23.txt`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/dt-gsk_D10_runs_log_2026-07-10_15.00.23.txt`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/dt-gsk_D30_log_2026-07-10_15.00.23.txt`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/dt-gsk_D30_runs_log_2026-07-10_15.00.23.txt`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/dt-gsk_D50_log_2026-07-10_15.00.23.txt`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/dt-gsk_D50_runs_log_2026-07-10_15.00.23.txt`
- `?? results/_ablation/baseline/dt-gsk/cec2017/summary/verification.json`
- `?? results/_ablation/no_ace/` (directory, untracked)
- `?? results/_ablation/no_psr/` (directory, untracked)

**Active-campaign note.** The DT-GSK scaffold ablation (`scripts/run_ablation.py`)
is RUNNING on this machine during preflight, writing to `results/_ablation/<cell>/`
(baseline mid-D100; `no_ace` and `no_psr` cells present; log stamps 2026-07-10).
Per Section 0.3, `results/` is staging-only, so this churn is **non-blocking**
(Phase 0 task 1: dirty paths touching only staging do not block freezing).
The dirty list is therefore time-varying while the campaign runs; the list above
is the Phase 0 fingerprint snapshot. Disposition: recorded here, in
`risk_register.csv` (R-0001), and in `decision_log.md` (D-0002). Phase 0 does
not wait for the campaign and does not touch `results/_ablation/`. Any later use
of these outputs must pass Section 2.4 controlled staging-to-evidence promotion.

No dirty path touches benchmark evidence, source code, configuration, tables,
figures, or analysis — the blocking condition of Phase 0 task 1 is not met.

## 3. Updated-prompt referent (Section 3.2)

The referent of "the updated prompt" / "the updated construction brief" IS the
master framework file itself:
`D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1/papers/PAPER_BUILD_PROMPT.md`.
No separate brief path is recorded. Source-line classification
(`source_line_traceability.csv`) therefore targets that file.

## 4. Target journal (FROZEN at Phase 4)

- **Frozen target (Phase 4, 2026-07-10, decision D-0010)**: **MDPI
  *Algorithms*** — the repository-wired template (`papers/Definitions/mdpi.cls`,
  class option `algorithms` in `papers/main.tex` line 5
  `\documentclass[algorithms,article,submit,moreauthors,pdftex]{Definitions/mdpi}`),
  frozen per the framework Phase 4 task 1 default and the explicit user
  instruction of 2026-07-10 ("use the current plan's target and flag R-0004
  for later").
- Current official journal instructions are recorded in
  `papers/build_prompt_phases/phase_04/journal_requirements.md` (with access
  date and online-verification status); the decision record is
  `phase_04/journal_decision.md`.
- **R-0004 (cover-letter venue mismatch) -- CLEARED 2026-07-11 (Phase 9); the paragraph below is the superseded Phase-0 statement**:
  `papers/cover_letter.md`/`.tex`/`.pdf` still address *Swarm and Evolutionary
  Computation* and MUST be rewritten for the frozen venue (or the venue
  revisited via change request) before Phase 9 rendering / Phase 11 packaging
  (risk register R-0004; `instruction_precedence.md`).

## 5. Controlled analysis bundle root

`papers/analysis/<release_id>/` (Section 7.13). The `<release_id>` placeholder
is bound when the evidence release is selected in Phase 2.
`primary_stats/statistical_results.csv` lives inside this bundle, not in the
governance root (Section 3.1).

**BOUND (Phase 2, 2026-07-10; SUPERSEDED 2026-07-20 -- see the banner at the top of this file):** `<release_id>` = `rel-2026-07-10-262fc16c9`
— the `benchmarks/cec_reference_results/` tree exactly as frozen at anchor
commit `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (three primary suites
cec2017/cec2011/cec2013, 7 optimizers each, plus context suites cec2020 and
cec2013lsgo). Per-file SHA-256 + size ledger over all 3409 files
(712,038,425 bytes): `papers/governance/evidence_release_manifest.json`.
Controlled analysis area: `papers/analysis/rel-2026-07-10-262fc16c9/`
(created empty in Phase 2; populated only by Phase 6+ controlled analyses).

## 6. Evidence boundaries

| Path | Boundary | Enforcement |
|---|---|---|
| `benchmarks/cec_reference_results/` | **Read-only immutable evidence** (Section 2.1/2.3) | Procedural (see limitation below) |
| `benchmarks/cec_suite_python/` | Evaluator source; version/hash frozen in Phase 2 | Procedural |
| `results/` | **Staging-only**; never citable as evidence without Section 2.4 promotion | Procedural |
| `reference_papers/` | Closed literature corpus (Section 2.2); read-only | Procedural |
| `papers/governance/` | Governance writes (this phase's only write target) | n/a |

**Documented technical limitation (read-only marking).** NTFS ACL enforcement
(`icacls` deny-write) is NOT applied: it would require elevation not available
to this non-interactive session. The read-only rule for
`benchmarks/cec_reference_results/` (and the staging-only rule for `results/`)
is enforced **procedurally** by this framework — no framework phase writes to
these paths, and Phase 2 checksum audits detect any violation. The framework
permits documenting this as a technical limitation (Phase 0 verification
procedures: "Verify protected evidence permissions or document technical
limitations"). Recorded as risk R-0006.

## 7. Source-boundary inventory (Phase 0 task 4)

| Expected class | Path (relative to project root) | Status | Detail |
|---|---|---|---|
| Literature corpus | `reference_papers/` | present | 57 PDF files |
| Bibliography | `papers/references.bib` | present | 57 `@` entries (matches PDF count; identity audit is Phase 1) |
| Immutable reference results | `benchmarks/cec_reference_results/` | present | 5 suites: cec2011, cec2013, cec2013lsgo, cec2017, cec2020. Optimizers: cec2011/cec2013/cec2017 each {agsk, apgsk, atmals-gsk, egsk, fdb-agsk, gsk, dt-gsk} (7); cec2013lsgo {decc-g, mos} (2); cec2020 {agsk} (1) |
| Benchmark evaluator source | `benchmarks/cec_suite_python/` | present | version/hash frozen in Phase 2 |
| Staging outputs | `results/` | present | `_ablation/`, `_analysis/`, `_run_all/`; staging-only |
| Algorithm source | `src/gsk_family/` | present | |
| Scripts | `scripts/` | present | |
| Main manuscript | `papers/main.tex` | present | MDPI class, option `algorithms` |
| Supplementary | `papers/supplementary.tex` | present | plus `papers/sections/` |
| Manuscript sections | `papers/sections/` | present | |
| Tables | `papers/tables/` | present | |
| Figures | `papers/figures/` | present | |
| Journal template | `papers/Definitions/` (`mdpi.cls`) | present | |
| Project config | `pyproject.toml` | present | project-root marker |

No expected source class is missing; none is `not_applicable`.

## 8. Toolchain state (Phase 0 task 5 — versions recorded, nothing installed)

| Tool | Version / status | Needed by |
|---|---|---|
| Python | 3.10.11 (`C:\AI\Python\Python310`) | all phases |
| pip | 26.1.2 | Phase 0 preflight |
| Git | 2.49.0.windows.1 | all phases |
| pdflatex | MiKTeX-pdfTeX 4.27 (MiKTeX 26.5) | Phase 9 |
| latexmk | 4.88 (9 March 2026) | Phase 9 |
| xelatex | MiKTeX-XeTeX 4.18 (MiKTeX 26.5) | Phase 9 (fallback engine) |
| bibtex / biber | MiKTeX-BibTeX 4.2 / biber 2.21 | Phase 9 |
| pandoc | 3.9.0.2 | Phase 9 (Word production) |
| 7z | **NOT FOUND** on PATH | Phase 12 packaging — mitigated by tar (R-0002) |
| tar | GNU tar 1.35 | Phase 12 packaging |
| certutil | present; `-hashfile SHA256` verified working | checksums, all phases |
| Get-FileHash | present (PowerShell 5.1 cmdlet) | checksums, all phases |
| python-docx | importable, 1.2.0 | Phase 9 (Word validation) |
| pypandoc | **NOT IMPORTABLE** (`ModuleNotFoundError`) | Phase 9 — mitigated by direct pandoc CLI (R-0003) |

Per Phase 0 task 5, nothing was installed; missing tools are risk-register rows
with the phase that needs them.

## 9. Phase state and defaults

- Phase state ledger: `phase_gate_register.csv` (this directory); Phase 0 is
  `IN_PROGRESS` at the time of this snapshot; Phases 1-12 `NOT_STARTED`;
  Phase 12 is the sole final implementation phase and sole ablation phase.
- Release ID: **`rel-2026-07-10-262fc16c9`** (bound in Phase 2, 2026-07-10; SUPERSEDED by `rel-2026-07-20-67d9345f9`, the shipped release;
  see Section 5 and `evidence_release_manifest.json`).
- Date convention: execution-context date 2026-07-10 used for Phase 0 stamps.

## 10. Phase 9 filename mappings (added 2026-07-11)

Dated note, Phase 9 Task A (dual-format production); appended, prior sections untouched.

| Build script | Intermediate | User-facing artefact | Reason |
|---|---|---|---|
| `papers/scripts/build_pdf.py` | `papers/main.pdf` | `papers/DT-GSK.pdf` | MDPI class requires the source to stay `main.tex`; script renames the PDF post-build |
| `papers/scripts/build_docx.py` | (pandoc output) | `papers/DT-GSK.docx` | Word companion named to match the PDF artefact |
| `papers/scripts/build_supplementary.py` | -- | `papers/supplementary.pdf` | filename already matches the source stem |

Build evidence: `papers/build_prompt_phases/phase_09/latex_build_report.md` (page counts, raw + normalized sha256).

## 11. Phase 9 Word-pipeline and validator commands (added 2026-07-11)

Dated note, Phase 9 (dual-format production); appended, prior sections untouched.
Implemented commands for the Appendix D.6 expected entry points (the D.6
name `papers/main.docx` maps to `papers/DT-GSK.docx` per Section 10;
`validate_docx.py` accepts `papers/main.docx` and resolves the recorded
mapping):

```bash
python papers/scripts/build_docx.py                     # -> papers/DT-GSK.docx
python papers/scripts/build_docx.py --supplementary     # -> papers/supplementary.docx
python papers/scripts/validate_docx.py papers/DT-GSK.docx
python papers/scripts/validate_docx.py papers/supplementary.docx
python papers/scripts/validate_cross_format_parity.py   # -> papers/governance/cross_format_consistency.csv
python papers/scripts/validate_evidence_bindings.py     # -> papers/build_prompt_phases/phase_09/evidence_binding_verification.csv
```

Shared helper: `papers/scripts/_validate_common.py`. Validation evidence:
`papers/governance/word_validation_report.md` (Gate 9 fallback report,
deviation D-WORD-01), `papers/governance/cross_format_consistency.csv`,
`papers/build_prompt_phases/phase_09/evidence_binding_verification.csv`.
