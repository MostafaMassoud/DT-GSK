"""Golden-values matrix: 7 optimizers x 6 suites, seed-pinned, hex-exact.

The acceleration campaign's certification backbone (CERT lens, 2026-07-25).
Before this test, only dt-gsk had pinned end-to-end values (4 cells in
test_dt_gsk_byte_stable.py); the other six algorithms were certified by
nothing — a green suite proved almost nothing about bit-identity outside
dt-gsk. This matrix pins one small cell per (optimizer, suite) so that ANY
silent numeric change in the RNG stream, trial kernel, optimizer loops, suite
dispatchers, adapter, or dt subsystems fails a single pytest run.

Policy (same as test_dt_gsk_byte_stable.py): fixtures are regenerated exactly
once per DELIBERATE result-changing release, never to make a red test green.
Mint with:  python tests/regression/test_family_golden_values.py --mint
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.runners.run_experiment import OPTIMIZER_FUNCTIONS
from gsk_family.types import OptimizerOptions

FIXTURE = Path(__file__).parent / "fixtures" / "family_golden_values.json"
SEED = 20240620
GENERATOR = "threefry"

ALGS = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]
# (suite, func, dim_or_None, budget). Small budgets: the pin certifies the
# trajectory prefix, which any bit-identity break perturbs immediately.
CELLS = [
    ("sphere", 1, 10, 3000),
    ("cec2017", 5, 10, 3000),
    ("cec2013", 1, 10, 3000),
    ("cec2020", 2, 10, 3000),
    ("cec2011", 1, None, 3000),
    ("cec2013lsgo", 1, 1000, 3000),
]


def _cell_key(suite: str, func: int, dim, budget: int) -> str:
    return f"{suite}|F{func}|D{dim if dim is not None else 'native'}|B{budget}"


def _run(alg: str, suite: str, func: int, dim, budget: int) -> float:
    problem = make_problem(suite, func, dim, max_nfes_override=budget)
    options = OptimizerOptions(seed=SEED, rand_generator=GENERATOR, values={})
    return float(OPTIMIZER_FUNCTIONS[alg](problem, options).best_fitness)


def _mint() -> None:
    out: dict[str, dict[str, dict[str, str | float]]] = {}
    for alg in ALGS:
        out[alg] = {}
        for suite, func, dim, budget in CELLS:
            key = _cell_key(suite, func, dim, budget)
            try:
                val = _run(alg, suite, func, dim, budget)
                out[alg][key] = {"hex": val.hex(), "float": val}
                print(f"  {alg:11} {key:34} {val:.10e}", flush=True)
            except Exception as exc:  # mint must be loud, never partial-silent
                print(f"  {alg:11} {key:34} MINT FAILED: {exc}", flush=True)
                raise
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(
        {"seed": SEED, "generator": GENERATOR, "values": out}, indent=1),
        encoding="utf-8")
    print(f"minted {sum(len(v) for v in out.values())} pins -> {FIXTURE}")


def _fixture():
    if not FIXTURE.is_file():
        pytest.skip("golden fixture not minted yet "
                    "(python tests/regression/test_family_golden_values.py --mint)")
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.mark.parametrize("alg", ALGS)
@pytest.mark.parametrize("cell", CELLS, ids=lambda c: f"{c[0]}-F{c[1]}")
def test_golden_value(alg: str, cell) -> None:
    suite, func, dim, budget = cell
    data = _fixture()
    key = _cell_key(suite, func, dim, budget)
    pinned = data["values"].get(alg, {}).get(key)
    if pinned is None:
        pytest.skip(f"no pin for {alg}/{key} (cell failed at mint time)")
    got = _run(alg, suite, func, dim, budget)
    assert got.hex() == pinned["hex"], (
        f"BIT-IDENTITY BREAK: {alg} on {key}: got {got!r} ({got.hex()}), "
        f"pinned {pinned['float']!r} ({pinned['hex']}). If this change was a "
        f"DELIBERATE result-changing release, re-mint the fixture and record "
        f"it in the CR register; never re-mint to silence an accident."
    )


if __name__ == "__main__":
    if "--mint" in sys.argv:
        _mint()
    else:
        print(__doc__)
