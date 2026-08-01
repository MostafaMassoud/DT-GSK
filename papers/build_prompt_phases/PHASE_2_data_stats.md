# PHASE 2 — Data Consolidation & Statistical Computation

> **⚑ Revision 2 addendum applies to this phase.** Before executing, read [ADDENDUM_R2_cec2013_and_ablation.md](ADDENDUM_R2_cec2013_and_ablation.md) §R2.C — a CEC2013 family panel and the CEC2017 scaffold ablation add tasks to this phase, and the addendum overrides this file where they disagree.

**Objective.** Turn the committed raw runs into the exact tables, ranks, effect sizes, and confidence intervals the paper reports, so that every headline number is reproducible from committed data by a single command.

> This file expands **Phase 2** of `papers/PAPER_BUILD_PROMPT.md` (§"PHASE 2 — Data consolidation & statistical computation"). It **follows** `papers/build_prompt_phases/PHASE_1_scope.md` (outline + claim table locked) and **hands to** `papers/build_prompt_phases/PHASE_3_tables_figures.md` (which consumes the source-of-truth CSVs produced here). Do **not** draft prose, edit `.tex`, or touch `benchmarks/cec_reference_results/**` in this phase.

All paths below are relative to the repo root:
`D:\AI\PhD-Projects\00-GSK-Family\02-GSK_Family_Python_v1.1`
Commands are given for PowerShell and Bash; the Python interpreter is `python`. Run the console entry points (`gsk-run`, `gsk-stats`, `gsk-validate`, `gsk-list`) from an environment where the package is installed (`pip install -e .`); the equivalent module form `python -m gsk_family.cli.<name>` also works if the scripts are not on `PATH`.

---

## Prerequisites

Do not start Phase 2 until all of the following are true:

1. **Phase 1 is closed.** `papers/build_prompt_phases/PHASE_1_scope.md` produced `outline.md` and `claims.md`; the PI has signed the contribution list; every claim has an evidence pointer and a risk/mitigation line. Phase 2 computes numbers **only** for claims that already exist in `claims.md` — do not invent statistics for claims the paper will not make.
2. **Phase 0 audit is closed.** Phase 0 enumerated the data ledger (optimizer × suite × dimension × #runs) and flagged which cells are current vs. missing. The committed reference panel `benchmarks/cec_reference_results/<suite>/<optimizer>/` (flat layout) carries the **full 7-optimizer panel** for cec2017, cec2011, and cec2013, and `results/_run_all/` holds local reproductions of all seven on the same three suites — expect zero missing panel cells. Any cell the ledger still flags must be a ticket with an owner before 2.1 runs.
3. **Reference tables are intact.** `benchmarks/cec_reference_results/{cec2011,cec2013,cec2013lsgo,cec2017,cec2020}/` are READ-ONLY and SHA-256 auditable. Confirm they are unmodified (`git status` clean under that tree) before any comparison.
4. **FP-regime sentinel is known.** The canonical CEC2017 floating-point regime sentinel is recorded in each run's `summary/environment.json` under `fp_regime.sentinel`; the committed prefix is `8bda40d8…` (full value `8bda40d80d1671fe6571a56195b1d0679208c20f8cb2ae14c24b56f469c15bdb`). Every regenerated cell must carry this sentinel.
5. **Commit is pinned.** Note the commit SHA you are computing against (`git rev-parse HEAD`); Phase 3/4 cite a commit SHA per headline number, so the numbers in this phase must be traceable to one revision.

**Quick prerequisite check** (all must pass before proceeding):
```
git rev-parse HEAD                                   # record the SHA
git status --porcelain benchmarks/cec_reference_results   # MUST be empty (reference intact)
gsk-list --suite CEC2017                             # confirm the ledger / which cells exist
```
Only the closed-set statistics citations may be used downstream — do not introduce any test whose citation is outside: `friedman1937use`, `demsar2006statistical` (Friedman/Nemenyi); `wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling` (pairwise + corrections); `vargha2000critique` (A12); `efron1993introduction` (BCa). The full 57-key bibliography is Appendix A of `papers/PAPER_BUILD_PROMPT.md`.

---

## Inputs

### Data ledger (from Phase 0)
- **The 7-algorithm panel** (fixed order for every table/figure): `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`, `dt-gsk`. Canonical in `src/gsk_family/analysis/project_policy.py` as `RUNNABLE_OPTIMIZERS`; the proposed method is `PROPOSED_OPTIMIZER = "dt-gsk"`, the baseline is `BASELINE_OPTIMIZER = "gsk"`. Reference-only comparators live in `REFERENCE_COMPARATORS = (gsk, agsk, apgsk, fdb-agsk, egsk, atmals-gsk)`. Algorithm-id normalization (hyphen/case aliases) is handled by `project_policy.normalize_algorithm_id`; use the canonical hyphenated ids above in every command and CSV.
- **Run counts (conventions — do not deviate):**

  | Suite      | Runs | Excluded | Dimensions            |
  |------------|------|----------|-----------------------|
  | CEC2017    | 51   | F2       | 10, 30, 50, 100       |
  | CEC2011    | 25   | —        | native (real-world)   |
  | CEC2013    | 51   | —        | 10, 30, 50            |
  | CEC2013LSGO| per config | —   | large-scale (native)  |
  | CEC2020    | per config | —   | per config            |

  The main-text panel is CEC2017 across `D ∈ {10, 30, 50, 100}`; CEC2013 (28 functions) is a **second comparison suite** and CEC2011 the real-world suite; cec2013lsgo/cec2020 are partial context suites, supplementary unless `claims.md` promotes them.
- **Seed policy:** `src/gsk_family/runners/seed_policy.py :: get_cec_seed(base_seed, dim, func, run)`; the campaign uses `base_seed = 20240620`, effective seed `get_cec_seed(20240620, dim, func, run) % 2147483646 + 1`. Regeneration must reproduce `summary/seed_schedule.csv` byte-for-byte — that file is the audit trail proving the seed policy was honored.

### Configs
`configs/*.yml`:
- `configs/all_cec2017.yml` — full CEC2017 family campaign.
- `configs/all_cec2011.yml` — CEC2011.
- `configs/agsk_cec2020.yml` — CEC2020 (AGSK).
- `configs/smoke.yml`, `configs/all_optimizers_smoke.yml`, `configs/golden_validation_smoke.yml`, `configs/performance_campaign_smoke.yml` — smoke/CI sizing (use for dry runs, **never** for paper numbers).
- `configs/experimental/{ism_diag.yml, ism_diag_15run.yml, ism_d10_scored.yml}` — ISM diagnostic sweeps (exploratory only).
- `configs/_ablation/<cell>.yml` — the scaffold-ablation cell configs, written by `scripts/run_ablation.py` (6 mechanisms + baseline = 7 cells).
- `configs/publish/dt_gsk_cec2017_final.yml` — the frozen publication config for the proposed method.

### Results tree
- `results/_run_all/<optimizer>/<suite>/` with subdirs `summary/`, `curves/`, `gen_logs/`.
- Per-cell `summary/` holds: `<optimizer>_<suite>_D<dim>.csv` (header `Function,Best,Median,Mean,Worst,SD`), `per_run.csv`, `seed_schedule.csv`, `run_config.json`, `phase0_protocol.json`, `environment.json` (FP sentinel), `verification.json`, and per-dimension text logs.
- `curves/` holds convergence CSVs (`Figure_F<k>_D<dim>_Run#<n>.csv`) consumed by `scripts/plot_convergence_from_curves.py`.
- `results/_analysis/` = aggregated stats/figure inputs (already contains `publication_polish/`). The `gsk-stats` default output root is `results/_run_all/_analysis/<suite>/`.

### Benchmarks (read-only)
- `benchmarks/cec_suite_python/{cec2011,cec2013,cec2013lsgo,cec2017,cec2020}/` — function implementations.
- `benchmarks/cec_reference_results/{same}/` — the committed reference panel (flat per-optimizer layout: `<opt>_<suite>_D<dim>.csv` + `per_run.csv` + `curves/` + `gen_logs/` + provenance JSONs; full 7-panel on cec2017/cec2011/cec2013). This is what the family report loads **first** for every optimizer, the proposed method included. **Never edit.**

### Analysis layer (`src/gsk_family/analysis/`)
- `statistics.py` — `wilcoxon_paired`, `holm_correction`, `benjamini_hochberg`, `friedman_rank`, `vargha_delaney`, `bootstrap_bca_ci`.
- `statistical_tests.py` — `wilcoxon_signed_rank`, `friedman_rank_test` (higher-level wrappers).
- `family_report.py` — `analyze_family`, `write_report`, `generate_family_report` (the orchestrator behind `gsk-stats`).
- `result_loader.py` — loads committed summaries into the panel structure; `load_algorithm` resolves each cell **reference-first** from `benchmarks/cec_reference_results/`, falling back to `results/_run_all/` only where the reference tree lacks the cell.
- `project_policy.py` — `RUNNABLE_OPTIMIZERS`, `REFERENCE_COMPARATORS`, `normalize_algorithm_id`.
- `figures.py` — `nemenyi_critical_difference` (CD value + rank-chart inputs).
- `latex_tables.py` — `friedman_ranks_latex`, `wilcoxon_summary_latex`.

---

## Tasks

**Order of operations.** Run the tasks in sequence — each consumes the previous one's committed output:
1. **2.1** — audit the committed 7-algorithm panel (and close any residual ticketed gap).
2. **2.2** — recompute the statistical panel from those committed summaries.
3. **2.3** — recompute the ablation deltas from the committed sweeps.
4. **2.4** — bind every table to one CSV, checksum the bundle, prove one-command reproducibility.
5. **2.5** — pin the convergence-curve inputs Phase 3 will plot.

Do not compute a statistic (2.2+) against a cell that is not yet committed and `gsk-validate`-green (2.1). Do not draft any table/figure here — that is Phase 3.

### 2.1 Audit the committed panel (regenerate only residual gaps)

The full 7-optimizer panel is already committed under `benchmarks/cec_reference_results/` for cec2017, cec2011, and cec2013, with `results/_run_all/` reproductions alongside — the expected regeneration set is **empty**. Audit the committed cells first; regenerate **only** a cell your Phase 0 ledger actually ticketed as missing or failing verification. Never re-run cells that are already committed and verified unless their `verification.json` fails the checks in 2.4.

**Micro-steps**

1. **Confirm what exists.** List the ledger and inspect a present cell's summary:
   - PowerShell: `gsk-list --suite CEC2017`
   - Bash: `gsk-list --suite CEC2017`
   - Then `git status results/_run_all` to see whether any optimizer tree is absent.

2. **Audit first, regenerate last.** The committed reference panel already carries every panel cell; a `_run_all` tree missing on this machine is not a paper gap while the reference cell exists. Prefer locating and committing existing bytes over recomputing; only regenerate when no committed/locatable artifact exists. For `dt-gsk`, the ISM core is byte-identity-locked — a regeneration must reproduce the committed numbers exactly; a diff (step 5) is the proof.

3. **Regenerate a cell with the frozen config.** Prefer the committed publication config so budget, seed policy, and FP regime are pinned by file rather than by flags:

   - Proposed method (`dt-gsk`), full CEC2017 panel dimension set, publication config:
     ```
     gsk-run --config configs/publish/dt_gsk_cec2017_final.yml --overwrite
     ```
   - A single missing comparator cell via the family config, scoping optimizer and dimension explicitly (respects the 51-run CEC2017 convention encoded in the config; do **not** pass `--runs` to override it):
     ```
     gsk-run --config configs/all_cec2017.yml --optimizer atmals-gsk --dimension 30
     ```
   - Whole-suite driver (equivalent orchestration, useful when regenerating several optimizers at once): `python scripts/run_all_cec2017.py` (siblings: `scripts/run_all_cec2011.py`, `scripts/run_all_cec2013.py`, `scripts/run_all_cec2013lsgo.py`, `scripts/run_all_cec2020.py`; `scripts/run_gsk_family.py` runs the family panel).

   Notes on flags: `--suite` selects the benchmark; `--dimension`/`--dimensions` accepts repeats, comma lists, `START:STOP`, or `native/default/all`; `--function`/`--functions` similarly (CEC2017 excludes F2 by config, not by flag); `--seed`/`--seed-policy`/`--rand-generator` should be left at config defaults; `--max-evaluations` is fixed by the config's budget (do not shorten it for the paper); `--parallel`/`--serial`/`--parallel-backend`/`--workers`/`--numba-threads` change speed only, not results (the `process` backend uses true multi-core workers); `--output-root` defaults to `results/_run_all`, `--reference-root` to `benchmarks/cec_reference_results`, `--data-root` to the suite's input tables. **Doubled-suite trap:** the runner writes `<output_root>/<optimizer>/<suite>/`, so point `--output-root` (or `output_root:` in the YAML) at the tree that *contains* the suite folders, never at a suite folder itself — otherwise you create a nested `<suite>/<opt>/<suite>/…` tree. `--generation-logs`/`--convergence-graphs` control the extra per-checkpoint and PNG artifacts. Use `--overwrite` only on a cell you intend to replace.

   **Per-optimizer regeneration notes.**
   - `egsk` is a runnable port (scipy-SLSQP substitutes MATLAB `fmincon`); it is runnable **and** a reference comparator. If the paper's `egsk` panel column uses the `fmincon` reference CSVs rather than the port, take those from `benchmarks/cec_reference_results/cec2017/` and do not overwrite them with port output — label which source each `egsk` number came from. Cross-check the port against the reference with `python scripts/validate_egsk_vs_reference.py`.
   - `atmals-gsk` is runnable; regenerate exactly like any comparator cell via `configs/all_cec2017.yml`.
   - `dt-gsk` core is byte-identity-locked. Regenerate from `configs/publish/dt_gsk_cec2017_final.yml`; if a frozen ISM profile is in play, `python scripts/validate_profile_lock.py` guards against accidental drift in the locked profile. Do **not** enable any opt-in tuning profile for the headline panel unless `claims.md` says so.

   **Per-suite driver matrix** (whole-suite regeneration; each respects its config's run count):
   | Suite       | Driver                                  | Family config             |
   |-------------|-----------------------------------------|---------------------------|
   | CEC2017     | `python scripts/run_all_cec2017.py`     | `configs/all_cec2017.yml` |
   | CEC2011     | `python scripts/run_all_cec2011.py`     | `configs/all_cec2011.yml` |
   | CEC2013     | `python scripts/run_all_cec2013.py`     | (per config)              |
   | CEC2013LSGO | `python scripts/run_all_cec2013lsgo.py` | (per config)              |
   | CEC2020     | `python scripts/run_all_cec2020.py`     | `configs/agsk_cec2020.yml`|
   `python scripts/run_gsk_family.py` runs the family panel across a suite in one call.

4. **Confirm where outputs landed.** A regenerated `dt-gsk` CEC2017 cell must appear under:
   `results/_run_all/dt-gsk/cec2017/summary/dt-gsk_cec2017_D<dim>.csv`
   plus `per_run.csv`, `seed_schedule.csv`, `run_config.json`, `environment.json`, `verification.json` in the same `summary/`, and convergence CSVs under `results/_run_all/dt-gsk/cec2017/curves/`. Confirm the FP sentinel:
   - Bash: `python -c "import json;print(json.load(open('results/_run_all/dt-gsk/cec2017/summary/environment.json'))['fp_regime']['sentinel'][:8])"`
   - Expected output: `8bda40d8`

5. **Confirm determinism (re-run one cell, diff).** Re-run a single small cell to a throwaway root and diff the summary CSV against the committed one — they must be byte-identical:
   - PowerShell:
     ```
     gsk-run --config configs/all_cec2017.yml --optimizer dt-gsk --dimension 10 --output-root results/_determinism_check --overwrite
     Compare-Object (Get-Content results/_run_all/dt-gsk/cec2017/summary/dt-gsk_cec2017_D10.csv) (Get-Content results/_determinism_check/dt-gsk/cec2017/summary/dt-gsk_cec2017_D10.csv)
     ```
     (No output from `Compare-Object` = identical.)
   - Bash:
     ```
     gsk-run --config configs/all_cec2017.yml --optimizer dt-gsk --dimension 10 --output-root results/_determinism_check --overwrite
     diff results/_run_all/dt-gsk/cec2017/summary/dt-gsk_cec2017_D10.csv results/_determinism_check/dt-gsk/cec2017/summary/dt-gsk_cec2017_D10.csv && echo DETERMINISTIC
     ```
   Delete `results/_determinism_check/` after confirming; do not commit it.

6. **Validate cell integrity.** Each cell carries a `summary/verification.json`; run the validator to confirm the cell is internally consistent (run count, seed schedule, budget, FP regime) before trusting it:
   ```
   gsk-validate --suite CEC2017 --proposed dt-gsk
   ```
   A non-zero exit means the cell fails a check — fix the cell (usually re-run under the canonical FP regime), do not paper over it. Also confirm the summary has the expected columns:
   - Bash: `head -1 results/_run_all/dt-gsk/cec2017/summary/dt-gsk_cec2017_D30.csv`
   - Expected: `Function,Best,Median,Mean,Worst,SD`

7. **Commit the regenerated cells** under `results/_run_all/<optimizer>/<suite>/`. Record in the ledger: optimizer, suite, dim, #runs, seed base, FP sentinel prefix, and commit SHA.

**Expected output of 2.1:** every ticketed cell present under `results/_run_all/`, each with `verification.json` green and `environment.json.fp_regime.sentinel == 8bda40d8…`; determinism diff empty; ledger updated.

---

### 2.2 Recompute the statistical panel from committed summaries

Compute the whole statistical panel from the **committed** summaries (never from in-memory run objects, never from stale copies). The one-command path is `gsk-stats`; the analysis functions are named below for the cases where a paper number needs to be produced or audited directly.

**2.2.0 Run the orchestrator.** `gsk-stats` calls `family_report.generate_family_report`, which loads committed summaries via `result_loader.py` (**reference-first**: each cell resolves from `benchmarks/cec_reference_results/` before any `results/_run_all/` fallback), ranks the panel, runs the tests, and writes the bundle:
```
gsk-stats --suite CEC2017 --proposed dt-gsk --dims 10,30,50,100
```
Defaults: `--results-root results/_run_all`, `--reference-root benchmarks/cec_reference_results`, `--out results/_run_all/_analysis/cec2017`, `--alpha 0.05`. To place the bundle where Phase 3 expects it, pass `--out results/_analysis/cec2017`. Repeat per suite (`--suite CEC2011` — native dims, omit `--dims`; `--suite CEC2013 --dims 10,30,50`), matching that suite's run count.

**Expected files written** (into `--out`, `<suite>` lower-cased):
- `cec2017_statistical_report.txt` — human-readable full report.
- `cec2017_friedman_ranks.csv` — Friedman mean-rank CSV (the CD-diagram / rank-chart input).
- `cec2017_friedman_ranks.tex` — LaTeX fragment (via `latex_tables.friedman_ranks_latex`).
- `cec2017_wilcoxon_summary.tex` — LaTeX fragment (via `latex_tables.wilcoxon_summary_latex`).
- `figures/` — Nemenyi CD diagram + rank charts (unless `--no-figures`).

`gsk-stats` prints, per dimension: `D<dim>: N=<n_funcs> Friedman p=<p> best=<alg> (<rank>)`. Capture stdout to the ledger. If it prints `no reproduced '<proposed>' summaries found …` the proposed cell is missing — return to 2.1. If it prints `reference directory not found` the `--reference-root` is wrong — do not proceed.

**Per-suite invocation** (match each suite's run count and dimensions):
```
gsk-stats --suite CEC2017 --proposed dt-gsk --dims 10,30,50,100 --out results/_analysis/cec2017
gsk-stats --suite CEC2011 --proposed dt-gsk                    --out results/_analysis/cec2011
gsk-stats --suite CEC2013 --proposed dt-gsk --dims 10,30,50     --out results/_analysis/cec2013
```
Omit `--dims` to let the suite's standard dimension set apply. Add `--no-figures` when you only want the CSV/TeX (figures are Phase 3's job, but the default render is a cheap sanity check).

**2.2.1 Friedman ranks per dimension across the 7-algorithm panel.** `statistics.friedman_rank(data)` where `data = {alg: [per-function metric, one per function]}`, all lists equal length. It returns a `FriedmanSummary` with χ², p-value, and average ranks (chi-squared approximation `χ² = (12N / (k(k+1))) · Σ(R̄_j − (k+1)/2)²`). The orchestrator already builds `data` per dimension from the committed summaries; the emitted `cec2017_friedman_ranks.csv` is the authoritative rank table. Citations: `friedman1937use`, `demsar2006statistical`.

**2.2.2 Nemenyi critical difference + CD inputs.** `figures.nemenyi_critical_difference(k, n_funcs, q_alpha=None)` returns the CD value for `k` algorithms over `n_funcs` problems at the studentized-range critical value. The rank CSV from 2.2.1 supplies the per-algorithm mean ranks; CD + ranks together are the CD-diagram inputs Phase 3 plots. Citation: `demsar2006statistical`.

**2.2.3 Pairwise Wilcoxon signed-rank vs. each baseline, corrected.** For the proposed method against each of the other six panel members, use per-function paired errors:
- `statistics.wilcoxon_paired(x, y, *, alternative="two-sided")` → `PairedWilcoxonResult` (pure-NumPy normal approximation with continuity correction; equivalent to scipy for n ≥ 10). Higher-level wrapper: `statistical_tests.wilcoxon_signed_rank`.
- Collect the raw p-values and labels, then **Holm-correct**: `statistics.holm_correction(p_values, labels, *, alpha=0.05, statistics=None)` → `HolmResult`. Holm is the default family-wise correction for the win/tie/loss significance marks. Do the six comparisons (`dt-gsk` vs each of `gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk`) as **one** family per dimension.
- Where the **text uses FDR framing**, additionally compute `statistics.benjamini_hochberg(...)`. Report BH only where the prose explicitly claims FDR control — do not mix Holm-adjusted and BH-adjusted p-values in the same claim.
- **Expected output:** one CSV per dimension `stats/wilcoxon_D<dim>.csv` with columns `comparison,raw_p,holm_p,holm_reject,a12,magnitude` (A12 filled in 2.2.4). The `gsk-stats` bundle also emits `cec2017_wilcoxon_summary.tex` via `latex_tables.wilcoxon_summary_latex` for the win/tie/loss row.

Citations: `wilcoxon1945individual`, `holm1979simple`, `benjamini1995controlling`. Reference-table comparisons (against committed comparator numbers rather than reproduced runs) can be produced with `python scripts/wilcoxon_reference.py`.

**2.2.4 Vargha–Delaney A12 effect sizes.** For every pairwise significance claim, attach an effect size: `statistics.vargha_delaney(x, y)` → `EffectSizeResult` (A12 statistic, magnitude ∈ {negligible, small, medium, large}, `n1`, `n2`), where `x`/`y` are per-run error values for the two algorithms on the same function (drawn from each cell's `summary/per_run.csv`). A12 > 0.5 means `x` stochastically dominates (is better than) `y`. Fill the `a12`/`magnitude` columns of `stats/wilcoxon_D<dim>.csv`. Citation: `vargha2000critique`.

**2.2.5 BCa bootstrap CIs for headline gaps.** For each headline gap the abstract/intro states (e.g. mean-rank gap of `dt-gsk` vs. the runner-up at a given D), compute a bias-corrected-and-accelerated CI: `statistics.bootstrap_bca_ci(rank_samples, *, n_boot=10000, alpha=0.05, rng, statistic=None)` → `(lo, hi, point)`. **`rng` is required** — pass a seeded `np.random.default_rng(<fixed seed>)` (the function raises `ValueError` on `rng=None` to prevent non-reproducible intervals); use the campaign base seed `20240620` so the interval is reproducible. `statistic` defaults to `np.mean`; the sample must contain ≥ 2 distinct values (a fully degenerate sample falls back to a point interval). **Expected output:** `stats/headline_bca.csv` with columns `gap_id,dimension,point,ci_lo,ci_hi,n_boot,alpha,seed`. Citation: `efron1993introduction`.

**2.2.6 Assemble the per-dimension summary metrics.** The per-dimension summary table needs the central-tendency numbers alongside the ranks. Read them straight from the committed panel summaries `benchmarks/cec_reference_results/cec2017/<opt>/<opt>_cec2017_D<dim>.csv` (columns `Function,Best,Median,Mean,Worst,SD`; fall back to `results/_run_all/<opt>/cec2017/summary/` only for a cell the reference tree lacks). Choose the reporting statistic once, in `claims.md`, and hold it for every table:
- mean ± SD (from `Mean`, `SD`), or
- median / IQR (from `Median`; IQR from `per_run.csv` if the paper uses it).
Compute the **win/tie/loss** count of `dt-gsk` vs. each comparator from the per-function paired outcome (the same `x`/`y` used in 2.2.3), and attach the Friedman rank row from 2.2.1. Emit `stats/summary_D<dim>.csv` with one row per algorithm: `algorithm,mean,sd,friedman_rank,wins,ties,losses_vs_baseline`. This is the source-of-truth CSV for the main per-dimension table.

**Expected output of 2.2:** the `gsk-stats` bundle per suite (`*_friedman_ranks.csv`, `*_friedman_ranks.tex`, `*_wilcoxon_summary.tex`, `*_statistical_report.txt`, `figures/`), plus `stats/summary_D<dim>.csv`, `stats/wilcoxon_D<dim>.csv` (with A12), and `stats/headline_bca.csv` (produced by the snippets in Worked Examples), all under the chosen `--out` (recommended `results/_analysis/cec2017/`).

---

### 2.3 Recompute ablation deltas (each mechanism on/off)

The paper's ablation reports the effect of turning each ISM mechanism on/off. Recompute the deltas from the committed sweep results — do not eyeball or hand-transcribe.

**Micro-steps**

1. **Locate the sweep configs and results.** The scaffold ablation is driven by `scripts/run_ablation.py`: **6 mechanisms + baseline = 7 cells** (`ace_enabled` ACE knowledge control, `psr_enabled` NLPSR population reduction, `bse_enabled` BSE stagnation escape, `linkage_blockwise_enabled` linkage-aware crossover, `local_search_enabled` Nelder–Mead endgame, `arch_enabled` elite archive; `argp`/`finalpolish`/`deepstall` are commented-out extras), with SGSM (`interaction_graph_enabled`) **off in every cell**. It writes one config per cell under `configs/_ablation/<cell>.yml` and runs each to `results/_ablation/<cell>/dt-gsk/<suite>/`. Flags: `--suite {cec2017,cec2011,cec2013}` (cec2011 → native dims), `--mode {remove-one,add-one}`, `--dimension` comma-list, `--runs` (default **25** — the paper's stated ablation design), `--workers`, `--only`, `--dry-run`. If a sweep cell is missing, regenerate it:
   ```
   python scripts/run_ablation.py --suite cec2017 --dimension 30 --only no_ace
   ```
   (The diagnostic configs `configs/experimental/{ism_diag.yml, ism_diag_15run.yml, ism_d10_scored.yml}` remain for exploratory checks only; label any number from them as diagnostic, never as a paper result.)

2. **Compute the deltas.** `python papers/scripts/generate_ablation_matrix.py --suite <suite> [--dimension <D>] [--full-cell baseline]` is the computation of record: it aggregates the cells into `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv` (mean Friedman rank per cell, delta vs the full cell, best-case counts, full-vs-cell Wilcoxon + Holm), reusing `analysis/statistics.py`. For any bespoke delta, reuse `friedman_rank` for rank deltas and `wilcoxon_paired` + `vargha_delaney` for per-mechanism significance and effect size, exactly as in 2.2.

3. **Tabulate.** The matrix CSV already carries one row per cell (mechanism disabled) with mean rank, delta vs full, best-case count, and the Holm-corrected verdict; `gen_ablation_table()` in `papers/scripts/generate_latex_tables.py` renders one `papers/tables/ablation_<tag>.tex` fragment per matrix. The matrix CSV is the source-of-truth for the ablation table (see 2.4).

4. **Handle each dimension separately.** ISM subsystems are gated by dimension (mid/high-D behaviour differs from low-D), so a mechanism's delta at D10 can flip sign at D100. Report deltas per dimension; never average a mechanism's effect across dimensions into one number that hides a sign change.

**Expected output of 2.3:** the matrix CSV(s) `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv` (one row per cell: mean Friedman rank, delta vs full, best-case counts, full-vs-cell Wilcoxon + Holm), every number traceable to a committed cell under `results/_ablation/<cell>/dt-gsk/<suite>/` and a `generate_ablation_matrix.py` invocation captured in the ledger.

### 2.4 Cross-verify: table number == script number == prose number

Every number that will appear in a table or in prose must equal the number a script emits from committed data. Bind each table to exactly one source-of-truth CSV.

**Micro-steps**

1. **One source-of-truth CSV per table.** For each planned exhibit in `claims.md`/`outline.md`, designate a single CSV:
   - Per-dimension summary table → `cec2017_friedman_ranks.csv` (+ the per-dimension mean/SD from `benchmarks/cec_reference_results/cec2017/<opt>/<opt>_cec2017_D<dim>.csv`, reference-first).
   - Pairwise Wilcoxon table → the p-value/A12 CSV from 2.2.3–2.2.4.
   - Headline-gap CIs → the BCa CSV from 2.2.5.
   - Ablation table → `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv` from 2.3.
   Collect these under a **`stats/` bundle** (recommended `results/_analysis/cec2017/stats/`, created in this phase) and write a `table_to_csv_map.md` (or `.csv`) listing `table id → source CSV → producing command`.

2. **Checksum/compare procedure.** Freeze the bundle with hashes so Phase 3/4 can prove nothing drifted:
   - Bash: `find results/_analysis/cec2017/stats -name '*.csv' -print0 | xargs -0 sha256sum > results/_analysis/cec2017/stats/CHECKSUMS.sha256`
   - PowerShell: `Get-ChildItem results/_analysis/cec2017/stats -Filter *.csv | Get-FileHash -Algorithm SHA256 | Format-List > results/_analysis/cec2017/stats/CHECKSUMS.txt`
   To re-verify later: recompute hashes and compare (`sha256sum -c CHECKSUMS.sha256`). Any mismatch = a number changed and every downstream exhibit citing it must be re-checked.

3. **Re-run-and-diff gate.** Re-running `gsk-stats` (2.2.0) into a scratch `--out` and diffing the resulting CSVs against the committed bundle must produce **no differences**. This is the "one command reproduces every statistic" check:
   - Bash:
     ```
     gsk-stats --suite CEC2017 --proposed dt-gsk --dims 10,30,50,100 --out results/_stats_recheck --no-figures
     diff -r results/_analysis/cec2017 results/_stats_recheck && echo REPRODUCIBLE
     rm -rf results/_stats_recheck
     ```
   - PowerShell:
     ```
     gsk-stats --suite CEC2017 --proposed dt-gsk --dims 10,30,50,100 --out results/_stats_recheck --no-figures
     Compare-Object (Get-Content results/_analysis/cec2017/cec2017_friedman_ranks.csv) (Get-Content results/_stats_recheck/cec2017_friedman_ranks.csv)
     Remove-Item -Recurse -Force results/_stats_recheck
     ```

4. **No orphan numbers.** Every number destined for the paper must appear in a bundle CSV; every bundle CSV must be referenced by at least one planned exhibit. Reconcile both directions.

**Expected `stats/` bundle layout** (the single source of truth handed to Phase 3):
```
results/_analysis/cec2017/
├── cec2017_friedman_ranks.csv        # gsk-stats: mean ranks per D (CD-diagram input)
├── cec2017_friedman_ranks.tex        # gsk-stats: LaTeX fragment
├── cec2017_wilcoxon_summary.tex      # gsk-stats: win/tie/loss LaTeX fragment
├── cec2017_statistical_report.txt    # gsk-stats: full human-readable report
├── figures/                          # gsk-stats: CD diagram + rank charts (sanity render)
└── stats/
    ├── summary_D10.csv  summary_D30.csv  summary_D50.csv  summary_D100.csv
    ├── wilcoxon_D10.csv wilcoxon_D30.csv wilcoxon_D50.csv wilcoxon_D100.csv
    ├── headline_bca.csv
    ├── (ablation matrix: results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv — bound via the map)
    ├── curve_selection.csv
    ├── table_to_csv_map.md
    └── CHECKSUMS.sha256               # (or CHECKSUMS.txt on PowerShell)
```

**Expected output of 2.4:** the `stats/` bundle above containing all source-of-truth CSVs (the ablation matrix stays under `results/ablation/` and is bound via the map), `table_to_csv_map.*`, and `CHECKSUMS.*`; a clean re-run diff (step 3); every planned exhibit in `claims.md` bound to exactly one CSV row-set.

---

### 2.5 Consolidate convergence-curve inputs (feeds Phase 3 figures)

Phase 3 plots representative convergence curves, but the **selection and consolidation** of the underlying CSVs is data work that belongs here:
1. Confirm the per-run curve CSVs exist under `benchmarks/cec_reference_results/cec2017/<opt>/curves/` (`Figure_F<k>_D<dim>_Run#<n>.csv`) for every algorithm/function/dimension the figure will show (`results/_run_all/<opt>/cec2017/curves/` is only the fallback tree).
2. Do **not** hand-pick the "best-looking" run. Fix the selection rule in `claims.md` (e.g. the median-final-error run per algorithm/function) and record which run number each curve uses, so the choice is reproducible and honest (include at least one hard case, not only wins).
3. Note the exact input paths in `table_to_csv_map.*`; Phase 3 renders from them via the convergence generators (`papers/scripts/generate_full_convergence.py`, `generate_cec2011_convergence.py`, `generate_cec2013_convergence.py` — all read curves/gen_logs from `benchmarks/cec_reference_results/`; `scripts/plot_convergence_from_curves.py` for single-cell renders) and must not smooth or edit plotted values.

**Expected output of 2.5:** a `curve_selection.csv` (`function,dimension,algorithm,run_number,source_csv`) in the stats bundle, pinning every convergence figure's inputs.

---

## Worked examples

### A. Regenerate one missing cell (proposed method, CEC2017 D30)
```
# 51-run CEC2017 convention is encoded in the config; do not override with --runs.
gsk-run --config configs/publish/dt_gsk_cec2017_final.yml --optimizer dt-gsk --dimension 30 --overwrite
# Output lands here:
#   results/_run_all/dt-gsk/cec2017/summary/dt-gsk_cec2017_D30.csv   (Function,Best,Median,Mean,Worst,SD)
#   results/_run_all/dt-gsk/cec2017/summary/{per_run.csv,seed_schedule.csv,run_config.json,environment.json,verification.json}
#   results/_run_all/dt-gsk/cec2017/curves/Figure_F*_D30_Run#*.csv
```

### B. Recompute the statistical panel (one command)
```
gsk-stats --suite CEC2017 --proposed dt-gsk --dims 10,30,50,100 --out results/_analysis/cec2017
# stdout (one line per D), e.g.:
#   D30: N=29  Friedman p=1.2e-08  best=dt-gsk (2.41)
# writes: cec2017_friedman_ranks.csv, cec2017_friedman_ranks.tex,
#         cec2017_wilcoxon_summary.tex, cec2017_statistical_report.txt, figures/
```

### C. Python snippet — A12 and BCa for a headline gap
```python
import numpy as np
from gsk_family.analysis.statistics import (
    vargha_delaney, wilcoxon_paired, holm_correction, bootstrap_bca_ci,
)

# per-run errors for two algorithms on the same function (from per_run.csv)
x = ism_errors        # dt-gsk per-run errors, one function
y = runnerup_errors   # runner-up per-run errors, same function

es = vargha_delaney(list(x), list(y))
print(es.a12, es.magnitude, es.n1, es.n2)   # e.g. 0.78 large 51 51

w = wilcoxon_paired(np.asarray(x), np.asarray(y), alternative="two-sided")
holm = holm_correction([w.p_value], ["dt-gsk vs runner-up"], alpha=0.05)

# BCa CI on a headline mean-rank gap sample (rng is REQUIRED)
rng = np.random.default_rng(20240620)
lo, hi, point = bootstrap_bca_ci(rank_gap_samples, n_boot=10000, alpha=0.05, rng=rng)
print(f"gap = {point:.3f}  95% BCa CI [{lo:.3f}, {hi:.3f}]")
```

### D. Compute pairwise Wilcoxon + Holm across the panel (snippet)
```python
import numpy as np
from gsk_family.analysis.statistics import wilcoxon_paired, holm_correction, vargha_delaney

proposed = "dt-gsk"
comparators = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk"]

pvals, labels, a12s = [], [], []
for c in comparators:
    x = per_function_error[proposed]   # length N_funcs (per-function summary metric)
    y = per_function_error[c]
    r = wilcoxon_paired(np.asarray(x), np.asarray(y), alternative="two-sided")
    pvals.append(r.p_value); labels.append(f"{proposed} vs {c}")
    a12s.append(vargha_delaney(list(x), list(y)).a12)

holm = holm_correction(pvals, labels, alpha=0.05)   # family-wise across the 6 comparisons
# write labels, raw p, holm-adjusted p/reject, a12 -> stats/wilcoxon_D30.csv
```

### E. Friedman ranks for one dimension (snippet)
```python
from gsk_family.analysis.statistics import friedman_rank

# one per-function metric list per algorithm, all equal length (= N functions)
data = {
    "gsk":       gsk_perfunc,        # e.g. mean error per function at D30
    "agsk":      agsk_perfunc,
    "apgsk":     apgsk_perfunc,
    "fdb-agsk":  fdbagsk_perfunc,
    "atmals-gsk":atmals_perfunc,
    "egsk":      egsk_perfunc,
    "dt-gsk":   ism_perfunc,
}
summary = friedman_rank(data)          # FriedmanSummary(chi2, p_value, average ranks)
print(summary.p_value, summary.ranks)  # ranks -> a row of cec2017_friedman_ranks.csv
```

### F. Recompute an ablation delta (concept)
```
# run (or top up) the scaffold-ablation cells: 6 mechanisms + baseline = 7 cells, SGSM off everywhere
python scripts/run_ablation.py --suite cec2017 --dimension 30 --runs 25
#   configs -> configs/_ablation/<cell>.yml ; output -> results/_ablation/<cell>/dt-gsk/cec2017/
# aggregate: mean rank per cell, delta vs baseline, best-case counts, full-vs-cell Wilcoxon+Holm
python papers/scripts/generate_ablation_matrix.py --suite cec2017 --dimension 30
#   -> results/ablation/ablation_matrix_rank_summary_cec2017_D30.csv
# render the LaTeX fragment(s): one papers/tables/ablation_<tag>.tex per matrix
python papers/scripts/generate_latex_tables.py
```

### G. Expected CD-input CSV shape (`cec2017_friedman_ranks.csv`)
A tidy mean-rank table — one row per algorithm (panel order), columns per dimension (lower rank = better). Feed the per-D mean-rank column plus `nemenyi_critical_difference(k=7, n_funcs=N)` to the Phase 3 CD-diagram renderer:
```
algorithm,D10,D30,D50,D100
gsk,4.90,5.12,5.03,4.88
agsk,4.10,4.05,3.98,4.20
apgsk,3.80,3.60,3.55,3.62
fdb-agsk,4.02,3.95,3.90,3.80
atmals-gsk,3.55,3.40,3.42,3.50
egsk,3.20,3.10,3.18,3.22
dt-gsk,2.43,2.41,2.30,2.28
```
(Values illustrative — the committed CSV is authoritative.)

---

## Pitfalls & anti-patterns

- **Editing reference results.** `benchmarks/cec_reference_results/**` is READ-ONLY and SHA-256 auditable. Never write into it, never "fix" a reference number. Comparisons read it; they never mutate it.
- **Mismatched run counts.** CEC2017 and CEC2013 are 51 runs (CEC2017 excludes F2; CEC2013 is 28 functions over D ∈ {10,30,50}); CEC2011 is 25 runs; the scaffold ablation is n = 25 by design. Do not pass `--runs` to override a panel config's count, and never promote a 15-run diagnostic (`configs/experimental/ism_diag_15run.yml`) result into a paper table.
- **Recomputing stats from stale summaries.** Always regenerate the bundle from the currently committed `results/_run_all/**` after any 2.1 change. A rank CSV computed before a cell was regenerated is an orphan — delete and recompute.
- **Forgetting the correction.** Raw pairwise Wilcoxon p-values are not reportable across six comparisons; apply `holm_correction` (family-wise) — and `benjamini_hochberg` **only** where the prose explicitly claims FDR control. Never mix corrected and uncorrected p-values in one claim.
- **Significance without effect size.** Every significance mark needs a Vargha–Delaney A12 alongside it. A significant-but-negligible result must be reported honestly, not as a win.
- **BCa without a seeded rng.** `bootstrap_bca_ci` requires an explicit seeded `rng`; passing `None` raises. Use a fixed seed so the CI is reproducible.
- **FP-regime drift.** Every regenerated cell's `environment.json.fp_regime.sentinel` must start `8bda40d8…` (CEC2017). A different sentinel means the floating-point regime drifted and the numbers are not comparable — discard and rerun under the canonical regime (`src/gsk_family/runners/fp_regime.py :: ensure_canonical_fp_regime`; see `docs/reference/fp_regime.md`).
- **Uncommitted determinism-check trees.** `results/_determinism_check/`, `results/_stats_recheck/`, and any scratch `--out` are throwaway; delete them so they never get mistaken for a panel cell.
- **Mixing `egsk` sources.** The `egsk` port (scipy-SLSQP) and the `fmincon` reference CSVs are two different provenances. Pick one per exhibit, state which, and never silently swap them mid-table.
- **Overriding config budgets or counts on the CLI.** Passing `--runs`, `--max-evaluations`, or `--seed` to "save time" produces numbers that are not the paper's numbers. Regenerate from the frozen config only.
- **Skipping `gsk-validate`.** A cell that was copied, partially written, or produced under a drifted regime can still parse. `gsk-validate` is the gate that catches it before it poisons a statistic.
- **Enabling a tuning profile for the headline panel.** ISM opt-in profiles change results; the headline panel uses the frozen `configs/publish/dt_gsk_cec2017_final.yml`. Use `scripts/validate_profile_lock.py` to confirm the locked profile.

---

## Exit gate

Phase 2 is done when **all** hold (P3 sign-off, per `PAPER_BUILD_PROMPT.md`):

1. **One-command reproducibility.** Every statistic the paper cites is reproducible from committed data by a single command (`gsk-stats …` for the panel; a pinned Python snippet for A12/BCa; `papers/scripts/generate_ablation_matrix.py` for ablation), and a re-run-and-diff against the committed bundle is empty.
2. **No orphan numbers.** Every number destined for a table/prose exists in a bundle CSV, and every bundle CSV is referenced by a planned exhibit — reconciled both directions.
3. **Ablation deltas computed.** `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv` exists, each row traceable to a committed cell under `results/_ablation/` and a `generate_ablation_matrix.py` invocation.
4. **Table→CSV binding map produced.** The `stats/` bundle (recommended `results/_analysis/cec2017/stats/`) contains all source-of-truth CSVs (`summary_D*.csv`, `wilcoxon_D*.csv`, `headline_bca.csv`, `curve_selection.csv`; the ablation matrix under `results/ablation/`), `table_to_csv_map.*`, and `CHECKSUMS.*`.
5. **Convergence inputs pinned.** `curve_selection.csv` fixes each figure's run by a stated rule; no curve is hand-picked.
6. **Provenance pinned.** FP sentinel `8bda40d8…` on every regenerated cell; commit SHA recorded per headline number; run counts match the suite convention.

---

## Hand-off

Deliver to **`papers/build_prompt_phases/PHASE_3_tables_figures.md`**:
- The frozen `stats/` bundle (source-of-truth CSVs + `table_to_csv_map.*` + `CHECKSUMS.*`) under `results/_analysis/<suite>/stats/`.
- The `gsk-stats` LaTeX fragments (`*_friedman_ranks.tex`, `*_wilcoxon_summary.tex`) and the CD-diagram inputs (`*_friedman_ranks.csv` + `nemenyi_critical_difference` values).
- `curve_selection.csv` pinning each convergence figure's run, plus the source curve CSVs under `benchmarks/cec_reference_results/cec2017/<opt>/curves/` (fallback: `results/_run_all/<opt>/cec2017/curves/`).
- The ledger update: per regenerated cell, its FP sentinel prefix, run count, and commit SHA.

**What Phase 3 must NOT do:** compute a new statistic, re-run a cell, average a per-dimension number across dimensions, smooth or hand-edit a plotted value, or introduce a number absent from the bundle. If Phase 3 needs a number the bundle lacks, it is a Phase 2 defect — route it back here, add it to a source-of-truth CSV, re-checksum, and only then continue.

Phase 3 builds tables/figures **only** from these committed CSVs (regenerating figures via the `papers/scripts/generate_*_convergence.py` generators, `scripts/plot_convergence_from_curves.py`, and `figures.py`); it must never hand-edit a plotted or tabulated number. Any number Phase 3 cannot bind to a bundle CSV is an orphan and must be sent back to Phase 2.
