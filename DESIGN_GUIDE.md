# DESIGN_GUIDE.md -- Design Principles and How to Extend

**Purpose.** This document records the design philosophy of the GSK-family Python project (`00-GSK_Family_Python`, PhD research software for the GSK optimizer family) and gives concrete, copy-pasteable recipes for extending it: adding an optimizer, a benchmark suite, a CLI command, a result artifact, or an analysis comparator. It is the "why it is shaped this way, and how to grow it without breaking it" reference.

**Audience.** Contributors and future-you adding code to `src/gsk_family/`. Read this *before* writing a new optimizer or analysis routine. This file covers design intent and extension procedure; it deliberately defers:
- exact directory/module layout to [ARCHITECTURE.md](ARCHITECTURE.md),
- line-level coding rules (typing, docstrings, naming, imports) to [CODING_STANDARD.md](CODING_STANDARD.md),
- benchmark protocol / seed / reproducibility rules to [BENCHMARK_RULES.md](BENCHMARK_RULES.md),
- determinism and threading performance contracts to [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md),
- repo-wide governance (what you may/may not touch, commit policy) to [PROJECT_RULES.md](PROJECT_RULES.md).

The agent operating contract is [SKILL.md](SKILL.md); the landing page is [README.md](README.md); copy-paste commands are in [runbook.md](runbook.md). Narrative developer docs live under [docs/development/](docs/development/) (notably `extension_guide.md`, `developer_guide.md`, `contributor_guide.md`).

---

## 1. Design principles

These are the load-bearing invariants. Every new module SHOULD reinforce them; none MAY silently violate them.

### 1.1 One optimizer contract, no exceptions

Every optimizer exposes exactly one entry point:

```python
def optimize(problem: BenchmarkProblem, options: OptimizerOptions | dict) -> OptimizerResult
```

- `BenchmarkProblem` (`benchmark_adapter/problem.py`) is a frozen dataclass: `suite`, `func_id`, `dim`, `lb`, `ub`, `optimum`, `evaluate`, `max_nfes`, `target_error`, plus metadata. It is the *only* channel through which an optimizer learns about the problem.
- `OptimizerResult` (`types.py`) is the *only* shape an optimizer returns.
- The runner (`runners/run_experiment.py`) dispatches through `OPTIMIZER_FUNCTIONS`, which maps each id to its `optimize`. It never reaches into an optimizer's internals.

**MUST**: a new optimizer conforms to this signature. **NEVER**: add a second public entry point, a bespoke result type, or a back-channel that bypasses `BenchmarkProblem`/`OptimizerResult`.

### 1.2 Thin adapters over algorithm cores

An optimizer module is an *adapter*, not the algorithm. Its job is to translate the uniform contract into whatever the underlying numerical kernel wants, and translate the kernel's output back. The cleanest example is `optimizers/dt_gsk.py` (~309 lines): it builds a config, wraps `problem.evaluate` as a batch objective, calls the vendored core `ism_gsk_optimize`, and packs the result. The heavy numerics live elsewhere (vendored `_dt_core.py`, `_dt_subsystems/`, `_kernels.py`).

**SHOULD**: keep adapter logic (option parsing, bounds normalization, result packing) separate from algorithm logic (the update rules). Numba-JIT hot loops belong in dedicated kernel modules, not inline in the adapter.

**Accepted duplication.** Several small module-private helpers (`_option_value`, `_scan_best`, `_append_convergence`, the `_MISSING` sentinel) are deliberately repeated across optimizer modules rather than centralized. Each optimizer module mirrors its published reference implementation as a self-contained unit, which keeps reference traceability line-local and means editing one optimizer can never perturb another's behavior or RNG draw order. Do not "deduplicate" these into a shared module without an explicit request plus green byte-stability gates; the duplication is a reviewed trade-off, not an oversight.

### 1.3 Separation of concerns: runner / optimizer / benchmark / analysis

The four layers each have a single responsibility and talk only through dataclass contracts:

| Layer | Package | Owns | Does NOT own |
|-------|---------|------|--------------|
| Runner | `runners/` | scheduling, seeds, parallelism, incremental output, self-healing process pool | the optimizer's math, the benchmark's math |
| Optimizer | `optimizers/` | the search algorithm behind `optimize()` | how it is scheduled, where results are written |
| Benchmark | `benchmark_adapter/` | `make_problem` -> `BenchmarkProblem` (bounds, evaluate, budget, optimum) | which optimizer runs, how stats are computed |
| Analysis | `analysis/` | statistics, tables, figures, reports from written CSVs | running optimizers or generating new trajectory data |

The runner imports each optimizer's `optimize` and the benchmark factory; it does *not* import the inverse. Analysis reads results off disk and never invokes an optimizer. See [ARCHITECTURE.md](ARCHITECTURE.md) for the full dependency graph.

### 1.4 Determinism by construction

A run is reproducible from `(seed_policy, base_seed, dim, func, run)` alone. The seed is computed *before* the optimizer starts (`runners/seed_policy.py`), passed in via `options.seed`, and the unified schedule `get_cec_seed(base_seed=20240620, dim, func, run)` (strides dim=1000003, func=1000033, run=1000037, mod 2147483646, +1) is identical across optimizers so cross-family comparisons are fair. Determinism is not an afterthought bolted on by a test; it is a property the design guarantees and the byte-stable regression gates protect.

**MUST**: derive all randomness from `options.seed` through a project RNG (`common/rng.RandomContext` / `common/threefry_rng`); **NEVER** call NumPy's global stream (`np.random.rand`, default `default_rng()` with no seed) inside an optimizer. Threading/BLAS pinning that this depends on is specified in [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md); the seed schedule itself in [BENCHMARK_RULES.md](BENCHMARK_RULES.md).

### 1.5 Vendored-core fidelity for dt-gsk

`dt-gsk` is THIS project's proposed method, byte-identically migrated from the source DT-GSK v2.1. Its core is **vendored and byte-identity-locked**:

- `optimizers/_dt_core.py` (~4983 lines) and `optimizers/_dt_subsystems/*` (bound_constraint, budget, budget_policy, basin_memory, gained_shared_junior, gained_shared_senior, interaction_graph, `_numba_accel`, `_dt_provenance`),
- the config builder `optimizers/_dt_profiles.py` and the 13-substream RNG `optimizers/_dt_rng.py`.

**NEVER edit these for behavior.** They are exempt from the docstring gate precisely because they are frozen imports, and their byte-identity is protected by KAT/regression gates. New DT-GSK functionality is added *around* the core (in the adapter or new sibling modules), never inside it. Details in section 5; rationale in [PROJECT_RULES.md](PROJECT_RULES.md).

### 1.6 Decoupled stats: pure functions in, loading separate

The analysis layer splits "load data" from "compute statistics" from "render output":

- **Computation** (`analysis/statistical_tests.py`, `analysis/statistics.py`) is a vendored, dependency-light core of pure functions that take plain `dict`s / NumPy arrays / file paths and return plain result objects (Wilcoxon, Friedman, Holm, BH, Vargha-Delaney A12, Cliff's delta, win/tie/loss, BCa bootstrap). These two modules are docstring-gate-exempt vendored stats.
- **Loading** (`analysis/result_loader.py`) reads result CSVs into structured tables.
- **Rendering** (`analysis/figures.py`, `analysis/latex_tables.py`) turns structured results into PNGs / LaTeX.
- **Orchestration** (`analysis/family_report.py`, `run_statistical_analysis`) wires them together.

This separation means the statistical functions are unit-testable on synthetic arrays with no disk I/O, and the loaders/renderers can change CSV schemas or output formats without touching the math.

---

## 2. The optimizer contract in detail

### 2.1 Inputs

`problem: BenchmarkProblem` (frozen) gives the optimizer everything it needs:

| Field | Meaning |
|-------|---------|
| `suite`, `func_id`, `dim` | problem identity and dimensionality |
| `lb`, `ub` | per-dimension bound arrays, each shape `(dim,)` (validated in `__post_init__`) |
| `evaluate(X)` | batch objective: takes a `(N, dim)` population, returns `(N,)` fitness |
| `max_nfes` | the evaluation budget (the single termination cap) |
| `optimum`, `target_error` | for error computation |

`options: OptimizerOptions | dict` carries run-level knobs (`types.py`): `seed` (required), `rand_generator` (default `"twister"`; dt-gsk forces `"threefry"`), `initial_population` (the runner's fair-start X0, drawn once per cell), `rng_state_after_initialization`, and a free-form `values` dict for per-optimizer overrides. Adapters MUST accept both an `OptimizerOptions` object and a plain dict (see `_option_value`/`_values_dict` in `dt_gsk.py` for the canonical reader).

### 2.2 Outputs

`OptimizerResult` (`types.py`) MUST be fully populated:

| Field | Source |
|-------|--------|
| `optimizer`, `suite`, `func_id`, `dim`, `seed` | echoed from problem/options |
| `best_x` | best solution vector, `float64`, shape `(dim,)` |
| `best_fitness` | raw objective at `best_x` |
| `error` | `compute_error(best_fitness, optimum, target_error)` (use `gsk_family.stats.compute_error`) |
| `nfes` | actual evaluations consumed |
| `termination` | `"max_evaluations"` etc. |
| `convergence` | a `ConvergenceTrace(nfes, best_fitness)` of best-so-far points |
| `runtime_seconds` | wall time via `time.perf_counter()` |
| `params` | resolved hyper-parameters recorded for provenance |
| `notes` | free text (e.g. `"self-init (fair-start exception)"`) |

### 2.3 Options / values overrides

Per-run hyper-parameter overrides flow through `options.values`. The dt-gsk adapter filters `values` against the `ISMGSKConfig` field set and against a `_RESERVED_FIELDS` set (`dim`, `seed`, `max_nfes`, `bounds`, `rand_generator`) that are resolved from the problem and never overridable, then applies the survivors with `dataclasses.replace`. A new optimizer SHOULD adopt the same pattern: a documented, whitelisted override surface, with run-level fields reserved.

### 2.4 Convergence trace

`evaluate` is batch; the trace is best-so-far over consumed evaluations. dt-gsk passes a `curve_callback(evals_used, best_f)` to its core and records one point per call, falling back to a single terminal point if none fired. A new optimizer MUST emit at least one trace point; richer traces feed the checkpoint-error curves the paper pack consumes (see section 6 and [BENCHMARK_RULES.md](BENCHMARK_RULES.md)).

---

## 3. How to ADD a new optimizer

Adding a runnable optimizer touches a small, fixed set of registration points. Miss one and the optimizer is invisible or mis-seeded.

1. **Implement the adapter.** Create `src/gsk_family/optimizers/<name>.py` exposing `optimize(problem, options) -> OptimizerResult`. Keep it thin (section 1.2); put hot loops in a kernel module. Every public symbol needs a docstring (docstring gate; see [CODING_STANDARD.md](CODING_STANDARD.md)).

2. **Register the id** in `optimizers/__init__.py` `OPTIMIZER_IDS` (the canonical tuple, currently `gsk, agsk, apgsk, atmals-gsk, egsk, fdb-agsk, dt-gsk`). Use a lowercase, hyphenated id.

3. **Wire dispatch** in `runners/run_experiment.py` `OPTIMIZER_FUNCTIONS` -- add `"<name>": optimize_<name>` and the matching import.

4. **Declare seed behavior** in `runners/seed_policy.py`. Decide which seed family the optimizer belongs to:
   - reference-linear (`REFERENCE_LINEAR_OPTIMIZERS`), reference-product (`REFERENCE_PRODUCT_OPTIMIZERS`), or
   - unified-only (`UNIFIED_ONLY_OPTIMIZERS`, like `dt-gsk`, which is forced onto `get_cec_seed` + threefry under *every* policy).
   Also set its `effective_rand_generator` behavior. **MUST NOT** invent a new ad-hoc seed formula; reuse an existing family unless the science demands otherwise, and document the choice. See [BENCHMARK_RULES.md](BENCHMARK_RULES.md).

5. **Expose it to analysis** if it is a GSK-family comparator: add it to `analysis/project_policy.py` `RUNNABLE_OPTIMIZERS` (and `REFERENCE_COMPARATORS` only if committed reference data exists). `cli/list.py` reads `OPTIMIZER_IDS`, so step 2 already makes `gsk-list` show it; no extra CLI edit is needed there.

6. **Add gates.** A smoke test that runs one tiny cell (e.g. `sphere`), a unit test for option parsing, and -- if the optimizer claims determinism -- a byte-stable regression cell. Keep ruff clean and pytest tiers green ([PROJECT_RULES.md](PROJECT_RULES.md), [CODING_STANDARD.md](CODING_STANDARD.md)).

**NEVER**: register an optimizer in only some of these places. The id in `OPTIMIZER_IDS`, the function in `OPTIMIZER_FUNCTIONS`, and the seed classification in `seed_policy.py` must agree.

---

## 4. How to ADD a suite, a CLI command, or a result artifact

### 4.1 A benchmark suite

Suites are owned by `benchmark_adapter/`, not by any optimizer. To add one:

1. Add the id to `benchmark_adapter/protocol.py` `CEC_SUITES` (currently `cec2011, cec2013, cec2013lsgo, cec2017, cec2020`; `sphere` is the smoke problem, registered separately).
2. Classify it: raw-objective (`RAW_OBJECTIVE_SUITES`) vs error-vs-optimum (`ERROR_VS_OPTIMUM_SUITES`), and native-dimension vs uniform-dimension (`is_native_dimension_suite`). CEC2011 is the heterogeneous case: 22 real-world problems with native per-problem dims and per-dimension bounds.
3. Add its `SuiteProtocol` (function ids, default dims, budget rule) and a `make_problem` branch in `benchmark_adapter/factory.py` that returns a valid `BenchmarkProblem` (bounds shape `(dim,)`, a working `evaluate`, correct `max_nfes`).
4. Ensure every optimizer's bounds handling copes. The dt-gsk adapter already supports both uniform `(lo, hi)` and per-dimension `(lb_array, ub_array)` bounds via `_resolve_bounds` (section 5.3).

The exact protocol values (CEC2017 excludes F2; CEC2011 budget 150000 NFEs; etc.) are normative in [BENCHMARK_RULES.md](BENCHMARK_RULES.md) -- do not duplicate them here.

### 4.2 A CLI command

Console scripts live in `cli/` (`run.py`, `list.py`, `validate.py`, `stats.py`; entry points `gsk-run`/`gsk-family-run`, `gsk-list`, `gsk-validate`, `gsk-stats`). To add one: create `cli/<verb>.py` with an `argparse`-based `main(argv) -> int`, keep the module a thin shell that calls into `runners/` or `analysis/` (the CLI parses args and prints; it does not contain logic), and register the console-script entry point in packaging. Match the existing output style -- the documentation-command smoke gate and the console-output-format policy both depend on stable text.

### 4.3 A result artifact

Result writing is centralized in `runners/output.py` (summary tables, per-run rows, curves, gen logs, seed schedule, environment/profile metadata). The layout is `results/_run_all/<optimizer>/<suite>/{summary,curves,gen_logs}/`. To add an artifact:

- Add a writer in `runners/output.py`, write **incrementally** so an interrupted campaign keeps completed cells, and never overwrite `benchmarks/cec_reference_results/` (READ-ONLY imported evidence).
- Preserve existing schemas. Summary rows are `Function,Best,Median,Mean,Worst,SD`; changing a column breaks reproduced-summary consumers and the analysis loaders.

Schema/format rules are normative in [BENCHMARK_RULES.md](BENCHMARK_RULES.md).

---

## 5. The dt-gsk migration design

`dt-gsk` is the project's contribution and its most constrained component. The design goal is *byte-for-byte trajectory reproduction* of the source DT-GSK v2.1 for any `(dim, seed, func, run)`.

### 5.1 The four pieces

| Piece | File | Role |
|-------|------|------|
| Vendored core | `optimizers/_dt_core.py` + `_dt_subsystems/*` | `ism_gsk_optimize(objective, config, curve_callback)` and all subsystem math (junior/senior gained-shared, interaction graph, basin memory, budget controllers, bound constraint). Frozen. |
| Profile builder | `optimizers/_dt_profiles.py` | `build_pub_config(dim, *, seed, max_nfes, bounds, rand_generator)` -- reproduces the source `pub` profile per dimension tier. |
| Substream RNG | `optimizers/_dt_rng.py` | 13 named, independent substreams from one run seed. |
| Adapter | `optimizers/dt_gsk.py` | the contract bridge described in section 2. |

### 5.2 Self-init 5*D fair-start exception

DT-GSK seeds its *own* substream RNG from `options.seed` and draws its *own* initial population of `np_init_mult * dim` individuals (the tuned `5*D` start). It therefore **does not consume** the runner's fair-start `initial_population` / X0. This is a *documented, intentional* fair-start exception: it preserves the source's byte-identical initialization while remaining fully deterministic for a given seed. The adapter records `notes="self-init (fair-start exception)"`. **Do not** "fix" this by injecting the runner X0 -- that would break byte-identity. (Rationale also in [PROJECT_RULES.md](PROJECT_RULES.md).)

### 5.3 Per-dimension vs uniform bounds

`_resolve_bounds` collapses uniform bounds to scalar `(lo, hi)` floats so CEC2017/sphere configs stay byte-identical to the source's scalar form, but returns `(lb_array, ub_array)` for heterogeneous bounds (CEC2011's per-variable ranges). `build_pub_config` mirrors this: array bounds become JSON-serializable immutable tuples that `bounds_matrix` later wraps into the `(2, D)` repair array. Any change to bounds handling MUST preserve both paths.

### 5.4 The pub profile dimension tiers

`build_pub_config` applies tier-specific overrides on top of `_PUB_COMMON`:

| Tier | Key additions |
|------|---------------|
| `D < 20` | `_PUB_D_LT_20` + escape overrides (extra BSE restarts, Cauchy escape) |
| `20 <= D < 50` | `_PUB_D_20_TO_49` + D30 best-status overrides |
| `D >= 50` | `_PUB_D_GE_50` + **SGSM** interaction-graph extras (`_SGSM_D_GE_50_EXTRA`) + adaptive-confidence + final-polish promotions |
| `D >= 100` | all of the above **plus** `_PUB_D_GE_100_EXTRA`: **TERRA** controllers, budget policy, basin memory, **SP-NLPSR**, coordinate local search, late-accept clipping |

These tiers are why DT-GSK at `D>=50` needs single-thread numba/BLAS for byte-stable determinism (prange/SGSM) and at `D>=100` runs TERRA -- a [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md) concern. The exact field values are an oracle locked by `tests/unit/test_dt_profiles.py`; treat `_dt_profiles.py` as data, not logic, and never hand-edit a value.

### 5.5 The 13 substreams

`_dt_rng.py` derives 13 named, position-locked substreams from one run seed: `init, core, ace, kexp, div, bse, arch, link, de, control, flow, basin, trust`. Substream isolation is what makes toggling a subsystem not perturb another's draws. The order is an **append-only contract** -- the first nine names are prefix-locked; new substreams may only be appended. Stream 0 (`init`) gets the seed verbatim; others get `(seed + 1_000_003*(idx+1)) % MAX_SAFE_SEED + 1`. The underlying Threefry-4x64-20 generator is reused from `common/threefry_rng.py` (byte-identical to the source). Locked by `tests/unit/test_dt_rng.py`.

See `docs/development/dt_gsk_core_reference.md` and `docs/algorithms/dt-gsk.md` for the migration narrative.

---

## 6. The analysis-layer design

The analysis layer turns written result CSVs into the paper's 7-algorithm GSK-family panel (6 comparators + dt-gsk). Its modules have crisp, non-overlapping roles:

| Module | Responsibility |
|--------|----------------|
| `analysis/statistics.py` | publication-grade effect sizes / multiple-comparison helpers (A12, Cliff's delta, Holm, BH). Vendored, docstring-exempt. |
| `analysis/statistical_tests.py` | the test core: Wilcoxon, Friedman ranks, BCa bootstrap, win/tie/loss, and the `run_statistical_analysis` orchestrator. Vendored, docstring-exempt. |
| `analysis/result_loader.py` | reads result CSVs into structured tables (GSK-family-only comparator scope); loads **reference-first** -- `load_algorithm` tries the committed reference panel (`benchmarks/cec_reference_results/`, the single source of truth for paper statistics), then falls back to the locally reproduced run. |
| `analysis/family_report.py` | ties loader + stats core + effect-size helpers + figure/table generators into one paper-grade report. |
| `analysis/figures.py` | Nemenyi critical-difference + rank charts (matplotlib Agg) from Friedman mean ranks. |
| `analysis/latex_tables.py` | `\input{}`-ready `tabular` fragments built straight from structured results (no intermediate CSV drift). |
| `analysis/project_policy.py` | dependency-free single source of truth for `RUNNABLE_OPTIMIZERS` / `REFERENCE_COMPARATORS`. |

### 6.1 `run_statistical_analysis` orchestration

`run_statistical_analysis(new_summary_csv, ref_base_dir, suite, dim, new_label="dt-gsk", excluded_funcs=(2,), zero_tol=1e-8, extra_comparators=None)` runs both Wilcoxon and Friedman against the discovered GSK-family references and returns a `StatAnalysisResult` whose `str()` is the formatted text (so existing `log.info(result)` callers keep working). It degrades gracefully when scipy is absent. The `gsk-stats` CLI (`cli/stats.py`) is the batch front end; the runner's opt-in `--stats` flag (default off; skips vanilla `gsk`; works on the fixed-dimension suites such as cec2017/cec2013 and the native-dimension cec2011 rollup) streams the per-dimension Wilcoxon+Friedman live during a campaign.

### 6.2 `extra_comparators` reference-self validation

`extra_comparators` is a `{label: summary_csv}` mapping folded into the panel beyond the auto-discovered references. Its motivating use is **reference-self validation**: when committed reference data exists for the proposed method, a `<OPT>-REF` comparator (the official reference DT-GSK results) is added so the proposed run is validated directly against its own reference *while* the GSK-family comparisons are retained. Each extra comparator joins both the pairwise Wilcoxon panel and the Friedman ranking; missing or empty CSVs are skipped, never fabricated.

### 6.3 Extending analysis

To add a statistic: add a pure function to `statistical_tests.py`/`statistics.py` taking plain arrays/dicts, unit-test it on synthetic data, then surface it through `family_report.py` -- **do not** make the test functions read files. To add a comparator: register it in `project_policy.py` and pass it as an `extra_comparator`. **NEVER** fabricate numerical results or convergence data, and **NEVER** overwrite `benchmarks/cec_reference_results/`.

The paper pack (`papers/scripts/generate_review_pack.py` -> `papers/DT-GSK-CEC2017-review.pdf`) builds 7-algorithm convergence grids from `CheckpointErrors_<alg>_F<k>_D<dim>.csv`; missing curves are logged to `*_missing.log`, never invented.

---

## 7. Anti-patterns to avoid

- **NEVER** edit the vendored dt-gsk core (`_dt_core.py`, `_dt_subsystems/*`) or its locked profile/RNG (`_dt_profiles.py`, `_dt_rng.py`) for behavior. Build new functionality around the core.
- **NEVER** call NumPy's global/un-seeded RNG inside an optimizer; route all randomness through the seeded project RNG (section 1.4).
- **NEVER** let an optimizer write files, decide its own seed, or read the disk; that is the runner's job (section 1.3).
- **NEVER** let an analysis function run an optimizer or generate trajectory data; analysis reads results, it does not produce them.
- **NEVER** couple a statistical function to disk I/O -- keep computation (plain arrays/dicts in, results out) separate from loading (section 1.6).
- **NEVER** half-register an optimizer (id without dispatch, dispatch without seed policy). Update all of `OPTIMIZER_IDS`, `OPTIMIZER_FUNCTIONS`, and `seed_policy.py` together (section 3).
- **NEVER** add a second public entry point or a bespoke result type; conform to `optimize()` -> `OptimizerResult` (section 1.1).
- **NEVER** change a result CSV schema (`Function,Best,Median,Mean,Worst,SD`) or console-output format without updating every consumer and the documentation/format gates (section 4.3).
- **NEVER** overwrite `benchmarks/cec_reference_results/` or fabricate any numbers, ranks, or curves.
- **AVOID** fattening adapters with algorithm math; push hot numerics into kernel modules (section 1.2).
- **AVOID** injecting the runner X0 into dt-gsk -- the `5*D` self-init is intentional and byte-identity-critical (section 5.2).

---

*Cross-references:* [PROJECT_RULES.md](PROJECT_RULES.md) | [ARCHITECTURE.md](ARCHITECTURE.md) | [BENCHMARK_RULES.md](BENCHMARK_RULES.md) | [CODING_STANDARD.md](CODING_STANDARD.md) | [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md) | [SKILL.md](SKILL.md) | [README.md](README.md) | [runbook.md](runbook.md) | [docs/development/extension_guide.md](docs/development/extension_guide.md) | [docs/development/dt_gsk_core_reference.md](docs/development/dt_gsk_core_reference.md) | [docs/algorithms/dt-gsk.md](docs/algorithms/dt-gsk.md)
