"""F1/F8 at D=5 and D=15: pinned against the C++ oracle that validated them.

These four cells were refused from the suite's beginning as "unavailable in the
reference data distribution". Investigation (2026-07-26) established the full
story: the official CEC2020 data distribution uses shuffle_data_<id>_D<dim>.txt
files as per-dimension AVAILABILITY MARKERS, loads them for every function, but
mathematically consumes them only for the hybrids (internal ids 4/6/16). Ids 1
and 22 ship no marker at D5/D15, so the MEX-faithful C++ loader could not
construct those cells and no ground truth was ever generated -- even though the
AGSK paper's own 5D tables report F1 and F8 results, proving the competition
itself ran them.

Validation that lifted the guard: the in-repo C++ oracle
(01-GSK_Family_MATLAB_v1.0/.../cec_suite_cpp/cec2020) was built with gcc 13.2
and fed dummy marker files; output was proven BIT-IDENTICAL between an identity
permutation and a reversed one (the marker content is never consumed for these
ids). Against that oracle, all four target cells agreed with this Python suite
to worst relative error 1.258e-15 -- three orders of magnitude inside the
repository's committed acceptance criterion (rel=1e-12,
test_cec2020_composition_zero_vector_matches_cpp_oracle) -- and the four
already-trusted control cells (F1/F8 at D10/D20) showed the same profile.

The pins below are the oracle's outputs (hex-exact float64 bits) on
deterministic splitmix64 probe points. The test asserts the same rel<=1e-12
criterion the repository already uses for cec2020 oracle agreement, and
additionally checks the current values have not drifted from the values that
passed validation (8-ULP band; the validated agreement itself spans up to 6).
"""

from __future__ import annotations

import numpy as np
import pytest

from gsk_family.benchmark_adapter.factory import make_problem

_MASK = (1 << 64) - 1
_REL_CRITERION = 1e-12  # the repo's committed cec2020 oracle-agreement criterion

#: (func, dim, point_index) -> oracle float64 bits, generated 2026-07-26 from the
#: in-repo C++ oracle (marker-invariance proven; see module docstring).
_ORACLE_BITS = {
    (1, 5, 0): 0x4210D3604C67FE5F, (1, 5, 1): 0x420249DF0871CCC0,
    (1, 5, 2): 0x41FE02EDEA675AFB, (1, 5, 3): 0x4212137F8DD7A13D,
    (1, 5, 4): 0x41F544AE1477BCA5, (1, 5, 5): 0x421B28F30D1FB860,
    (1, 5, 6): 0x41E82D4732501A40, (1, 5, 7): 0x41FC1F87E75BE6DF,
    (1, 15, 0): 0x42355C2D16DDDAFA, (1, 15, 1): 0x422D28B59222CCF9,
    (1, 15, 2): 0x4242BA34CD885A82, (1, 15, 3): 0x423F392BB723693F,
    (1, 15, 4): 0x42439FEC9FB28697, (1, 15, 5): 0x4231A00BB0E79356,
    (1, 15, 6): 0x423D0C5211F17C5C, (1, 15, 7): 0x423770A764F12448,
    (8, 5, 0): 0x40A248415E998F61, (8, 5, 1): 0x40A5521C4E2506D0,
    (8, 5, 2): 0x40B2F93BF451E9EC, (8, 5, 3): 0x40ABE9B50AF789C8,
    (8, 5, 4): 0x40A58B1D9B5F0C75, (8, 5, 5): 0x40B18F355C24E268,
    (8, 5, 6): 0x40B0F16DE9FA4622, (8, 5, 7): 0x40B2826DCB07F678,
    (8, 15, 0): 0x40BFD670DC33184B, (8, 15, 1): 0x40C06D115A1EF944,
    (8, 15, 2): 0x40C4C2C02AC6C628, (8, 15, 3): 0x40C19F8DF1286DDC,
    (8, 15, 4): 0x40C003AFB4A6166E, (8, 15, 5): 0x40C0A1B2B603B855,
    (8, 15, 6): 0x40BD672664C72AA6, (8, 15, 7): 0x40C26FCF81429E5C,
}


def _splitmix64_points(func_id: int, dim: int, n: int = 8) -> np.ndarray:
    """The oracle's deterministic probe points, regenerated exactly."""
    s = (0x20200000 + func_id * 100 + dim) & _MASK
    out = np.empty((n, dim), dtype=np.float64)
    for p in range(n):
        for i in range(dim):
            s = (s + 0x9E3779B97F4A7C15) & _MASK
            z = s
            z = ((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9) & _MASK
            z = ((z ^ (z >> 27)) * 0x94D049BB133111EB) & _MASK
            z = (z ^ (z >> 31)) & _MASK
            out[p, i] = -100.0 + 200.0 * ((z >> 11) * (1.0 / 9007199254740992.0))
    return out


def _ulp_distance(a: float, b: float) -> int:
    ia = int(np.float64(a).view(np.uint64))
    ib = int(np.float64(b).view(np.uint64))
    if ia >= 1 << 63:
        ia = (1 << 63) - ia
    if ib >= 1 << 63:
        ib = (1 << 63) - ib
    return abs(ia - ib)


@pytest.mark.parametrize("func_id,dim", [(1, 5), (1, 15), (8, 5), (8, 15)])
def test_restored_cell_matches_cpp_oracle(func_id: int, dim: int) -> None:
    """Each restored cell agrees with its validation-time oracle values."""
    problem = make_problem("cec2020", func_id, dim)
    values = np.asarray(problem.evaluate(_splitmix64_points(func_id, dim))).ravel()
    for p, v in enumerate(values):
        oracle = float(np.uint64(_ORACLE_BITS[(func_id, dim, p)]).view(np.float64))
        rel = abs(v - oracle) / max(abs(oracle), 1e-300)
        assert rel <= _REL_CRITERION, (
            f"F{func_id} D={dim} p{p}: rel {rel:.3e} vs oracle criterion "
            f"{_REL_CRITERION:g} ({v!r} vs {oracle!r})"
        )
        # The validated Python<->C++ agreement itself spans up to 6 ULP (F8 D=5;
        # NumPy-vectorized vs scalar C++ summation order), so the drift band must
        # admit the measured agreement: 8 = validated worst (6) + small headroom.
        # An earlier revision set 4 and failed against its own validation data.
        assert _ulp_distance(v, oracle) <= 8, (
            f"F{func_id} D={dim} p{p}: drifted beyond the 8-ULP band around the "
            f"validation-time oracle ({v!r} vs {oracle!r}); investigate before re-pinning"
        )


def test_protocol_exclusions_still_refused() -> None:
    """Lifting the data guard must not have loosened the protocol guard."""
    for func_id in (6, 7):
        with pytest.raises(ValueError, match="not defined at D=5"):
            make_problem("cec2020", func_id, 5)
