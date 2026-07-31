# Researcher Handbook

> **What this page is.** A start-to-finish playbook for running reproducible
> experiments with this package and reporting them so others can re-run them.
>
> **Who it is for.** Researchers planning a benchmark campaign, a comparison
> across optimizers, or a release that needs an evidence trail.
>
> **What you will get.** A recommended workflow, a campaign-design checklist, the
> rule for picking the right result column, a reporting checklist, and the exact
> evidence commands (with what each one produces).
>
> **Prerequisites.** Install and basic running are covered in the
> [User Guide](../getting-started/user_guide.md) and
> [Tutorial](../getting-started/tutorial.md). For determinism details see
> [Reproducibility](reproducibility.md); for timing see
> [Performance](performance.md). Term definitions live in
> [the glossary](../reference/glossary.md).

## Optimizer and suite roster

Before designing a campaign, know what is runnable. The package ships **seven
runnable optimizers** (one of which, `egsk`, also serves as a committed reference
comparator), and **six benchmark suites**:

| Optimizer id | Role |
|---|---|
| `gsk` | Vanilla Gaining-Sharing Knowledge baseline. |
| `agsk` | Adaptive GSK with `(kf, kr)` pools and LPSR population reduction. |
| `apgsk` | Adaptive-pool GSK with the negative-`KF` gate. |
| `fdb-agsk` | Fitness-distance-balance donor selection on top of AGSK. |
| `atmals-gsk` | Memory-roulette pools with a local-search stage. |
| `dt-gsk` | **This project's proposed method** (Dimension-Tiered Gaining-Sharing Knowledge). |
| `egsk` | Runnable optimizer (MATLAB port; scipy-SLSQP substitutes `fmincon`); also reported in the panel from committed reference CSVs. |

The six suites are `sphere`, `cec2011`, `cec2013`, `cec2013lsgo`, `cec2017`, and
`cec2020`. The headline scored set for the paper is **CEC2017**, which excludes
the withdrawn/unstable F2 (functions F1, F3–F30) across D = 10/30/50/100.
**CEC2011** (22 real-world problems, native per-function dimensions, 25 runs)
and **CEC2013** (the second comparison suite: 28 functions, D = 10/30/50, 51
runs) are full comparison suites — the committed reference panel under
`benchmarks/cec_reference_results/<suite>/<optimizer>/` carries all seven
optimizers for CEC2017, CEC2011, and CEC2013, and it is the paper's single
source of truth (a local run under `results/_run_all/` is only a fallback; see
[Statistical Analysis — Data sources](statistical_analysis.md#data-sources)).
`cec2020` (agsk only) and `cec2013lsgo` (`decc-g`, `mos`) carry partial context
panels. List the live roster at any time with `gsk-list`.

`dt-gsk` is a deliberate **fair-start exception**: it self-initializes its own
`5*D` (`np_init_mult * D`) population from the shared unified `threefry(seed)`
stream rather than consuming the runner's fair-start population. Because it draws
from the identical shared seed and generator, it stays directly comparable to the
rest of the family — see [Reproducibility — Seeds](reproducibility.md#seeds) and
[Seed Policy — DT-GSK Unified-Only Seeding](../reference/seed_policy.md).

## Recommended Workflow

Plan small, confirm it works, then scale up. Each step below either builds
confidence cheaply or produces an artifact you will archive.

1. **Install and test the environment.** Confirms the package imports and the
   optimizers run before you spend compute. See
   [Reproducibility — Environment](reproducibility.md#environment).

   ```powershell
   python -m pip install -e ".[dev]"
   python -m pytest -q
   ```

2. **Choose a YAML configuration.** One file defines the whole campaign
   (optimizers, suite, functions, dimensions, runs, seeds, budget). Start from a
   file in `configs/` (see [Configuration](../getting-started/configuration.md)).
   Useful starting points already in the tree:

   | Config | Purpose |
   |---|---|
   | `configs/smoke.yml` | Smallest end-to-end smoke; fastest pipeline check. |
   | `configs/all_optimizers_smoke.yml` | Five GSK-family comparators (`gsk`, `agsk`, `apgsk`, `atmals-gsk`, `fdb-agsk`), reduced budget. |
   | `configs/all_optimizers_cec2017_reduced.yml` | CEC2017 panel at a reduced budget. |
   | `configs/all_cec2017.yml` | Full CEC2017 campaign. |
   | `configs/all_cec2011.yml` | Full CEC2011 (native per-function dimensions). |
   | `configs/golden_validation_smoke.yml` | Golden/validation smoke check. |
   | `configs/performance_campaign_smoke.yml` | Timing/profiling smoke. |

3. **Run a reduced-budget smoke campaign.** A short run with a small
   `max_evaluations` that exercises the full pipeline without waiting for a real
   campaign. Use it to catch config mistakes early.

   ```powershell
   gsk-run --config configs/all_optimizers_smoke.yml --root .
   ```

4. **Inspect per-run and summary outputs.** Open `per_run.csv` and the summary
   CSVs under `results/_run_all/<optimizer>/<suite>/summary/` and check the
   numbers are sane (see [Result Schema](../reference/result_schema.md)). Sanity
   checks worth doing: no `NaN` in the `error` column for a known-optimum suite,
   `termination` is `target_error_reached` or `max_evaluations`, and `nfes`
   never exceeds the configured budget.
5. **Run the full intended campaign.** The real budget, the real run count.
6. **Validate against imported reference tables where available** with
   `gsk-validate --compare` (see [Evidence Commands](#evidence-commands)).
7. **Archive** the config, environment, summaries, traces, and verification
   output (see [Reporting](#reporting) below).

To confirm parallel and serial runs agree, run the same campaign once normally
and once with `--serial` and byte-compare the deterministic artifacts (see
[Reproducibility](reproducibility.md) and
[Numerical Examples — Parallel determinism](numerical_examples.md#parallel-determinism)).

## Campaign Design

One YAML file per campaign is the experiment record. Treat it as the primary
provenance artifact — not your shell history.

Record these fields in the YAML so the run is fully specified:

| Field | Why it matters |
|---|---|
| optimizer ids | Which methods ran; pick from the runnable roster above. |
| suite | One of the six suites; sets functions and bounds. |
| functions | Which function ids; CEC2017 scoring omits F2. |
| dimensions | Problem sizes (CEC2017 paper set: 10/30/50/100). |
| runs | Independent repetitions per cell (CEC convention: 51). |
| seed and seed policy | `base_seed` + `seed_policy` fix every random draw. |
| random generator label | `threefry` (default) for the unified family stream. |
| evaluation budget | `max_evaluations` / `max_nfes` caps the search. |
| optimizer options | Per-optimizer overrides (e.g. local search toggles). |

Do not rely on shell history as the only experiment record. The YAML plus the
`environment.json` written next to the results (see
[Reproducibility](reproducibility.md#environment)) together capture what ran. A
single `(optimizer, suite, function, dimension, run)` tuple is one **cell**; the
campaign is the full cross-product of those axes, and every cell gets one
deterministically scheduled seed.

## Fair Comparisons

To compare optimizers head-to-head, give them the same starting conditions.

Set these in the campaign YAML:

```yaml
seed_policy: unified
rand_generator: threefry
```

With the [unified seed policy](../reference/glossary.md), the runner provides a
matching [fair-start](../reference/glossary.md) population for the same
`(dimension, function, run)` cell, so every optimizer begins each run from the
same population and post-initialization RNG state. Differences in the results
then reflect the optimizers, not the luck of their initial draws. The
[Seed Policy](../reference/seed_policy.md) reference gives the exact formulas;
[Numerical Examples — Unified seed and fair start](numerical_examples.md#unified-seed-and-fair-start)
works the derivation by hand.

The unified seed is computed from the cell coordinates only:

```text
seed = mod(base_seed + 1000003*Dim + 1000033*Function + 1000037*Run,
           2147483646) + 1
```

Because the optimizer id and suite are **not** inputs, the same `(Dim, Function,
Run)` cell yields the identical seed (and identical fair-start population) for
every optimizer — that independence is exactly what makes the comparison fair.
`dt-gsk` is the one documented exception: it always seeds via this unified
formula but self-inits a `5*D` population from the same `threefry(seed)` stream
instead of reusing the runner's fair-start array (see
[Seed Policy — DT-GSK Unified-Only Seeding](../reference/seed_policy.md)).

## Result Interpretation

Pick the column that matches what the suite knows about its own optimum.

- Use **`error`** when the suite has a known optimum (the reported value is the
  gap to that optimum).
- Use raw **`best_fitness`** when the suite has no finite known optimum.
- Check **`statistics_basis`** in the run metadata when comparing across suites,
  so you are not mixing error-based and fitness-based numbers.

These columns and the metadata fields are defined in the
[Result Schema](../reference/result_schema.md).

## Statistical comparison

A campaign on its own gives raw numbers; the paper needs a defensible
head-to-head verdict. This project ships a paper-grade comparison suite
(`gsk-stats`) that ranks the proposed `dt-gsk` against the GSK-family panel and
emits Friedman ranks, a Nemenyi critical-difference diagram, pairwise Wilcoxon
tests with Holm correction, and effect sizes. All panel data — the proposed
method included — is loaded **reference-first** from
`benchmarks/cec_reference_results/<suite>/<optimizer>/` (the single source of
truth); a local run under `results/_run_all/` is only a fallback for missing
cells. The full methodology, the 7-algorithm panel definition, data sources,
options, and outputs live in
[Statistical Analysis](statistical_analysis.md). The short version:

```powershell
# Produce the family report (figures + CSV + LaTeX)
gsk-stats --suite CEC2017 --dims 10,30,50,100

# The second comparison suite (28 functions, D = 10/30/50)
gsk-stats --suite CEC2013 --dims 10,30,50
```

For an advisor-facing PDF (no LaTeX toolchain required), build the review pack:

```powershell
python papers/scripts/generate_review_pack.py
```

This writes `papers/DT-GSK-CEC2017-review.pdf` with a Friedman/Holm dashboard,
per-function mean tables, and 7-algorithm convergence grids. Missing convergence
curves are logged to `papers/DT-GSK-CEC2017-review_missing.log` and **never
fabricated**.

## Ablation study (DT-GSK)

The scaffold ablation isolates each DT-GSK mechanism by disabling exactly one
per cell. `scripts/run_ablation.py` drives it: six mechanisms
(`ace_enabled` ACE, `psr_enabled` NLPSR, `bse_enabled` BSE,
`linkage_blockwise_enabled` linkage crossover, `local_search_enabled`
Nelder-Mead, `arch_enabled` elite archive) plus a full-scaffold baseline give
seven cells, with SGSM — the ISM interaction-structure memory,
`interaction_graph_enabled` — off in every cell, because that supporting
mechanism is ablated separately on the CEC2013 hold-out design. Key flags:
`--suite {cec2017,cec2011,cec2013}` (cec2011 uses native dimensions),
`--mode {remove-one,add-one}`, `--dimension` (comma list), `--runs` (default
25, the paper's stated ablation design), `--workers`, `--only`, and `--dry-run`.
The driver writes one config per cell under `configs/_ablation/` and each
cell's output to `results/_ablation/<cell>/dt-gsk/<suite>/`.

```powershell
# Inspect the generated configs first, then run at D=30
python scripts/run_ablation.py --dimension 30 --dry-run
python scripts/run_ablation.py --dimension 30 --runs 25 --workers 2

# Aggregate the cells into the rank-summary matrix, then render its LaTeX table
python papers/scripts/generate_ablation_matrix.py --suite cec2017 --dimension 30
python papers/scripts/generate_latex_tables.py
```

`generate_ablation_matrix.py` rolls the cells up into
`results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv` (mean
Friedman rank, delta vs full, best-case counts, full-vs-cell Wilcoxon with
Holm), and `generate_latex_tables.py` renders one `papers/tables/ablation_<tag>.tex`
per matrix. The full stage ordering lives in the root `runbook.md` ("Full Paper
Pipeline" and "DT-GSK Ablation" sections).

## Reporting

A reported result should be re-runnable from the report alone. Include the
following so a reader can reconstruct the run:

- commit or archive identifier;
- Python version (the exact interpreter; the project supports CPython 3.10–3.13);
- dependency versions (`python -m pip freeze`);
- suite and function list;
- dimensions and run count;
- evaluation budget;
- optimizer options;
- seed policy and base seed;
- whether local search was enabled;
- validation status and any known caveats.

The two non-negotiable provenance artifacts are the **campaign YAML** and the
`environment.json` the runner writes under
`results/_run_all/<optimizer>/<suite>/summary/`. Together they pin config,
package versions, platform, and budget. Archive them alongside the summaries,
`per_run.csv`, convergence/`gen_logs`, and any `verification.json`.

## Evidence Commands

The standing evidence for a campaign comes from the runner and the validator
themselves. Compare a generated run tree against the imported reference tables
with:

```powershell
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

This writes `verification.json` beside the run and prints a one-line verdict
with the win/tie/loss tally. Read a reduced-budget comparison as a consistency
and schema check, not a final performance claim (see
[Performance](performance.md) and
[Reproducibility — Bit-Exact Caveats](reproducibility.md#bit-exact-caveats)).

The full evidence trail for one campaign is therefore:

| Command | Produces | Read it as |
|---|---|---|
| `gsk-run --config <yaml> --root .` | summaries, `per_run.csv`, curves, `environment.json` | the raw run record |
| `gsk-validate --compare <run> <ref>` | `verification.json`, win/tie/loss verdict | a schema + consistency check |
| `gsk-stats --suite <SUITE>` | Friedman/Wilcoxon report, CD figures, LaTeX/CSV | the statistical verdict |
| `python papers/scripts/generate_review_pack.py` | `papers/DT-GSK-CEC2017-review.pdf` | the advisor-facing summary |

To confirm parallel and serial runs produce identical artifacts, run the same
config once normally and once with `--serial` and byte-compare the deterministic
numeric artifacts. Keep generated output outside
`benchmarks/cec_reference_results/` so a run never overwrites an imported
read-only reference table.
