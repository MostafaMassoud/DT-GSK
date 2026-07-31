"""Seed policies for reproducible GSK-family experiments."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass

MAX_SAFE_SEED = 2_147_483_646
DEFAULT_BASE_SEED = 20_240_620
SEED_POLICIES = ("reference", "unified", "native", "derived")

REFERENCE_LINEAR_OPTIMIZERS = {"gsk", "atmals-gsk"}
# dt-gsk is always treated as unified (threefry + shared get_cec_seed) under
# every seed policy; it is intentionally excluded from the reference-mode
# linear/product classifications above.
UNIFIED_ONLY_OPTIMIZERS = {"dt-gsk"}
REFERENCE_PRODUCT_OPTIMIZERS = {"agsk", "apgsk", "fdb-agsk"}


@dataclass(frozen=True)
class SeedScheduleRow:
    """One seed schedule row."""

    dim: int
    function: int
    run: int
    seed: int


def get_cec_seed(base_seed: int, dim: int, func: int, run: int) -> int:
    """Return the unified GSK-family CEC seed."""
    return (
        int(base_seed)
        + 1_000_003 * int(dim)
        + 1_000_033 * int(func)
        + 1_000_037 * int(run)
    ) % MAX_SAFE_SEED + 1


def normalize_optimizer_id(optimizer: str) -> str:
    """Return canonical optimizer id."""
    return optimizer.strip().lower().replace("_", "-")


def normalize_seed_policy(policy: str | None) -> str:
    """Return canonical seed policy."""
    if policy is None or str(policy).strip() == "":
        return "unified"
    normalized = str(policy).strip().lower()
    if normalized not in SEED_POLICIES:
        raise ValueError(f"Unsupported seed policy {policy!r}; expected one of {SEED_POLICIES}.")
    return normalized


def reference_run_seed(optimizer: str, base_seed: int, dim: int, func: int, run: int) -> int:
    """Return deterministic reference-mode seed for an optimizer.

    The two legacy formulas replicate the seed schedules hard-coded in the
    original reference implementations so their published tables stay
    traceable: GSK/ATMALS-GSK used the linear ``base + 9973*func + (run-1)``
    schedule, while AGSK/APGSK/FDB-AGSK used the ``dim*func*run`` product
    schedule. They exist only for reference-parity replay; the ``unified``
    policy (``get_cec_seed``) is the canonical schedule for new campaigns.
    """
    opt = normalize_optimizer_id(optimizer)
    if opt in REFERENCE_LINEAR_OPTIMIZERS:
        return int(base_seed) + 9_973 * int(func) + (int(run) - 1)
    if opt in REFERENCE_PRODUCT_OPTIMIZERS:
        return int(dim) * int(func) * int(run)
    return get_cec_seed(base_seed, dim, func, run)


def derive_run_seed(base_seed: int, optimizer: str, suite: str, dim: int, func: int, run: int) -> int:
    """Return native/derived diagnostic hashed seed."""
    opt_code = sum(ord(ch) for ch in normalize_optimizer_id(optimizer))
    suite_code = sum(ord(ch) for ch in suite.strip().lower())
    return (
        int(base_seed)
        + 1_000_003 * opt_code
        + 1_000_033 * suite_code
        + 10_000_019 * int(dim)
        + 10_000_169 * int(func)
        + 10_000_379 * int(run)
    ) % MAX_SAFE_SEED + 1


def seed_for_run(
    policy: str,
    optimizer: str,
    suite: str,
    base_seed: int,
    dim: int,
    func: int,
    run: int,
) -> int:
    """Return the scheduled run seed for a policy."""
    seed_policy = normalize_seed_policy(policy)
    if normalize_optimizer_id(optimizer) in UNIFIED_ONLY_OPTIMIZERS:
        # dt-gsk always uses the unified shared seed, regardless of policy.
        return get_cec_seed(base_seed, dim, func, run)
    if seed_policy == "reference":
        return reference_run_seed(optimizer, base_seed, dim, func, run)
    if seed_policy == "unified":
        return get_cec_seed(base_seed, dim, func, run)
    return derive_run_seed(base_seed, optimizer, suite, dim, func, run)


def effective_rand_generator(policy: str, optimizer: str, requested: str | None = "threefry") -> str:
    """Return the reference-policy generator label to pass to ``RandomContext``.

    ``threefry`` resolves to the bundled counter-based Threefry-4x64-20 generator
    that reproduces the reference ``rng(seed, 'threefry')`` stream bit-for-bit.
    """
    seed_policy = normalize_seed_policy(policy)
    opt = normalize_optimizer_id(optimizer)
    requested_norm = (requested or "threefry").strip().lower()
    if opt in UNIFIED_ONLY_OPTIMIZERS:
        # dt-gsk always uses threefry (unified), regardless of policy.
        return "twister" if requested_norm == "twister" else "threefry"
    if seed_policy == "reference":
        if opt in REFERENCE_PRODUCT_OPTIMIZERS or opt == "atmals-gsk":
            return "seed"
        return "twister"
    if seed_policy == "unified":
        if requested_norm == "twister":
            return "twister"
        return "threefry"
    return requested_norm


def make_seed_schedule(
    policy: str,
    optimizer: str,
    suite: str,
    base_seed: int,
    dimensions: Iterable[int],
    functions: Iterable[int],
    runs: Iterable[int],
) -> list[SeedScheduleRow]:
    """Build a deterministic seed schedule."""
    rows: list[SeedScheduleRow] = []
    for dim in dimensions:
        for func in functions:
            for run in runs:
                rows.append(
                    SeedScheduleRow(
                        dim=int(dim),
                        function=int(func),
                        run=int(run),
                        seed=seed_for_run(policy, optimizer, suite, base_seed, int(dim), int(func), int(run)),
                    )
                )
    return rows


def _schedule_map(rows: Iterable[SeedScheduleRow | Mapping[str, int]]) -> dict[tuple[int, int, int], int]:
    """Convert schedule rows into a comparable cell-to-seed mapping."""
    mapped: dict[tuple[int, int, int], int] = {}
    for row in rows:
        if isinstance(row, SeedScheduleRow):
            key = (row.dim, row.function, row.run)
            seed = row.seed
        else:
            key = (int(row["Dim"]), int(row["Function"]), int(row["Run"]))
            seed = int(row["Seed"])
        mapped[key] = int(seed)
    return mapped


def verify_unified_seed_schedule(
    schedules: Mapping[str, Iterable[SeedScheduleRow | Mapping[str, int]]],
) -> bool:
    """Return True when every optimizer has identical seeds for matching cells."""
    iterator = iter(schedules.items())
    try:
        _, first_rows = next(iterator)
    except StopIteration:
        return True
    expected = _schedule_map(first_rows)
    for _, rows in iterator:
        if _schedule_map(rows) != expected:
            return False
    return True
