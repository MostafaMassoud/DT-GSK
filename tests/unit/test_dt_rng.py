"""Known-answer and contract tests for the vendored DT-GSK substream RNG.

The fixture ``data/dt_rng_kat.json`` was generated from the SOURCE DT-GSK
``rng.py`` (loaded standalone), so these tests prove the migrated substream layer
reproduces the source draws bit-for-bit and preserves the append-only contract.
"""
from __future__ import annotations

import dataclasses
import json
from pathlib import Path

import pytest

from gsk_family.optimizers._dt_rng import (
    SUBSTREAM_NAMES,
    RNGStreams,
    _child_seed,
    normalize_generator_name,
)

_FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "dt_rng_kat.json").read_text(encoding="utf-8"))
_SEEDS = [int(s) for s in _FIXTURE["seeds"]]


def test_substream_names_order_is_load_bearing():
    assert SUBSTREAM_NAMES == (
        "init", "core", "ace", "kexp", "div", "bse", "arch", "link", "de",
        "control", "flow", "basin", "trust",
    )
    assert len(set(SUBSTREAM_NAMES)) == len(SUBSTREAM_NAMES)


def test_substream_names_match_dataclass_fields():
    fields = tuple(f.name for f in dataclasses.fields(RNGStreams))
    assert fields == SUBSTREAM_NAMES


def test_prefix_lock_first_nine():
    assert SUBSTREAM_NAMES[:9] == (
        "init", "core", "ace", "kexp", "div", "bse", "arch", "link", "de",
    )


def test_default_generator_is_threefry():
    assert normalize_generator_name(None) == "threefry"
    assert normalize_generator_name("") == "threefry"
    assert normalize_generator_name("SEED") == "seed"


@pytest.mark.parametrize("seed", _SEEDS)
def test_child_seed_matches_source(seed):
    expected = _FIXTURE["child_seeds"][str(seed)]
    got = [_child_seed(seed, i) for i in range(len(SUBSTREAM_NAMES))]
    assert got == expected
    assert _child_seed(seed, 0) == seed  # init stream uses run seed verbatim


@pytest.mark.parametrize("seed", _SEEDS)
def test_random_streams_match_source(seed):
    gen = _FIXTURE["generator"]
    n = _FIXTURE["n_random"]
    streams = RNGStreams.from_seed(seed, gen)
    entry = _FIXTURE["seeds"][str(seed)]
    for name in SUBSTREAM_NAMES:
        got = [float(x) for x in getattr(streams, name).random(n)]
        assert got == entry[name], f"substream {name!r} mismatch at seed {seed}"


@pytest.mark.parametrize("seed", _SEEDS)
def test_integers_permutation_scalar_match_source(seed):
    gen = _FIXTURE["generator"]
    entry = _FIXTURE["seeds"][str(seed)]
    s2 = RNGStreams.from_seed(seed, gen)
    assert [int(x) for x in s2.core.integers(0, 1000, size=4)] == entry["_core_integers_0_1000_4"]
    s3 = RNGStreams.from_seed(seed, gen)
    assert [int(x) for x in s3.ace.permutation(6)] == entry["_ace_permutation_6"]
    s4 = RNGStreams.from_seed(seed, gen)
    assert float(s4.de.random()) == entry["_de_random_scalar"]


def test_substreams_are_independent():
    """Exhausting one substream must not change another's draws."""
    a = RNGStreams.from_seed(777, "threefry")
    b = RNGStreams.from_seed(777, "threefry")
    _ = a.init.random(100)  # advance init on `a` only
    assert list(a.core.random(4)) == list(b.core.random(4))
