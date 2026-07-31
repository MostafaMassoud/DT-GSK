"""One-shot converter: CEC2013LSGO ``cdatafiles/*.txt`` -> ``data.pkl``.

Mirrors the CEC2013 / CEC2017 / CEC2020 layout (single pickled dict with
``('__np_array__', dtype_str, shape, bytes)`` leaf tuples) so that
``transforms.py`` can load a SHA-256-verified blob instead of touching
the filesystem 75 times.

Run from the repo root::

    # default: read from in-suite ``data/`` directory
    python -m benchmarks.cec_suite_python.cec2013lsgo.make_data_pkl

    # read from an arbitrary external source (e.g. C++ reference repo)
    python -m benchmarks.cec_suite_python.cec2013lsgo.make_data_pkl /path/to/cdatafiles

Output
------
* ``benchmarks/cec_suite_python/cec2013lsgo/data.pkl``
* SHA-256 of the new pickle (paste into ``transforms.py``'s
  ``_EXPECTED_SHA256`` constant).

Source layout (input ``.txt`` files)
------------------------------------
For every function F1..F15:
    F{id}-xopt.txt    -- shift vector (1000 floats for F1-F12, F15;
                          905 for F13; 1000 for F14 split into per-group)

For grouped functions F4..F11, F13, F14:
    F{id}-p.txt       -- permutation vector (single CSV line, 1-indexed)
    F{id}-s.txt       -- group sizes (one int per line)
    F{id}-w.txt       -- group weights (one float per line)
    F{id}-R25.txt     -- 25x25 orthogonal rotation matrix (CSV per row)
    F{id}-R50.txt     -- 50x50 orthogonal rotation matrix
    F{id}-R100.txt    -- 100x100 orthogonal rotation matrix

Output layout (in the pickle)
-----------------------------
Flat dict mapping ``"F{id}-{kind}"`` -> encoded ndarray::

    {
        "F1-xopt":  ('__np_array__', '<f8', (1000,),  <bytes>),
        "F2-xopt":  ('__np_array__', '<f8', (1000,),  <bytes>),
        ...
        "F4-xopt":  ('__np_array__', '<f8', (1000,),  <bytes>),
        "F4-p":     ('__np_array__', '<i8', (1000,),  <bytes>),  # 0-indexed
        "F4-s":     ('__np_array__', '<i8', (7,),     <bytes>),
        "F4-w":     ('__np_array__', '<f8', (7,),     <bytes>),
        "F4-R25":   ('__np_array__', '<f8', (25, 25), <bytes>),
        "F4-R50":   ('__np_array__', '<f8', (50, 50), <bytes>),
        "F4-R100":  ('__np_array__', '<f8', (100, 100), <bytes>),
        ...
    }

Notes
-----
* The permutation vector is converted to **0-indexed int64** at build
  time, so the loaded ``transforms.load_perm`` returns the array as-is
  with no per-call conversion overhead.
* Rotation matrices are stored in their **original** (non-transposed)
  row-major form.  ``transforms.load_rotation`` returns them unchanged;
  the NumPy-fallback path applies ``.T`` for the BLAS matmul, while the
  Numba kernels consume the row-major layout directly.
* The SHA-256 of the resulting pickle is printed at the end of the run.
  Paste it into ``transforms.py``'s ``_EXPECTED_SHA256`` constant before
  committing.
"""

from __future__ import annotations

import hashlib
import os
import pickle
import re
import sys

import numpy as np

# Functions that have only an xopt file (no grouping data).
_XOPT_ONLY = (1, 2, 3, 12, 15)
# Functions with full grouping data (xopt + p + s + w + 3 rotation matrices).
_GROUPED = (4, 5, 6, 7, 8, 9, 10, 11, 13, 14)
_ALL = tuple(sorted(set(_XOPT_ONLY) | set(_GROUPED)))
_ROT_DIMS = (25, 50, 100)

_HERE = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_SOURCE = os.path.join(_HERE, "data")
_OUT_PATH = os.path.join(_HERE, "data.pkl")


def _np_to_tuple(arr: np.ndarray) -> tuple:
    """Encode an ndarray as ``('__np_array__', dtype_str, shape, bytes)``."""
    arr = np.ascontiguousarray(arr)
    return ("__np_array__", arr.dtype.str, tuple(arr.shape), arr.tobytes())


def _read_floats(path: str) -> list[float]:
    """Read whitespace- and comma-separated floats from a text file."""
    vals: list[float] = []
    with open(path) as f:
        for line in f:
            for tok in line.strip().split(","):
                tok = tok.strip()
                if tok:
                    vals.append(float(tok))
    return vals


def _read_ints(path: str) -> list[int]:
    """Read whitespace- and comma-separated ints from a text file."""
    out: list[int] = []
    with open(path) as f:
        for line in f:
            for tok in line.strip().split(","):
                tok = tok.strip()
                if tok:
                    out.append(int(float(tok)))
    return out


def _read_matrix(path: str, n: int) -> np.ndarray:
    """Read an n*n CSV matrix (one row per line)."""
    rows: list[list[float]] = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = [float(v) for v in line.split(",") if v.strip()]
            rows.append(row)
    arr = np.asarray(rows, dtype=np.float64)
    if arr.shape != (n, n):
        raise RuntimeError(
            f"{os.path.basename(path)}: expected ({n},{n}), got {arr.shape}"
        )
    return arr


def build_payload(source_dir: str) -> dict:
    """Read every ``F{id}-*.txt`` from *source_dir* into the pickle dict."""
    if not os.path.isdir(source_dir):
        raise FileNotFoundError(
            f"CEC2013LSGO source directory not found: {source_dir}"
        )

    payload: dict[str, tuple] = {}
    missing: list[str] = []

    for fid in _ALL:
        # ---- xopt: float64 vector (length depends on function) ----
        xopt_path = os.path.join(source_dir, f"F{fid}-xopt.txt")
        if not os.path.isfile(xopt_path):
            missing.append(os.path.basename(xopt_path))
        else:
            xopt = np.asarray(_read_floats(xopt_path), dtype=np.float64)
            payload[f"F{fid}-xopt"] = _np_to_tuple(xopt)

        if fid in _GROUPED:
            # ---- p: 0-indexed int64 permutation vector ----
            p_path = os.path.join(source_dir, f"F{fid}-p.txt")
            if not os.path.isfile(p_path):
                missing.append(os.path.basename(p_path))
            else:
                perm_1based = np.asarray(_read_ints(p_path), dtype=np.int64)
                perm = perm_1based - 1  # convert to 0-indexed
                payload[f"F{fid}-p"] = _np_to_tuple(perm)

            # ---- s: int64 group sizes ----
            s_path = os.path.join(source_dir, f"F{fid}-s.txt")
            if not os.path.isfile(s_path):
                missing.append(os.path.basename(s_path))
            else:
                sizes = np.asarray(_read_ints(s_path), dtype=np.int64)
                payload[f"F{fid}-s"] = _np_to_tuple(sizes)

            # ---- w: float64 group weights ----
            w_path = os.path.join(source_dir, f"F{fid}-w.txt")
            if not os.path.isfile(w_path):
                missing.append(os.path.basename(w_path))
            else:
                weights = np.asarray(_read_floats(w_path), dtype=np.float64)
                payload[f"F{fid}-w"] = _np_to_tuple(weights)

            # ---- R25 / R50 / R100 rotation matrices ----
            for n in _ROT_DIMS:
                r_path = os.path.join(source_dir, f"F{fid}-R{n}.txt")
                if not os.path.isfile(r_path):
                    missing.append(os.path.basename(r_path))
                    continue
                R = _read_matrix(r_path, n)
                payload[f"F{fid}-R{n}"] = _np_to_tuple(R)

    if missing:
        raise RuntimeError(
            f"CEC2013LSGO build aborted: {len(missing)} files missing "
            f"from {source_dir}\n  " + "\n  ".join(missing[:20])
            + ("\n  ..." if len(missing) > 20 else "")
        )

    return payload


# Audit L-2 lsgo: automatic SHA-256 update.  The previous workflow
# printed the new hash and asked the author to paste it into
# ``transforms.py``, which is error-prone (copy-paste, trailing
# whitespace, forgetting the step entirely, committing a data.pkl whose
# hash doesn't match the constant so every worker crashes at import).
# ``_update_transforms_sha256`` rewrites the ``_EXPECTED_SHA256 = "..."``
# line in ``transforms.py`` in-place.  Pass ``--no-update`` on the CLI
# if you explicitly want the old print-only behaviour (e.g. to compute a
# hash for review without touching the source tree).
_TRANSFORMS_PATH = os.path.join(os.path.dirname(__file__), "transforms.py")
_SHA256_LINE_RE = re.compile(
    r'^(\s*_EXPECTED_SHA256\s*=\s*")[0-9a-fA-F]{64}(".*)$',
    re.MULTILINE,
)


def _update_transforms_sha256(new_sha: str) -> tuple[bool, str]:
    """Rewrite the ``_EXPECTED_SHA256`` line in ``transforms.py``.

    Returns
    -------
    (updated, message)
        ``updated`` is True if the file was changed, False if the line
        was already equal to *new_sha* (idempotent no-op).
    """
    if not os.path.isfile(_TRANSFORMS_PATH):
        return (False, f"transforms.py not found at {_TRANSFORMS_PATH}")
    with open(_TRANSFORMS_PATH, encoding="utf-8") as fh:
        src = fh.read()
    m = _SHA256_LINE_RE.search(src)
    if m is None:
        return (
            False,
            "could not find '_EXPECTED_SHA256 = \"<64 hex>\"' line in "
            "transforms.py -- audit L-2 regex is out of date or the "
            "constant was renamed.",
        )
    old_sha = m.group(0).split('"')[1]
    if old_sha == new_sha:
        return (False, f"transforms.py already at {new_sha[:12]}...")
    new_src = _SHA256_LINE_RE.sub(rf'\g<1>{new_sha}\g<2>', src, count=1)
    with open(_TRANSFORMS_PATH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(new_src)
    return (True, f"transforms.py updated: {old_sha[:12]}... -> {new_sha[:12]}...")


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    update_transforms = True
    positional: list[str] = []
    for arg in argv:
        if arg == "--no-update":
            update_transforms = False
        elif arg.startswith("--"):
            raise SystemExit(f"make_data_pkl: unknown option {arg!r}")
        else:
            positional.append(arg)
    if positional:
        source_dir = os.path.abspath(positional[0])
    else:
        source_dir = _DEFAULT_SOURCE

    print(f"Source  : {source_dir}")
    payload = build_payload(source_dir)
    blob = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
    with open(_OUT_PATH, "wb") as fh:
        fh.write(blob)
    sha = hashlib.sha256(blob).hexdigest()
    print(f"Wrote   : {_OUT_PATH}")
    print(f"Bytes   : {len(blob):,}")
    print(f"Entries : {len(payload)}")
    print(f"SHA-256 : {sha}")
    print()
    if update_transforms:
        changed, msg = _update_transforms_sha256(sha)
        tag = "[updated]" if changed else "[no-op]"
        print(f"{tag} {msg}")
    else:
        print("--no-update requested; paste this into transforms.py manually:")
        print(f"    _EXPECTED_SHA256 = '{sha}'")


if __name__ == "__main__":
    main()
