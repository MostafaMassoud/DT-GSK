# Validation Report

> **What this page is.** A snapshot of what the automated tests currently check,
> the commands that reproduce that state, and what validation work is still
> outstanding.
>
> **Who it is for.** Reviewers and researchers who need to know how far the
> implementation has been verified before they rely on it.
>
> **What you will get.** The coverage of the test suite, the verification
> commands, the current pass status (with the count framed honestly), and the
> remaining validation work.
>
> **Prerequisites.** The reproduction procedure is in
> [Reproducibility](reproducibility.md); evidence commands are in the
> [Researcher Handbook](researcher_handbook.md). Terms are defined in
> [the glossary](../reference/glossary.md).

This report records the current validation state of the Python implementation.

## Current Automated Validation

The test suite checks the pipeline end to end — from imports through to the
generated HTML docs. It currently covers:

- imports and package discovery;
- config parsing and defaults;
- seed formulas and deterministic schedules;
- numeric compatibility helpers;
- benchmark adapter shape and metadata checks;
- all seven runnable optimizer smoke paths (`gsk`, `agsk`, `apgsk`, `fdb-agsk`,
  `atmals-gsk`, `egsk`, `dt-gsk`);
- fair-start and deterministic replay behavior;
- dt-gsk byte-for-byte parity with its source project (`01-Python/03-DT-GSK-v2.1`), locked by `tests/regression/test_dt_gsk_byte_stable.py` on sphere and CEC2017 at D=10 and D=30 (the lock deliberately stays below the `D>=50` SGSM/parallel-kernel tier, which is thread-sensitive; that tier is guarded instead by `test_dt_graph_backend_parity.py` and `test_dt_polish_incumbent_consistent.py`);
- the statistical-analysis suite (Friedman/Wilcoxon, the result/reference
  loaders, figures, LaTeX, and the `gsk-stats` CLI);
- runner output schema;
- reference loading and verification;
- parallel runner determinism;
- documentation command behavior;
- source docstring coverage;
- generated HTML local link coverage.

The tests are organized so you can target a layer directly:

| Directory | Scope |
|---|---|
| `tests/unit/` | Pure-function checks: bounds, donors, population, reduction, RNG, seed policy, numeric compat, statistics/Friedman, loaders, figures, LaTeX, CLI parsing. |
| `tests/smoke/` | End-to-end happy paths for every optimizer, the runner, the `--stats` flag, the `gsk-stats` CLI, and the documentation commands. |
| `tests/regression/` | Golden locks: `test_dt_gsk_byte_stable.py` (source parity), `test_validation_ladder.py`, `test_fp_regime.py` (FP-regime sentinel), `test_pool_self_heal.py` (process-pool recovery), `test_dt_graph_backend_parity.py` (interaction-graph backends bit-identical at `D>=50`), `test_dt_polish_incumbent_consistent.py` (final-polish incumbent consistency), and `test_dt_gsk_curve_monotone.py` (best-so-far convergence contract). |
| `tests/performance/` | `test_parallel_runner.py` (parallel/serial determinism and profile metadata). |

The dt-gsk byte-stability lock asserts exact `best_fitness` values at
`seed=12345` and `max_nfes=3000` for four cells — sphere F1 (D=10, D=30) and
CEC2017 F1 (D=10) / F3 (D=30) — so any change to the vendored DT-GSK core, the
RNG substream layer, or the pub-profile config that perturbs the trajectory fails
immediately.

## Latest Verification Commands

Run the test suite to regenerate the automated-validation evidence:

```powershell
python -m pytest
```

Run a focused subset while iterating, e.g. only the regression locks or only the
statistics layer:

```powershell
python -m pytest tests/regression -q
python -m pytest tests/unit/test_statistics.py tests/unit/test_statistical_tests_friedman.py -q
```

To check generated summaries against the imported reference tables, point
`gsk-validate` at a finished run tree (use a temporary output root so it does
not touch your campaign results):

```powershell
gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
```

This is one link in the evidence chain documented in the
[Researcher Handbook — Evidence Commands](researcher_handbook.md#evidence-commands).

### EGSK port vs reference (paired)

EGSK is the one optimizer that cannot be byte-validated (its reference runs
MATLAB `fmincon`, substituted here by `scipy`-SLSQP). It is instead validated by
a **paired per-run** test: the EGSK reference ships per-run checkpoint logs with
seeds matching the unified Threefry schedule, so the Python EGSK is run at each
reference seed and the final errors are paired. The method, the reproducible
command, and the measured agreement are in the
[EGSK Validation Appendix](egsk_validation_appendix.md).

```powershell
python scripts/validate_egsk_vs_reference.py --dims 10,30,50 --funcs 1,3,5,7,9,11,15,21,27,30 --runs 15 --out egsk_validation.json
```

## Current Status

Run the full suite to reproduce the validation state for yourself:

```powershell
python -m pytest -q
```

All tests pass at the time of writing; the count grows as tests are added, so
treat the number printed by `pytest -q` on your checkout as authoritative rather
than any figure quoted here. The suite is grouped into `tests/unit/`,
`tests/smoke/`, `tests/regression/`, and `tests/performance/` (see the table
above) plus the top-level `tests/test_imports.py`.

Beyond the automated suite, `gsk-validate --compare` checks generated summaries
against the imported reference tables and records the verdict in
`verification.json`. A reduced-budget comparison is a consistency and schema
check, not a full-campaign equivalence claim — see
[Reproducibility — Bit-Exact Caveats](reproducibility.md#bit-exact-caveats).

The `gsk-stats` statistical suite is also covered: `tests/smoke/` exercises the
`gsk-stats` CLI and the runner's `--stats` live-report flag, and `tests/unit/`
exercises the Friedman/Wilcoxon math, the result/reference loaders, the figure
renderers, and the LaTeX table builders. The statistical methodology those tests
guard is documented in [Statistical Analysis](statistical_analysis.md).

## Remaining Validation Work

The following raise the evidence from reduced smoke checks to full campaigns:

- Run full-budget campaigns where runtime allows.
- Produce statistical equivalence reports for reference-vs-Python comparisons
  (the `gsk-stats` family report and the review pack already produce the
  comparison artifacts; see [Statistical Analysis](statistical_analysis.md)).
- Archive generated validation artifacts under a dated release evidence folder,
  following the [Reporting checklist](researcher_handbook.md#reporting).

These items track the open evidence gap mirrored in
[Performance — Remaining measurement work](performance.md#remaining-measurement-work);
the automated suite already passes, so the outstanding work is campaign scale and
archival, not code correctness.
