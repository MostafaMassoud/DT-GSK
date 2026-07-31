"""The two optimizer registries must not drift apart.

There are two: ``optimizers.OPTIMIZER_IDS`` (what the CLI and config validator
will *accept*) and ``runners.run_experiment.OPTIMIZER_FUNCTIONS`` (what can
actually be *dispatched*). Registering in one but not the other produced a
working, tested, committed optimizer that died at the command line with
"Unsupported optimizer(s): mos-cec2013lsgo, shade-ils, decc-g" -- a failure no
unit test caught because every test called OPTIMIZER_FUNCTIONS directly and
never went through the CLI's validation path.
"""

from __future__ import annotations

from gsk_family.optimizers import (
    EXTERNAL_OPTIMIZER_IDS,
    FAMILY_OPTIMIZER_IDS,
    OPTIMIZER_IDS,
)
from gsk_family.runners.run_experiment import OPTIMIZER_FUNCTIONS


def test_every_accepted_id_is_dispatchable() -> None:
    """Anything the config validator accepts must have a dispatch entry."""
    missing = sorted(set(OPTIMIZER_IDS) - set(OPTIMIZER_FUNCTIONS))
    assert not missing, (
        f"accepted by OPTIMIZER_IDS but not dispatchable via OPTIMIZER_FUNCTIONS: "
        f"{missing}. The CLI would accept these and then fail at dispatch."
    )


def test_every_dispatchable_id_is_accepted() -> None:
    """Anything dispatchable must be accepted by the config validator."""
    missing = sorted(set(OPTIMIZER_FUNCTIONS) - set(OPTIMIZER_IDS))
    assert not missing, (
        f"dispatchable via OPTIMIZER_FUNCTIONS but rejected by OPTIMIZER_IDS: "
        f"{missing}. `--optimizer <id>` fails with 'Unsupported optimizer(s)' "
        f"even though the implementation is present and working."
    )


def test_family_panel_is_exactly_seven() -> None:
    """The statistical panel is seven methods; externals must not leak into it."""
    assert len(FAMILY_OPTIMIZER_IDS) == 7, FAMILY_OPTIMIZER_IDS
    assert not set(FAMILY_OPTIMIZER_IDS) & set(EXTERNAL_OPTIMIZER_IDS)
    assert set(OPTIMIZER_IDS) == set(FAMILY_OPTIMIZER_IDS) | set(EXTERNAL_OPTIMIZER_IDS)


def test_ids_are_unique() -> None:
    """No duplicate ids in either registry."""
    assert len(OPTIMIZER_IDS) == len(set(OPTIMIZER_IDS))
