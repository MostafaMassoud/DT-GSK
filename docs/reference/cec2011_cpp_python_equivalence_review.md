# CEC2011 C++ vs Python Equivalence Review

## Scope

This review compares the CEC2011 C++ reference implementation against the
Python evaluator in `benchmarks/cec_suite_python/cec2011`. The optimizer logic
is out of scope except where benchmark behavior affects optimizer results.

Reference sources reviewed:

- `benchmarks/cec_suite_cpp/cec2011/src/cec2011_problems_a.cpp`
- `benchmarks/cec_suite_cpp/cec2011/src/cec2011_problems_b.cpp`
- `benchmarks/cec_suite_cpp/cec2011/src/cec2011_problems_c.cpp`
- `benchmarks/cec_suite_cpp/cec_tools/tests/data/cec2011_expected.csv`
- `benchmarks/cec_suite_cpp/cec_tools/tests/data/cec2011_points_F*.txt`
- `benchmarks/cec_suite_cpp/cec_tools/tests/data/cec2011_bounds.txt`

(Reference paths are relative to the migration source archive, which is not part
of this repository — the C++ trees were the porting inputs, retained here as
provenance, consistent with the other four equivalence reviews.)

Python sources reviewed:

- `benchmarks/cec_suite_python/cec2011/functions.py`
- `benchmarks/cec_suite_python/cec2011/problems_basic.py`
- `benchmarks/cec_suite_python/cec2011/problems_antenna.py`
- `benchmarks/cec_suite_python/cec2011/problems_power.py`
- `benchmarks/cec_suite_python/cec2011/problems_hydrothermal.py`
- `benchmarks/cec_suite_python/cec2011/problems_spacecraft.py`
- `benchmarks/cec_suite_python/cec2011/orbital_mechanics.py`
- `benchmarks/cec_suite_python/cec2011/_numba.py`

## Suite Protocol Context

The benchmark adapter registers CEC2011 in
`src/gsk_family/benchmark_adapter/protocol.py`:

- 22 real-world problems (`function_ids = 1..22`), each at a fixed native
  dimension (`default_dimensions = "native"`). The per-function dimensions in
  the mapping table below are taken directly from `_FUNCTION_DIMS` in
  `functions.py` and were re-verified against it (all 22 match).
- Raw-objective statistics: CEC2011 is a member of
  `RAW_OBJECTIVE_SUITES = {cec2011, cec2013lsgo}`, so the adapter reports the
  raw objective with no subtracted optimum. Accordingly `problem.optimum` is
  `NaN` and `problem.target_error` is `NaN` (these problems have no published
  global optimum; `functions.py` documents `f*(F_i) = 0.0` only as a nominal
  label). This is asserted by
  `test_native_raw_objective_suites_use_nan_optimum_and_no_target` in
  `tests/unit/test_benchmark_adapter.py`.
- CEC2011 is one of the three suites that carry committed reference evidence
  under `benchmarks/cec_reference_results/cec2011/` (alongside CEC2013 and
  CEC2017); the other two in-code CEC suites — CEC2013LSGO and CEC2020 — do not.

This review therefore checks *evaluator* parity — objective values, bounds, and
the NaN/degenerate quirks — which is what the optimizer sees on every call.

## Function Mapping

| Function | Native D | Python evaluator | Reference work package | Review result |
|---:|---:|---|---|---|
| F01 | 6 | `f01_fm_sound` | A | Probe-match |
| F02 | 30 | `f02_lennard_jones` | A | Fixed: zero-distance NaN behavior |
| F03 | 1 | `f03_bifunctional_catalyst` | A | Fixed: reference RK45 path |
| F04 | 1 | `f04_stirred_tank` | A | Probe-match |
| F05 | 30 | `f05_tersoff_sib` | A | Probe-match |
| F06 | 30 | `f06_tersoff_sic` | A | Probe-match |
| F07 | 20 | `f07_spread_spectrum` | A | Probe-match |
| F08 | 7 | `f08_tnep` | A | Probe-match |
| F09 | 126 | `f09_energy_brokerage` | B | Probe-match |
| F10 | 12 | `f10_antenna_array` | A | Fixed: endpoint tie behavior |
| F11 | 120 | `f11_dynamic_eld_5unit` | B | Probe-match |
| F12 | 240 | `f12_dynamic_eld_10unit` | B | Probe-match |
| F13 | 6 | `f13_static_eld_6unit` | B | Probe-match |
| F14 | 13 | `f14_static_eld_13unit` | B | Probe-match |
| F15 | 15 | `f15_static_eld_15unit` | B | Probe-match |
| F16 | 40 | `f16_static_eld_40unit` | B | Probe-match |
| F17 | 140 | `f17_static_eld_140unit` | B | Probe-match |
| F18 | 96 | `f18_hydrothermal_case1` | B | Probe-match |
| F19 | 96 | `f19_hydrothermal_case2` | B | Probe-match |
| F20 | 96 | `f20_hydrothermal_case3` | B | Probe-match |
| F21 | 26 | `f21_messenger` | C | Probe-match |
| F22 | 22 | `f22_cassini_huygens` | C | Probe-match |

## Findings And Fixes

### F02 Lennard-Jones

Severity: High.

The Python evaluator clamped zero inter-atomic distances to `1e-15`. The C++
reference intentionally does not guard this case: coincident atoms produce
`Inf - Inf`, yielding `NaN`, and the final CEC2011 wrapper maps objective
`NaN` to `0.0`.

Fix:

- Removed the zero-distance clamp.
- Preserved divide/invalid floating-point behavior with `np.errstate`.
- Existing dispatcher-level `NaN -> 0.0` handling now produces the reference
  value for degenerate vectors.

### F03 Bifunctional Catalyst

Severity: Medium.

The Python evaluator used SciPy RK45. The C++ reference uses a restricted
reference-compatible Dormand-Prince RK5(4) path with the same controller,
step-size rules, and tolerances used by the reference code. SciPy’s adaptive
decisions caused small but measurable probe differences.

Fix:

- Added `_bifunctional_catalyst_nb` in `_numba.py`.
- Routed F03 through that path when Numba is available.
- Kept the SciPy fallback for environments without Numba.

### F10 Circular Antenna Array

Severity: Medium.

The vectorized Python array-factor sweep produced a tiny endpoint difference
at 360 degrees for a symmetric probe. That changed whether the endpoint was
classified as a side lobe. The C++ reference computes endpoints with scalar
summation order.

Fix:

- Added `_array_factor_scalar`.
- Kept the fast vectorized sweep for normal grid computation.
- Recomputed the 0-degree and 360-degree endpoints with scalar reference order.
- Evaluated the two null-control angles through the same scalar helper.

### Committed Regression Guards

The full 66-probe oracle sweep and the 22-row bounds check (see *Validation
Results*) were run against the external migration-source C++ archive, which is
not committed to this repository. The reproducible in-repo guards for the three
fixes above are two unit tests in `tests/unit/test_benchmark_adapter.py`, which
hard-code the reference values:

- `test_cec2011_f4_f6_match_reference_probe_values` — F04 probes (e.g.
  `cec2011_func(4, [2.5]) == 29.042242154614943`, `rel=1e-12`) and the F05/F06
  Tersoff degenerate-vs-`q1` values.
- `test_cec2011_f2_f3_f10_match_reference_probe_values` — guards the three
  quirks found by this review:
  - **F02 (NaN → 0.0):** the coincident-atom vector
    `[2, 2, pi/2, 0, ..., 0]` produces `Inf - Inf → NaN` after the zero-distance
    clamp was removed, and the dispatcher's `NaN → 0.0` rule (documented at
    "The CEC2011 reference wrapper maps objective NaN to zero" in `functions.py`)
    yields `cec2011_func(2, x) == 0.0`.
  - **F03 (reference RK path):** `cec2011_func(3, [0.75]) ==
    1.7423862846074083e-05` (`rel=1e-12, abs=1e-15`).
  - **F10 (endpoint tie):** `cec2011_func(10, [0.6]*6 + [0.0]*6) ==
    -7.5468782284276479` (`rel=1e-12`).

The bounds-mutation contract is covered by
`test_cec2011_bounds_are_copied_into_mutable_problem_arrays`.

## Wrapper And Bounds Review

The dispatcher behavior was reviewed for:

- Function ID routing.
- Native dimensions.
- Bounds.
- Single-vector and batch input shape handling.
- Raw objective statistics.
- Final `NaN -> 0.0` objective behavior.

Result:

- All 22 bounds entries matched `cec2011_bounds.txt`.
- All 66 fixed C++ oracle probes matched after fixes.

## Validation Results

Commands run from the project root (at the time of the review, an earlier
project location):

```powershell
python -m ruff check benchmarks\cec_suite_python\cec2011\_numba.py benchmarks\cec_suite_python\cec2011\problems_basic.py benchmarks\cec_suite_python\cec2011\problems_antenna.py tests\unit\test_benchmark_adapter.py
```

Result:

```text
All checks passed.
```

```powershell
python -m pytest tests\unit\test_benchmark_adapter.py tests\smoke\test_runner_smoke.py -q
```

Result:

```text
32 passed
```

Full C++ oracle probe comparison (against the external migration-source
archive; the oracle CSV and points files are not committed to this repository —
see *Committed Regression Guards* above for the in-repo subset):

```text
checked=66 failures=0
```

Bounds comparison (against `cec2011_bounds.txt` in the same external archive):

```text
checked_bounds=22 failures=0
```

CLI smoke check:

```powershell
python run.py --root . --optimizer gsk --suite cec2011 --function 2,3,10 --runs 2 --max-evaluations 200 --parallel --workers 2 --output-root results/_diagnostics/cec2011_cpp_python_review_smoke --overwrite
```

Result:

```text
PASS GSK
```

The smoke run used only 200 evaluations and 2 runs, so its comparison table is
an execution check, not a publication-quality optimizer comparison.

## Final Conclusion

The Python CEC2011 evaluator is now equivalent to the reviewed C++ reference
for the committed fixed-vector oracle:

- 22/22 functions have matching bounds.
- 66/66 C++ probe values match.
- The known reference quirks are protected by regression tests.
- Remaining exactness risk is limited to environments without Numba, where F03
  falls back to SciPy RK45 and may not be probe-identical.
