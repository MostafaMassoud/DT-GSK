"""BUG-RESUME-01 regression: a resume must not drop or mis-compute summary rows.

Two independent failure modes are covered:

1. **Truncation** -- a resume that touches one function used to rewrite
   ``<alg>_<suite>_D<dim>.csv`` with only that function, erasing every untouched
   one (the file was opened ``"w"`` and fed this session's artifacts only).
2. **Subset statistics** -- a *partially* resumed function used to be summarised
   over the newly executed runs alone, so 6 new runs of a 25-run cell produced
   Best/Median/Mean/Worst/SD over 6 values. This one is invisible in the output,
   which is why it is asserted explicitly.
"""
from __future__ import annotations

import csv

import numpy as np
import pytest

from gsk_family.runners.output import RunArtifact, write_summary_tables
from gsk_family.stats import format_scientific, summarize
from gsk_family.types import RunRecord

SUITE = "cec2013lsgo"
OPT = "gsk"
DIM = 1000


def _artifact(func: int, run: int, value: float) -> RunArtifact:
    record = RunRecord(
        optimizer=OPT, suite=SUITE, function=func, dimension=DIM, run=run,
        seed=1000 + run, best_fitness=value, error=float("nan"), nfes=1000,
        termination="max_evaluations", runtime_seconds=1.0,
    )
    return RunArtifact(
        record=record, result=None, statistics_basis="raw_objective",
        optimum=0.0, target_error=float("nan"), max_nfes=1000,
    )


def _read(path):
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return {int(r["Function"]): r for r in csv.DictReader(handle)}


def _seed_bank(summary_dir, funcs, runs_per_func):
    """Write a complete summary for `funcs` as a prior campaign would have."""
    artifacts = [
        _artifact(f, r, 100.0 * f + r)
        for f in funcs
        for r in range(1, runs_per_func + 1)
    ]
    write_summary_tables(summary_dir, OPT, SUITE, artifacts)
    return artifacts


def test_resume_touching_one_function_keeps_the_others(tmp_path):
    """Mode 1: untouched functions must survive, byte-for-byte."""
    funcs = [1, 2, 3, 8, 15]
    _seed_bank(tmp_path, funcs, runs_per_func=5)
    path = tmp_path / f"{OPT}_{SUITE}_D{DIM}.csv"
    before = _read(path)
    assert sorted(before) == funcs

    # Resume: only F8 runs this session.
    resumed = [_artifact(8, r, 800.0 + r) for r in range(1, 6)]
    write_summary_tables(tmp_path, OPT, SUITE, resumed)

    after = _read(path)
    assert sorted(after) == funcs, (
        f"resume dropped functions: kept {sorted(after)}, expected {funcs}"
    )
    for f in funcs:
        if f == 8:
            continue
        assert after[f] == before[f], f"untouched F{f} was rewritten"


def test_partially_resumed_function_uses_all_banked_runs(tmp_path):
    """Mode 2: stats must cover every banked run, not just the new ones."""
    funcs = [1, 8]
    _seed_bank(tmp_path, funcs, runs_per_func=5)
    path = tmp_path / f"{OPT}_{SUITE}_D{DIM}.csv"

    # F8 has 5 runs banked; this session executes only 2 more (runs 6-7).
    new_vals = [806.0, 807.0]
    resumed = [_artifact(8, r, v) for r, v in zip((6, 7), new_vals)]
    banked_vals = [800.0 + r for r in range(1, 6)] + new_vals   # all 7

    write_summary_tables(
        tmp_path, OPT, SUITE, resumed,
        bank_counts={(DIM, 8): len(banked_vals)},
        bank_values={(DIM, 8): banked_vals},
    )

    row = _read(path)[8]
    expected = summarize(np.array(banked_vals, dtype=float))
    assert row["Best"] == format_scientific(expected.best)
    assert row["Worst"] == format_scientific(expected.worst)
    assert row["Mean"] == format_scientific(expected.mean)

    # And it must NOT be the 2-run subset -- the pre-fix behaviour.
    subset = summarize(np.array(new_vals, dtype=float))
    assert row["Best"] != format_scientific(subset.best), (
        "summary was computed from this session's runs only (BUG-RESUME-01 mode 2)"
    )


def test_cec2011_rollup_also_merges(tmp_path):
    """The CEC2011 single rollup had the identical truncation defect."""
    arts = [_artifact(f, r, 10.0 * f + r) for f in (1, 2, 5) for r in range(1, 4)]
    write_summary_tables(tmp_path, OPT, "cec2011", arts)
    path = tmp_path / f"{OPT}_cec2011.csv"
    assert sorted(_read(path)) == [1, 2, 5]

    write_summary_tables(tmp_path, OPT, "cec2011", [_artifact(2, 1, 999.0)])
    assert sorted(_read(path)) == [1, 2, 5], "cec2011 rollup dropped functions"


# --- exhaustive coverage: every registered algorithm x every registered suite ---
# The fix lives in one shared writer with ZERO branches on `optimizer` and exactly
# one on `suite` (the CEC2011 rollup), so coverage is provable by inspection. This
# matrix asserts it empirically anyway, because "applies to all algorithms and all
# suites" is the property the author needs guaranteed, not inferred.

ALL_OPTIMIZERS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]
ALL_SUITES = ["cec2011", "cec2013", "cec2013lsgo", "cec2017", "cec2020", "sphere"]


def _artifact_for(opt: str, suite: str, dim: int, func: int, run: int,
                  value: float) -> RunArtifact:
    record = RunRecord(
        optimizer=opt, suite=suite, function=func, dimension=dim, run=run,
        seed=1000 + run, best_fitness=value, error=float("nan"), nfes=1000,
        termination="max_evaluations", runtime_seconds=1.0,
    )
    return RunArtifact(
        record=record, result=None, statistics_basis="raw_objective",
        optimum=0.0, target_error=float("nan"), max_nfes=1000,
    )


@pytest.mark.parametrize("opt", ALL_OPTIMIZERS)
@pytest.mark.parametrize("suite", ALL_SUITES)
def test_resume_preserves_functions_for_every_optimizer_and_suite(opt, suite, tmp_path):
    """No algorithm/suite combination may drop untouched functions on resume."""
    dim = 1000 if suite == "cec2013lsgo" else 10
    funcs = [1, 2, 3, 7]

    first = [
        _artifact_for(opt, suite, dim, f, r, 100.0 * f + r)
        for f in funcs for r in (1, 2)
    ]
    write_summary_tables(tmp_path, opt, suite, first)

    path = (tmp_path / f"{opt}_{suite}.csv" if suite == "cec2011"
            else tmp_path / f"{opt}_{suite}_D{dim}.csv")
    assert path.is_file(), f"{opt}/{suite}: summary was not created"
    before = _read(path)
    assert sorted(before) == funcs

    # Resume: only F3 is executed this session.
    write_summary_tables(
        tmp_path, opt, suite,
        [_artifact_for(opt, suite, dim, 3, r, 300.0 + r) for r in (1, 2)],
    )

    after = _read(path)
    assert sorted(after) == funcs, (
        f"{opt}/{suite}: resume dropped functions -- kept {sorted(after)}, "
        f"expected {funcs}"
    )
    for f in funcs:
        if f != 3:
            assert after[f] == before[f], f"{opt}/{suite}: untouched F{f} rewritten"
