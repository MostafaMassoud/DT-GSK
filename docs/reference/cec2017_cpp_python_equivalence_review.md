# CEC2017 C++ vs Python Equivalence Review

## Scope

This review compares the CEC2017 C++ reference evaluator with the Python
implementation in `benchmarks/cec_suite_python/cec2017`. Optimizer logic is
out of scope except where benchmark evaluator behavior affects optimizer
results.

Reference sources reviewed:

- `benchmarks/cec_suite_cpp/cec2017/src/cec17_func.cpp`
- `benchmarks/cec_suite_cpp/cec2017/src/cec2017_problem.cpp`
- `benchmarks/cec_suite_cpp/cec2017/input_data/`
- `benchmarks/cec_suite_cpp/cec_tools/tests/data/cec2017_expected.csv`
- `benchmarks/cec_suite_cpp/cec_tools/tests/data/points_D10.txt`
- `benchmarks/cec_suite_cpp/cec_tools/tests/data/points_D30.txt`
- `benchmarks/cec_suite_cpp/cec_tools/tests/data/points_D50.txt`
- `benchmarks/cec_suite_cpp/cec_tools/tests/data/points_D100.txt`
- `benchmarks/cec_suite_cpp/cec_tools/tests/unit/cec2017_tests.cpp`

Python sources reviewed:

- `benchmarks/cec_suite_python/cec2017/functions.py`
- `benchmarks/cec_suite_python/cec2017/basic.py`
- `benchmarks/cec_suite_python/cec2017/simple.py`
- `benchmarks/cec_suite_python/cec2017/hybrid.py`
- `benchmarks/cec_suite_python/cec2017/composition.py`
- `benchmarks/cec_suite_python/cec2017/transforms.py`
- `benchmarks/cec_suite_python/cec2017/utils.py`
- `benchmarks/cec_suite_python/cec2017/_numba.py`
- `benchmarks/cec_suite_python/cec2017/data.pkl`

## Suite Protocol Context

The benchmark adapter registers CEC2017 in
`src/gsk_family/benchmark_adapter/protocol.py`, and it is the project's
**primary / development suite**:

- 30 implemented functions (`function_ids = 1..30`). The default comparison set
  is 29 functions — `default_function_ids = (1,) + (3..30)` — because F2 is
  excluded (see *Numerical And Wrapper Findings*); F2 stays constructible on
  explicit request. This is asserted by
  `test_cec2017_default_functions_exclude_f2_but_explicit_f2_is_constructible`
  in `tests/unit/test_benchmark_adapter.py`.
- Error-vs-optimum statistics (CEC2017 is a member of
  `ERROR_VS_OPTIMUM_SUITES = {cec2013, cec2017, cec2020}`), `target_error =
  1e-8`, and known optima `f* = 100 * func_id` (`cec2017_fopt` in
  `functions.py`; the F1 optimum `100.0` is asserted by
  `test_known_optimum_suites_use_error_statistics`).
- Runner dimensions `D ∈ {10, 30, 50, 100}`, all four of which carry committed
  reference evidence under `benchmarks/cec_reference_results/cec2017/`. CEC2017
  is one of the three suites with committed reference evidence (with CEC2011 and
  CEC2013).

## Function Mapping

| Functions | Category | Python modules | Reference data | Result |
|---|---|---|---|---|
| F01-F10 | Shifted/rotated simple functions | `simple.py`, `basic.py`, `transforms.py` | `shift_data_*.txt`, `M_*_D*.txt` | Oracle-match |
| F11-F20 | Hybrid functions | `hybrid.py`, `basic.py`, `transforms.py` | `shift_data_*.txt`, `M_*_D*.txt`, `shuffle_data_*_D*.txt` | Oracle-match |
| F21-F28 | Composition functions | `composition.py`, `basic.py`, `transforms.py` | composition shift and matrix stacks | Oracle-match |
| F29-F30 | Composition of hybrid functions | `composition.py`, `hybrid.py`, `transforms.py` | composition shifts, matrices, and 10-row shuffle data | Oracle-match |

Supported oracle dimensions reviewed: `D=10`, `D=30`, `D=50`, and `D=100`.

## Data Parity

The Python `data.pkl` bundle is SHA-256 checked by `transforms.py` before
deserialization. The loaded arrays are reconstructed from a custom array tuple
format and then marked read-only to prevent accidental mutation during a run.

Direct data checks against the C++ text files:

| Data kind | Checked items | Result |
|---|---:|---|
| Simple/hybrid shifts | 20 | Match |
| Composition shifts | 10 | Match |
| Simple/hybrid rotation matrices | 101 | Match |
| Composition rotation stacks | 58 | Match |
| Hybrid shuffle permutations | 41 | Match after one-based to zero-based conversion |
| Composition-hybrid shuffle permutations | 8 | Match after reshaping to `(10, D)` and one-based to zero-based conversion |

No data mismatch was found.

## Numerical And Wrapper Findings

The Python evaluator matched the C++ fixed-vector oracle from the external
migration-source archive (the `cec2017_expected.csv` oracle and `points_D*.txt`
files are not committed to this repository; the in-repo subset is the D10
zero-vector guard in *Regression Test Added*):

```text
checked=600 failures=0
max_rel=7.448e-15
```

The largest relative difference was:

```text
F03 D30 point 1
expected = 1088370639.4186068
got      = 1088370639.4186149
abs diff = 8.106231689453125e-06
rel diff = 7.448e-15
```

That difference is far below the C++ test tolerance of `1e-10` relative error.

Wrapper behavior reviewed:

- Function IDs `1..30` route correctly.
- Bounds are uniform `[-100, 100]^D`.
- Known optima are `100 * function_id`.
- Batch and scalar calls are both supported.
- Non-finite input is rejected at the dispatcher.
- F2 is implemented for evaluator parity but remains marked deprecated because
  the original competition reporting excluded it.
- The runner may exclude F2 in publication workflows, while the evaluator can
  still validate F2 against the C++ oracle.

## Regression Test Added

The committed guard is
`test_cec2017_d10_zero_vector_matches_cpp_oracle_all_functions` in
`tests/unit/test_benchmark_adapter.py`. It hard-codes the C++ oracle value for
every one of the 30 functions at the D10 zero vector and checks each with
`rel=1e-11`. For F2 it expects the `DeprecationWarning` while still checking the
numeric value. Two representative committed constants:

- **F01 (shifted-rotated Bent Cigar):**
  `cec2017_func(1, zeros(10)) == 29975432515.940056`.
- **F03 (shifted-rotated Zakharov):**
  `cec2017_func(3, zeros(10)) == 1343217.0396465289`.

The `rel=1e-11` test band is the in-repo guard; it is stricter than the `1e-10`
relative tolerance the external C++ harness applied to its own 600-probe sweep,
and comfortably above the observed `max_rel=7.448e-15` (below).

### Strict Fixed-Order Evaluation Mode

Unlike CEC2013, the CEC2017 evaluator ships an opt-in strict fixed-order
floating-point path. `make_problem("cec2017", ..., benchmark_fp_mode="strict")`
(valid modes are `BENCHMARK_FP_MODES = ("default", "strict")` in
`benchmark_adapter/factory.py`) routes the sensitive cells through a fixed-order
evaluator and stamps `"Strict fixed-order ..."` into `problem.notes`. This is
covered by `test_cec2017_strict_fp_mode_evaluates_sensitive_function`. It exists
to make the rotation/`libm` ordering deterministic when bit-stability matters
more than throughput.

## Validation Commands

Executed from the project root (at the time of the review, an earlier
project location):

```powershell
python -m pytest tests\unit\test_benchmark_adapter.py::test_cec2017_d10_zero_vector_matches_cpp_oracle_all_functions -q
```

Result:

```text
1 passed
```

Full external oracle comparison:

```text
checked=600 failures=0 max_rel=7.448e-15
```

Data parity comparison:

```text
checked_data_items=238 failures=0
checked_comp_hybrid_shuffles=8 failures=0
```

## Final Conclusion

The Python CEC2017 evaluator is equivalent to the reviewed C++ reference for
the committed fixed-vector oracle:

- 600/600 expected-value rows matched.
- All reviewed shift, rotation, and shuffle data matched the C++ input files.
- No evaluator code fix was required.
- A regression test was added to protect all 30 functions on a compact D10
  C++ oracle probe.

Residual risk is limited to ordinary floating-point implementation differences
below the validated tolerance. Optimizer-level result differences should be
investigated only after this evaluator-level oracle remains green.

## Downstream Reuse

The CEC2017 composition kernels `f22`, `f24`, and `f25` (in `composition.py`)
are reused as the ground-truth implementation for public CEC2020 F8, F9, and
F10: the CEC2020 dispatcher delegates those three functions to these kernels
with CEC2020 shift/rotation data overrides. Because of that delegation, the
CEC2020 committed guard values for F8/F9/F10 at the D10 zero vector are
byte-identical to the CEC2017 F22/F24/F25 constants in that same committed test
(e.g. F22 at the D10 zero vector → `5302.4980403395475`). See
`cec2020_cpp_python_equivalence_review.md` for the full mapping.
