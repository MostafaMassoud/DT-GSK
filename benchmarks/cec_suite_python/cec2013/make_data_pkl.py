"""One-shot converter: CEC2013 ``data/*.txt`` -> ``data.pkl``.

Mirrors the CEC2017 layout (single pickled dict with ``('__np_array__',
dtype_str, shape, bytes)`` leaf tuples) so that ``transforms.py`` can load a
SHA-256-verified blob instead of touching the filesystem 13 times.

Run from the repo root::

    python -m benchmarks.cec_suite_python.cec2013.make_data_pkl

Obtaining the source files (AUDIT-30)
-------------------------------------
This script reads from a ``data/`` subdirectory **relative to this file**
(i.e. ``benchmarks/cec_suite_python/cec2013/data/``).  That directory is **not**
checked into the repository -- only the pre-built ``data.pkl`` is committed.
To rebuild ``data.pkl`` from scratch:

1. Download the official CEC2013 benchmark data files from the competition
   page (Liang et al., "Problem Definitions and Evaluation Criteria for the
   CEC 2013 Special Session on Real-Parameter Optimization", 2013).  The
   original reference code ships the required text files inside an
   ``input_data/`` directory.
2. Create ``benchmarks/cec_suite_python/cec2013/data/`` and copy the two kinds of
   source files into it (see "Source layout" below).
3. Run this script.  It will also auto-update the ``_EXPECTED_SHA256``
   constant in ``transforms.py`` (pass ``--no-update`` to skip).

Output
------
* ``benchmarks/cec_suite_python/cec2013/data.pkl``
* SHA-256 of the new pickle (auto-written into ``transforms.py``'s
  ``_EXPECTED_SHA256`` constant unless ``--no-update`` is passed).

Source layout (input)
---------------------
* ``data/shift_data.txt``  -- 10 rows x 100 cols of float64
                              (shift vectors for 10 rotation groups)
* ``data/M_D{n}.txt``      -- 10*n rows x n cols of float64
                              (10 stacked nxn rotation matrices)
                              for n in VALID_DIMS = (2, 5, 10, 20, 30,
                              40, 50, 60, 70, 80, 90, 100)

These files correspond to the CEC2013 competition reference source's
``input_data/M_D*.txt`` and ``input_data/shift_data.txt``.  The numeric
content must match the official release exactly -- any modification will
produce a different ``data.pkl`` hash and break the SHA-256 check in
``transforms.py``.

Output layout (in the pickle)
-----------------------------
``{
    "shift_flat": ('__np_array__', '<f8', (1000,), <bytes>),
    "rotations": {
        2:   ('__np_array__', '<f8', (10, 2, 2), <bytes>),
        5:   ('__np_array__', '<f8', (10, 5, 5), <bytes>),
        ...
        100: ('__np_array__', '<f8', (10, 100, 100), <bytes>),
    },
}``

The ``shift_flat`` field preserves the C-level flat-sequential indexing
semantics (see ``transforms._load_shift_flat``); ``_get_shifts_for_dim`` then
slices the first ``10*dim`` doubles per call.
"""

from __future__ import annotations

import hashlib
import os
import pickle
import re
import sys

import numpy as np

VALID_DIMS = (2, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100)

_HERE = os.path.dirname(os.path.abspath(__file__))
_DATA_DIR = os.path.join(_HERE, "data")
_OUT_PATH = os.path.join(_HERE, "data.pkl")


def _np_to_tuple(arr: np.ndarray) -> tuple:
    """Encode an ndarray as ``('__np_array__', dtype_str, shape, bytes)``."""
    arr = np.ascontiguousarray(arr)
    return ("__np_array__", arr.dtype.str, tuple(arr.shape), arr.tobytes())


def build_payload() -> dict:
    """Read all CEC2013 ``data/*.txt`` files into the pickle-ready dict."""
    # --- shift_data.txt ----------------------------------------------------
    shift_path = os.path.join(_DATA_DIR, "shift_data.txt")
    raw_shift = np.loadtxt(shift_path)  # (10, 100)
    if raw_shift.shape != (10, 100):
        raise RuntimeError(
            f"shift_data.txt must be 10x100, got {raw_shift.shape}"
        )
    shift_flat = np.ascontiguousarray(raw_shift.ravel(), dtype=np.float64)

    # --- M_D{n}.txt for each valid dim ------------------------------------
    rotations: dict[int, tuple] = {}
    for dim in VALID_DIMS:
        path = os.path.join(_DATA_DIR, f"M_D{dim}.txt")
        raw = np.loadtxt(path)
        if raw.shape != (10 * dim, dim):
            raise RuntimeError(
                f"M_D{dim}.txt must be {10 * dim}x{dim}, got {raw.shape}"
            )
        block = np.ascontiguousarray(
            raw.reshape(10, dim, dim), dtype=np.float64,
        )
        rotations[dim] = _np_to_tuple(block)

    return {
        "shift_flat": _np_to_tuple(shift_flat),
        "rotations": rotations,
    }


# Audit L-2 (cec2013): automatic SHA-256 update.  Same pattern as
# cec2013lsgo/make_data_pkl.py -- rewrite the ``_EXPECTED_SHA256`` line
# in ``transforms.py`` in-place so the human never has to copy-paste.
# Pass ``--no-update`` on the CLI to restore the old print-only
# behaviour (e.g. to compute a hash for review only).
_TRANSFORMS_PATH = os.path.join(_HERE, "transforms.py")
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
    for arg in argv:
        if arg == "--no-update":
            update_transforms = False
        elif arg.startswith("--"):
            raise SystemExit(f"make_data_pkl: unknown option {arg!r}")

    payload = build_payload()
    blob = pickle.dumps(payload, protocol=pickle.HIGHEST_PROTOCOL)
    with open(_OUT_PATH, "wb") as fh:
        fh.write(blob)
    sha = hashlib.sha256(blob).hexdigest()
    print(f"Wrote   : {_OUT_PATH}")
    print(f"Bytes   : {len(blob):,}")
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
