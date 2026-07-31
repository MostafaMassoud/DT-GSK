"""Byte-identity test for the ported DT-GSK ``pub`` profile config builder.

The fixture ``fixtures/dt_config_kat.json`` was generated from the SOURCE
project's ``Config -> apply_step2_profile -> _build_dt_gsk_config`` chain, so
this proves ``build_pub_config`` reproduces the source's per-dimension
``DTGSKConfig`` field-for-field.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from gsk_family.optimizers._dt_profiles import build_pub_config

_FIXTURE = json.loads(
    (Path(__file__).parent / "fixtures" / "dt_config_kat.json").read_text(encoding="utf-8")
)
_DIMS = [int(d) for d in _FIXTURE["configs"]]


def _normalize(obj: object) -> object:
    """JSON-roundtrip so tuples->lists and int dict keys->str match the fixture."""
    return json.loads(json.dumps(obj, sort_keys=True))


@pytest.mark.parametrize("dim", _DIMS)
def test_pub_config_matches_source(dim: int) -> None:
    cfg = build_pub_config(
        dim,
        seed=int(_FIXTURE["seed"]),
        max_nfes=10_000 * dim,
        bounds=tuple(_FIXTURE["bounds"]),
    )
    built = _normalize(dataclasses.asdict(cfg))
    expected = _FIXTURE["configs"][str(dim)]
    assert isinstance(built, dict)
    # Contract: every SOURCE field is reproduced field-for-field. New DT-GSK
    # additions not present in the source baseline (e.g. the deep-stall multi-start
    # fields) are outside this parity contract -- their byte-safety is covered by
    # the byte-stability KAT and their own tests.
    diffs = {
        key: {"built": built.get(key), "source": expected.get(key)}
        for key in set(expected)
        if built.get(key) != expected.get(key)
    }
    assert not diffs, f"pub config mismatch at dim={dim}:\n" + json.dumps(diffs, indent=2, sort_keys=True)
