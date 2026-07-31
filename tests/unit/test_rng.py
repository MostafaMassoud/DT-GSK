from __future__ import annotations

import numpy as np
import pytest

from gsk_family.common.rng import (
    RandomContext,
    create_fair_start,
    effective_python_generator,
    init_population,
)
from gsk_family.common.threefry_rng import ThreefryGenerator
from gsk_family.runners.seed_policy import MAX_SAFE_SEED


def test_generator_mapping_documents_python_native_equivalents() -> None:
    assert effective_python_generator("threefry") == "threefry"
    assert effective_python_generator("twister") == "twister"
    assert effective_python_generator("seed") == "mcg16807"
    # Only threefry, twister, and seed are supported; everything else is rejected.
    for removed in ("state", "mt19937", "philox", "pcg64", "default"):
        with pytest.raises(ValueError, match="Unsupported RNG"):
            effective_python_generator(removed)


def test_threefry_reproduces_reference_stream() -> None:
    # Known-answer draws from the external reference rng(36240853, 'threefry').
    rng = RandomContext(36240853, "threefry")
    expected = [
        0.62232472400163363,
        0.90044585359382412,
        0.52093254454396842,
        0.11974483490432918,
        0.29883890686202602,
    ]
    np.testing.assert_allclose(rng.random((5,)), expected, rtol=0.0, atol=1e-15)


def test_threefry_matrix_fill_is_column_major() -> None:
    # Reference rand(m, n) fills column-major; flattening in Fortran order
    # must recover the raw scalar stream for the same seed.
    raw = RandomContext(2024, "threefry").random((6,))
    matrix = RandomContext(2024, "threefry").random((2, 3))
    np.testing.assert_array_equal(np.asarray(matrix).flatten(order="F"), raw)


def test_threefry_randi_matches_reference() -> None:
    # randi(100, 1, 8) from the external reference rng(36240853, 'threefry').
    rng = RandomContext(36240853, "threefry")
    expected = [63, 91, 53, 12, 30, 62, 18, 42]
    np.testing.assert_array_equal(np.asarray(rng.randi(100, size=8)), expected)


def test_threefry_randperm_matches_reference() -> None:
    # randperm(10) from the reference; permutation is 0-based, so +1 to compare.
    rng = RandomContext(36240853, "threefry")
    expected = [4, 7, 5, 8, 9, 3, 6, 1, 10, 2]
    np.testing.assert_array_equal(np.asarray(rng.permutation(10)) + 1, expected)


# Known-answer draws for seeds at the top of the unified cell-seed range
# (1..MAX_SAFE_SEED). For these seeds the Threefry counter's high word exceeds
# int64 max, which previously made the Numba kernel raise "int too big to
# convert" because the counter words were boxed as int64 instead of uint64.
# Values were computed from the (overflow-safe) pure-Python kernel.
_TOP_SEED_KAT = {
    2147483640: [0.47468552309968826, 0.20243528499081864, 0.584188445267141, 0.141573755524819],
    2147483641: [0.8023204547587107, 0.5645347275151096, 0.7174769560725629, 0.17688680419700342],
    2147483642: [0.9221191564494224, 0.8194235967101524, 0.3384223042695278, 0.16293878167851172],
    2147483643: [0.9642497783035212, 0.6200871318065317, 0.894148513320724, 0.6423553716376789],
    2147483644: [0.17989199168714098, 0.9966109417181469, 0.8838319585754056, 0.15664214371230056],
    2147483645: [0.3015623520451203, 0.0641732590778189, 0.34199650897349265, 0.31110667800845326],
    2147483646: [0.022545800434594865, 0.5250766802852321, 0.5985575843881217, 0.4782472388051705],
}


def test_threefry_does_not_overflow_at_top_of_seed_range() -> None:
    # MAX_SAFE_SEED is the largest seed the unified policy can emit; it (and the
    # handful below it) must not raise OverflowError in the Numba kernel.
    assert MAX_SAFE_SEED == 2147483646
    for seed, expected in _TOP_SEED_KAT.items():
        direct = ThreefryGenerator(seed).random(4)
        np.testing.assert_allclose(direct, expected, rtol=0.0, atol=1e-15)
        # The full RandomContext path (threefry label) must agree too.
        viacontext = RandomContext(seed, "threefry").random((4,))
        np.testing.assert_array_equal(np.asarray(viacontext), np.asarray(direct))


def test_twister_reproduces_reference_stream() -> None:
    # rand(5,1) from the external reference rng(5, 'twister').
    rng = RandomContext(5, "twister")
    expected = [
        0.221993171089739,
        0.870732306177376,
        0.206719155339426,
        0.918610907937922,
        0.488411188794829,
    ]
    np.testing.assert_allclose(rng.random((5,)), expected, rtol=0.0, atol=1e-15)


def test_seed_mcg16807_reproduces_reference_stream() -> None:
    # rand(5,1) from the reference RandStream('mcg16807', 'Seed', 5).
    rng = RandomContext(5, "seed")
    expected = [
        0.564544678928584,
        0.302418752714255,
        0.751976868487884,
        0.475228675862415,
        0.168355219610201,
    ]
    np.testing.assert_allclose(rng.random((5,)), expected, rtol=0.0, atol=1e-15)


def test_seed_mcg16807_overflow_fold_for_large_seeds() -> None:
    # seed 32768 makes (seed << 16) == 2**31 exactly, exercising the seeding fold
    # x0 = (seed << 16) mod (2**31 - 2**15); reference RandStream('mcg16807','Seed',32768).
    rng = RandomContext(32768, "seed")
    expected = [
        0.256454467892858,
        0.230241875271426,
        0.675197686848788,
        0.0475228675862415,
        0.71683552196102,
    ]
    np.testing.assert_allclose(rng.random((5,)), expected, rtol=0.0, atol=1e-15)


def test_reference_generators_are_distinct_and_deterministic() -> None:
    # threefry, twister (MT19937) and seed (mcg16807) must be different
    # algorithms, each deterministic for a given seed.
    labels = ["threefry", "twister", "seed"]
    streams = {}
    for label in labels:
        a = np.asarray(RandomContext(2024, label).random(6))
        b = np.asarray(RandomContext(2024, label).random(6))
        np.testing.assert_array_equal(a, b)  # deterministic
        streams[label] = tuple(a.tolist())
    assert len(set(streams.values())) == len(labels)  # all distinct


def test_twister_and_seed_matrix_fill_is_column_major() -> None:
    for label in ("twister", "seed"):
        raw = np.asarray(RandomContext(2024, label).random(6))
        matrix = np.asarray(RandomContext(2024, label).random((2, 3)))
        np.testing.assert_array_equal(matrix.flatten(order="F"), raw)


def test_random_context_replay_is_deterministic() -> None:
    a = RandomContext(123, "twister")
    b = RandomContext(123, "twister")

    np.testing.assert_allclose(a.random((3, 4)), b.random((3, 4)))
    np.testing.assert_array_equal(a.randi(1, 5, size=(10,)), b.randi(1, 5, size=(10,)))


def test_random_context_state_copy_restore() -> None:
    rng = RandomContext(456, "threefry")
    _ = rng.random((2, 2))
    state = rng.copy_state()
    expected = rng.random((3,))

    rng.restore_state(state)
    actual = rng.random((3,))

    np.testing.assert_allclose(actual, expected)


def test_randi_is_inclusive_and_randperm_is_zero_based() -> None:
    rng = RandomContext(789, "twister")

    draws = rng.randi(3, size=(100,))
    assert np.min(draws) >= 1
    assert np.max(draws) <= 3

    draws2 = rng.randi(4, 7, size=(100,))
    assert np.min(draws2) >= 4
    assert np.max(draws2) <= 7

    perm = rng.permutation(8)
    np.testing.assert_array_equal(np.sort(perm), np.arange(8))


def test_init_population_draws_within_bounds() -> None:
    rng = RandomContext(100, "twister")
    lb = np.array([-1.0, 10.0])
    ub = np.array([1.0, 20.0])

    pop = init_population(rng, 5, 2, lb, ub)

    assert pop.shape == (5, 2)
    assert np.all(pop[:, 0] >= -1.0)
    assert np.all(pop[:, 0] <= 1.0)
    assert np.all(pop[:, 1] >= 10.0)
    assert np.all(pop[:, 1] <= 20.0)


def test_fair_start_captures_post_initialization_state() -> None:
    seed = 20240620
    lb = np.array([-5.0, -5.0, -5.0])
    ub = np.array([5.0, 5.0, 5.0])

    fair = create_fair_start(seed, "threefry", 4, 3, lb, ub)
    direct = RandomContext(seed, "threefry")
    expected_x0 = init_population(direct, 4, 3, lb, ub)
    expected_next = direct.random((6,))

    restored = RandomContext(seed, "threefry")
    restored.restore_state(fair.rng_state_after_initialization)
    actual_next = restored.random((6,))

    np.testing.assert_allclose(fair.initial_population, expected_x0)
    np.testing.assert_allclose(actual_next, expected_next)
    assert fair.rng_info.requested_generator == "threefry"
    assert fair.rng_info.effective_generator == "threefry"


def test_random_context_rejects_unknown_generator() -> None:
    with pytest.raises(ValueError, match="Unsupported RNG"):
        RandomContext(1, "unknown")

