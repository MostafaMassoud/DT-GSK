"""Top-level namespace for bundled benchmark suites and reference evidence."""

from __future__ import annotations

import sys

from benchmarks import cec_suite_python as cec_suite


# Compatibility for stale Numba caches and external scripts created before the
# Python benchmark package was renamed to ``cec_suite_python``. Runtime code uses
# the explicit new package name; this alias only keeps old serialized module
# paths importable.
sys.modules.setdefault(__name__ + ".cec_suite", cec_suite)
