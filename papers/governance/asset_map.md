# Manuscript Asset Map — Phase 2, Tasks 11–12

> **HISTORICAL — two companion registers in this directory are retired (SE-022, 2026-07-22).**
>
> | File | Status | Authoritative replacement |
> |---|---|---|
> | `table_figure_source_map.csv` (46 rows) | **RETIRED.** A Phase-2 exhibit plan whose `manuscript_location` and `exists` columns were never re-derived after the Phase-8 rewire, the figure→table conversions, or the convergence-grid panel split. | `artifact_binding.csv` — 59 rows, one per shipped exhibit, with `manuscript_label` and `latex_location` repaired against the sources on 2026-07-22 and now gated by `papers/scripts/validate_artifact_labels.py`. |
> | `requirements_traceability_matrix.csv` (2,153 rows) | **HISTORICAL.** Its `line_no` column anchors into `PAPER_BUILD_PROMPT.md` at the 2026-07-14 revision; those line numbers no longer resolve. | `phase_gate_register.csv` (phase state) and `review_2026_07_22/requirements_compliance_matrix.csv` (current compliance). |
>
> Neither file is read by any script — both are documentation registers, retained
> unedited as dated records. Do **not** cite either as current state. The Phase-2
> content below is likewise a dated snapshot.

| Field | Value |
|---|---|
| Phase | Phase 2 — Immutable empirical evidence, benchmark, and provenance audit |
| Tasks | 11 (manuscript-asset audit), 12 (raw/derived separation audit) |
| Anchor commit | `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (verified = current HEAD) |
| Date | 2026-07-10 |
| Companion artifact | `table_figure_source_map.csv` (per-exhibit generator/source map) |
| Evidence handling | `benchmarks/cec_reference_results/` read + hashed only; zero writes. `results/` inventoried by counts only (see `staging_inventory.md`); `results/_ablation/` churn from the live campaign ignored per Section 6.10. |

Classification vocabulary (Phase 2 task 11): `keep`, `verify`, `regenerate`,
`rewrite`, `move`, `archive`, `remove`, plus `intentional-gap` for
deliberately absent exhibits. Generator/source mappings below were verified
**by reading generator code**, never inferred from filenames (Section 4.1).

---

## 1. `papers/` inventory and classification

### 1.1 Manuscript sources

| Asset | Class | Classification | Notes |
|---|---|---|---|
| `papers/main.tex` | prose/spine | verify | MDPI class spine (`Definitions/mdpi.cls`, `algorithms` option); venue conflict with cover letter is OPEN C-08 (Phase 4). |
| `papers/sections/introduction.tex` | prose | rewrite | Phase 4 drafting rebuilds prose under claims-matrix control. |
| `papers/sections/literature_review.tex` | prose | rewrite | Includes taxonomy figure (kept); citations re-validated against locked corpus. |
| `papers/sections/proposed_algorithm.tex` | prose | rewrite | Includes flowchart + NLPSR analytic figure (kept). |
| `papers/sections/performance.tex` | prose | rewrite | **Contains a main-text "Component and Overlay Ablations" subsection (`sec:exp:ablation`, line ~639) — violates Section 1.3 main-manuscript ablation prohibition (conflict class C-04); content must move to supplement-only, at most one neutral pointer.** Also carries the contradictory main-text T22 caption (defect F-11.3). |
| `papers/sections/conclusions.tex` | prose | rewrite | Phase 4. |
| `papers/sections/supplementary_content.tex` | prose | rewrite | Parametric pilot sections conditional on promoted parametric release; trace figures blocked on GenLog release (see CSV). |
| `papers/supplementary.tex` | spine | verify | Wraps `sections/supplementary_content.tex`. |
| `papers/references.bib` | administrative | keep | 57 locked entries (Phase 1 frozen corpus; CR-0004 metadata corrections already applied). |
| `papers/cover_letter.tex` / `cover_letter.md` / `cover_letter.pdf` | administrative | rewrite | Venue names Elsevier *Swarm and Evolutionary Computation* vs repository-wired MDPI class — OPEN C-08, Phase 4 decides; PDF is a stale render. |
| `papers/Definitions/` (`mdpi.cls`, `mdpi.bst`, `journalnames.tex`, logos) | journal class | keep | Present and referenced by `main.tex`. |
| `papers/PAPER_BUILD_PROMPT.md` | governance | keep | Master framework (rank 2). |
| `papers/PAPER_REVIEW_PROMPT.md` | governance | keep | Companion review prompt; examples only. |
| `papers/README.md` | docs | verify | Still describes the R2 addendum as covering the ablation "added for revision 2" — superseded framing (C-01/C-02); correct on the review pack mechanics. |
| `papers/build_prompt_phases/` (11 files) | companions | keep | Rank-5 examples only, per `instruction_precedence.md`; never edited (Section 12.4). |

### 1.2 Rendered outputs at `papers/` root

| Asset | Classification | Notes |
|---|---|---|
| `papers/DT-GSK.pdf` | regenerate | Stale build of `main.tex` (pre-Phase-4 content); rebuilt by `build_pdf.py` in Phase 9. |
| `papers/supplementary.pdf` | regenerate | Stale build; rebuilt by `build_supplementary.py`. |
| `papers/DT-GSK-clean.pdf` | archive | Unreferenced by any script/doc; superseded manual build variant. |
| `papers/DT-GSK-CEC2017-review.pdf` | archive | Advisor review pack built by `generate_review_pack.py` **from `results/_run_all/` staging that has since been thinned away** — inputs no longer exist; non-manuscript, non-admissible. |
| `papers/DT-GSK-CEC2017-review_missing.log` | archive | Missing-panel log of the same stale review-pack run. |

### 1.3 Generator and build scripts (`papers/scripts/`)

All 18 expected scripts from Section 4.1 exist (plus `sitecustomize.py`, a
src-layout path bootstrap — keep). Classification is about required action
before use, not code deletion.

| Script | Reads | Writes | Classification / required action |
|---|---|---|---|
| `generate_latex_tables.py` | `results/paper_tables/T{1..16}.csv` (+ `results/ablation/ablation_matrix_rank_summary*.csv` for ablation fragments) | `papers/tables/T01..T16.tex`, `ablation_<tag>.tex` | verify — input dir is legitimately absent until the Phase 6 task 23 export; ablation branch is Phase-12-only; script fails loudly when inputs missing (good). Must gain bundle-provenance pass-through per Section 4.4. |
| `generate_parametric_tables.py` | `results/paper_tables/T21.csv`, `T22.csv` | `papers/tables/T21.tex`, `T22.tex` | verify — conditional on promoted parametric release (Section 4.4); otherwise T21/T22 marked unavailable. |
| `generate_t16_bca.py` | reference tree via `result_loader.load_algorithm` (reference-first, fallback exists); BCa seed 20260422 | `papers/tables/T16_bca.tex` | verify — run only after task 10 strict-source guard disables the `results/_run_all` fallback. |
| `generate_nemenyi_cd.py` | **`papers/tables/T16.tex` (rendered LaTeX parsed by regex)** | `papers/figures/ranks/nemenyi_cd_d50.pdf` | rewrite (Phase 7) — rendered-artifact-as-source defect F-12.1; re-point to the authoritative machine-readable rank output. |
| `generate_rank_charts.py` | `results/paper_tables/T16.csv` | `papers/figures/ranks/friedman_gsk_family.pdf` | verify — same Phase 6 input condition; fails loudly when missing (good). |
| `generate_full_convergence.py` | `benchmarks/cec_reference_results/cec2017/` (ISM `CheckpointErrors_*`, GSK `curves/`) | `all_funcs_D{10,50}_{a,b,c}.pdf` | rewrite (CR-0001) — code reads the reference tree (docstring stale, says `results/`); must become seven-curve family overlay before Phase 7. |
| `generate_cec2011_convergence.py` | `benchmarks/cec_reference_results/cec2011/` | `cec2011_{a,b,c}.pdf` | rewrite (CR-0001) — same; docstring stale, code reference-first. |
| `generate_cec2013_convergence.py` | reference tree **then `results/_run_all` and `results/<opt>` fallbacks** | `cec2013_{a..d}.pdf` | rewrite — wrap fallbacks under the strict guard; add dimension to output filenames (Section 8.5 overwrite hazard); CR-0001 seven-curve. |
| `generate_trace_figures.py` | `results/dt-gsk/**/GenLog_*` (staging; gone) | `ace_probability_F14_D10.pdf`, `accept_diversity_F14_D10.pdf` | verify — BLOCKED until a validated GenLog diagnostic release is promoted (Section 8.5); immutable release has no `GenLog_*`. |
| `generate_adaptive_params_panel.py` | `results/dt-gsk/**/GenLog_*` (staging; gone) | `adaptive_params_all_D10.pdf` | verify — same GenLog promotion condition. |
| `generate_nlpsr_trajectory.py` | none (analytic equation) | `nlpsr_trajectory.pdf` | keep — conceptual; verify formula vs frozen code in Phase 3. |
| `generate_flowchart.py` / `generate_taxonomy_figure.py` | none (authored spec) | flowchart / taxonomy PDFs (+`_preview.png`) | keep — conceptual art generators. |
| `generate_review_pack.py` | reference tree gen_logs, falls back to `results/_run_all` | `papers/DT-GSK-CEC2017-review.pdf` | keep (non-manuscript tooling) — reference seven-curve overlay implementation pattern for CR-0001; its staging fallback must never feed a manuscript exhibit. |
| `generate_ablation_matrix.py` | `results/_ablation/` staging | `results/ablation/ablation_matrix_rank_summary*.csv` | keep, Phase-12-only — MUST NOT run for the primary paper (Section 6.10). |
| `build_pdf.py` | LaTeX sources | `papers/DT-GSK.pdf` | keep. |
| `build_supplementary.py` | LaTeX sources | `papers/supplementary.pdf` | keep. |
| `build_docx.py` | `main.tex` + figures (Ghostscript rasterisation) | `papers/DT-GSK.docx` | verify — **confirmed: `main()` parses no CLI arguments; the `--supplementary` entry point expected by Appendix D.6 does not exist yet** (Section 4.1 audit note recorded; Phase 9 dependency). |

### 1.4 Tables and figures

Full per-exhibit map (T01–T22, T16_bca, ablation fragments, all committed and
planned figures): **`table_figure_source_map.csv`** in this directory.
Highlights:

- **T01–T16**: regenerate; sole sanctioned input producer is the Phase 6
  task 23 export from the controlled analysis bundle (Section 7.13);
  `results/paper_tables/` is currently absent — a recorded-as-`missing`,
  non-failing state per Section 4.4.
- **T16_bca**: regenerate under the strict-source guard.
- **T21/T22**: conditional on a promoted parametric release; **defect
  F-11.3** — the same `T22.tex` is `\input` twice with contradictory
  captions (main claims CEC2017 D=50 full comparison; supplement declares an
  n=3, 3-function, D=30 pilot whose Wilcoxon p is floor-bounded at 0.25).
- **T06**: duplicate inclusion main + supplement (Section 8.1 redundancy).
- Convergence grids: reference-tree-sourced but two-series; CR-0001
  seven-curve redesign before Phase 7. `all_funcs_D50_*.pdf` are orphans.
- Trace figures: orphan derivatives of vanished GenLog staging; blocked on a
  Section 2.4 diagnostic promotion.

## 2. T17–T20 — intentional gap (task 11 requirement)

`papers/tables/` contains `T01..T16, T16_bca, T21, T22` and **no
`T17.tex`–`T20.tex`**. Per Section 4.1 this is a **deliberate, documented
numbering gap**: the fragments MUST NOT be invented and the surviving tables
MUST NOT be renumbered merely to close the gap. Recorded here and as four
`intentional-gap` rows in `table_figure_source_map.csv`. No generator emits
T17–T20 (verified against `generate_latex_tables.py` and
`generate_parametric_tables.py` code).

## 3. Stale runbook claim — `results/paper_tables/` "from the stats pass"

**STALE (recorded per Phase 2 task 11).** `runbook.md` line 101
("`# --- 6. Tables (need results/paper_tables/ CSVs from the stats pass) ---`")
and lines ~208–210 ("needs the `results/paper_tables/` CSVs produced by the
stats pass"), mirrored at `docs/getting-started/runbook.md` line 123, claim
the T-CSV inputs come from the historical statistics pass (whose outputs are
the *different* files `results/_run_all/_analysis/<suite>/…`; nothing in the
current toolchain writes `results/paper_tables/`). Their **sole sanctioned
producer is the Phase 6 task 23 export from the controlled analysis bundle**
(Sections 4.4 and 7.13), with bundle provenance (release ID, source paths,
checksums) on every exported CSV. Cross-recorded as conflict row **C-11** in
`instruction_precedence.md`. Runbook files themselves are left untouched
(Section 12.4); the claim is marked stale here, not edited there.

## 4. Raw/derived separation audit (task 12)

Classification frame per Section 6.5: raw immutable evidence → verified
derived evidence → rendered artifacts; rendered artifacts never source data.

### 4.1 Findings

| id | Finding | Status / owner |
|---|---|---|
| F-12.1 | `generate_nemenyi_cd.py` parses **`papers/tables/T16.tex`** (a rendered artifact) as its numerical source for the CD diagram — the only exhibit-sources-exhibit chain found. | KNOWN defect, pre-assigned: **Phase 7 fixes** (re-point to authoritative rank CSV from the analysis bundle). Not fixed in Phase 2 by design. |
| F-12.2 | For every data-backed exhibit, raw evidence exists in `benchmarks/cec_reference_results/` (checksummed in `data_ledger.csv`), so **no number's ultimate source is an exhibit** — with the temporary caveat that the derived middle layer (`results/paper_tables/` T-CSVs, controlled stats bundle) is absent at the anchor, leaving committed `.tex`/figure files as the only *current* in-repo carriers of their rendered values. Acceptable only because Phase 6 re-derives everything from raw before any number is asserted in prose. | Recorded; resolved structurally by Phase 6 task 23 + Phase 7 regeneration. |
| F-12.3 | **Exception to F-12.2:** T21/T22 (parametric pilot) have **no raw evidence anywhere in the repository** — `results/paper_tables/T21,T22.csv` absent, sweep staging `results/dt-gsk/sweeps/parametric-study/` absent, no promoted parametric release. The committed `T21.tex`/`T22.tex` are currently the *sole* carriers of those numbers. | Per Section 4.4: locate/document historical sweep provenance in `assumption_register.csv` or record the regeneration command, promote via `scripts/promote_evidence.py`, else mark T21/T22 unavailable in `evidence_gap_register.md`. |
| F-12.4 | Same-statistic duplication risk: Friedman mean ranks will exist in T16.tex, `friedman_gsk_family.pdf`, the CD diagram, and the stats bundle (`*_friedman_ranks.csv`). No authoritative output is currently designated. | Phase 5/6 must designate the analysis-bundle CSV as authoritative and equality-test the rest (Section 6.5). |
| F-12.5 | Evidence write protection: sampled evidence files (`cec2017/dt-gsk/per_run.csv`, `cec2011/gsk/per_run.csv`, `cec2013/egsk/environment.json`) are **writable — no filesystem read-only attribute is set** on the reference tree. Checksums for all 174 ledger cells are now pinned in `data_ledger.csv`/`experiment_matrix.csv`. | `write_protection_status` must be established/recorded by the release-manifest task (Section 6.6) and enforced by `promote_evidence.py` (task 10). |
| F-12.6 | Metadata-overwrite defect (cross-reference): `cec2017/apgsk/` cell metadata (`per_run.csv`, `seed_schedule.csv`, `environment.json`, `run_config.json`) reflects a **D100-only re-run (env timestamp 2026-07-08, commit `20cfed0a…`)**, deleting per-run/seed/environment evidence for D10/D30/D50 while their summary CSVs, curves (29/dim), and CheckpointErrors (29/dim) remain. Exactly the "existing immutable evidence is never overwritten" violation Section 2.4 prohibits, committed before the freeze. Ledger carries three `DEFECT` rows (`comparability_status = blocked-pending-recovery-or-new-release`). | BLOCKER for full-panel per-run claims at cec2017 D10/30/50; resolution = recover pre-overwrite metadata from history into a **new** release, or scope reduction (Phase 2 exit criteria). |

### 4.2 Stale / orphan derivative list

| Artifact | Why stale/orphan | Disposition |
|---|---|---|
| `papers/figures/convergence/all_funcs_D50_{a,b,c}.pdf` | Generated alongside D10 grids; referenced by no `.tex`. | archive (exhibit plan may re-adopt) |
| `papers/figures/convergence/F{01,04,15,22}_D{30,50}.png` (8 files) | Legacy per-function rasters; referenced only by a superseded companion file. | archive |
| `papers/figures/taxonomy/metaheuristic_tree_preview.png`, `papers/figures/flowchart/dt_gsk_flowchart_preview.png` | Preview rasters, not manuscript inputs. | archive |
| `papers/figures/traces/*.pdf` (3 files) | Source GenLog staging deleted; no admissible diagnostic release. | verify → regenerate-after-promotion or drop |
| `papers/DT-GSK-CEC2017-review.pdf` + `_missing.log` | Built from thinned-away `results/_run_all` staging. | archive |
| `papers/DT-GSK-clean.pdf` | Unreferenced build variant. | archive |
| `papers/DT-GSK.pdf`, `papers/supplementary.pdf` | Pre-rebuild renders; will drift from Phase 4–7 content. | regenerate (Phase 9) |
| `results/_run_all/_analysis/<suite>/` stats bundle (12 files) | Historical stats-pass output; superseded by the Phase 5/6 controlled analysis bundle; non-admissible staging. | quarantined in place (see `staging_inventory.md`) |
| `papers/tables/T01–T16, T16_bca, T21, T22` committed values | Derived inputs absent at anchor (F-12.2/F-12.3). | regenerate (T21/T22 conditional) |
| `papers/figures/ranks/*.pdf` | Inputs absent (T16.csv) / rendered-source defect (F-12.1). | regenerate (Phase 7) |

No manuscript table or figure was found whose number lacks a raw-evidence
path **except** T21/T22 (F-12.3) and the apgsk D10/30/50 per-run layer
(F-12.6) — both explicitly blocked/conditioned above; and no exhibit other
than F-12.1 is consumed as a data source by any generator.

---

*Written by the Phase 2 task 9/11–13 execution agent. No file under
`benchmarks/cec_reference_results/`, `papers/tables/`, `papers/figures/`,
`papers/sections/`, or `results/` was modified.*
