# CEC2020 Python Benchmark Suite

Pure Python/NumPy implementation of the IEEE CEC2020 bound-constrained
single-objective benchmark suite.

## Role

CEC2020 is a context suite.  It is importable, tested, and runnable through the
runner (`scripts/run_all_cec2020.py`, `configs/agsk_cec2020.yml`); the imported
reference panel carries AGSK only, so the suite stays outside the main
7-optimizer paper comparison.

## Function Groups

| Range | Type | Count |
|---|---|---:|
| F1 | unimodal | 1 |
| F2-F4 | multimodal | 3 |
| F5-F7 | hybrid | 3 |
| F8-F10 | composition | 3 |

Bias convention:

```text
F1=100, F2=1100, F3=700, F4=1900, F5=1700,
F6=1600, F7=2100, F8=2200, F9=2400, F10=2500
```

## Supported Dimensions

The runner-facing Python suite follows the staged CEC2020 C++/MEX protocol:

- Default supported dimensions are `D in {5, 10, 15, 20}`.
- F6 and F7 are **undefined at `D=5` by the protocol** (Yue et al. 2019 §2.1:
  "for F6 and F7, D = 10, 15, 20"). Permanently refused.
- F1 and F8 at `D=5`/`D=15` were **restored 2026-07-26** after validation
  against the in-repo C++ oracle (worst rel 1.258e-15 vs the committed 1e-12
  criterion; marker-invariance proven). Previously refused for lack of oracle
  ground truth -- the official distribution ships no shuffle availability-
  marker files for ids 1/22 at those dims, though the content is never
  consumed by them. Pins: `tests/regression/test_cec2020_restored_cells.py`.
- The Python dispatcher rejects unsupported cells up front so benchmark runs do
  not produce values for combinations that have no C++ reference ground truth.

## Implementation Notes

- CEC2020 basic functions do not bake in shrink rates; callers apply shrink
  through the transform pipeline.
- F4 Griewank-Rosenbrock uses `s_flag=0, r_flag=0`; the optimum is at x=0, not
  at the shift vector.
- Public F8-F10 map to staged-MEX internal ids 22, 24, and 25. The validated
  C++ oracle matches the CEC2017 composition kernels when evaluated with the
  CEC2020 internal-id data files, so the Python implementation reuses those
  audited kernels with explicit CEC2020 data overrides.
