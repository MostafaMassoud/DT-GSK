# CEC2013-LSGO Python Benchmark Suite

Pure Python/NumPy implementation of the IEEE CEC2013 large-scale global
optimization (LSGO) benchmark suite.

## Role

CEC2013-LSGO is the large-scale arm of the publication campaign — one of the
three scored suites alongside CEC2017 and CEC2011.

Paper settings:

- 15 functions.
- D = 1000 native (F13-F14 use D = 905: 20 overlapping groups, overlap 5).
- n = 25 independent runs (`configs/family_cec2013lsgo.yml` /
  `configs/baselines_cec2013lsgo.yml`).
- budget = 3,000,000 evaluations per run.
- Optimal value `f* = 0` for every function; the runner records raw fitness
  (`statistics_basis = raw`).

## Function Groups

| Range | Type | D |
|---|---|---:|
| F1-F3 | fully separable (Elliptic, Rastrigin, Ackley) | 1000 |
| F4-F7 | partially separable: 7 rotated groups + 700-dim separable remainder | 1000 |
| F8-F11 | partially separable: 20 rotated groups, no remainder | 1000 |
| F12 | fully non-separable (Rosenbrock) | 1000 |
| F13-F14 | overlapping groups, conforming / conflicting (overlap = 5) | 905 |
| F15 | fully non-separable (Schwefel 1.2) | 1000 |

## Reference-Compatibility Notes

- Transform chains match the C++ reference `Benchmarks.cpp`: T_osz applies to
  **all** dimensions (unlike standard CEC2013, where it touches only the first
  and last elements), followed by T_asy and the Lambda ill-conditioning
  scaling, applied *inside* each base function.
- Shift vectors, permutation vectors, rotation matrices, group sizes, and
  weights are bundled in a SHA-256-verified `data.pkl`; regenerate it from the
  reference `cdatafiles/*.txt` with `make_data_pkl.py`.
- Each function's native dimension is enforced: requesting any other `D`
  raises (`benchmark_adapter/factory.py`).

## Implementation Map

```text
cec2013lsgo/
  __init__.py
  functions.py       # unified entry point for all 15 functions (cec2013lsgo_func)
  composite.py       # F1-F15 implementations; selects the batch or serial
                     #   kernel at every JIT call site via _kernel_mode
  basic.py           # six base functions with embedded LSGO transforms
  transforms.py      # data.pkl loading, T_osz/T_asy/Lambda, group infrastructure
  make_data_pkl.py   # one-shot cdatafiles/*.txt -> data.pkl converter
  data.pkl           # bundled shift/permutation/rotation/group data (SHA-256-verified)
  _numba.py          # 22 batch JIT kernels (parallel=True): fused single-pass
                     #   shift+transform+evaluate kernels for D=1000 (standalone
                     #   transforms, fused cores, shifted full-D, fused group,
                     #   fused separable-remainder); the 4 group kernels are
                     #   deliberately fastmath=False
  _numba_serial.py   # serial (parallel=False) twins of all 22 batch kernels —
                     #   skip the fixed parallel-launch tax on single-row
                     #   dispatches (group-kernel twins bit-identical by
                     #   construction; fastmath twins rel<=3e-15)
  _kernel_mode.py    # suite-local thread-local switch that routes an opted-in
                     #   optimizer's evaluations to the serial twins (default off)
```

## Serial-Kernel Notes

The suite mirrors the CEC2017 serial-kernel design (see
`cec2017/_numba_serial.py` for the full rationale, and
`docs/development/OPTIMIZER_PERFORMANCE_AUDIT.md`, "ROUND 3", 2026-07-17, for
the landing record):

- At `numba_threads: 1` every `parallel=True` kernel pays a fixed
  parallel-runtime launch per call (~45-135 us idle, up to ~300 us under
  campaign contention) — still 60-90% of a single-row evaluation even at
  D=1000. `_numba_serial.py` re-jits the same `py_func` objects with
  `parallel` dropped; `_kernel_mode.py` holds the thread-local switch, a
  deliberately separate flag from cec2017's so one suite's scope can never
  route the other suite's kernels.
- Numerical contract: the 4 hot group kernels are `fastmath=False`, so their
  twins are bit-identical (0 ULP) by construction; the fastmath twins carry
  the project's documented rel <= 3e-15 contract. The landing parity sweep was
  4,080/4,080 rows bitwise across all 15 functions x K in {1, 3, 30} (audit
  register, ROUND 3).
- In THIS project the twins are opt-in per problem via
  `make_problem(..., serial_kernels=True)` only; the runner has no
  `serial_kernel_optimizers` key and no campaign has ever enabled them. They
  were measured performance-neutral-to-negative here at every batch size
  (docs/development/PORT_05_TUNING_TRIAGE.md), so they exist for correctness
  tooling, not speed. The sibling project's per-optimizer opt-in history
  (odo/sgo-social/sns un-freeze) does not apply here.
- The FP-regime sentinel probes LSGO F1 through the default batch path and is
  untouched by construction.

**SNS row-exact resolver (sibling-project note; no consumer here).** In the
sibling project, constructing an LSGO problem with `serial_kernels=True`
appends a "Serial-kernel" marker to `problem.notes`, and its `sns` optimizer
keys on that marker to select `_resolve_iteration_rowexact`, a row-exact
dependency-wave resolver that evaluates exactly the counted NFE rows —
(`sns` does not exist in this project; nothing here consumes the marker) —
replacing, for serial-kernel problems only, the speculative whole-population
fixpoint that over-evaluates several times the counted NFE per iteration. The
resolver keys purely on the problem's "Serial-kernel" note, so since the
2026-07-17 un-freeze it applies wherever serial kernels are requested — now
including cec2017. Non-serial-kernel (batch-path) runs remain byte-untouched
(see the `sns.py` module docstring for the gate record).

## Performance Notes

- Fused single-pass kernels (shift + transforms + evaluate) eliminate the
  `M x 1000` intermediate allocations; `prange(M)` outer parallelism with
  sequential, cache-friendly inner loops over dimensions/groups.
- Fused group kernels process all 7-20 groups in one call: 3-7x for the group
  functions at D >= 905. Fused separable-remainder kernels read the 700-dim
  remainder directly through column indices: 1.8-3.2x for F4-F7.
- Serial-twin end-to-end gains at the ROUND 3 landing (F4, 30k NFE): toa 5.3x,
  saro 4.4x, ema 1.7x, gsk 1.5x (audit register, 2026-07-17).
- The campaign config also sets `telemetry_points: 256` (raw-log storage
  thinning) and `diversity_points: 256` (LSGO-only compute thinning of the
  per-generation O(N*D) diversity snapshot; protocol sign-off 2026-07-17) —
  see `configs/README.md`.
