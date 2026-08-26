# BENCHMARK_RULES.md

**Purpose.** This document codifies the benchmark and experiment-protocol rules
for the DT-GSK repository: which suites exist, the exact per-suite
function/dimension/run/budget protocol, how bounds and the seed/RNG regime are
fixed, how reference evidence is treated, the result CSV schema, and the
7-algorithm GSK-family comparison panel. **Every number below is the repository's
ground truth** — it mirrors `src/gsk_family/benchmark_adapter/protocol.py`,
`benchmark_adapter/factory.py`, `runners/config.py`, `runners/seed_policy.py`,
and `analysis/result_loader.py`. Treat this as a standard: it uses MUST / SHOULD /
NEVER and is binding on anyone running campaigns, importing references, or
generating paper tables.

**Audience.** Researchers running benchmark campaigns, anyone preparing tables
or figures for the DT-GSK paper, and reviewers auditing reproducibility.

**Sibling governance files** (all at the project root): overall conduct in
[PROJECT_RULES.md](PROJECT_RULES.md); the optimizer/result-contract design in
[DESIGN_GUIDE.md](DESIGN_GUIDE.md); the module map in
[ARCHITECTURE.md](ARCHITECTURE.md); code conventions in
[CODING_STANDARD.md](CODING_STANDARD.md); determinism/threading/JIT in
[PERFORMANCE_RULES.md](PERFORMANCE_RULES.md). Operating contract: [SKILL.md](SKILL.md);
landing page: [README.md](README.md); copy-paste commands: [runbook.md](runbook.md).
This file owns the **benchmark protocol**; it defers algorithm internals,
threading, and code style to the cross-linked files above.

---

## 1. The six benchmark suites

The project supports exactly six suites. They are declared in
`SUPPORTED_SUITES` / `SUITE_PROTOCOLS` in
`src/gsk_family/benchmark_adapter/protocol.py` and constructed by
`make_problem(...)` in `benchmark_adapter/factory.py`. NEVER add, rename, or
silently extend this set.

| Suite | Functions (public IDs) | Default functions | Dimensions | Budget (NFEs) | Statistics basis | Optimum / target |
|---|---|---|---|---|---|---|
| `sphere` | F1 | F1 | D=10 (smoke) | `10000*D` | `error_vs_optimum` | optimum 0, target 1e-8 |
| `cec2011` | F1–F22 | F1–F22 | **native** (per-problem) | **150000** | **`raw_objective`** | optimum NaN (no known optimum) |
| `cec2013` | F1–F28 | F1–F28 | 10/30/50 | `10000*D` | `error_vs_optimum` | per-function `fopt`, target 1e-8 |
| `cec2013lsgo` | F1–F15 | F1–F15 | **native** (large-scale, e.g. D=1000) | `3000000` | **`raw_objective`** | optimum NaN |
| `cec2017` | F1–F30 | **F1, F3–F30 (F2 excluded)** | 10/30/50/100 | `10000*D` | `error_vs_optimum` | per-function `fopt`, target 1e-8 |
| `cec2020` | F1–F10 | F1–F10 | 5/10/15/20 | per-dim (see below) | `error_vs_optimum` | per-function `fopt`, target 1e-8 |

Concrete facts from the code:

- **`sphere`** — pure-Python smoke-test problem (`SuiteProtocol.notes = "Pure
  Python smoke-test problem."`). Use it to verify the toolchain before a real
  campaign; do NOT report it as scientific evidence.
- **`cec2011`** — 22 real-world application problems with **native per-problem
  dimensions** and **per-dimension (heterogeneous) bounds**. `default_dimensions`
  is the literal string `"native"`; statistics basis is `raw_objective`; the
  adapter optimum is `NaN`.
- **`cec2013`** — 28 functions, fixed dims 10/30/50, error-vs-optimum; the
  **second GSK-family comparison suite** (51 runs; a full 7-optimizer reference
  panel is committed, see §6). The SGSM-overlay ablation additionally uses a
  CEC2013 D=50 hold-out design (four cells: full / no-adaptive / no-sgsm /
  no-finalpolish), which has since been promoted to cover CEC2017 D=50 and
  D=100 as well.
- **`cec2013lsgo`** — 15 large-scale functions, native dims (D=1000; F13/F14 are
  D=905), `raw_objective` for comparability with imported references; budget
  `3000000` NFEs, 25 runs. **F3/F6/F10 are an exception to that comparability:**
  this bank evaluates the *transformed* Ackley chain (T_osz → T_asy(0.2) →
  Lambda(10) → ackley, the Molina-package form SHADE-ILS uses), so those three
  functions are NEVER comparable to a published raw-Ackley table such as MOS's.
  The DECC-G transcription's variant was never verified, so treat its F3/F6/F10
  entries the same way. See the `benchmark_variant.json` sidecar in each
  `cec2013lsgo/<alg>/` directory and
  `papers/governance/production_deviation_record.md` D-8.2.
- **`cec2017`** — 30 functions implemented, **F2 implemented but excluded from
  the default/scored set** (see §2). Dims 10/30/50/100.
- **`cec2020`** — 10 functions, dims 5/10/15/20, with **per-dimension budgets**
  from `CEC2020_BUDGETS = {5: 50000, 10: 1000000, 15: 3000000, 20: 10000000}`.
  Two cell sets are refused by `make_problem`:
  `CEC2020_PROTOCOL_EXCLUDED_CELLS = {(6,5),(7,5)}` (F6/F7 are specified for
  D = 10/15/20 only — Yue et al. 2019, TR 201911 §2.1), and
  `CEC2020_UNAVAILABLE_CELLS`, which is **empty since 2026-07-26** — the former
  F1/F8 gaps at D=5/D=15 were validated against the in-repo C++ oracle and
  restored (pinned by `tests/regression/test_cec2020_restored_cells.py`). The
  committed bank uses **30 runs** per cell.

`RAW_OBJECTIVE_SUITES = {cec2011, cec2013lsgo}` and
`ERROR_VS_OPTIMUM_SUITES = {cec2013, cec2017, cec2020}` are the authoritative
basis partitions. **Statistics MUST be computed in the suite's declared basis**;
NEVER mix raw-objective and error-vs-optimum numbers in one table.

---

## 2. CEC2017 protocol (the paper's primary suite)

The DT-GSK paper's headline evidence is CEC2017. Reproduce it exactly.

1. **Functions: F1, F3–F30 — F2 is EXCLUDED.**
   - `default_function_ids("cec2017") = (1,) + tuple(range(3, 31))` in
     `protocol.py` (note: `notes = "F2 is implemented but excluded from default
     comparisons."`).
   - The analysis layer enforces the same exclusion:
     `SUITE_EXCLUDED_FUNCS["CEC2017"] = {2}` in `analysis/result_loader.py`.
   - **Why F2 is excluded:** F2 has a documented numerical-instability issue in
     the reference CEC2017 implementation (the high-degree polynomial term
     overflows / is platform-sensitive). It is excluded by the benchmark
     maintainers themselves, not by us. F2 *is* still implemented and can be
     requested explicitly (`--function 2`), but it MUST NOT appear in scored
     comparisons, ranks, Wilcoxon/Friedman panels, or paper tables.
2. **Dimensions: D = 10, 30, 50, 100** (`CEC2017_DIMS = (10, 30, 50, 100)`;
   `SUITE_DIMS["CEC2017"] = [10, 30, 50, 100]`). A dimension outside this set is
   rejected by `validate_dimension`.
3. **Runs: 51 independent runs per cell** (CEC2017 convention; the runbook's
   campaign command uses `--runs 51`).
4. **Budget: `10000 * D` NFEs** (`max_nfes=_max_nfes(10_000 * d, ...)` in
   `factory.py`): 100000 at D=10, 300000 at D=30, 500000 at D=50, 1000000 at
   D=100.
5. **Statistics basis: `error_vs_optimum`** — report `f(x) - fopt` clamped at the
   `target_error = 1e-8` threshold (values below the threshold are treated as
   solved). The five reported statistics are Best, Median, Mean, Worst, SD over
   the 51 runs (§7).

**Scored CEC2017 set = F1, F3..F30 at D in {10,30,50,100}, 51 runs, budget
10000*D, error-vs-optimum.** Anything else is a diagnostic, not the protocol.

Run it via the runbook's "CEC2017 All Optimizers" command (see
[runbook.md](runbook.md)).

---

## 3. CEC2011 protocol (real-world problems)

CEC2011 is the project's real-world / engineering validation suite and follows a
**different** protocol from CEC2017. Do not transfer CEC2017 assumptions onto it.

1. **22 real-world problems, F1–F22** (`function_ids = range(1, 23)`), all in the
   default set.
2. **Native per-problem dimensions.** `default_dimensions = "native"`. Each
   problem's dimension is intrinsic: `make_problem` calls `cec2011_dim(fid)` and
   **rejects any explicit dimension that differs from the native one**
   (`raise ValueError(f"cec2011 F{fid} has native D={native_dim}, got D={d}.")`).
   Always run CEC2011 with `--dimension native`.
3. **Per-dimension (heterogeneous) bounds.** Bounds come from
   `cec2011_bounds(fid)` and are per-coordinate vectors `lb`/`ub` — different
   variables in one problem can have different ranges. Optimizers MUST honor the
   full `lb`/`ub` vectors (§4).
4. **Budget: 150000 NFEs** (`max_nfes=_max_nfes(150_000, ...)`), independent of
   dimension. This is the CEC2011 competition budget.
5. **Runs: ~25 independent runs per problem** (the runbook campaign uses
   `--runs 25`).
6. **Statistics basis: `raw_objective`.** The adapter `optimum` is `NaN` (no
   known global optimum), so statistics are reported on the **raw objective
   value**, not on an error. `SUITE_EXCLUDED_FUNCS["CEC2011"] = set()`.
7. **F2 is NOT excluded.** CEC2011 F2 is the Lennard–Jones potential — a
   legitimate engineering problem with no numerical-instability issue. The F2
   exclusion is a **CEC2017-only** rule; applying it to CEC2011 is an error.

Run it via the runbook's "CEC2011 — native per-problem dims" command.

---

## 4. Bounds rules

Bounds are produced by the suite-specific `*_bounds(...)` helpers and stored on
`BenchmarkProblem.lb` / `.ub` (vectors of length `dim`). Two regimes exist and
**every optimizer MUST support both**:

- **Uniform (scalar-broadcast) bounds — CEC2013/CEC2017/CEC2020/sphere.** A
  single `[lb, ub]` is broadcast across all coordinates (e.g. CEC2017 is
  `[-100, 100]^D`).
- **Per-dimension (heterogeneous) bounds — CEC2011.** `lb`/`ub` are full
  per-coordinate vectors; coordinates have different ranges.

Rules:

- An optimizer MUST clip / reflect / reinitialize against the **per-coordinate**
  `lb`/`ub` arrays, never against a single assumed scalar range. The dt-gsk
  adapter (`optimizers/dt_gsk.py`) explicitly supports both uniform and
  per-dimension bounds.
- NEVER hard-code `[-100, 100]` (or any CEC2017 range) into a bound-handling
  path; read `problem.lb` / `problem.ub`.
- Bound construction is owned by `benchmark_adapter`; bound *handling* utilities
  live in `common/bounds.py`. See [ARCHITECTURE.md](ARCHITECTURE.md) for the
  module split and [DESIGN_GUIDE.md](DESIGN_GUIDE.md) for the optimizer contract.

---

## 5. The seed / RNG regime rule

Reproducibility hinges on recording **and matching** the RNG regime. Every
result MUST record three things: the **base seed**, the **generator**, and the
**seed scheme**. The runner writes all three into run metadata
(`base_seed`, `rand_generator`, `seed_policy` fields, plus a seed-schedule CSV
`Dim,Function,Run,Seed`) — see `runners/run_experiment.py` and
`runners/output.py`.

**Canonical regime (use this for all comparison campaigns):**

- **Base seed `20240620`** — `DEFAULT_BASE_SEED = 20_240_620` in
  `runners/seed_policy.py` (also `ExperimentConfig.seed` default).
- **Generator: bundled Threefry-4x64-20** (`rand_generator = "threefry"`,
  resolved by `effective_rand_generator`). Implementation in
  `common/threefry_rng.py`, driven through `common/rng.py::RandomContext`.
- **Seed scheme: unified `get_cec_seed`** —
  `seed = (base_seed + 1000003*dim + 1000033*func + 1000037*run) % 2147483646 + 1`.
  This is the `unified` `seed_policy` (the default).

**dt-gsk is forced onto this regime under ALL policies.**
`UNIFIED_ONLY_OPTIMIZERS = {"dt-gsk"}`: `seed_for_run` and
`effective_rand_generator` short-circuit dt-gsk to threefry + `get_cec_seed`
regardless of the requested `seed_policy`. This guarantees the proposed method
and its comparators draw from the same per-cell seed at a given
`(dim, func, run)`.

**Rules:**

- A result MUST carry `base_seed` + `rand_generator` + `seed_policy` in its
  metadata. A result with no recorded regime is **not** admissible evidence.
- You MUST NOT silently compare results produced under different RNG/seed
  regimes. Different base seed, generator, or scheme = different experiment.
- The reference-self comparator (`<OPT>-REF`) and committed reference CSVs were
  produced under their own historical regimes; treat them as imported evidence
  (§6), label them, and never present them as if drawn from the unified regime.

**Cautionary example (real).** Earlier source-side work compared an `04`-era
result set generated with **NumPy PCG64 and base seed `123456`** against
target-side results generated with **Threefry and base seed `20240620`** and
read the gap as an algorithmic difference. It was a regime mismatch, not a
method effect. (The legacy `123456 + func_id*9973 + (run-1)` formula and the
PCG64 lineage are documented in `docs/development/dt_gsk_core_reference.md`; the
present `reference` policy's linear-seed label
`base_seed + 9973*func + (run-1)` in `reference_run_seed` is its descendant.)
**Lesson: pin base seed + generator + scheme before reading any cross-set
delta.** When in doubt, regenerate both sides under the canonical regime.

See [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md) for the single-thread pinning
(NUMBA/OMP/MKL/OPENBLAS = 1) that byte-stable determinism additionally requires.

---

## 6. Reference evidence rules

Imported reference evidence lives under
`benchmarks/cec_reference_results/<suite>/<alg>/` (resolved by
`_BENCHMARKS_DIR` in `analysis/result_loader.py`) in a flat per-optimizer
layout: per-dimension summary CSVs, `per_run.csv`, `curves/`, `gen_logs/`, plus
seed/environment/verification provenance files. Present algorithm directories
today, per suite (verified on disk): the **full 7-optimizer GSK-family panel**
— `agsk`, `apgsk`, `atmals-gsk`, `egsk`, `fdb-agsk`, `gsk`, **and the proposed
`dt-gsk`** — for **all five CEC suites** (`cec2011`, `cec2013`,
`cec2013lsgo`, `cec2017`, `cec2020`). External large-scale baselines sit in a
sibling tree, `_external_baselines/cec2013lsgo/` (`decc-g`, `mos`,
`shade-ils`); per CR-0019 they are out of paper scope — context only, and
admissible in no panel, figure, or statistic (see that tree's README for the
MOS objective-variant caveat). This
tree is the **single source of truth for all paper data and statistics**.

Rules:

- `benchmarks/cec_reference_results/` is **READ-ONLY**. NEVER overwrite, edit, or
  "regenerate over" an imported reference file. Locally reproduced results go to
  `results/_run_all/<optimizer>/<suite>/...` instead.
- **Reference naming** (per `_reference_csv_path`): fixed-dim suites use
  `<alg>_<suite>_D<dim>.csv`; CEC2011 uses the rollup `<alg>_<suite>.csv`.
- **Provenance is mandatory.** Every loaded result is tagged
  `reproduced_locally`, `imported_reference`, `derived_summary`, or
  `unavailable` (`PROVENANCE_*` constants). `load_algorithm` loads
  **reference-first**: the committed reference panel is the single source of
  truth for paper statistics (the proposed `dt-gsk` included), and a locally
  reproduced run under `results/_run_all/` is only a fallback for cells the
  reference tree does not carry. Use `provenance_report(...)` /
  `availability_matrix(...)` when you need to state where each cell came from.

**Round-1 revision evidence (`_revision/`).** The four reviewer-requested
experiments — E1 refinement basis, E2 matched population, E3 uniform-vs-tiered,
E4 parameter sensitivity — are promoted as release
**`rev-rel-2026-08-26-dd42d37eb`** under
`benchmarks/cec_reference_results/_revision/`, whose manifest carries 252 files:
30 `_configs/*.yml`, 221 per-arm result files under
`<arm>/dt-gsk/cec2017/summary/`, and one `_provenance/` driver log. The analysis
bundle is `papers/analysis/rev-rel-2026-08-26-dd42d37eb/` (governance: CR-0023,
D-0047). The release is **additive and non-superseding**: the primary release
`rel-2026-07-20-67d9345f9` and the ablation release `abl-rel-2026-07-20` are
used read-only and nothing in either is re-minted. Protocol, binding:

- All four are **CEC2017**, the 29 scored functions (F1, F3–F30), the suite's
  own protocol budget `10000 * D` (§2), and the **unified Threefry schedule at
  base seed 20240620** (`seed_policy: unified`) — the same regime as the frozen
  panel, so every new cell pairs with it at matched `(dim, func, run)`. The
  unified formula `get_cec_seed(base, dim, func, run)`
  (`runners/seed_policy.py`) carries no optimizer or cell term, so that pairing
  is verifiable rather than assumed; every analysis JSON records
  `"seed_mismatches": 0`.
- **E1–E3 use 51 runs**, matching the panel. E1 covers D = 50 and D = 100 and
  mints exactly one new arm (`e1_basis_coordinate`); its other two arms are read
  from the frozen ablation release. E2 and E3 cover all four CEC2017 dimensions.
- **E4 uses 15 runs** across 27 one-factor cells at D in {30, 100}. Runs are
  reduced rather than functions, so every E4 cell still spans the full scored
  set.
- **E4 is exploratory and descriptive only.** NEVER compute a hypothesis test or
  a corrected p-value on it, and never mix it with the supplement's S6 ablation
  material.
- Legs stage under `results/_revision/<leg>/` rather than `results/_run_all/`,
  and are promoted into the read-only tree deliberately. E1 is driven by
  `scripts/run_e1_basis_contrast.py` rather than a YAML config because it reaches
  a research hook the shipped config, profile, CLI and adapter surface
  deliberately does not forward; nothing under `src/` is modified. The
  pre-registration binding all four is
  `papers/review_2026_08_24/revision_experiments_preregistration.md` (signed
  2026-08-25, before any result existed).

---

## 7. Result CSV schema

Local summaries are written by `runners/output.py` under
`results/_run_all/<optimizer>/<suite>/{summary,curves,gen_logs}/`. The summary
schema is fixed; do not alter the header or column order.

- **Per-dimension summary:** `<optimizer>_<suite>_D<dim>.csv`, header
  **`Function,Best,Median,Mean,Worst,SD`** (one row per function, values via
  `format_scientific`).
- **CEC2011 rollup:** because CEC2011 dims are native/per-problem, a single
  rollup `<optimizer>_<suite>.csv` is written with the **same header**
  `Function,Best,Median,Mean,Worst,SD`, one row per problem.
- The loader (`load_summary_csv`) also tolerates legacy reference variants
  (`Func`/numeric IDs; eGSK's `F,Min,Median,Max,Mean,Std`), but **new local
  output MUST be the canonical `Function,Best,Median,Mean,Worst,SD` schema.**

Statistics semantics: Best/Median/Mean/Worst/SD are computed over the cell's
runs, in the suite's declared basis (error-vs-optimum for
CEC2013/2017/2020/sphere; raw-objective for CEC2011/CEC2013-LSGO). NEVER change
the basis of a committed schema.

---

## 8. The GSK-family comparison panel (7 algorithms)

The paper compares **the GSK family only** — 7 algorithms = the 6 reference
comparators + the proposed dt-gsk:

- **Reference comparators (6):** `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `egsk`,
  `atmals-gsk` (`REFERENCE_COMPARATORS` in `analysis/project_policy.py`).
- **Proposed:** `dt-gsk` (`PROPOSED_OPTIMIZER`); baseline `gsk`.

Runnability + comparator-data note:

- **All 6 comparators are runnable** plus dt-gsk →
  `RUNNABLE_OPTIMIZERS = (gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk)`
  (7 runnable optimizers). `egsk` now has a real kernel
  (`src/gsk_family/optimizers/egsk.py`), so `python run.py --optimizer egsk` works.
- **`egsk`'s panel cell is sourced from committed port data.** The Python `egsk`
  substitutes `scipy`-SLSQP for MATLAB `fmincon` in its interior-point
  refinement; the committed `egsk` panel CSVs are that **Python (`scipy`-SLSQP)
  port run** (the comparator of record), not a MATLAB `fmincon` reference. The
  panel reads these committed CSVs rather than a fresh local run so the numbers
  are fixed and reproducible.
- **Panel data:** full committed reference panels (all 7 algorithms, the
  proposed `dt-gsk` included) exist for **all five CEC suites** — `cec2017`,
  `cec2011`, `cec2013`, `cec2013lsgo`, and `cec2020`;
  `gsk-stats` loads them reference-first (§6).

The statistical panel (Friedman ranks, Nemenyi CD, pairwise Wilcoxon + Holm,
Vargha–Delaney A12 / Cliff's delta, win/tie/loss) is built by `gsk-stats` over
exactly these 7 algorithms. Algorithm internals and the stats orchestrator are
out of scope here; see [ARCHITECTURE.md](ARCHITECTURE.md) and
[DESIGN_GUIDE.md](DESIGN_GUIDE.md).

---

## 9. NEVER fabricate benchmark or convergence numbers

This is non-negotiable and overrides convenience:

- **NEVER** invent, interpolate, extrapolate, hand-edit, or "fill in" a Best /
  Median / Mean / Worst / SD value, a convergence-curve point, a checkpoint
  error, or a rank. Numbers come only from an actual run or a committed
  reference file.
- A missing cell stays missing. The review-pack generator logs absent
  convergence curves to `*_missing.log` and renders nothing for them
  (see [runbook.md](runbook.md) §"Paper Review Pack"); the loader returns
  `unavailable`. Do not paper over a gap — re-run or report it as missing.
- Do not relabel an `imported_reference` value as `reproduced_locally`, and do
  not move a number between suites/bases to make a table look complete.
- Determinism, the result schema, and the console-output format are part of the
  contract — preserve them (see [PROJECT_RULES.md](PROJECT_RULES.md) and
  [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md)).

---

## 10. How to run a campaign

Do not retype long flag lists from memory — use the canonical commands in
[runbook.md](runbook.md). Quick map:

| Goal | Where |
|---|---|
| Smoke test (seconds) | [runbook.md](runbook.md) §"Smoke Test" |
| CEC2017 all optimizers (F1:30, dims 10/30/50/100, 51 runs) | §"CEC2017 All Optimizers" |
| CEC2011 (F1:22, `--dimension native`, 25 runs) | §"Other Full Sweeps" |
| CEC2020 / CEC2013 / CEC2013-LSGO sweeps | §"Other Full Sweeps" |
| CEC2013 family panel (F1:28, dims 10/30/50, 51 runs) | §"CEC2013 Family Panel" |
| DT-GSK scaffold ablation (`scripts/run_ablation.py`, 7 cells, default 25 runs) | §"DT-GSK Ablation (CEC2017)" |\r\n| Journal revision experiments E1–E4 (`scripts/run_revision_experiments.py`, 4 legs, 32,451 runs) | §"Journal Revision Experiments (one command)" |
| Config-file launchers (`scripts/run_all_*.py`, `configs/*.yml`) | §"Config Launchers" |
| Validate / compare against references | §"Results And Validation" |
| Statistical analysis (`gsk-stats`) and live `--stats` | §"Statistical Analysis" |

Operating rules while running: prefer the self-healing **process** backend at a
conservative `--workers 2` (raise deliberately with CPU+RAM headroom); avoid the
thread backend for real campaigns; results are written **incrementally** so an
interrupted campaign keeps completed cells (use `--overwrite` only to recompute).
The threading/JIT determinism requirements live in
[PERFORMANCE_RULES.md](PERFORMANCE_RULES.md).
