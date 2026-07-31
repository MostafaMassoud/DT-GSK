# PERFORMANCE_RULES.md

**Purpose.** This document is the authoritative standard for *performance and
runtime determinism* in the `00-GSK_Family_Python` project: how Numba JIT is
warmed and cached, how threads are pinned so the proposed `dt-gsk` optimizer
stays byte-stable, how the self-healing parallel execution backend behaves, how
to keep memory bounded, how interrupted campaigns resume, and how to measure and
report runtime honestly. The cardinal rule throughout: **speed is the
optimization, determinism is the invariant** — no performance change may ever
alter a produced number, a seed schedule, or a result schema.

**Audience.** Anyone launching real CEC/CEC2011 campaigns, tuning worker counts,
diagnosing a slow or crashing run, or interpreting the `profile.json` /
`environment.json` timing artifacts. Read this alongside the operational
companions:

- [CODING_STANDARD.md](CODING_STANDARD.md) — how the code that implements these
  rules is written (vectorization, JIT decorator conventions, docstring gate).
- [PROJECT_RULES.md](PROJECT_RULES.md) — the umbrella governance (in-place work,
  commit/push policy, read-only reference data, determinism contract).
- [BENCHMARK_RULES.md](BENCHMARK_RULES.md) — suite budgets, dimensions, and the
  read-only evidence policy that performance work must not disturb.
- [ARCHITECTURE.md](ARCHITECTURE.md) and [DESIGN_GUIDE.md](DESIGN_GUIDE.md) — the
  module layout and design intent behind the runner and optimizers.
- [runbook.md](runbook.md) — the terse copy-paste command companion; the
  narrative version lives in [README.md](README.md) and the agent operating
  contract in [SKILL.md](SKILL.md).
- [docs/research/performance.md](docs/research/performance.md) — the in-depth
  performance reference (parallel backends, warmup, profiling artifacts, the
  explicit "remaining measurement work" gap). This governance file codifies the
  *rules*; that page is the narrative reference.

Capitalized **MUST / SHOULD / NEVER** are normative.

---

## 1. Numba JIT: suite kernels and the dt-gsk accelerator

Two distinct families of Numba kernels exist; they are cached and warmed the same
way but live in different places.

1.1 **Benchmark-suite kernels.** Each bundled CEC suite ships its own
`_numba.py` so the expensive benchmark math runs as compiled code:

| Suite        | Kernel module                                            |
|--------------|----------------------------------------------------------|
| cec2011      | `benchmarks/cec_suite_python/cec2011/_numba.py`          |
| cec2013      | `benchmarks/cec_suite_python/cec2013/_numba.py`          |
| cec2013lsgo  | `benchmarks/cec_suite_python/cec2013lsgo/_numba.py`      |
| cec2017      | `benchmarks/cec_suite_python/cec2017/_numba.py`          |
| cec2020      | `benchmarks/cec_suite_python/cec2020/_numba.py`          |

`sphere` is pure Python (no suite JIT). `runners/performance.py:_suite_numba_enabled`
probes each suite module for a `HAS_NUMBA` flag and reports it on the console
(`suite JIT={enabled|disabled|n/a}`).

1.2 **The dt-gsk optimizer accelerator.** `dt-gsk` has its *own* JIT kernels in
the vendored `src/gsk_family/optimizers/_dt_subsystems/_numba_accel.py` — bound
repair, population radius, ACE simplex projection, junior/senior mutation,
crossover masks, archive distance/insertion, PSR target, and accept-rate stats.
This module is **byte-identity-locked** (see
[PROJECT_RULES.md](PROJECT_RULES.md)); its parallel/`fastmath` policy is fixed by
the vendored invariants and **MUST NEVER be edited for performance**. Kernels
that reduce across population members are compiled `fastmath=False` to preserve
the bit-identical-to-reference parity target; only per-individual,
order-insensitive kernels may use `fastmath=True`. If numba is unavailable the
module degrades gracefully (its `*_fast` exports become `None`).

1.3 **On-disk cache (`.nbc`/`.nbi`).** Every hot kernel is declared
`@njit(cache=True, ...)` (25 such kernels in `cec2017/_numba.py` alone), so Numba
writes a compiled-object cache (`.nbc`) and an index (`.nbi`) into the
`__pycache__` directory beside each kernel module on first compile. The cache is
keyed by source hash and Numba/LLVM version, so it is rebuilt automatically when
the kernel source or toolchain changes.
- You SHOULD let the cache populate naturally on the first warmed run.
- You **NEVER** delete, copy, or relocate the `.nbc`/`.nbi` cache of *another
  project or checkout* outside this repository root. Cache files are local
  build artifacts, not shared state; treat them as untracked and
  project-private.
- The Numba cache is not committed and **MUST NOT** be added to version control.

1.4 **Warmup hides compilation from timed runs.** First-call JIT compilation must
not inflate measurements. `runners/performance.py:warm_benchmark_cells` imports,
loads, and evaluates each cell once (probing the bound midpoint) to trigger data
load and kernel compilation before the timed loop. In the process backend each
spawned worker also warms the first cell once in `_init_process_worker`
(`run_experiment.py`).
- Enable with `--warmup`; scope with `--warmup-scope {selected|suite}`.
- You **MUST** warm what you measure and only that: warming the whole suite for a
  few-cell campaign inflates setup time without improving the timed numbers. Use
  `--warmup-scope selected` (the default-style choice) unless you genuinely run
  the full suite grid.
- Warmup timings land in `profile.json` as `benchmark_warmup`,
  `benchmark_warmup_seconds_total`, and `warmup_scope`.

---

## 2. Thread pinning for byte-stable determinism

This is the most important rule in this document for the proposed method.

2.1 **Why single-threaded math is required.** `dt-gsk` runs heavier internal
machinery as dimension grows: at **D >= 50** it activates `prange`/SGSM parallel
kernels, and at **D >= 100** it adds the TERRA / SP-NLPSR controllers (overlay
thresholds described in the `build_pub_config` profile and confirmed by the
committed reference logs). Floating-point reductions whose *summation order*
depends on how many threads split the work will drift bit-for-bit across machines
and runs. Byte-stable determinism therefore requires the BLAS/OpenMP/Numba math
layers to run **single-threaded** so reduction order is fixed. This is thread
pinning.

2.2 **The pinning environment.** The byte-stable dt-gsk environment — captured
in the produced run metadata (`results/_run_all/dt-gsk/<suite>/summary/environment.json`
and the per-dimension run logs) — pins **all six** math-thread variables to `1`:

```
OMP_NUM_THREADS=1
MKL_NUM_THREADS=1
OPENBLAS_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1
NUMEXPR_NUM_THREADS=1
NUMBA_NUM_THREADS=1
```

- For any **byte-identity** dt-gsk run (regression parity, reproducing the
  committed reference numbers, or a serious campaign whose numbers must match),
  you **MUST** export these six variables to `1` in the launching shell *before*
  Python imports numpy/numba, and you **MUST** run single-process (`--serial`) or
  with `--workers 1` so no second axis of parallelism reorders the math.
- These are process-environment variables. Several (notably `OMP`/`MKL`/
  `OPENBLAS`/`VECLIB`/`NUMEXPR`) are read by their libraries *at import time*, so
  setting them after import has no effect — set them in the shell, not in Python.

PowerShell:

```powershell
$env:OMP_NUM_THREADS=1; $env:MKL_NUM_THREADS=1; $env:OPENBLAS_NUM_THREADS=1
$env:VECLIB_MAXIMUM_THREADS=1; $env:NUMEXPR_NUM_THREADS=1; $env:NUMBA_NUM_THREADS=1
python run.py --root . --optimizer dt-gsk --suite cec2017 --serial
```

2.3 **How the runner manages Numba threads.** Within a run, the runner controls
*Numba's* thread count programmatically (it cannot retroactively change the
import-time BLAS variables — those are the launcher's responsibility per 2.2):
- `runners/performance.py:configure_numba_runtime` resolves the Numba thread
  count. With `--numba-threads N` (`numba_threads` in config, default `0` = auto)
  it sets exactly `N`. In auto mode under external parallelism it caps Numba to
  roughly `logical_cores // workers` (mode `auto_parallel_cap`) so
  `workers x numba_threads` stays within the core budget; otherwise it leaves
  Numba at its default.
- Each spawned process worker then calls `numba.set_num_threads(...)` in
  `_init_process_worker` to the resolved per-worker value.
- The active state is printed (`format_numba_runtime_line`) and recorded in
  `environment.json`/`profile.json` under `numba_runtime`.

2.4 **Rules.**
- For a byte-identity dt-gsk run, set the six env vars to `1` **and** pass
  `--numba-threads 1` (or rely on `--serial`/`--workers 1` driving the auto cap
  to 1). NEVER trust an unpinned shell for parity work.
- For exploratory throughput on the cheaper optimizers / low dims, you MAY leave
  the env unset and let the auto cap manage Numba threads.
- NEVER assume thread count is irrelevant for dt-gsk at D >= 50 — it is the
  difference between a byte-stable result and a silent parity drift.

2.5 **The floating-point-regime sentinel (`runners/fp_regime.py`).** Thread
pinning fixes reduction order *within* a run; the FP-regime sentinel fixes the
numba-JIT floating-point regime *across* a campaign. Under memory pressure numba
can silently fall back to its object/interpreter path for some cells, which
splits a campaign's floating-point regime and makes cross-campaign deltas
untrustworthy. `fp_regime.py` is a **fail-closed SHA-256 sentinel**: it records
the active FP regime as a hash and halts (rather than silently proceeding) when a
later cell would run under a different regime. The mechanism is documented in
[docs/reference/fp_regime.md](docs/reference/fp_regime.md).

- **MUST** run paired campaign arms (the two sides of any cross-campaign delta —
  e.g. Numba-on vs Numba-off, or two configurations you intend to diff)
  **sequentially, never two in parallel.** Concurrent arms can land in different
  numba-fallback states and split the FP regime between them.
- **MUST** verify, before trusting any cross-campaign delta, that the paired arms
  carry **matching FP-regime sentinels** and show **zero guard-cell differences**.
  A sentinel mismatch means the two arms are not comparable — a regime artifact,
  not an algorithmic effect (compare the cautionary regime-mismatch example in
  [BENCHMARK_RULES.md](BENCHMARK_RULES.md) §5).
- **NEVER** disable or bypass the sentinel to "get a run through." A fail-closed
  halt is protecting evidence integrity ([PROJECT_RULES.md](PROJECT_RULES.md) §3).

---

## 3. Parallel execution model

3.1 **Backends.** Independent cells (`optimizer, suite, function, dimension, run`)
are the unit of parallelism. Selectable via `--parallel-backend`:
- `process` (default): a reused `ProcessPoolExecutor` over the spawn context —
  true multi-core, no GIL contention. **The only correct choice for real
  campaigns.** Tiny runs (estimated task count not greater than the worker count)
  fall back in-process to avoid spawn overhead.
- `thread`: a `ThreadPoolExecutor`. The optimizer loop is Python/NumPy and holds
  the GIL, so it does not scale for CPU-bound work; worse, calling
  `parallel=True` Numba kernels from many threads can **deadlock**. You **NEVER**
  use `--parallel-backend thread` for a real CEC/Numba campaign — use the process
  backend, or `--serial` for a single clean process.

3.2 **Self-healing process pool.** `run_experiment.py` wraps each cell's dispatch
in a recovery loop: if a worker dies (intermittent Numba/spawn crash, or OOM) it
detects the `BrokenProcessPool`, tears the pool down, and rebuilds it, retrying
up to `max_pool_rebuilds = 3` times. If failures persist it runs that one cell on
the reliable **serial** backend, then rebuilds a fresh pool for the next cell — so
the campaign always completes. The recovery path **NEVER** falls back to the
thread backend (parallel Numba kernels can hang when driven from many threads).
This is by design and **MUST NOT** be "simplified" away.

3.3 **Flags.**
- `--parallel` / `--serial` enable/disable parallel execution (`--parallel` and
  `--serial` are mutually exclusive). Parallel is the default; `--serial` is the
  simplest way to get a clean stack trace and is the reference point for the
  byte-identity check.
- `--workers N` sets the process worker count. The automatic default is
  **conservatively 2** (`DEFAULT_WORKER_COUNT = 2` in `runners/parallel.py`;
  `default_worker_count` returns `min(2, cores)`, i.e. 1 on a single-core box).
  This keeps a copied command from saturating a shared workstation.
- You SHOULD start campaigns at `--parallel --workers 2` and raise the worker
  count **deliberately**, only after confirming spare CPU **and** RAM.

3.4 **Automatic CEC2017 composition cap.** CEC2017 composition cells (`F21`–`F30`)
JIT-compile heavy Numba/LLVM kernels; letting too many automatic workers compile
them at once can exhaust LLVM memory. `effective_worker_count` therefore caps
*automatic* CEC2017 `F>=21` cells to `DEFAULT_CEC_PROCESS_WORKER_CAP = 8`
effective workers. The default of 2 is already below this guard; an **explicit**
`--workers N` is respected as the user's chosen tradeoff and is recorded
(`worker_cap_applied`, `worker_cap_functions`, `worker_cap_workers`).

3.5 **Nested-thread control.** Two axes of parallelism multiply: external workers
x internal Numba/BLAS threads. The runner caps Numba per-worker (Section 2.3) to
keep the product within the core budget. When you raise `--workers`, lower or pin
Numba accordingly — do not let `workers x numba_threads` exceed logical cores, or
the run thrashes and slows down.

---

## 4. Memory rules

4.1 **One optimizer at a time when tight.** A full `--all-optimizers` sweep keeps
several optimizers' artifacts and JIT state cycling. On a memory-constrained
machine, run a single `--optimizer <id>` at a time; results are written
incrementally (Section 5) so splitting a sweep across separate invocations loses
nothing.

4.2 **The conservative worker cap bounds peak memory.** Peak RAM scales with the
number of concurrently spawned workers (each re-imports the stack and may compile
JIT kernels). The default of 2 workers and the 8-worker CEC2017 composition cap
exist primarily as **memory** guards, not just CPU guards. Raise `--workers` only
with headroom to spare.

4.3 **Large dimensions are expensive.** `cec2013lsgo` uses native dimensions of
**D=1000** (F1–F12, F15) and **D=905** (F13–F14) — these are by far the most
memory- and time-expensive cells in the project. Native-dimension `cec2011`
problems and `dt-gsk` at **D=50 / D=100** are the next-heaviest. For these:
- Prefer fewer workers (often `--workers 1` or `--serial`) so a single large cell
  is not multiplied by concurrency.
- Use reduced budgets / fewer runs to scope a trial before committing to a full
  campaign.

---

## 5. Incremental persistence and resume

5.1 **Results are written per cell, not at the end.** As each `(function,
dimension)` cell finishes, the runner flushes `per_run.csv`, the convergence
curves and checkpoint logs (`write_curves_and_logs`), the reproduced summary
tables (`write_summary_tables`), and the per-dimension reference-style summary /
run-log artifacts. An interrupted campaign therefore keeps **every completed
cell** on disk.

5.2 **Resume by omitting `--overwrite`.** On restart the runner reads the existing
`per_run.csv` and skips any cell whose `(function, dimension, run, seed)` is
already present, logging `[resume] skipped N already completed run task(s)`. So:
- To **resume** an interrupted campaign: re-run the same command **without**
  `--overwrite`. Completed cells are skipped; only missing cells run.
- `--overwrite` discards prior per-run rows and recomputes from scratch. Use it
  only when you intend to replace results — NEVER as a habitual flag, or you
  throw away recoverable work.
- Resume relies on the seed schedule being stable. Determinism (the unified seed
  policy, see [BENCHMARK_RULES.md](BENCHMARK_RULES.md)) is what makes skip-by-seed
  correct; do not change seed inputs mid-campaign.

---

## 6. Budgets and runtime expectations

6.1 **Per-suite budgets (the cost ceiling per run).**

| Suite       | Budget (NFEs)             | Dimensions                      |
|-------------|---------------------------|---------------------------------|
| cec2017     | `10000 * D`               | D = 10 / 30 / 50 / 100          |
| cec2011     | `150000` (fixed)          | native, per-problem (22 probs)  |
| cec2013     | suite default             | 10 / 30 / 50                    |
| cec2020     | suite default             | 5 / 10 / 15 / 20                |
| cec2013lsgo | suite default             | native D=1000 / D=905           |
| sphere      | suite default             | 10                              |

CEC2017's scored set excludes F2 (F1, F3–F30), 51 runs. CEC2011 uses native
per-problem dimensions and heterogeneous per-dimension bounds, ~25 runs. Budgets
and run counts are fixed by protocol and **MUST NOT** be changed for speed; see
[BENCHMARK_RULES.md](BENCHMARK_RULES.md).

6.2 **Where the time goes.** `dt-gsk` at **D=50 and D=100 is the slow part** of
any campaign: the SGSM overlay (D >= 50) and TERRA/SP-NLPSR controllers (D >= 100)
do substantially more per-generation work than the lighter GSK-family
comparators. The reference D100 CEC2017 logs are visibly the longest. Plan wall
time around these cells, not around the cheap D10 sweeps. Budget large
`cec2013lsgo` runs separately.

---

## 7. Measurement, profiling, and honest reporting

7.1 **Profiling artifacts.** `--profile` writes
`results/_run_all/<optimizer>/<suite>/summary/profile.json` with: `parallel` /
`parallel_backend`; `workers` / `workers_auto` / `workers_requested` /
`workers_effective`; the `worker_cap_*` fields; `tasks_dispatched` /
`tasks_completed` / `tasks_skipped_or_failed`; `optimizer_wall_seconds`;
`benchmark_warmup*` and `warmup_scope`; `numba_runtime`; the benchmark backend /
FP mode; and `run_runtime_seconds` keyed by `function, dimension, run, seed`.
Every run also writes `environment.json` (Python version, CPU cores, platform,
git commit, timestamp, `runtime_seconds_total`, `numba_runtime`, worker
metadata). The `Time/s` column in the console summary tables is the **wall-clock
time per (function, dimension) cell**, not the sum of per-run times.

7.2 **Timing is diagnostic only.** Wall-clock timing **MUST** be treated as
diagnostic: it is *not* intended to reproduce reference (MATLAB/C++) wall-clock
times — the Python port uses different libraries, process startup, and
local-search implementations. Use `profile.json` to compare configurations on the
**same machine**, never to make cross-toolchain speed claims.

7.3 **Never invent benchmarks.** You **NEVER** fabricate, estimate, or
extrapolate a runtime/throughput number. Report only what was measured, name the
machine and configuration (the `environment.json` provenance), and state the
config explicitly. The performance reference
([docs/research/performance.md](docs/research/performance.md)) keeps an explicit
"remaining measurement work" table of comparison reports (reference-vs-Python,
Numba-on-vs-off, vectorized-vs-not, single-thread-vs-parallel) that are still
pending full campaigns — **MUST** leave that gap honestly stated rather than
filling it with guessed figures. Fabricating numerical or convergence data
violates [PROJECT_RULES.md](PROJECT_RULES.md).

7.4 **Optimize without changing numbers.** Any performance change — vectorizing a
loop, adjusting a worker default, enabling a kernel — MUST be validated against
the determinism gates (config KAT, RNG KAT, the dt-gsk byte-stable regression)
before it is accepted. If a "faster" path changes a single produced value, it is
a regression, not an optimization. See [CODING_STANDARD.md](CODING_STANDARD.md)
for the gate commands and the vectorization conventions.
