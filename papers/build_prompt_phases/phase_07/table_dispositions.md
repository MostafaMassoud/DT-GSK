# Phase 7 — Table Dispositions (Task B)

Evidence lock: all empirical inputs restricted to the frozen Phase 6 analysis
bundle `papers/analysis/rel-2026-07-10-262fc16c9/` and the staging export
`results/paper_tables/` (itself exported exclusively from that bundle,
Phase 6 task 23; see `results/paper_tables/provenance.json`).

## T21 / T22 — parameter-sensitivity tables: NOT-GENERATED (EG-006)

- Disposition: **NOT-GENERATED**. No admissible parameter-sensitivity
  release exists (evidence gap register entry **EG-006**; Phase 6
  disposition). `results/paper_tables/provenance.json` records: "T21/T22
  (parametric sensitivity) NOT exported: no admissible sensitivity release
  exists (EG-006)".
- `papers/scripts/generate_parametric_tables.py` was **not run** for output.
  Its output destination was verified as already fixed: it writes to
  `papers/tables/` (`_OUT = _PAPER_DIR / "tables"`, lines 20-21).
- STALE-ARTIFACT WARNING: legacy committed `papers/tables/T21.tex` and
  `papers/tables/T22.tex` remain on disk from a pre-Phase-6 build. They are
  STALE (Phase 6 finding: legacy committed `papers/tables/*.tex` are stale;
  regenerate, never trust) and MUST NOT be `\input{}` by the manuscript
  until an admissible sensitivity release exists and closes EG-006. They
  were intentionally not regenerated and not deleted in this task (deletion
  is a repo-curation decision for the orchestrator).

## T17–T20 — DO-NOT-CREATE rule

- Table IDs T17–T20 are **not defined** in the Phase 4 exhibit plan
  (`papers/build_prompt_phases/phase_04/exhibit_plan.csv`) and have no
  admissible data source. **Do not create** `T17.tex`–`T20.tex` (or any
  exhibit claiming those IDs) in any Phase 7 or later build step. Any
  future need for new table IDs must go through an exhibit-plan revision,
  never ad-hoc creation.

## Ablation tables — SUPPRESSED (P6)

- Pre-generation assertion (2026-07-11): `results/ablation/` does not
  exist and **zero** `ablation_matrix_rank_summary*.csv` files exist
  anywhere under `results/` (including `results/_ablation/`, which was
  never read). `generate_latex_tables.py` scans only
  `results/ablation/ablation_matrix_rank_summary*.csv`; nothing was
  reachable.
- Belt-and-braces: a `--skip-ablation` flag was added to
  `papers/scripts/generate_latex_tables.py` and used for the Phase 7 run,
  so the ablation scan is not executed at all and no `ablation_<tag>.tex`
  can be emitted regardless of future directory contents
  (exhibit_plan.csv P6: ablation exhibits are
  DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY).
- Result: **no ablation .tex artifact was produced.**

## Diagnostic-release-gated figure generators — NOT RUN

- `papers/scripts/generate_trace_figures.py` and
  `papers/scripts/generate_adaptive_params_panel.py` are gated on a
  validated promoted GenLog diagnostic release. **No promoted GenLog
  release exists**, so neither script was run (per binding constraints;
  exhibits F-TRACE / F-ADAPT remain unavailable per the evidence gap
  register).

## Superseded legacy figure

- `papers/figures/ranks/nemenyi_cd_d50.pdf` (old single-dim CD diagram,
  produced by the retired T16.tex-parsing flow) is SUPERSEDED by the four
  bundle-wired diagrams in `papers/figures/nemenyi/`. The old file was not
  regenerated; manuscript references must be repointed in the writing
  phase.
