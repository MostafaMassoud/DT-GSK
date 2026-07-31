# CEC2013LSGO C++ to Python Equivalence Review

## Scope

This review audits the Python CEC2013 large-scale global optimization evaluator
against the standalone C++ CEC2013LSGO implementation. The suite contains
15 functions:

- F1-F12 and F15 use D=1000;
- F13-F14 use D=905;
- raw-objective statistics are used by the benchmark adapter.

The C++ harness does not ship a fixed-vector CSV oracle for this suite. The
audit therefore focuses on data parity, API parity, identities at known
construction points, finite smoke checks, and documented bounds provenance.

## Suite Protocol Context

The benchmark adapter registers CEC2013LSGO in
`src/gsk_family/benchmark_adapter/protocol.py`:

- 15 large-scale functions (`function_ids = 1..15`) at native dimensions
  (`default_dimensions = "native"`): D=1000 for F1–F12 and F15, D=905 for
  F13–F14. `cec2013lsgo_dim()` in `functions.py` is the authority — F13/F14 use
  20 overlapping groups with overlap 5, which yields 905.
- Raw-objective statistics: CEC2013LSGO is the second member of
  `RAW_OBJECTIVE_SUITES = {cec2011, cec2013lsgo}` (its module docstring records
  this as "for comparability with imported references"), so `problem.optimum`
  and `problem.target_error` are both `NaN`.
- **No committed reference-results tree.** CEC2013LSGO is in code
  (`CEC_SUITES`) and constructible through `make_problem`, but
  `benchmarks/cec_reference_results/` contains only `cec2011`, `cec2013`, and
  `cec2017` — there is no `cec_reference_results/cec2013lsgo/`. The suite is
  wired and evaluator-audited, but it is not part of the committed optimizer
  reference evidence.
- The only committed unit test is
  `test_cec2013lsgo_native_dimensions_are_function_specific` in
  `tests/unit/test_benchmark_adapter.py`, which asserts the native-dimension
  contract (`make_problem("cec2013lsgo", 1).dim == 1000`,
  `make_problem("cec2013lsgo", 13).dim == 905`). The data- and functional-parity
  sweeps below were run as review-time audit scripts, not as default unit tests
  (see *Regression Coverage Recommendation*).

## Data Parity

Every data artifact represented in Python `data.pkl` was compared with the C++
input text files:

- `F{id}-xopt.txt`;
- permutation vectors `F{id}-p.txt`, converted from 1-based C++ text to
  0-based Python arrays;
- group sizes `F{id}-s.txt`;
- group weights `F{id}-w.txt`;
- rotation matrices `F{id}-R25.txt`, `F{id}-R50.txt`, and `F{id}-R100.txt`.

Result:

```text
LSGO data/API parity failures 0
```

## API And Metadata

The Python suite matches the C++ native dimensions:

| Function range | Dimension |
|---|---:|
| F1-F12 | 1000 |
| F13-F14 | 905 |
| F15 | 1000 |

The Python adapter exposes CEC2013LSGO as a native-dimension suite and uses
raw-objective statistics, matching the imported reference-result convention.

## Bounds

Python intentionally diverges from the C++ source bounds for F9-F11:

| Function | Python bounds | C++ source bounds | Reason |
|---:|---|---|---|
| F9 | `[-5, 5]` | `[-100, 100]` | Python follows the technical report |
| F10 | `[-32, 32]` | `[-5, 5]` | Python follows the technical report |
| F11 | `[-100, 100]` | `[-32, 32]` | Python follows the technical report |

This divergence is documented first-class in the suite source: the `_BOUNDS`
dict in `functions.py` carries per-function inline comments
(`9: (-5.0, 5.0)  # tech report: [-5,5]; C++ ref has bug ([-100,100])`, and the
matching comments for F10/F11), and the exported constant
`CEC2013LSGO_BOUNDS_PROVENANCE = "cec2013_lsgo_tech_report"` records the
decision. The C++ reference cross-pasted the `[-5,5]`, `[-32,32]`, and
`[-100,100]` domains among F9/F10/F11; Python follows the technical report so
the reported optima remain valid. All other function bounds match the C++
source.

## Functional Checks

The Python evaluator passed the same identity/smoke categories used by the C++
harness:

- `f(xopt) == 0` where the construction implies it;
- `F12(xopt + 1) == 0` for shifted Rosenbrock;
- F14 excluded from the `xopt` identity because the overlapping conflicting
  shifts intentionally cannot be satisfied by one global vector;
- all-zero vector finite for every function;
- deterministic in-bounds pattern vector finite for every function;
- repeated evaluation deterministic.

Result:

```text
LSGO functional failures 0
```

## Findings

No CEC2013LSGO evaluator bug was found in this pass. The only C++ vs Python
difference is the intentional F9-F11 bounds provenance decision.

## Regression Coverage Recommendation

Full LSGO data parity is intentionally not placed in the default unit-test path
because it loads and compares large D=1000 artifacts. Keep it as an audit
script/checklist item for benchmark-conversion reviews, release validation, or
data repacking changes.

## Residual Risk

There is no fixed-vector C++ CSV oracle for CEC2013LSGO. The current evidence
supports structural parity and functional sanity, but future changes to LSGO
base formulas should add a small committed probe oracle if exact C++ pointwise
tracking becomes a release requirement.
