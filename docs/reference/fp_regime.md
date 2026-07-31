# Floating-Point Regime Verification

> **What this page is.** The reference for the project's floating-point-regime
> guard — why it exists, the failure it prevents, the fail-closed sentinel
> contract, and the operational rules that make paired benchmark comparisons
> trustworthy.
>
> **Who it is for.** Anyone running paired campaigns, comparing results across
> runs, or auditing reproducibility for a paper or release.
>
> **Prerequisites.** Determinism basics are in
> [Reproducibility](../research/reproducibility.md); parallel-execution
> mechanics are in [Performance](../research/performance.md).

## 1. The failure this prevents

Every JIT kernel module in this project guards its `import numba` and silently
degrades to a pure-NumPy fallback when that import fails
(`optimizers/_dt_subsystems/_numba_accel.py`,
`benchmarks/cec_suite_python/*/_numba.py`, `common/threefry_rng.py`,
`common/reference_rng.py`, `optimizers/_kernels.py`). numba/llvmlite imports can
fail **transiently under memory pressure** — a spawn-storm of many parallel
workers each importing numba at once on a loaded machine can raise
`ImportError`, `OSError`, or a partial-import
`AttributeError: module 'numba' has no attribute 'core'`.

A worker that hits this at bootstrap runs its **entire life** with NumPy-fallback
kernels. Fallback results are deterministic but **not bit-identical** to the JIT
(fastmath) kernels — reassociated reductions and different SIMD lowering move the
last bits. Such a worker is therefore in a second, internally-consistent
**floating-point regime**: on chaotic/multimodal cells it deterministically
selects **different basins**. The damage is invisible in summary statistics and
single-run tests, and it silently poisons any **paired cross-campaign
comparison**.

**Bit-exact witness.** CEC2017 F20 D10, seed 54241459: the identical run finishes
at error `0.3121732559816` with the ISM acceleration kernel in fallback versus
error `0.0` (a different basin) in the fully-JIT regime — reproducibly in each
regime. In an affected wide campaign, ~17 % of runs diverged (only the tasks that
landed on the poisoned worker process(es)).

## 2. The fix: an explicit, verified, fail-closed contract

`runners/fp_regime.py` turns the regime into a recorded contract:

- **`canonical_fp_regime(suite)`** deterministically imports numba (with retry —
  a failed import is evicted from `sys.modules`, so a retry after `gc.collect()`
  can genuinely succeed), imports every kernel module and reads its JIT flag, then
  runs a fixed sequence of **thread-invariant probe kernels** (a Threefry draw,
  three ISM `*_fast` kernels, and the suite's probe cell — CEC2017 uses F20 D10)
  and hashes their outputs into a numeric **sentinel** (SHA-256).
- **`ensure_canonical_fp_regime(suite, expected_sentinel=None)`** fails closed:
  it raises `FPRegimeError` when any kernel module is in NumPy fallback, or when a
  provided sentinel does not match. A degraded process refuses to run rather than
  emit regime-2 numbers.

The runner calls it in the **parent** (covering serial and thread backends) and
in the process-pool **`initializer`** with the parent's expected sentinel; a
non-canonical or mismatched worker dies at spawn, and the existing pool-rebuild
logic retries and ultimately falls back to the parent's verified serial backend.
A campaign can no longer mix regimes by construction. The full `fp_regime`
payload — per-module JIT flags, numba/llvmlite versions, and the sentinel — is
recorded in each run's `environment.json`. This process-level JIT regime is
distinct from the evaluator-level `benchmark_fp_mode` knob described in §7.

**Probe invariants.** All probes are thread-count invariant (sequential kernels,
or `prange` kernels whose iterations are per-element/per-row independent), so a
worker capped at one numba thread computes the same sentinel as the parent
running the full pool. The sentinel hashes only numeric probe outputs, so **two
campaigns are FP-comparable exactly when their sentinels match**. It is
machine/build-specific (fastmath results depend on llvmlite/CPU-SIMD) — within
one machine+build the fully-JIT regime is a single sentinel.

## 3. Which regime the published evidence corresponds to

The fully-JIT regime (all kernel flags `True`): the byte-stability KAT golden
values and the committed reference results. The latter was verified empirically —
committed comparator references reproduce **bit-for-bit** (all summary statistics
to full precision, including the outlier-sensitive Worst/SD) under the fixed
runner on the worst-case chaotic cell (CEC2017 F20 D10). The recorded sentinel in
`environment.json` makes the regime verifiable per campaign.

## 4. The guard-cell validity check

The sentinel is the mechanism; the **guard-cell check is the empirical proof**.
When two paired arms include cells that must be identical by construction (e.g. a
control and a variant that is provably a no-op on those cells), a valid
comparison requires **both**: the two arms record the same sentinel, **and** they
show **zero differences** on the should-be-identical cells. If either fails, the
comparison is contaminated — discard and re-run. This is what first surfaced the
bug (34/87 should-be-identical guard cells differed → invalid → root-caused →
fixed).

## 5. Operational rules

1. **Never run two heavy campaign arms in parallel** — that doubles memory
   pressure and is the actual trigger. Run arms strictly sequentially; use
   parallelism *within* an arm (worker pool), not *across* arms.
2. **Worker count does not change results** (the sentinel is thread/worker
   invariant); it only changes memory pressure and thus fail-closed abort risk.
   If large/high-D cells abort, lower the worker count.
3. **Before trusting any cross-campaign paired delta**, confirm matching
   sentinels and zero guard-cell differences.
4. **Fail closed, never fall back silently** — a degraded process aborts (and is
   re-run) rather than emitting divergent numbers.

## 6. Tests

`tests/regression/test_fp_regime.py` locks the contract: fail-closed rejection
when a kernel is in fallback, sentinel determinism and thread invariance, and
process-order insensitivity of `dt-gsk` against the byte-stability golden value
(with and without a prior `create_fair_start`, refuting the call-order red
herring).

## 7. A distinct control: `benchmark_fp_mode` (evaluator summation order)

The sentinel above governs *which kernel implementation* a process runs (JIT vs
NumPy fallback). A second, orthogonal control governs *summation order inside the
CEC2017 objective* for a few order-sensitive functions. Do not conflate them.

`benchmark_fp_mode` is a run config field (default `default`; CLI
`--benchmark-fp-mode {default,strict}`), validated by
`normalize_benchmark_fp_mode` against `BENCHMARK_FP_MODES = ("default",
"strict")` in `benchmark_adapter/factory.py`. It is recorded in
`run_config.json` and `phase0_protocol.json`.

- **Scope.** Only the `cec2017` evaluator consumes it — the adapter passes
  `fp_mode` to `cec2017_func` and calls every other suite's evaluator without it,
  so `benchmark_fp_mode` is a no-op for `cec2011`, `cec2013`, `cec2013lsgo`,
  `cec2020`, and `sphere`.
- **What `strict` does.** For the order-sensitive functions
  `_STRICT_FP_FUNCTIONS = {1, 12, 13}` (F1, F12, F13), `cec2017_func` evaluates
  them with `strict_fp=True`, routing through fixed-order, non-`fastmath`
  "strict" kernel variants (a strict bent-cigar and strict shift-rotate) so the
  summation order is deterministic and independent of SIMD lowering / `fastmath`
  reassociation. `default` uses the ordinary `fastmath` kernels. Other CEC2017
  functions are unaffected by the mode.
- **Relationship to the sentinel.** The two are independent: the sentinel pins
  the JIT regime for the *whole process*; `benchmark_fp_mode` selects a
  summation-order variant *within the CEC2017 objective*. Recording both in the
  run metadata makes a campaign's floating-point handling fully described.

The committed reference results were produced under `benchmark_fp_mode=default`
(recorded in every reference `run_config.json`), so that is the mode a
reproduction should use to match them.
