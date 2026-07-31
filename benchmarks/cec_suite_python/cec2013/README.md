# CEC2013 Python Benchmark Suite

Pure Python/NumPy implementation of the IEEE CEC2013 single-objective
real-parameter benchmark suite.

## Role

CEC2013 is an external hold-out suite (library-only in the current campaigns).

Paper settings:

- D=10, 30, 50.
- n=51 independent runs.
- budget = 10000 * D evaluations.
- no function exclusions.

CEC2013 supports D=100 internally, but D=100 is not part of the paper hold-out
tables because public GSK-family reference baselines are unavailable for that
cell.

## Function Groups

| Range | Type | Count |
|---|---|---:|
| F1-F5 | unimodal | 5 |
| F6-F20 | multimodal | 15 |
| F21-F28 | composition | 8 |

Optimal values follow the CEC2013 bias convention:

```text
f*(F_i) = -1400 + 100*(i-1)
```

The search domain is `[-100, 100]^D` for all functions.

## Supported Dimensions

D in {2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100}.

## Implementation Map

```text
cec2013/
  __init__.py
  functions.py
  basic.py
  simple.py
  composition.py
  transforms.py
  _numba.py          # batch JIT kernels: 19 parallel=True formula/transform
                     #   kernels + 2 deliberately parallel-free ones
                     #   (osz_func_nb / asy_func_nb).  No fastmath anywhere
                     #   (audit M-03).
  _numba_serial.py   # serial (parallel=False) twins of all 21 batch kernels —
                     #   skip the parallel-launch tax on single-row dispatches
                     #   (BIT-IDENTICAL to the batch kernels: no fastmath in
                     #   this suite, so there is no reassociation fork)
  _kernel_mode.py    # suite-local thread-local switch that routes an opted-in
                     #   optimizer's evaluations to the serial twins (default
                     #   off)
  make_data_pkl.py
  data.pkl
```

## Performance Notes

- Per-suite Numba kernels cover hot base-function and transform paths.
- Asymmetry indices and composition constants are cached.
- Rotation matrices are cached and transposed for repeated batch evaluation.

## Serial-Kernel Notes

Suite mirror of the CEC2017 serial-twin design — see
`cec2017/_numba_serial.py` for the full rationale.

- A CEC2013 evaluation runs a *pipeline* of kernels (conditioning + a formula
  core for the simple functions; up to 5 components x 2-3 kernels for
  F21-F28), so the numba parallel-runtime launch is paid several times per
  call and dominates single-row dispatches: measured 113-1121 us/FE (batch=1,
  16 threads) versus 4-49 us/FE on the twins.
- `_numba_serial.py` re-jits the same `py_func` objects with `parallel`
  dropped and `cache=False` (a `cache=True` re-jit silently reloads the
  PARALLEL artifact); `_kernel_mode.py` holds the thread-local switch, which
  is independent of the other suites' switches.
- `osz_func_nb` / `asy_func_nb` are already `parallel`-free, so their "twin"
  is the batch dispatcher itself and their call sites are not mode-routed.
- Parity: exhaustive sweep of 28 functions x D in {10, 30, 50} x 256 rows gave
  **0 ULP / 0.0 relative difference everywhere**.
- Opt in per optimizer via the campaign config's `serial_kernel_optimizers`
  allowlist; `make_problem(..., serial_kernels=True)` appends a
  "Serial-kernel" marker to the problem notes for provenance.
