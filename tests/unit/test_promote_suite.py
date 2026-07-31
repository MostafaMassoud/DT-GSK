"""Refusal and dry-run semantics of papers/scripts/promote_suite.py.

These tests run against the REAL staging trees read-only: the dry run must
write nothing, and the cec2020 stage-2 lock must hold for as long as its
campaign is incomplete. Nothing here ever executes an actual promotion.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

_ROOT = Path(__file__).resolve().parents[2]
_SPEC = importlib.util.spec_from_file_location(
    "promote_suite", _ROOT / "papers" / "scripts" / "promote_suite.py",
)
promote_suite = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(promote_suite)


def _tree_snapshot(root: Path) -> set[Path]:
    return {p for p in root.rglob("*") if p.is_file()} if root.exists() else set()


def test_unknown_suite_is_refused() -> None:
    with pytest.raises(SystemExit):
        promote_suite.main(["--suite", "cec2099"])


def test_cec2020_locked_while_campaign_incomplete() -> None:
    """Stage-2 lock: with any bank absent/partial/uncommitted, refuse."""
    if (promote_suite.REF / "cec2020").exists():
        pytest.skip("cec2020 already promoted; lock test is moot")
    with pytest.raises(SystemExit) as exc:
        promote_suite.main(["--suite", "cec2020"])
    # The refusal must be a promotion refusal, not a crash.
    assert "REFUSED" in str(exc.value)


def test_dry_run_writes_nothing() -> None:
    """The cec2013lsgo dry run gates + plans but leaves the tree untouched."""
    if (promote_suite.REF / "cec2013lsgo").exists():
        pytest.skip("cec2013lsgo already promoted; dry-run precondition gone")
    before_ref = _tree_snapshot(promote_suite.REF)
    before_gov = _tree_snapshot(promote_suite.GOV)
    rc = promote_suite.main(["--suite", "cec2013lsgo", "--dry-run"])
    assert rc == 0
    assert _tree_snapshot(promote_suite.REF) == before_ref
    assert _tree_snapshot(promote_suite.GOV) == before_gov


def test_existing_destination_is_refused(tmp_path, monkeypatch) -> None:
    """A second promotion into an existing suite directory must refuse."""
    fake_ref = tmp_path / "ref"
    (fake_ref / "cec2013lsgo").mkdir(parents=True)
    monkeypatch.setattr(promote_suite, "REF", fake_ref)
    with pytest.raises(SystemExit) as exc:
        promote_suite.main(["--suite", "cec2013lsgo"])
    assert "already exists" in str(exc.value)
