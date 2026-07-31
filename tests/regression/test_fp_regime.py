"""FP-regime regression locks (process-order insensitivity + fail-closed gate).

Background (docs/reference/fp_regime.md): every
JIT kernel module guards its ``import numba`` and silently degrades to pure
NumPy when that import fails, which happens transiently under memory pressure
in spawned campaign workers. Such a worker runs every task in a second
deterministic floating-point regime (verified witness: CEC2017 F20 D10 seed
54241459 -> error 3.1217325598e-01 instead of 0.0). These tests lock:

1. the canonical regime is verified and fingerprinted (sentinel) per process;
2. a process with numba unavailable is rejected fail-closed, never silently
   degraded;
3. results are insensitive to process history / call order — in particular,
   calling ``create_fair_start`` (the runner's pre-run fair-start draw) before
   an dt-gsk ``optimize()`` must not change the trajectory;
4. the sentinel is invariant to the numba thread cap applied to workers.
"""
from __future__ import annotations

import os
import struct
import subprocess
import sys
from pathlib import Path

import pytest

from gsk_family.runners.fp_regime import (
    FPRegimeError,
    canonical_fp_regime,
    ensure_canonical_fp_regime,
)

_ROOT = Path(__file__).resolve().parents[2]

# Golden best_fitness for the cheap KAT cell (sphere F1 D10, seed 12345,
# max_nfes 3000) — same value test_dt_gsk_byte_stable.py locks. This value
# was produced in (and defines) the canonical fully-JIT regime.
_KAT_SPHERE_D10 = 0.2945738850554555


def _subprocess_env(extra_pythonpath: str | None = None) -> dict[str, str]:
    """Environment for a fresh child interpreter with project paths set."""
    env = dict(os.environ)
    paths = [str(_ROOT / "src"), str(_ROOT)]
    if extra_pythonpath:
        paths.insert(0, extra_pythonpath)
    env["PYTHONPATH"] = os.pathsep.join(paths)
    return env


def _run_child(code: str, extra_pythonpath: str | None = None) -> subprocess.CompletedProcess[str]:
    """Run ``code`` in a fresh interpreter from the project root."""
    return subprocess.run(
        [sys.executable, "-c", code],
        cwd=str(_ROOT),
        env=_subprocess_env(extra_pythonpath),
        capture_output=True,
        text=True,
        timeout=600,
    )


def test_canonical_regime_is_jit_complete_and_deterministic() -> None:
    """This process must be fully JIT and the sentinel must be stable."""
    payload = ensure_canonical_fp_regime("sphere")
    assert payload["jit_complete"] is True
    assert all(flag is True for flag in payload["kernel_flags"].values())
    repeat = canonical_fp_regime("sphere")
    assert repeat["sentinel"] == payload["sentinel"]
    # The same expected sentinel must verify cleanly.
    ensure_canonical_fp_regime("sphere", expected_sentinel=payload["sentinel"])
    with pytest.raises(FPRegimeError):
        ensure_canonical_fp_regime("sphere", expected_sentinel="0" * 64)


def test_numba_fallback_is_rejected_fail_closed(tmp_path: Path) -> None:
    """A process whose numba import fails must refuse to run (no silent regime)."""
    stub = tmp_path / "numba"
    stub.mkdir()
    (stub / "__init__.py").write_text(
        'raise ImportError("simulated numba import failure (regression test)")\n',
        encoding="utf-8",
    )
    code = (
        "from gsk_family.runners.fp_regime import ensure_canonical_fp_regime, FPRegimeError\n"
        "try:\n"
        "    ensure_canonical_fp_regime('sphere')\n"
        "except FPRegimeError:\n"
        "    print('REJECTED')\n"
        "else:\n"
        "    print('ACCEPTED')\n"
    )
    completed = _run_child(code, extra_pythonpath=str(tmp_path))
    assert completed.returncode == 0, completed.stderr
    assert "REJECTED" in completed.stdout, (
        "numba-fallback process was not rejected: "
        f"stdout={completed.stdout!r} stderr={completed.stderr!r}"
    )


@pytest.mark.parametrize("prior_call", ["plain", "prefair"])
def test_dt_gsk_process_order_insensitivity(prior_call: str) -> None:
    """create_fair_start before optimize() must not change the trajectory.

    Both arms run in fresh interpreters and must reproduce the byte-stability
    golden value, so any process-history sensitivity (or regime drift) fails
    loudly against the committed reference regime.
    """
    prelude = ""
    if prior_call == "prefair":
        prelude = (
            "from gsk_family.common.rng import create_fair_start\n"
            "create_fair_start(12345, 'threefry', 100, 10, -100.0, 100.0)\n"
        )
    code = (
        f"{prelude}"
        "import struct\n"
        "from gsk_family.benchmark_adapter.factory import make_problem\n"
        "from gsk_family.optimizers.dt_gsk import optimize\n"
        "from gsk_family.types import OptimizerOptions\n"
        "problem = make_problem('sphere', 1, dim=10, max_nfes_override=3000)\n"
        "result = optimize(problem, OptimizerOptions(seed=12345, rand_generator='threefry'))\n"
        "print(struct.pack('<d', float(result.best_fitness)).hex())\n"
    )
    completed = _run_child(code)
    assert completed.returncode == 0, completed.stderr
    expected_hex = struct.pack("<d", _KAT_SPHERE_D10).hex()
    assert completed.stdout.strip().splitlines()[-1] == expected_hex, (
        f"arm={prior_call}: best_fitness bits diverged from the golden regime "
        f"(got {completed.stdout.strip()!r}, expected {expected_hex})"
    )


def test_sentinel_thread_invariance() -> None:
    """The sentinel must not depend on the worker numba-thread cap."""
    parent = canonical_fp_regime("sphere")
    code = (
        "import numba\n"
        "numba.set_num_threads(1)\n"
        "from gsk_family.runners.fp_regime import canonical_fp_regime\n"
        "print(canonical_fp_regime('sphere')['sentinel'])\n"
    )
    completed = _run_child(code)
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip().splitlines()[-1] == parent["sentinel"], (
        "sentinel differs under numba thread cap: worker-vs-parent comparison "
        "would spuriously fail"
    )
