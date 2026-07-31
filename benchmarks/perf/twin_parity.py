"""Measure parallel-vs-serial kernel agreement for a CEC suite.

Establishes the NUMERICAL CONTRACT that each ``_numba_serial.py`` docstring
claims, instead of inheriting a number from a harness this repository does not
contain. ``cec2017/_numba_serial.py`` cites
``benchmarks/perf/cec2017_twin_parity.py`` for "93.20% bitwise / worst 13 ULP" —
that file does not exist here, so the figure cannot be re-derived. This is its
replacement, written to cover every suite that has twins.

What it does
------------
For each compiled kernel dispatcher in ``<suite>/_numba.py`` that has a serial
twin, feed identical pseudo-random inputs to both and compare the results
*bitwise*, reporting the ULP distance where they differ. Kernel signatures vary,
so the harness introspects each ``py_func`` and supplies plausible arrays; any
kernel whose signature it cannot satisfy is reported as SKIPPED rather than
silently omitted -- a skipped kernel is an unmeasured kernel, and the difference
matters when the output is used to justify a fidelity class.

Usage
-----
    python benchmarks/perf/twin_parity.py --suite cec2013
    python benchmarks/perf/twin_parity.py --suite cec2013 --rows 64 --dims 10 30
"""

from __future__ import annotations

import argparse
import importlib
import struct
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

SUITES = ("cec2013", "cec2017", "cec2020", "cec2013lsgo", "cec2011")


def _ulp_distance(a: float, b: float) -> int:
    """Signed-magnitude ULP distance between two float64s."""
    if a == b:
        return 0
    ia = struct.unpack("<q", struct.pack("<d", a))[0]
    ib = struct.unpack("<q", struct.pack("<d", b))[0]
    if ia < 0:
        ia = np.int64(-0x8000000000000000) - ia
    if ib < 0:
        ib = np.int64(-0x8000000000000000) - ib
    return int(abs(int(ia) - int(ib)))


def _try_call(fn, x: np.ndarray, dim: int):
    """Call ``fn`` with plausible arguments built from the SAME input ``x``.

    ``x`` is supplied by the caller and never regenerated here. An earlier
    revision drew fresh randoms inside this function, so the batch kernel and
    its twin were fed *different* inputs; the harness then reported ULP
    distances around 9.2e18 -- the whole float64 range -- and pronounced
    bit-identical suites "class (b)". Comparing two kernels requires giving
    them the same numbers.
    """
    import inspect

    n_args = len(inspect.signature(fn).parameters)
    candidates = [
        (x,),
        (x, dim),
        (x, np.ascontiguousarray(x[0]), dim),
        (x, np.ascontiguousarray(x[0])),
    ]
    for args in candidates:
        if len(args) != n_args:
            continue
        try:
            return np.asarray(fn(*[a.copy() if isinstance(a, np.ndarray) else a
                                   for a in args]), dtype=np.float64).ravel()
        except Exception:
            continue
    return None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--suite", required=True, choices=SUITES)
    ap.add_argument("--rows", type=int, default=32)
    ap.add_argument("--dims", type=int, nargs="+", default=[10, 30, 50])
    ap.add_argument("--seed", type=int, default=20240620)
    args = ap.parse_args(argv)

    base = f"benchmarks.cec_suite_python.{args.suite}"
    try:
        batch = importlib.import_module(f"{base}._numba")
        serial = importlib.import_module(f"{base}._numba_serial")
    except ModuleNotFoundError as exc:
        print(f"{args.suite}: no serial twins available ({exc})")
        return 2

    names = [n for n in dir(batch)
             if not n.startswith("__") and hasattr(getattr(batch, n), "py_func")]
    rng = np.random.default_rng(args.seed)

    total = same = 0
    worst = 0
    worst_kernel = ""
    skipped: list[str] = []
    per_kernel: dict[str, tuple[int, int, int]] = {}

    for name in sorted(names):
        b = getattr(batch, name)
        try:
            s = getattr(serial, name)
        except Exception as exc:
            skipped.append(f"{name} (no twin: {type(exc).__name__})")
            continue
        k_tot = k_same = k_worst = 0
        for dim in args.dims:
            # ONE input array, handed to both kernels. See _try_call's docstring.
            x = rng.standard_normal((args.rows, dim)) * 50.0
            vb = _try_call(b, x, dim)
            vs = _try_call(s, x, dim) if vb is not None else None
            if vb is None or vs is None or vb.shape != vs.shape:
                continue
            for i in range(vb.size):
                k_tot += 1
                if vb[i].tobytes() == vs[i].tobytes():
                    k_same += 1
                else:
                    k_worst = max(k_worst, _ulp_distance(float(vb[i]), float(vs[i])))
        if k_tot == 0:
            skipped.append(f"{name} (signature not satisfiable)")
            continue
        per_kernel[name] = (k_tot, k_same, k_worst)
        total += k_tot
        same += k_same
        if k_worst > worst:
            worst, worst_kernel = k_worst, name

    print(f"\n{args.suite}: twin parity over {total:,} values, "
          f"{len(per_kernel)} kernels, dims {args.dims}, rows {args.rows}")
    if total:
        pct = 100.0 * same / total
        print(f"  bitwise identical : {same:,}/{total:,}  ({pct:.4f}%)")
        print(f"  worst ULP         : {worst}"
              f"{f'  ({worst_kernel})' if worst else ''}")
        print(f"  fidelity class    : "
              f"{'(a) bit-identical' if worst == 0 else '(b) float-reassociation'}")
    for name, (t, s_, w) in sorted(per_kernel.items(), key=lambda kv: -kv[1][2]):
        if w:
            print(f"    {name:32} {s_:>6}/{t:<6} bitwise   worst {w} ULP")
    if skipped:
        print(f"  SKIPPED ({len(skipped)}) — unmeasured, not passed:")
        for s_ in skipped:
            print(f"    {s_}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
