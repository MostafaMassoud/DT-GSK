# Project Structure

> **What this page is.** A directory-by-directory map of the repository — what
> every maintained area holds. **Who it is for.** Developers orienting in the
> codebase. **See also.** [Architecture](architecture.md) for the runtime layout
> and [Module Dependencies](module_dependencies.md) for dependency direction.

This document describes every maintained project area. Large numeric benchmark
data and imported reference evidence are summarized by directory because they
contain many generated or third-party files; use `gsk-list --references` and
`Get-ChildItem -Recurse benchmarks` for exhaustive local enumeration.

## Root Files

| Path | Purpose |
|---|---|
| `.gitignore` | Ignore generated caches, build output, and experiment results. |
| `ARCHITECTURE.md` | Authoritative structural map of the system (layers, contracts, ownership); the reference-folder [architecture.md](architecture.md) summarizes it. |
| `CITATION.cff` | Citation metadata for research use. |
| `MANIFEST.in` | Source-distribution inclusion rules for docs, configs, scripts, tests, and package data. |
| `pyproject.toml` | Build metadata, dependencies, package discovery, and console scripts. |
| `README.md` | Detailed root landing page with commands, documentation map, validation, reproducibility, and maintenance guidance. |
| `REPO_MAP.md` | One-screen newcomer orientation to the repository's three cooperating parts. |
| `requirements.txt` | Runtime dependency pins mirroring `pyproject.toml` for plain-`pip` installs. |
| `requirements-dev.txt` | Development dependency pins (runtime plus test/lint/build tooling). |
| `run.py` | Canonical source-checkout runner for direct campaign execution. |
| `runbook.md` | Quick copy-paste operational command reference. |
| `SKILL.md` | Project-specific agent operating contract. |
| `PROJECT_RULES.md` | The project "constitution": binding engineering rules for the codebase. |
| `CODING_STANDARD.md` | Python coding standard for the package. |
| `DESIGN_GUIDE.md` | Design principles and the guide to extending the system. |
| `BENCHMARK_RULES.md` | Rules governing benchmark evaluation and protocol fidelity. |
| `PERFORMANCE_RULES.md` | Rules governing performance and parallel-execution work. |
| `FINAL_RELEASE_REPORT.md` | DT-GSK final release report (CEC2017). |

The root Markdown operating documents are `README.md` (landing page),
`SKILL.md` (agent operating contract), and `runbook.md` (command reference). The
full documentation package lives under `docs/`, organized into themed subfolders
(`getting-started/`, `reference/`, `algorithms/`, `development/`, `research/`,
`prompt/`) with `docs/index.md` as the entry point; the review and audit prompts
live in `docs/prompt/`.

## Directories

| Path | Purpose |
|---|---|
| `benchmarks/` | Python CEC evaluator and imported reference evidence. |
| `configs/` | YAML experiment configurations. |
| `docs/` | Canonical documentation in themed subfolders (getting-started, reference, algorithms, development, research, prompt) with `docs/index.md` as the entry point. |
| `docs/html/` | Generated browsable HTML documentation site. |
| `papers/` | Manuscript sources (`main.tex`), the matplotlib review pack (`scripts/generate_review_pack.py` -> `DT-GSK-CEC2017-review.pdf`), figure/table generators (`scripts/generate_latex_tables.py`, `scripts/generate_ablation_matrix.py`, the `scripts/generate_*_convergence.py` grids, and more), and bibliography. |
| `reference_papers/` | Acquisition bundle for the manuscript's citations: `references.bib`, a grouped index (`README.md`), a flat checklist (`PAPERS_LIST.md`), and the 57 cited PDFs named `<bibkey>.pdf` (gitignored, copyrighted). |
| `results/` | Generated experiment output: `_run_all/` (campaign trees plus the `_analysis/` statistics output), `_ablation/` (per-cell DT-GSK ablation runs), and `ablation/` (aggregated ablation rank-summary matrices). This directory is not source evidence. |
| `scripts/` | CEC suite launchers, the documentation builder, and developer utilities. |
| `src/gsk_family/` | Importable Python package. |
| `tests/` | Pytest unit, smoke, regression, and performance checks. |

### Reference Results

`benchmarks/cec_reference_results/<suite>/<optimizer>/` is the committed
reference panel — the paper's single source of truth for all data and
statistics. Each optimizer directory is flat (no `summary/` subdirectory):
per-dimension summary CSVs `<opt>_<suite>_D<dim>.csv` (plus a
`<opt>_cec2011.csv` all-functions rollup for cec2011), `per_run.csv`, the
provenance files (`environment.json`, `run_config.json`, `seed_schedule.csv`,
`verification.json`, `phase0_protocol.json`), `curves/` (per-run convergence
CSVs), and `gen_logs/` (`CheckpointErrors_*.csv`). The full 7-optimizer panel
(`gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`, `dt-gsk`) exists
for exactly the three suites that carry committed reference evidence: `cec2017`,
`cec2011`, and `cec2013`. The `cec2020` and `cec2013lsgo` suites are runnable in code but ship no committed reference statistics here. Rendered PNGs and
`*_log_*.txt` reports are not committed (both are regenerable). Two sibling trees sit beside the suite folders: `_ablation/` (DT-GSK scaffold and SGSM-overlay ablation cells, with a `manifest.json`) and `_paper_tables/` (the frozen `T*.csv` manuscript tables).

## Source Package

| Path | Purpose |
|---|---|
| `src/gsk_family/__init__.py` | Package marker and version surface. |
| `src/gsk_family/types.py` | Shared dataclasses for optimizer and run records. |
| `src/gsk_family/stats.py` | Error, summary, and formatting helpers. |
| `src/gsk_family/analysis/` | Post-run statistical comparison: Friedman/Wilcoxon/Holm tests, Vargha-Delaney/Cliff effect sizes, BCa bootstrap, Nemenyi CD and rank figures, and LaTeX tables. |
| `src/gsk_family/benchmark_adapter/` | Suite protocol metadata, problem factory, and shape validation. |
| `src/gsk_family/cli/` | `gsk-list`, `gsk-run`, `gsk-validate`, and `gsk-stats` entry points. |
| `src/gsk_family/common/` | reference-compatible RNG, rounding, donor, bounds, population, and reduction helpers. |
| `src/gsk_family/optimizers/` | GSK family optimizer kernels and optimizer-local helper modules. |
| `src/gsk_family/runners/` | Config parsing, seed policy, execution, output writers, parallel dispatch, profiling, floating-point-regime verification (`fp_regime.py`), and reference verification. |

### Analysis Package

The `analysis/` package is the post-run statistical layer behind `gsk-stats`:

| Path | Purpose |
|---|---|
| `analysis/family_report.py` | Orchestrator (`generate_family_report`, `analyze_family`, `write_report`) tying the loaders, tests, figures, and tables together. |
| `analysis/statistics.py` | Test kernel: paired Wilcoxon, Friedman ranks, Holm/Benjamini-Hochberg/Bonferroni corrections, Vargha-Delaney A12, win/tie/loss, and `bootstrap_bca_ci`. |
| `analysis/statistical_tests.py` | Higher-level Wilcoxon/Friedman result records and table formatting used by the live `--stats` pass. |
| `analysis/result_loader.py` | Discover and load reference and reproduced summary tables — reference-first: the committed panel is the single source of truth, a locally reproduced run is only a fallback; suite/dimension defaults. |
| `analysis/project_policy.py` | Single source of truth for `RUNNABLE_OPTIMIZERS` and the `REFERENCE_COMPARATORS` panel. |
| `analysis/figures.py` | Nemenyi critical-difference and rank-chart PNG rendering. |
| `analysis/latex_tables.py` | Friedman-rank and Wilcoxon-summary LaTeX fragments. |

## Configs

| Path | Purpose |
|---|---|
| `configs/smoke.yml` | Fast smoke experiment. |
| `configs/all_optimizers_smoke.yml` | Fast all-optimizer sphere smoke experiment with profiling metadata. |
| `configs/all_optimizers_cec2017_reduced.yml` | Reduced all-optimizer CEC2017 parity experiment. |
| `configs/golden_validation_smoke.yml` | Reduced reference-backed validation campaign. |
| `configs/performance_campaign_smoke.yml` | Serial-versus-parallel performance smoke campaign. |
| `configs/all_cec2011.yml` | CEC2011 suite campaign template. |
| `configs/all_cec2017.yml` | CEC2017 suite campaign template. |
| `configs/agsk_cec2020.yml` | AGSK CEC2020 campaign template. |
| `configs/_ablation/` | Generated per-cell ablation configs written by `scripts/run_ablation.py`. |
| `configs/_recover/` | Recovery configs for regenerating lost reference cells (e.g. `apgsk_cec2017_recover.yml`). |
| `configs/experimental/` | Opt-in experimental and diagnostic campaign configs. |
| `configs/publish/` | Publication campaign configs (e.g. `dt_gsk_cec2017_final.yml`). |
| `configs/README.md` | Notes on the config files. |

## Scripts

| Path | Purpose |
|---|---|
| `scripts/run_all_cec2011.py` | Launch CEC2011 campaign through `gsk-run`. |
| `scripts/run_all_cec2013.py` | Launch CEC2013 campaign through `gsk-run`. |
| `scripts/run_all_cec2013lsgo.py` | Launch CEC2013LSGO campaign through `gsk-run`. |
| `scripts/run_all_cec2017.py` | Launch CEC2017 campaign through `gsk-run`. |
| `scripts/run_all_cec2020.py` | Launch CEC2020 campaign through `gsk-run`. |
| `scripts/run_gsk_family.py` | Source-checkout run wrapper for direct campaign execution. |
| `scripts/run_ablation.py` | DT-GSK scaffold ablation launcher (remove-one/add-one cells on `cec2017`/`cec2011`/`cec2013`); writes `configs/_ablation/<cell>.yml` and `results/_ablation/<cell>/`. |
| `scripts/build_docs_html.py` | Generate the browsable HTML documentation package from Markdown and Python docstrings. |
| `scripts/validate_profile_lock.py` | Profile-lock gate guarding the published parameter profiles. |
| `papers/scripts/check_reproducibility_manifest.py` | Gates `reproducibility_manifest.json` against disk and against the freeze manifest's `files[]`, and checks its recorded anchor. Added at pass-54 after that file went stale inside its own pass three times. Run it after every rebuild. |
| `scripts/validate_egsk_vs_reference.py` | Paired per-run validation of the Python EGSK port against the imported MATLAB reference checkpoint logs. |
| `scripts/parity_trace.py` | Reference-parity diagnostic for tracing optimizer streams. |
| `scripts/wilcoxon_reference.py` | Standalone Wilcoxon reference-comparison diagnostic. |
| `scripts/analyze_dt_diagnostics.py` | Offline reader that aggregates opt-in DT-GSK per-generation diagnostic traces into summary CSVs. |
| `scripts/plot_convergence_from_curves.py` | Render convergence-graph PNGs from already-committed curve CSVs, without re-running an optimizer. |
| `scripts/run_campaign.py` | One-command, resumable driver for the whole post-fix evidence campaign; runs everything still missing, in order, and never overwrites completed work. |
| `scripts/retime_comparators.py` | Re-time the six comparator algorithms on CEC2017 on one idle machine, for a single-environment runtime table (RT-001). |
| `scripts/promote_evidence.py` | Promote an accepted staging bundle into the immutable `benchmarks/cec_reference_results/` evidence tree. |
| `scripts/recover_apgsk_perrun.py` | One-off recovery of the lost apgsk CEC2017 D10/30/50 per-run rows into the reference tree (anomaly A2-004). |
| `scripts/run_overlay_ablation_51.py` | Run the SGSM-overlay direct-isolation ablation at 51 runs per cell for CEC2017 (D50/D100) and CEC2013 (D50). |
| `scripts/run_revision_experiments.py` | One-command, resumable driver for the five revision experiments E1-E5 (refinement-basis contrast, DT-GSK at the comparators' `NP = 100`, uniform-vs-tiered configuration, parameter sensitivity, and dimension-boundary sensitivity); writes under `results/_revision/`. |
| `scripts/run_e1_basis_contrast.py` | The E1 coordinate-basis arm of the refinement-basis contrast: the shipped configuration in every respect except the polish basis, paired against the frozen no-refinement and eigenframe arms. |
| `scripts/README.md` | Notes on the scripts. |

## Documentation

`docs/index.md` is the maintained index. The canonical guides are grouped into
themed subfolders: `getting-started/`, `reference/`, `algorithms/`,
`development/`, `research/`, and `prompt/` (the review and audit prompts). Rich
workflow diagrams and numerical examples live in `docs/reference/diagrams.md`
and `docs/research/numerical_examples.md`.

## Tests

| Path | Purpose |
|---|---|
| `tests/unit/` | Focused helper, algorithm, stats, seed, and API tests. |
| `tests/smoke/` | Fast optimizer and runner smoke tests. |
| `tests/regression/` | End-to-end and validation-ladder regression tests. |
| `tests/performance/` | Parallel-runner and performance checks. |
| `tests/test_imports.py` | Top-level smoke check that the package and its scaffold modules import. |
