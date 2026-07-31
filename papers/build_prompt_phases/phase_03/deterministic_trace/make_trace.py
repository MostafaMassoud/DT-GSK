"""Phase 3 deterministic trace: a tiny fixed-seed DT-GSK run whose best-so-far
telemetry is captured at the result layer (NOT by instrumenting the
profile-locked ISM core). Validates the pseudocode's monotone global-best return
and budget-exact accounting. Re-run: identical output for the same seed."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from gsk_family.benchmark_adapter.factory import make_problem
from gsk_family.optimizers.ism_gsk import optimize
from gsk_family.types import OptimizerOptions

OUT = Path(__file__).resolve().parent
SUITE, FUNC, DIM = "cec2017", 1, 10   # F1 = shifted-rotated sphere
BUDGET = 3000                          # small; keeps deep-stall inert (< min_budget)
SEED = 20240620


def run_once() -> dict:
    problem = make_problem(SUITE, FUNC, dim=DIM, max_nfes_override=BUDGET)
    r = optimize(problem, OptimizerOptions(seed=SEED, rand_generator="threefry"))
    conv = r.convergence
    bsf = np.asarray(conv.best_fitness, dtype=np.float64)
    nfes = np.asarray(conv.nfes)
    monotone = bool(np.all(np.diff(bsf) <= 1e-12))
    return {
        "problem": {"suite": SUITE, "func": FUNC, "dim": DIM, "max_nfes": BUDGET},
        "seed": SEED, "generator": "threefry",
        "nfes_used": int(r.nfes),
        "best_fitness": float(r.best_fitness),
        "budget_exact": int(r.nfes) == BUDGET,
        "convergence_points": int(bsf.size),
        "nfes_head": [int(x) for x in nfes[:5]],
        "bsf_head": [float(x) for x in bsf[:5]],
        "bsf_tail": [float(x) for x in bsf[-5:]],
        "best_so_far_monotone_nonincreasing": monotone,
        "notes": str(getattr(r, "notes", "")),
    }


def main() -> None:
    t1 = run_once()
    t2 = run_once()
    t1["determinism_repeat_identical"] = (
        t1["best_fitness"] == t2["best_fitness"] and t1["nfes_used"] == t2["nfes_used"]
    )
    (OUT / "trace_cec2017_F1_D10_S20240620.json").write_text(
        json.dumps(t1, indent=2), encoding="utf-8"
    )
    print(json.dumps(t1, indent=2))


if __name__ == "__main__":
    main()
