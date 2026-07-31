"""Validate CI-critical experiment profile locks and campaign config locks.

Two families of lock live here.

*Profile locks* (the original three) pin the smoke/CI configs so that the
performance and golden-validation harnesses keep measuring what they claim to.

*Campaign locks* pin the configs that produce published evidence. They exist
because a one-character edit between pre-registration and run is otherwise
undetectable: nothing else in the repository would notice if ``runs`` moved from
30 to 25, if ``seed_policy`` slipped to ``reference`` (which silently destroys
the run-level pairing every paired test depends on), or if dt-gsk's LSGO linkage
table lost its ``1000`` entry -- that last one does not error, it warns once and
falls back to the nearest configured dimension, changing every result.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


#: The seven-algorithm panel every published statistic is computed over.
FAMILY_PANEL = ["gsk", "agsk", "apgsk", "fdb-agsk", "atmals-gsk", "egsk", "dt-gsk"]

#: dt-gsk's per-dimension linkage block sizes for the CEC2013LSGO campaign.
#: Locked retroactively: the banks in results/_run_all were produced with this
#: exact table, and the DEFAULT profile has no dim=1000 entry -- a rerun without
#: this config falls back to block_size=10 and does not reproduce them.
LSGO_LINKAGE_BLOCK_SIZE_BY_DIM = {
    1: 1, 5: 5, 6: 5, 7: 5, 10: 5, 12: 5, 13: 5, 15: 5, 20: 5, 22: 5, 26: 5,
    30: 5, 40: 5, 50: 10, 96: 10, 100: 10, 120: 10, 126: 10, 140: 10, 240: 10,
    905: 50, 1000: 50,
}

#: Configs whose worker count is supplied on the command line instead of pinned
#: in the file, so the operator can size the run to the machine. Pinning it in
#: the config would silently override the flag the runbook tells them to pass.
CLI_WORKER_CONFIGS = {
    "configs/family_cec2017.yml",
    "configs/family_cec2011.yml",
    "configs/family_cec2013.yml",
    "configs/family_cec2013lsgo.yml",
    "configs/family_cec2020.yml",
    "configs/agsk_cec2020.yml",
}

#: Shared protocol invariants: every published cell is paired across optimizers
#: by (dimension, function, run) seed identity, and no campaign may overwrite.
_CAMPAIGN_INVARIANTS: dict[str, Any] = {
    "seed": 20240620,
    "seed_policy": "unified",
    "rand_generator": "threefry",
    "max_evaluations": 0,
    "overwrite": False,
    "data_root": "benchmarks/cec_suite_python",
    "output_root": "results/_run_all",
}

REQUIRED_LOCKS: dict[str, dict[str, Any]] = {
    "configs/all_optimizers_smoke.yml": {
        "parallel": True,
        "parallel_backend": "thread",
        "warmup": True,
        "profile": True,
        "seed_policy": "unified",
        "rand_generator": "threefry",
    },
    "configs/golden_validation_smoke.yml": {
        "parallel": True,
        "warmup": True,
        "profile": True,
        "seed_policy": "unified",
        "rand_generator": "threefry",
    },
    "configs/performance_campaign_smoke.yml": {
        "parallel": True,
        "parallel_backend": "thread",
        "warmup": True,
        "profile": True,
        "seed_policy": "unified",
        "rand_generator": "threefry",
    },
    # ---- campaign locks -------------------------------------------------
    "configs/family_cec2017.yml": {
        **_CAMPAIGN_INVARIANTS,
        "optimizers": FAMILY_PANEL,
        "suite": "cec2017",
        "runs": 51,
        "dimensions": [10, 30, 50, 100],
    },
    "configs/family_cec2011.yml": {
        **_CAMPAIGN_INVARIANTS,
        "optimizers": FAMILY_PANEL,
        "suite": "cec2011",
        "runs": 25,
    },
    "configs/family_cec2013.yml": {
        **_CAMPAIGN_INVARIANTS,
        "optimizers": FAMILY_PANEL,
        "suite": "cec2013",
        "runs": 51,
        "dimensions": [10, 30, 50],
    },
    "configs/family_cec2013lsgo.yml": {
        **_CAMPAIGN_INVARIANTS,
        "optimizers": FAMILY_PANEL,
        "suite": "cec2013lsgo",
        "runs": 25,
        "dimensions": "native",
    },
    # Pre-registered 2026-07-28 (SAP Addendum 1). Every value below was fixed
    # before a single CEC2020 datum existed; changing one voids that.
    "configs/family_cec2020.yml": {
        **_CAMPAIGN_INVARIANTS,
        "optimizers": FAMILY_PANEL,
        "suite": "cec2020",
        "functions": "all",
        "runs": 30,
        "dimensions": [5, 10, 15, 20],
    },
    # AGSK-only subset of the same panel. Its ONLY legitimate difference from
    # the family config is the optimizer list; it carried seed_policy:
    # reference until 2026-07-28, which would have made its rows unpairable.
    "configs/agsk_cec2020.yml": {
        **_CAMPAIGN_INVARIANTS,
        "optimizers": ["agsk"],
        "suite": "cec2020",
        "runs": 30,
        "dimensions": [5, 10, 15, 20],
    },
    "configs/dtgsk_cec2013lsgo.yml": {
        **_CAMPAIGN_INVARIANTS,
        "optimizers": ["dt-gsk"],
        "suite": "cec2013lsgo",
        "runs": 25,
        "optimizer_options.linkage_block_size_by_dim": LSGO_LINKAGE_BLOCK_SIZE_BY_DIM,
    },
}

_MISSING = object()


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load one YAML mapping from disk."""
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping.")
    return data


def _lookup(data: dict[str, Any], dotted_key: str) -> Any:
    """Resolve a dotted key path, returning a sentinel when absent."""
    value: Any = data
    for part in dotted_key.split("."):
        if not isinstance(value, dict) or part not in value:
            return _MISSING
        value = value[part]
    return value


def validate_profile_locks(root: Path) -> list[str]:
    """Return profile-lock mismatches for CI-critical and campaign configs."""
    failures: list[str] = []
    for relative, expected_values in REQUIRED_LOCKS.items():
        path = root / relative
        if not path.exists():
            failures.append(f"{relative}: missing")
            continue
        data = _load_yaml(path)
        for key, expected in expected_values.items():
            observed = _lookup(data, key)
            if observed is _MISSING:
                failures.append(f"{relative}: expected {key}={expected!r}, key absent")
            elif observed != expected:
                failures.append(
                    f"{relative}: expected {key}={expected!r}, observed {observed!r}"
                )
        if relative in CLI_WORKER_CONFIGS:
            if "workers" in data:
                failures.append(
                    f"{relative}: workers must stay unset -- it is passed as "
                    f"--workers on the command line, and pinning it here would "
                    f"silently override that flag (observed {data['workers']!r})"
                )
            continue
        workers = int(data.get("workers", 0) or 0)
        if bool(data.get("parallel", False)) and workers <= 0:
            failures.append(f"{relative}: parallel configs must pin workers > 0")
    return failures


def main(argv: list[str] | None = None) -> int:
    """Validate profile locks and return a process exit code."""
    parser = argparse.ArgumentParser(description="Validate GSK profile-lock configs.")
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root.")
    args = parser.parse_args(argv)

    failures = validate_profile_locks(args.root.resolve())
    if failures:
        print("Profile-lock validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print(f"Profile-lock validation passed for {len(REQUIRED_LOCKS)} configs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
