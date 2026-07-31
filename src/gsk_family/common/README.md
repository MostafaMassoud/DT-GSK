# Common Helpers

This package contains shared reference-compatible behavior used by multiple
optimizers.

## Files

| File | Purpose |
|---|---|
| `bounds.py` | GSK midpoint bounds repair. |
| `donors.py` | Junior and senior gained-sharing donor index helpers. |
| `numeric_compat.py` | Reference-compatible rounding, sorting, shape, and index helpers. |
| `population.py` | Population initialization and fair-start handling. |
| `reduction.py` | Adaptive population reduction helper. |
| `reference_rng.py` | Reference-matching `twister` (MT19937) and `seed` (mcg16807) generators. |
| `rng.py` | Random context, generator mapping, and fair-start payloads. |
| `threefry_rng.py` | Counter-based Threefry-4x64-20 generator matching the reference stream bit-for-bit. |

Keep algorithm-specific behavior in optimizer modules. Put shared numerical
semantics here when more than one optimizer uses them.
