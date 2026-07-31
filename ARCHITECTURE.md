# ARCHITECTURE.md -- Structural Map of the GSK-Family Python System

**Purpose.** This document is the authoritative structural map of the
DT-GSK repository: what the system is made of, how the pieces are
layered, which way dependencies point, and how data flows from a command line
through an optimization run into reproducible result tables, statistics, and
papers. It is descriptive (the *shape* of the system) and normative only where
structure is load-bearing for determinism and reproducibility.

**Audience.** Maintainers, contributors, and reviewers who need to locate a
responsibility, understand a coupling, or extend the system without breaking the
optimizer contract, the seed schedule, or the byte-identity lock on the
proposed `dt-gsk` core.

**Scope boundary.** This file covers *structure*. For the *why* behind the
design decisions and *how-to* recipes for extension, see
[DESIGN_GUIDE.md](DESIGN_GUIDE.md). For the rules that constrain changes, see
[PROJECT_RULES.md](PROJECT_RULES.md), [CODING_STANDARD.md](CODING_STANDARD.md),
[BENCHMARK_RULES.md](BENCHMARK_RULES.md), and
[PERFORMANCE_RULES.md](PERFORMANCE_RULES.md). Deeper per-topic reference lives
under [docs/reference/](docs/reference/).

---

## 1. System overview

This is PhD research software for the **GSK optimizer family**. It is three
cooperating subsystems in one pure-Python package (`src/gsk_family/`, CPython
3.10):

1. **An optimizer runtime.** Seven runnable optimizers behind one uniform
   contract: `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`, and the
   project's proposed method `dt-gsk` (Dimension-Tiered Gaining-Sharing Knowledge). `egsk`
   is **both** runnable (`optimizers/egsk.py`, a MATLAB port whose interior-point
   refinement uses `scipy`-SLSQP in place of `fmincon`) **and** a reference
   comparator -- the statistical panel reports `egsk` from the committed
   `scipy`-SLSQP **port** CSVs (the comparator of record), not a MATLAB `fmincon`
   reference.
2. **A CEC benchmark runtime.** A benchmark adapter and runner stack that turns a
   `(suite, function, dimension, run)` cell into a deterministic optimization run
   and writes CEC-style result tables. Six suites are wired:
   `sphere`, `cec2011`, `cec2013`, `cec2013lsgo`, `cec2017`, `cec2020`.
3. **Analysis and paper tooling.** A statistical-analysis layer
   (`analysis/` + the `gsk-stats` console script) and a paper review-pack
   pipeline (`papers/scripts/`) that consume the produced results and committed
   reference evidence.

The single connective tissue is the optimizer contract
`optimize(problem, options) -> OptimizerResult` (Section 4) and the unified seed
schedule (Section 5). Everything else is built so those two stay stable.

The proposed optimizer's numerical core is **vendored and
byte-identity-locked**: `optimizers/_dt_core.py` plus the `_dt_subsystems/`
package were migrated byte-identically from the source DT-GSK v2.1 project and
**MUST NOT** be edited for behavior. See Section 4.2 and
[PROJECT_RULES.md](PROJECT_RULES.md).

---

## 2. Package map

### 2.1 Directory tree

```
DT-GSK/
|-- run.py                          # canonical thin entry point -> cli.run:main
|-- pyproject.toml                  # console scripts, packaging (src layout)
|-- README.md  SKILL.md  runbook.md # landing / agent contract / commands
|-- ARCHITECTURE.md                 # (this file)
|-- src/gsk_family/                 # the package (src layout)
|   |-- types.py                    # OptimizerOptions / OptimizerResult / RunRecord
|   |-- stats.py                    # compute_error, summarize, format helpers
|   |-- cli/                        # console-script entry points
|   |   |-- run.py  list.py  validate.py  stats.py
|   |-- runners/                    # experiment orchestration
|   |   |-- config.py               # ExperimentConfig + load_config
|   |   |-- run_experiment.py       # execution, process pool, --stats hook
|   |   |-- parallel.py  output.py  seed_policy.py
|   |   |-- verification.py  performance.py
|   |   |-- fp_regime.py            # fail-closed SHA-256 floating-point-regime sentinel
|   |-- optimizers/                 # the optimizer family
|   |   |-- gsk.py  agsk.py  apgsk.py  fdb_agsk.py  atmals_gsk.py  egsk.py
|   |   |-- dt_gsk.py              # adapter onto the vendored core
|   |   |-- _dt_core.py            # VENDORED, byte-identity-locked (~4983 lines)
|   |   |-- _dt_subsystems/        # VENDORED subsystem package
|   |   |   |-- bound_constraint.py  budget.py  budget_policy.py
|   |   |   |-- basin_memory.py  interaction_graph.py
|   |   |   |-- gained_shared_junior.py  gained_shared_senior.py
|   |   |   |-- _numba_accel.py  _dt_provenance.py
|   |   |-- _dt_profiles.py        # build_pub_config (dim-aware overlays)
|   |   |-- _dt_rng.py             # 13-substream RNG layer
|   |   |-- _kernels.py  atmals_helpers.py  fdb_scores.py
|   |-- common/                     # shared optimizer building blocks
|   |   |-- rng.py  threefry_rng.py  reference_rng.py
|   |   |-- population.py  bounds.py  donors.py
|   |   |-- reduction.py  numeric_compat.py
|   |-- benchmark_adapter/          # CEC suites behind one problem contract
|   |   |-- factory.py  problem.py  protocol.py
|   |-- analysis/                   # statistics + report builders
|       |-- statistics.py  statistical_tests.py   # VENDORED stats core
|       |-- result_loader.py  project_policy.py
|       |-- family_report.py  figures.py  latex_tables.py
|-- benchmarks/
|   |-- cec_suite_python/           # benchmark function data (default data_root)
|   |-- cec_reference_results/      # READ-ONLY imported reference evidence
|-- results/_run_all/               # reproduced results (write target)
|-- scripts/                        # build/run/validate helpers (build_docs_html.py, run_ablation.py ...)
|-- papers/                         # manuscript + papers/scripts review-pack pipeline
|-- reference_papers/               # bibliography acquisition bundle (bib + index; PDFs gitignored)
|-- configs/                        # YAML experiment configs
|-- docs/                           # themed Markdown + generated docs/html/
|-- tests/                          # unit / smoke / regression gates
```

### 2.2 Module roles

**`cli/`** -- thin argument-parsing front doors; they build/normalize config and
call into `runners`/`analysis`. Console scripts are declared in `pyproject.toml`:

| Script | Entry | Role |
| --- | --- | --- |
| `gsk-run`, `gsk-family-run` | `cli.run:main` | run experiments |
| `gsk-list` | `cli.list:main` | list optimizers/suites |
| `gsk-validate` | `cli.validate:main` | validate config/inputs |
| `gsk-stats` | `cli.stats:main` | build the GSK-family statistical report |

`run.py` (repo root) is the canonical runner and simply delegates to
`cli.run:main`.

**`runners/`** -- the execution engine.
- `config.py`: `ExperimentConfig` (frozen dataclass) + `load_config`; the single
  normalized request object. Defaults matter: `seed_policy="unified"`,
  `rand_generator="threefry"`, `parallel_backend="process"`,
  `data_root="benchmarks/cec_suite_python"`,
  `reference_root="benchmarks/cec_reference_results"`,
  `output_root="results/_run_all"`.
- `run_experiment.py`: orchestrates the run -- expands cells, drives a
  self-healing process pool, calls `optimize` per cell, hands results to the
  output writers, and hosts the opt-in per-dimension `--stats` analysis hook.
- `parallel.py`: worker-count policy (`default_worker_count`).
- `output.py`: result writers + on-disk schema (`output_dirs` -> `summary`,
  `curves`, `curves/graphs`, `gen_logs`); CEC summary CSVs and checkpoint logs.
- `seed_policy.py`: the unified seed (`get_cec_seed`), policy resolution
  (`seed_for_run`), generator resolution (`effective_rand_generator`), and
  `UNIFIED_ONLY_OPTIMIZERS` (which pins `dt-gsk`).
- `verification.py`, `performance.py`: run verification and timing/profiling.
- `fp_regime.py`: the fail-closed SHA-256 floating-point-regime sentinel that
  keeps every campaign in one numba-JIT FP regime (guarding against a silent
  numba fallback under memory pressure splitting the regime mid-campaign). See
  [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md) and
  [docs/reference/fp_regime.md](docs/reference/fp_regime.md).

**`optimizers/`** -- the family plus the vendored core.
- `gsk.py`, `agsk.py`, `apgsk.py`, `fdb_agsk.py`, `atmals_gsk.py`, `egsk.py`:
  native implementations of the comparators, each exposing `optimize(...)`.
  `egsk.py` is a MATLAB port (its interior-point refinement uses `scipy`-SLSQP in
  place of `fmincon`); its statistical-panel cell is sourced from the committed
  `scipy`-SLSQP port CSVs (the comparator of record).
- `dt_gsk.py`: the **adapter** wrapping `_dt_core.ism_gsk_optimize` into the
  uniform contract (Section 4.2).
- `_dt_core.py` + `_dt_subsystems/`: **VENDORED, byte-identity-locked.** The
  subsystems cover bound constraint handling, the evaluation budget controller
  and its policy, basin memory, the interaction graph, the junior/senior
  gained-shared operators, the numba acceleration shims (`_numba_accel.py`), and
  provenance (`_dt_provenance.py`).
- `_dt_profiles.py`: `build_pub_config` -- the dimension-aware "pub" config,
  with the SGSM overlay at `dim >= 50` and TERRA / SP-NLPSR at `dim >= 100`.
- `_dt_rng.py`: the DT-GSK 13-substream RNG layer (Section 5.2).
- `_kernels.py`, `atmals_helpers.py`, `fdb_scores.py`: shared numeric helpers.

**`common/`** -- reusable, optimizer-agnostic building blocks shared by the
*comparator* optimizers (the dt-gsk core does not route its draws through
`rng.RandomContext`):
- `rng.py`: `RandomContext` (single-stream RNG context, fair-start helpers).
- `threefry_rng.py`: counter-based Threefry-4x64-20 generator.
- `reference_rng.py`: reference-compatible Twister / Mcg16807 generators.
- `population.py`, `bounds.py`, `donors.py`, `reduction.py`,
  `numeric_compat.py`: population init, bound repair, donor selection,
  population reduction, and numeric-compatibility shims.

**`benchmark_adapter/`** -- the CEC suites behind one problem contract.
- `problem.py`: `BenchmarkProblem` (frozen dataclass) -- `lb`/`ub`/`dim`/
  `evaluate`/`max_nfes`/`optimum`/`target_error` and validation. Supports
  per-dimension bounds (the `lb`/`ub` arrays carry one entry per variable).
- `factory.py`: `make_problem` -- builds a `BenchmarkProblem` for a suite cell;
  suite data modules are imported lazily so each worker loads only its suite.
- `protocol.py`: per-suite protocol (dimensions, function ids, statistics basis,
  suite normalization).

**`analysis/`** -- downstream consumers of results (Section 8).
- `statistics.py`, `statistical_tests.py`: the **VENDORED stats core**
  (Wilcoxon, Friedman, Holm, BH, Vargha-Delaney A12, Cliff's delta,
  win/tie/loss, BCa bootstrap, `run_statistical_analysis`).
- `result_loader.py`: reference-first loaders (`load_algorithm` tries the
  committed reference panel first, then the locally reproduced run);
  `SUITE_DIMS`.
- `project_policy.py`: `RUNNABLE_OPTIMIZERS` (the seven), `REFERENCE_COMPARATORS`
  (six; `egsk` is in both -- runnable, but reported from reference CSVs),
  id normalization.
- `family_report.py`: `generate_family_report` -- the report orchestrator.
- `figures.py`: Nemenyi critical-difference + rank charts.
- `latex_tables.py`: LaTeX table fragments.

**`benchmarks/`** -- data, not code path: `cec_suite_python/` is the default
benchmark `data_root`; `cec_reference_results/` is **READ-ONLY** imported
evidence (Section 7).

---

## 3. Layering and dependency direction

The system is a layered stack. **Dependencies point downward only**; nothing in
a lower layer imports an upper layer.

```
                +-------------------+      +------------------------+
   user  -->    |  cli/  +  run.py  |      |  papers/scripts/       |
                +---------+---------+      +-----------+------------+
                          |                            | (reads results,
                          v                            |  reference data)
                +-------------------+                  |
                |     runners/      |                  |
                | (config, run,     |                  |
                |  output, seed)    |                  |
                +----+---------+----+                  |
                     |         |                       |
                     v         v                       |
        +------------------+  +---------------------+   |
        |   optimizers/    |  | benchmark_adapter/  |   |
        | (family + ism    |  | (problem/factory/   |   |
        |  adapter + core) |  |  protocol)          |   |
        +--------+---------+  +----------+----------+   |
                 |                       |              |
                 v                       v              |
                +-------------------------+             |
                |        common/          |             |
                | (rng, bounds, donors,   |             |
                |  population, numeric)   |             |
                +-------------------------+             |
                                                        |
   results/_run_all/  <-- written by runners ----+      |
                                                  |      v
                                       +----------+--------------+
                                       |       analysis/         |
                                       | (stats core, loaders,   |
                                       |  family_report, figures)|
                                       +-------------------------+
```

Rules:
- `cli/` depends on `runners/` (and `analysis/` for `gsk-stats`) -- nothing
  depends on `cli/`.
- `runners/` depends on `optimizers/`, `benchmark_adapter/`, `common/`, and
  `types.py`/`stats.py`. It does **not** depend on `analysis/` for execution;
  the only coupling is the opt-in `--stats` hook, which imports
  `run_statistical_analysis` from `analysis/` (Section 8.3).
- `optimizers/` and `benchmark_adapter/` depend on `common/` and `types.py`,
  never on `runners/` or `cli/`.
- `analysis/` and `papers/scripts/` are **downstream consumers**: they read the
  produced `results/_run_all/` tables and the committed reference data; the
  execution path never depends on them.
- The `dt-gsk` core (`_dt_core` + `_dt_subsystems`) intentionally does
  **not** import `common/rng.RandomContext`; it reuses only the low-level
  generators (`common/threefry_rng`, `common/reference_rng`) through its own
  `_dt_rng` layer so toggling it cannot perturb the other optimizers.

The "downward only" rule is what keeps the optimizer contract and seed schedule
auditable. See [PROJECT_RULES.md](PROJECT_RULES.md) for the enforcement gates and
[DESIGN_GUIDE.md](DESIGN_GUIDE.md) for the rationale.

---

## 4. The optimizer contract and the adapter pattern

### 4.1 The uniform contract

Every runnable optimizer exposes:

```python
optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict) -> OptimizerResult
```

- `BenchmarkProblem` (`benchmark_adapter/problem.py`): frozen, validated; carries
  `suite`, `func_id`, `dim`, `lb`, `ub` (per-variable arrays), `optimum`,
  `target_error`, `max_nfes`, `statistics_basis`, and the `evaluate` callable.
- `OptimizerOptions` (`types.py`): `seed`, `rand_generator` (default
  `"twister"`), an optional fair-start `initial_population`, and a free-form
  `values` mapping for optimizer-specific overrides.
- `OptimizerResult` (`types.py`): `best_x`, `best_fitness`, `error`, `nfes`,
  `termination`, a `ConvergenceTrace` (`nfes` + `best_fitness` arrays),
  `runtime_seconds`, and a `params`/`notes` provenance block.

This uniform shape is what lets `runners/` treat all seven optimizers
interchangeably and what lets `output.py` write one schema regardless of
optimizer. Do not widen or reshape these dataclasses casually; see
[CODING_STANDARD.md](CODING_STANDARD.md).

### 4.2 The dt-gsk adapter pattern

`optimizers/dt_gsk.py` is an **adapter**, not a reimplementation. It bridges the
uniform contract to the vendored core (`_dt_core.ism_gsk_optimize` with its
`ISMGSKConfig` / `ISMGSKResult` types):

1. Reads `seed` and `rand_generator` (defaulting to `"threefry"`) from
   `options`.
2. Resolves the search box via `_resolve_bounds`: uniform bounds collapse to a
   scalar `(lo, hi)` (so CEC2017/sphere configs stay byte-identical to the
   source); heterogeneous **per-dimension** bounds (CEC2011) pass through as
   `(lb_array, ub_array)`.
3. Builds the dimension-aware "pub" `ISMGSKConfig` via
   `_dt_profiles.build_pub_config(dim, seed=..., max_nfes=..., bounds=...,
   rand_generator=...)` (SGSM overlay at `dim >= 50`, TERRA/SP-NLPSR at
   `dim >= 100`).
4. Applies optional per-run overrides from `options.values` that name real
   `ISMGSKConfig` fields (run-level fields `dim`/`seed`/`max_nfes`/`bounds`/
   `rand_generator` are reserved).
5. Wraps `problem.evaluate` as a batch `objective(population) -> fitness` and a
   `curve_callback` that records best-so-far convergence points.
6. Runs the core; the core's `BudgetController` is the single evaluation cap, and
   `nfes_used` is reported as `OptimizerResult.nfes`.

**Documented fair-start exception:** dt-gsk seeds its own substream RNG and
draws its own `np_init_mult * dim` initial population, so it **ignores** the
runner's injected `initial_population` while still using the unified seed. The
result records `notes="self-init (fair-start exception)"`. This is intentional --
it preserves the tuned, byte-identical initialization and keeps the run fully
deterministic for a given seed. Do not "fix" this to consume the injected `X0`.

---

## 5. RNG and seed architecture

Reproducibility is structural. Two layers cooperate.

### 5.1 The unified seed schedule

`runners/seed_policy.py` defines the unified CEC seed:

```python
get_cec_seed(base_seed=20_240_620, dim, func, run)
  = (base_seed + 1_000_003*dim + 1_000_033*func + 1_000_037*run) % 2_147_483_646 + 1
```

`seed_for_run(policy, optimizer, suite, base_seed, dim, func, run)` resolves the
per-cell seed. Four policies exist (`reference`, `unified`, `native`,
`derived`), but `dt-gsk` is listed in `UNIFIED_ONLY_OPTIMIZERS` and is therefore
forced onto `get_cec_seed` and the `threefry` generator under **every** policy.
`effective_rand_generator(...)` enforces the same pin for the generator label.

### 5.2 The dt-gsk 13-substream layer

`optimizers/_dt_rng.py` adds named-substream isolation on top of the unified
seed. From one run seed it builds 13 independent substreams, in this fixed,
load-bearing order:

```
init, core, ace, kexp, div, bse, arch, link, de, control, flow, basin, trust
```

- Each substream's child seed is assigned by **position** (`_child_seed`): stream
  0 (`init`) gets the run seed verbatim; the rest get
  `(seed + 1_000_003*(index+1)) % MAX_SAFE_SEED + 1`.
- `SUBSTREAM_NAMES` is **append-only**: the first nine names are prefix-locked by
  an in-module assertion; new substreams may only be appended at the end.
- Substreams wrap the *target's* reference-compatible generators
  (`ThreefryGenerator` from `common.threefry_rng`; Twister/Mcg16807 from
  `common.reference_rng`) via the `ReferenceRNG` NumPy-`Generator`-like wrapper.
  No draws go through `common.rng.RandomContext`, so toggling a subsystem cannot
  disturb another subsystem's draws or any other optimizer.

For the full policy table and reference-stream equivalence, see
[docs/reference/seed_policy.md](docs/reference/seed_policy.md).

---

## 6. Execution flow

A run is a deterministic pipeline from a CLI/config request to result files.

```
gsk-run / python run.py / YAML config
        |
        v
cli.run:main  -- parse args, build ExperimentConfig (runners/config.py)
        |
        v
runners.run_experiment.run_experiment(config)
   |  expand (optimizer x suite x dim x function x run) into cells
   |  resolve per-cell seed (seed_policy.seed_for_run)  ---------+
   |                                                             |
   |  for each cell (on the self-healing process pool):          |
   |     make_problem(suite, func, dim) ---> BenchmarkProblem    |
   |     optimize(problem, OptimizerOptions(seed, ...)) ---------+--> OptimizerResult
   |                                                             |
   |  collect results -> RunArtifact (output.py)                 |
   v                                                             v
output writers (runners/output.py)            optional --stats hook
   |   summary/  : <opt>_<suite>_D<dim>.csv     (run_experiment ->
   |               + CEC2011 rollup <opt>_cec2011.csv   analysis.run_statistical_analysis,
   |   curves/   : median-run Figure_*.csv             per-dim Wilcoxon+Friedman,
   |   curves/graphs/ : optional convergence PNGs      printed live)
   |   gen_logs/ : CheckpointErrors_<opt>_F<k>_D<dim>.csv
   v
results/_run_all/<optimizer>/<suite>/{summary,curves,gen_logs}/
```

Key structural properties:
- **Self-healing process backend.** The default `parallel_backend="process"`
  uses a `ProcessPoolExecutor` with a `spawn` context and a per-process
  initializer (`_init_process_worker`) that pins numba threads. On a
  `BrokenProcessPool` the pool is rebuilt so a dead worker does not abort the
  campaign. It auto-falls back to the in-process backend when process mode is
  disabled.
- **Incremental writes.** Results are written per cell, so an interrupted
  campaign keeps every completed cell.
- **Per-cell determinism.** The seed for a cell is a pure function of
  `(base_seed, dim, func, run)` (and optimizer/policy), independent of worker
  count, worker identity, or execution order.

For thread-pinning and parallelism tuning, see
[PERFORMANCE_RULES.md](PERFORMANCE_RULES.md). For suite protocols, budgets, and
the per-dimension result schema, see [BENCHMARK_RULES.md](BENCHMARK_RULES.md) and
[docs/reference/result_schema.md](docs/reference/result_schema.md).

---

## 7. Reference evidence vs reproduced results

Two result trees with strictly different ownership:

| Tree | Role | Mutability |
| --- | --- | --- |
| `results/_run_all/<opt>/<suite>/` | Locally **reproduced** runs (this machine) | Written by the runner; safe to regenerate |
| `benchmarks/cec_reference_results/<suite>/<alg>/` | **Imported** comparator evidence | **READ-ONLY** -- never overwrite |

- The runner only ever writes under `results/_run_all/` (default `output_root`).
- `cec_reference_results/` is consumed read-only by the analysis layer and the
  paper scripts as the **single source of truth for paper statistics**: full
  7-optimizer panels (the proposed `dt-gsk` included) are committed for
  `cec2017`, `cec2011`, and `cec2013` in a flat `<suite>/<optimizer>/` layout
  (per-dimension summary CSVs, `per_run.csv`, `curves/`, `gen_logs/`, plus
  seed/environment/verification provenance files); `cec2020` (agsk only) and
  `cec2013lsgo` (decc-g, mos) are partial context suites. Analysis loads this
  tree **first** and falls back to `results/_run_all/` only for cells the
  reference tree lacks (Section 8.1). It is the `reference_root` default in
  `ExperimentConfig`.
- **NEVER** point a run's `output_root` at `cec_reference_results/`, and
  **NEVER** fabricate numbers into either tree. See
  [BENCHMARK_RULES.md](BENCHMARK_RULES.md) and
  [PROJECT_RULES.md](PROJECT_RULES.md).

---

## 8. The statistical-analysis pipeline

### 8.1 Inputs and outputs

`gsk-stats` (`cli/stats.py` -> `analysis/family_report.generate_family_report`)
builds the paper-grade GSK-family comparison:

- **All seven algorithms -- the proposed `dt-gsk` included -- load
  reference-first** from the committed panel
  `benchmarks/cec_reference_results/<suite>/<optimizer>/`, the single source of
  truth for paper statistics (`egsk` is reported from its committed reference
  CSVs even though it is also runnable).
- A locally reproduced run under `results/_run_all/<optimizer>/<suite>/summary/`
  is only a fallback for cells the reference tree does not carry
  (`result_loader.load_algorithm`).
- Outputs land in `results/_run_all/_analysis/<suite>/` (or `--out`).

### 8.2 The 7-algorithm panel

The report assembles a **7-algorithm** panel (6 GSK-family comparators +
`dt-gsk`) and produces:
- a Friedman test with mean ranks;
- a Nemenyi critical-difference diagram + rank charts (`analysis/figures.py`);
- pairwise Wilcoxon signed-rank tests with a Holm correction;
- Vargha-Delaney A12 / Cliff's delta effect sizes and win/tie/loss;
- LaTeX table fragments (`analysis/latex_tables.py`).

The statistical primitives live in the **vendored** `analysis/statistics.py` and
`analysis/statistical_tests.py` (BCa bootstrap, the tests above, and the
`run_statistical_analysis` orchestrator).

### 8.3 The `--stats` runner hook

`run_experiment` carries an **opt-in, default-off** per-dimension hook
(`statistical_analysis` in `ExperimentConfig`). When enabled it streams a live
per-dimension Wilcoxon + Friedman panel during a run by calling
`analysis.run_statistical_analysis` (`_emit_statistical_analysis`). It is the
only execution-time coupling from `runners/` into `analysis/`, it skips vanilla
`gsk`, works on the fixed-dimension suites (e.g. `cec2017`, `cec2013`) and the
native-dimension `cec2011` rollup, and folds in a `<OPT>-REF`
reference-self validation comparator when committed reference data exists.

See [docs/research/statistical_analysis.md](docs/research/statistical_analysis.md)
for the methodology narrative.

---

## 9. The papers review-pack pipeline

`papers/scripts/generate_review_pack.py` builds
`papers/DT-GSK-CEC2017-review.pdf` directly with matplotlib `PdfPages` (no LaTeX
toolchain required). It renders the 7-algorithm GSK-family convergence grids from
the per-cell `CheckpointErrors_<alg>_F<k>_D<dim>.csv` logs (written by
`runners/output.py`). The wider `papers/scripts/` set also generates the Nemenyi
CD figure, rank charts, parametric/BCa tables, the manuscript figures, the
per-suite convergence grids (`generate_full_convergence.py`,
`generate_cec2011_convergence.py`, `generate_cec2013_convergence.py` -- these
read curves and gen_logs from `benchmarks/cec_reference_results/`), and the
DT-GSK ablation matrix (`generate_ablation_matrix.py`, which aggregates the
`scripts/run_ablation.py` cells under `results/_ablation/` into
`results/ablation/` rank-summary CSVs).

**Provenance rule:** missing curves are logged to `*_missing.log` (e.g.
`papers/DT-GSK-CEC2017-review_missing.log`) and are **NEVER fabricated**. This
pipeline is a pure consumer of `results/_run_all/` and
`benchmarks/cec_reference_results/`; it never writes into either evidence tree.

---

## 10. Documentation system

Documentation is a themed Markdown tree under `docs/`, rendered to a static site:

```
docs/
|-- getting-started/  (tutorial, user_guide, configuration, runbook, troubleshooting, explainer)
|-- reference/        (api, architecture, result_schema, seed_policy, benchmark_protocol, ...)
|-- algorithms/       (gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk)
|-- development/      (developer_guide, contributor_guide, extension_guide, egsk_port_spec, history/, ...)
|-- research/         (statistical_analysis, reproducibility, performance, validation_report, ...)
|-- prompt/           (authoring prompts)
|-- html/             (GENERATED static site -- api/ + assets/)
```

- `docs/html/` is **generated** by `scripts/build_docs_html.py`, which renders
  every `*.md` page and extracts API docs from Python docstrings (the `html/`
  directory is skipped as a source). Do not hand-edit `docs/html/`.
- These root governance files (this one and its siblings) are the high-level
  *rules*; the in-depth per-topic material lives under `docs/`. This file is the
  structural index into that tree -- for the structural reference companion see
  [docs/reference/architecture.md](docs/reference/architecture.md),
  [docs/reference/module_dependencies.md](docs/reference/module_dependencies.md),
  and [docs/reference/project_structure.md](docs/reference/project_structure.md).

The doc set is gated: a fixed doc list must exist, the HTML must rebuild, and
every generated HTML relative link must resolve (smoke tests). Treat
[runbook.md](runbook.md) as the copy-paste command source, [README.md](README.md)
as the landing page, and [SKILL.md](SKILL.md) as the agent operating contract.

---

## 11. Cross-references

| Concern | Go to |
| --- | --- |
| Rationale, design trade-offs, how-to-extend recipes | [DESIGN_GUIDE.md](DESIGN_GUIDE.md) |
| Governance rules and what is locked | [PROJECT_RULES.md](PROJECT_RULES.md) |
| Suite protocols, budgets, result schema, evidence rules | [BENCHMARK_RULES.md](BENCHMARK_RULES.md) |
| Style, docstrings, dataclass/typing conventions, gates | [CODING_STANDARD.md](CODING_STANDARD.md) |
| Numba/BLAS thread pinning, parallelism, JIT caching | [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md) |
| Commands | [runbook.md](runbook.md) |
| Agent operating contract | [SKILL.md](SKILL.md) |
| Deep per-topic reference | [docs/reference/](docs/reference/) |
