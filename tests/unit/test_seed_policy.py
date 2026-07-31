from __future__ import annotations

from gsk_family.runners.seed_policy import (
    DEFAULT_BASE_SEED,
    derive_run_seed,
    effective_rand_generator,
    get_cec_seed,
    make_seed_schedule,
    reference_run_seed,
    seed_for_run,
    verify_unified_seed_schedule,
)


def test_unified_seed_formula_matches_documented_example() -> None:
    assert get_cec_seed(20240620, 30, 7, 12) == 69241386


def test_unified_seed_formula_range_is_safe() -> None:
    seed = get_cec_seed(2_147_483_646, 1000, 30, 999)
    assert 1 <= seed <= 2_147_483_646


def test_reference_seed_rules_match_optimizer_families() -> None:
    assert reference_run_seed("gsk", DEFAULT_BASE_SEED, 30, 7, 12) == DEFAULT_BASE_SEED + 9973 * 7 + 11
    assert reference_run_seed("atmals-gsk", DEFAULT_BASE_SEED, 30, 7, 12) == DEFAULT_BASE_SEED + 9973 * 7 + 11
    assert reference_run_seed("agsk", DEFAULT_BASE_SEED, 30, 7, 12) == 30 * 7 * 12
    assert reference_run_seed("apgsk", DEFAULT_BASE_SEED, 30, 7, 12) == 30 * 7 * 12
    assert reference_run_seed("fdb-agsk", DEFAULT_BASE_SEED, 30, 7, 12) == 30 * 7 * 12


def test_seed_for_run_selects_policy() -> None:
    unified = seed_for_run("unified", "gsk", "cec2017", DEFAULT_BASE_SEED, 30, 7, 12)
    reference = seed_for_run("reference", "gsk", "cec2017", DEFAULT_BASE_SEED, 30, 7, 12)
    derived = seed_for_run("derived", "gsk", "cec2017", DEFAULT_BASE_SEED, 30, 7, 12)
    native = seed_for_run("native", "gsk", "cec2017", DEFAULT_BASE_SEED, 30, 7, 12)

    assert unified == get_cec_seed(DEFAULT_BASE_SEED, 30, 7, 12)
    assert reference == reference_run_seed("gsk", DEFAULT_BASE_SEED, 30, 7, 12)
    assert derived == derive_run_seed(DEFAULT_BASE_SEED, "gsk", "cec2017", 30, 7, 12)
    assert native == derived


def test_effective_rand_generator_policy_rules() -> None:
    assert effective_rand_generator("reference", "gsk", "threefry") == "twister"
    assert effective_rand_generator("reference", "agsk", "threefry") == "seed"
    assert effective_rand_generator("unified", "gsk", "seed") == "threefry"
    assert effective_rand_generator("unified", "gsk", "twister") == "twister"
    assert effective_rand_generator("derived", "gsk", "seed") == "seed"


def test_verify_unified_seed_schedule_detects_mismatch() -> None:
    schedule_a = make_seed_schedule(
        "unified",
        "gsk",
        "cec2017",
        DEFAULT_BASE_SEED,
        dimensions=[10],
        functions=[1, 3],
        runs=[1, 2],
    )
    schedule_b = make_seed_schedule(
        "unified",
        "agsk",
        "cec2017",
        DEFAULT_BASE_SEED,
        dimensions=[10],
        functions=[1, 3],
        runs=[1, 2],
    )
    assert verify_unified_seed_schedule({"gsk": schedule_a, "agsk": schedule_b})

    bad = list(schedule_b)
    bad[0] = type(bad[0])(bad[0].dim, bad[0].function, bad[0].run, bad[0].seed + 1)
    assert not verify_unified_seed_schedule({"gsk": schedule_a, "agsk": bad})
