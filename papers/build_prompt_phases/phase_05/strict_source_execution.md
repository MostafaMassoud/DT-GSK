# Phase 5 (tasks 14-15) — Strict-source execution design and deterministic-output contract

- **Date:** 2026-07-10 (pre-registered BEFORE any outcome inspection; this document designs Phase 6 execution, it reports no statistical outcome).
- **Release of record:** rel-2026-07-10-262fc16c9 — `benchmarks/cec_reference_results/` at anchor commit `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` (`papers/governance/evidence_release_manifest.json`).
- **Binding inputs honored:** `papers/build_prompt_phases/phase_04/exhibit_plan.csv` pre-registrations P1–P8; `papers/governance/claims_evidence_matrix.csv`; `papers/build_prompt_phases/phase_05/source_resolution_map.csv` (tasks 13–14, same date); `papers/governance/seed_and_pairing_audit.md`; `papers/governance/phase2_anomaly_register.csv`.

## 1. Strict-source guard: activation and mechanics

Every Phase 6 analysis command MUST run with the strict-source guard active. Two equivalent activations (verified against `src/gsk_family/analysis/result_loader.py`):

1. Environment variable: `GSK_STRICT_SOURCE=1` (checked by `strict_source_enabled()`; accepted truthy values `1/true/yes/on`).
2. Programmatic: `set_strict_source(True)` — this is what `gsk-stats --strict-source` threads through (`src/gsk_family/cli/stats.py`).

Guard semantics in strict mode (as implemented in `result_loader.py`; cited, not modified):

- `load_reproduced()` / `_reproduced_csv_path()` raise `StrictSourceViolation` unconditionally — `results/` staging is never resolvable.
- `load_algorithm()` fails loudly (`StrictSourceViolation`) when a requested cell is missing from the reference release instead of falling back to staging.
- `audit_source_open(path, role)` is the chokepoint: every opened data file is resolved and checked with `Path.is_relative_to(benchmarks/cec_reference_results)`; any path outside the release raises `StrictSourceViolation`. Every open (both modes) is appended to the collectable audit list returned by `get_source_audit()`.

**Allowed input root (exclusive):** `benchmarks/cec_reference_results/` (release rel-2026-07-10-262fc16c9). **Forbidden inputs (hard failure, no exceptions):** `results/` (all of it), `results/_run_all/`, and the quarantined ablation staging `results/_ablation/`. A read attempt anywhere outside the release aborts the analysis run; partial outputs from an aborted run are deleted before rerun (no mixed-provenance output directory).

**Coverage requirement for direct readers (pre-registered obligation on Phase 6 scripts):** `audit_source_open()` is currently wired into `load_summary_csv()` (summary CSVs). Any Phase 6 code path that opens `per_run.csv`, `gen_logs/CheckpointErrors_*.csv`, or any other release file directly MUST call `audit_source_open(path, role=<role>)` immediately before opening it, with roles from the fixed vocabulary: `summary_csv`, `per_run_csv`, `checkpoint_log`, `metadata_json`. This makes the guard's outside-the-release rejection and the audit log complete for all three input resolutions in `source_resolution_map.csv`. A Phase 6 run in which any opened evidence file is absent from the audit log is invalid.

## 2. Output area and source-use log

- **Output directory (fixed):** `papers/analysis/rel-2026-07-10-262fc16c9/<suite>/` with `<suite>` in `{cec2017, cec2013, cec2011}`. No analysis output is ever written into `results/` or into the release tree (release is read-only; read-only compliance per the Phase 2 audits).
- **Source-use log (mandatory, per output directory per run):** after each analysis command completes (or fails), the content of `get_source_audit()` is serialized as `source_use_log.json` next to the outputs, schema:

```json
{
  "release": "rel-2026-07-10-262fc16c9",
  "anchor_commit": "262fc16c91fbe5608a1a0b0c5df3cbcd009edc21",
  "command": "<exact argv>",
  "strict_source": true,
  "started_utc": "<ISO-8601>",
  "finished_utc": "<ISO-8601>",
  "status": "ok | StrictSourceViolation | error",
  "opened": [ {"path": "<resolved absolute path>", "role": "summary_csv|per_run_csv|checkpoint_log|metadata_json"} ]
}
```

  `clear_source_audit()` is called at the start of each command so each log covers exactly one command. (The existing `gsk-stats --strict-source` CSV emission `source_use_audit.csv` may additionally be produced by that tool; `source_use_log.json` is the Phase 6 artifact of record and is written even on failure, mirroring the `finally:` behavior in `src/gsk_family/cli/stats.py`.)
- Every `source_use_log.json` is checked post-run: all `opened[].path` entries must be under `benchmarks/cec_reference_results/`; any other prefix (in particular `results/` or `results/_ablation/`) is a hard Phase 6 gate failure even if the run "succeeded".

## 3. Data-availability dispositions (fixed now, before outcomes)

1. **apgsk CEC2017 D10/D30/D50 per-run gap** (`phase2_anomaly_register.csv` A2-004/A2-006; `seed_and_pairing_audit.md` Sec. 6, anomaly A1): `cec2017/apgsk/per_run.csv` carries D100 only (1,479 rows). Disposition, binding for Phase 6: run-level quantities vs apgsk at CEC2017 D10/D30/D50 (per-function Wilcoxon, A12/Cliff, BCa CIs, run-level W/T/L) are **disclosed-unavailable** — explicit `n/a` cells plus a standard footnote; the vs-apgsk comparison at those dimensions is carried by the pre-specified **function-level Wilcoxon signed-rank across per-function means** (apgsk summary CSVs are complete and verified 580/580 against gen_logs final checkpoints). apgsk D100 run-level analyses proceed normally (1,479/1,479 verified). The audit's Option 1 (gen_logs final-checkpoint columns as a sanctioned per-run source for the missing dims) may be adopted **only** through a registered change request plus `papers/governance/data_ledger.csv` entry before Phase 6 execution; absent that CR this disposition stands. No silent switching, no imputation, no hand-written rows.
2. **CEC2011 error column** (`phase2_anomaly_register.csv` A2-017): `error` is NaN by design on cec2011; all cec2011 run-level statistics use `best_fitness`. cec2011 exhibits report native problem dimensions.
3. **T-SENS / F-TRACE / F-ADAPT:** not resolvable from rel-2026-07-10-262fc16c9 (no sensitivity sweep; no `GenLog_*` diagnostic files — release `gen_logs/` contain exactly the `CheckpointErrors_*` files). Disposition: disclosed-unavailable via `papers/governance/evidence_gap_register.md`; computable only from a future validated promoted release.
4. **Ablation (X-ABL-01..03):** DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY (P6). `results/_ablation/` is quarantined staging and is a forbidden input in every phase of this build.

## 4. Pairing and aggregation rules (restated as execution constraints)

- **Pairing:** the unified seed schedule `get_cec_seed(20240620, dim, func, run)` yields identical seeds across all 7 panel algorithms per `(dim, func, run)`; pairing is VALID for every comparator pair on cec2017/cec2013/cec2011 (identical instances, identical seeds, shared initial populations) — verified by full recomputation of 70,813 schedule rows + 16,514 gen-log rows with 0 mismatches in `papers/governance/seed_and_pairing_audit.md` (Secs. 2–4, 7). All paired run-level tests therefore pair run *r* with run *r*.
- **Pseudoreplication rule:** across-function claims use function-level aggregation only — Friedman over functions on per-function summary statistics [friedman1937use; demsar2006statistical], Wilcoxon across functions on per-function means as the GSK-family convention [wilcoxon1945individual]. Run-level data support per-function pairwise tests and effect sizes where per-run evidence exists [vargha2000critique]; runs are NEVER pooled across functions as if independent.
- **Multiplicity:** Holm is the only primary correction [holm1979simple]; family = one comparator set per (suite, dimension) as pre-registered per exhibit. Benjamini–Hochberg [benjamini1995controlling] appears ONLY in separately-labeled exploratory files (`*_exploratory_bh.csv`); no primary file carries a BH column, no mixed families.
- **Convergence aggregation (P2):** per-checkpoint MEAN error across all runs per algorithm from `gen_logs/CheckpointErrors_<alg>_F<f>_D<d>.csv`; identical basis for all 7 curves; representative-run fallback only on documented absence; no smoothing/extrapolation; display-only log floor documented at render time.
- **Curve selection (P5):** strata (difficulty terciles; DT-GSK standing) computed from release summary CSVs only, emitted to the `curve_selection` output family BEFORE any curve is rendered or viewed; fill priority and tie-breaks exactly as pre-registered in exhibit_plan.csv P5.

## 5. Deterministic outputs (task 15)

Fixed rules; any deviation is a Phase 6 defect.

- **Naming scheme (fixed; single authority for all analysis output filenames):** `papers/analysis/rel-2026-07-10-262fc16c9/<suite>/<family>_<suite>[_D<dim>][_<qualifier>].csv`
  - `<family>` in `{friedman_ranks, nemenyi_cd, wilcoxon_holm, wilcoxon_run, effect_sizes, bca_ci, descriptive_stats, convergence_checkpoints, curve_selection, robustness, cost, rank_trend, class_ranks}` — the complete family vocabulary used by `analysis_registry.csv` (Gate-5 normalization). Schema docs in `papers/build_prompt_phases/phase_05/analysis_output_schemas/` cover `friedman_ranks`, `wilcoxon_holm`/`wilcoxon_run`, `effect_sizes`, `bca_ci`, `descriptive_stats`, `convergence_checkpoints`, `curve_selection`; the remaining families' schemas are fixed in their governing plans (`robustness_plan.md` Secs. 1.0/3–4 for `robustness`; SAP Sec. 9 for `cost`; SAP Sec. 12 for `rank_trend`; SAP Sec. 11 for `class_ranks`; SAP Sec. 5 for the conditional `nemenyi_cd` companion). Family semantics: `wilcoxon_holm` = across-function function-level Wilcoxon+Holm; `wilcoxon_run` = per-function run-level Wilcoxon+Holm; `cost` = runtime summaries; `rank_trend` = rank-vs-dimension descriptive trend; `class_ranks` = exploratory function-class descriptives; `nemenyi_cd` = conditional CD-diagram data (only when the omnibus is significant).
  - `<suite>` in `{cec2017, cec2013, cec2011}`; `<dim>` in `{10,30,50,100}` (cec2017), `{10,30,50}` (cec2013); the `_D<dim>` token is omitted for cec2011 (native dims live in the `dimension` column), omitted for families whose single file spans dimensions in a `dimension` column (`cost`, `rank_trend`, `class_ranks`, `robustness`), and replaced by `_overall` for the descriptive cross-dimension rank aggregates.
  - `<qualifier>`: `exploratory_bh` (separately-labeled exploratory duplicates of the run-level `wilcoxon_run` files), and — for the `robustness` family only — the fixed check tags `r01_mean_vs_median`, `r02_floor_sensitivity`, `r03_lofo_friedman`, `r04_disputed_cell_exclusion`, `r05_unpaired_companion`, `r06_holm_vs_bh`, `r07_secondary_suite_effect`, `r08_overall_aggregation_variants` (crosswalk in `robustness_plan.md` Sec. 1.0). `robustness` family files are emitted under the `<suite>/robustness/` subdirectory (`robustness_plan.md` Sec. 3); all other families sit directly under `<suite>/`.
  - Examples: `friedman_ranks_cec2017_D30.csv`, `friedman_ranks_cec2017_overall.csv`, `wilcoxon_holm_cec2017_D50.csv`, `wilcoxon_run_cec2017_D50.csv`, `wilcoxon_run_cec2017_D50_exploratory_bh.csv`, `bca_ci_cec2011.csv`, `curve_selection_cec2017_D100.csv`, `cost_cec2017.csv`, `rank_trend_cec2017.csv`, `class_ranks_cec2017.csv`, `robustness_cec2017_r02_floor_sensitivity.csv`.
  - PHASE_12 ablation analyses follow the same `<family>_<suite>[_D<dim>]` pattern under `papers/analysis/<future-ablation-release-id>/ablation/` with families `{ablation_matrix_rank_summary, ablation_overlay_rank_summary, ablation_polish_toggle, ablation_effects_<study>, ablation_overhead_<study>}` (pre-registered in `ablation_preregistration.md`).
- **CSV schemas:** exactly as specified per family in `analysis_output_schemas/*.schema.md`. Header row always present; no extra columns; column order fixed.
- **Sort order (all families):** `suite` (fixed per file), then `dimension` ascending, then `function` ascending, then `algorithm` (and `comparator` where present) in P1 panel order: `gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk`. Pairwise families anchor `dt-gsk` as the proposed side and order the comparator column by P1.
- **Float format:** every float is written as C-locale `%.6e` (six significant decimals, exponent notation, `.` decimal separator). Integers written as plain integers. Missing/disclosed-unavailable values written literally as `n/a` (never empty, never 0, never NaN).
- **Bootstrap determinism:** BCa bootstrap [efron1993introduction] with `B = 10000` resamples; base seed `20240620`; per-cell RNG = `numpy.random.default_rng(numpy.random.SeedSequence([20240620, <suite_ordinal>, <dimension>, <function>, <comparator_P1_index>]))` with `suite_ordinal` in `{2017, 2013, 2011}` and `comparator_P1_index` the 0-based P1 position — one independent, reproducible stream per (suite, dim, function, comparator); resampling order fixed by iterating cells in the file sort order.
- **Locale / encoding:** `LC_ALL=C`, `LANG=C` for every analysis command; files written UTF-8 without BOM, `\n` newlines, comma delimiter, minimal quoting.
- **Software versions:** recorded per output directory in `run_manifest.json`: the host environment fields copied from `papers/governance/reproducibility_manifest.json` (Python 3.10.11, pip 26.1.2, git 2.49.0.windows.1, OS Windows-10-10.0.26200-SP0, anchor commit) plus runtime-captured `numpy`, `scipy`, `pandas`, `matplotlib` versions and the exact command lines executed. Rendering-stage figure determinism (fonts, dpi) is a Phase 7 concern; Phase 6 emits CSVs only.
- **Idempotence check:** each Phase 6 command run twice back-to-back must produce byte-identical CSVs (hash-compared); a mismatch is a hard failure.

## 6. Command template (Phase 6)

```
LC_ALL=C LANG=C GSK_STRICT_SOURCE=1 python <analysis entrypoint> \
  --suite <suite> --dims <dims> \
  --reference-root benchmarks/cec_reference_results \
  --out papers/analysis/rel-2026-07-10-262fc16c9/<suite>
```

For the existing CLI: `gsk-stats --strict-source --suite CEC2017 --dims 10,30,50,100 --out papers/analysis/rel-2026-07-10-262fc16c9/cec2017` (strict mode disables the reproduced-proposed path by construction; the proposed algorithm's cells resolve from the release like every comparator's). Every command's `source_use_log.json` + `run_manifest.json` are committed alongside the output CSVs.

## 7. Citations used by the planned analyses

`friedman1937use`, `demsar2006statistical`, `wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling` (exploratory only), `vargha2000critique`, `efron1993introduction` — all present in `papers/governance/allowed_citation_keys.txt`.
