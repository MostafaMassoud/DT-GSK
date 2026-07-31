# Optimizers

This package contains all implemented GSK family optimizer kernels. Seven
optimizers ship: `gsk`, `agsk`, `apgsk`, `fdb-agsk`, `atmals-gsk`, `egsk`, and
`dt-gsk`.

DT-GSK ships a single `pub` profile. The vendored, byte-locked core is
`_dt_core.py`, `_dt_subsystems/`, `_dt_rng.py`, and `_dt_profiles.py`;
these must not be modified.

## Files

| File | Optimizer Or Helper |
|---|---|
| `gsk.py` | Baseline GSK. |
| `agsk.py` | Adaptive GSK. |
| `apgsk.py` | Adaptive-parameters GSK. |
| `fdb_agsk.py` | Fitness-Distance Balance AGSK. |
| `fdb_scores.py` | FDB score helpers. |
| `atmals_gsk.py` | ATMALS-GSK. |
| `atmals_helpers.py` | ATMALS local helper functions. |
| `egsk.py` | EGSK (SLSQP-hybridized GSK; `scipy`-SLSQP substitutes the reference `fmincon`). |
| `dt_gsk.py` | DT-GSK (Dimension-Tiered GSK; this project's proposed method) — the `optimize()` adapter. |
| `_kernels.py` | Shared vectorized GSK update kernels. |
| `_dt_profiles.py` | DT-GSK dimension-aware `pub` profile (config tier builder). |
| `_dt_rng.py` | DT-GSK named-substream RNG layer. |
| `_dt_core.py` | DT-GSK core driver. |
| `_dt_subsystems/` | DT-GSK subsystems (vendored byte-for-byte from the source project). |

Every optimizer exposes:

```python
optimize(problem, options)
```

Algorithm-level documentation lives in `docs/algorithms/`.
