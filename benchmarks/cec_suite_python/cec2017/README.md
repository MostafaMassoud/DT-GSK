# CEC2017 Python Benchmark Suite

Pure Python/NumPy implementation of the IEEE CEC2017 single-objective
real-parameter benchmark suite.

## Role

CEC2017 is the primary campaign benchmark suite.

Paper settings:

- D=10, 30, 50, 100.
- n=51 independent runs.
- budget = 10000 * D evaluations.
- F2 is excluded from aggregate comparisons because the CEC2017 organizers
  deprecated it for numerical instability.

## Function Groups

| Range | Type | Count |
|---|---|---:|
| F1-F3 | unimodal | 3 |
| F4-F10 | multimodal | 7 |
| F11-F20 | hybrid | 10 |
| F21-F30 | composition and composition-of-hybrids | 10 |

Bias convention: `f_i* = i * 100`.

## Supported Dimensions

- F1-F10 and F21-F28: D in {2, 10, 20, 30, 50, 100}.
- F11-F19: D in {10, 30, 50, 100}.
- F20: D in {10, 20, 30, 50, 100}.
- F29-F30: D in {10, 30, 50, 100}.

## Reference-Compatibility Notes

- F14 and F20 emulate the C++ Schaffer F7 global-buffer quirk.
- F8 follows the reference behavior where the step modification is overwritten
  by the transform path.
- F9 Levy uses `w = 1 + (z - 1) / 4`, so the internal minimum is at z=1.
- Shift, rotation, and shuffle data are bundled in `data.pkl`.

## Implementation Map

```text
cec2017/
  __init__.py
  functions.py       # unified entry point for all 30 functions (cec2017_func)
  basic.py           # base benchmark functions (verified against cec17_func.cpp)
  simple.py          # F1-F10: shifted + rotated single base functions
  hybrid.py          # F11-F20: hybrid functions
  composition.py     # F21-F30: composition functions (cf01-cf10 + cf_cal)
  transforms.py      # transform layer: shift/rotation/shuffle data + caching
  utils.py           # visualization (surface_plot) and timing (time_batch) helpers
  data.pkl           # bundled shift, rotation, and shuffle data
  _numba.py          # batch JIT kernels (parallel=True): the 19 base-function
                     #   kernels + the shift/rotate transform
  _numba_serial.py   # serial (parallel=False) twins of the batch kernels —
                     #   skip the ~60 us/call parallel-launch tax on single-row
                     #   dispatches (fastmath parity rel<=3e-15, bit-identical
                     #   under strict fp)
  _kernel_mode.py    # thread-local switch that routes an opted-in optimizer's
                     #   evaluations to the serial twins (default off)
```

## Performance Notes

- Per-suite Numba kernels accelerate common base functions and transforms.
- Rotation matrices are cached and transposed for fast row-batch evaluation.
- Composition weights are vectorized in NumPy/Numba paths.
- Shuffle-group caching in `transforms.py` is guarded by data-root identity so
  F20 warmup cannot contaminate F29/F30 composition-hybrid shuffles.
