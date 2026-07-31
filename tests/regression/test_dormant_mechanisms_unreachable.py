"""C-003 / M-025: dormant research hooks are unreachable from every public path.

The `research_oracle_blocks` / `research_oracle_basis` parameters of
``dt_gsk_optimize`` are retained as keyword-only research hooks. They are NOT
deleted (the optimizer core is hash-pinned by the algorithm freeze manifest, and
editing it would invalidate the frozen evidence), so this test proves instead
that no configuration, profile, CLI, or adapter path can activate them.

If a future change makes them reachable, that is a trajectory-affecting change
and requires a new evidence release -- this test is the tripwire.
"""
from __future__ import annotations

import dataclasses
import inspect
import re
from pathlib import Path

import pytest

from gsk_family.optimizers import _dt_core, _dt_profiles, dt_gsk

HOOKS = ("research_oracle_blocks", "research_oracle_basis")
SRC = Path(_dt_core.__file__).resolve().parent


def test_hooks_exist_but_default_to_none():
    """They are keyword-only and inert unless explicitly passed."""
    sig = inspect.signature(_dt_core.dt_gsk_optimize)
    for hook in HOOKS:
        assert hook in sig.parameters, f"{hook} vanished; update the dormant inventory"
        p = sig.parameters[hook]
        assert p.kind is inspect.Parameter.KEYWORD_ONLY, f"{hook} must stay keyword-only"
        assert p.default is None, f"{hook} must default to None (inert)"


def test_hooks_are_not_configuration_fields():
    """No dataclass config surface exposes them, so no YAML/CLI can set them."""
    cfg_cls = getattr(_dt_core, "DTGSKConfig", None)
    if cfg_cls is None or not dataclasses.is_dataclass(cfg_cls):
        pytest.skip("DTGSKConfig not a dataclass in this build")
    names = {f.name for f in dataclasses.fields(cfg_cls)}
    for hook in HOOKS:
        assert hook not in names, f"{hook} became a config field -> reachable"


def test_no_profile_sets_the_hooks():
    """The frozen profile builders never populate them."""
    text = Path(_dt_profiles.__file__).read_text(encoding="utf-8")
    for hook in HOOKS:
        assert hook not in text, f"{hook} referenced in _dt_profiles.py"


def test_public_adapter_does_not_forward_arbitrary_kwargs():
    """dt_gsk.py must call the core with an explicit, closed argument list."""
    text = Path(dt_gsk.__file__).read_text(encoding="utf-8")
    for hook in HOOKS:
        assert hook not in text, f"{hook} referenced in the public adapter"
    # every call into the core passes named arguments only -- no **kwargs splat
    for call in re.findall(r"dt_gsk_optimize\((.*?)\)", text, re.DOTALL):
        assert "**" not in call, (
            "public adapter forwards **kwargs into the core; a caller could "
            "then inject a dormant research hook"
        )


def test_no_runner_or_cli_path_references_the_hooks():
    """Nothing in the shipped runner/CLI/config surface mentions them."""
    root = SRC.parent            # src/gsk_family
    offenders = []
    for py in root.rglob("*.py"):
        if py.name == "_dt_core.py":          # the sole legitimate definition site
            continue
        body = py.read_text(encoding="utf-8", errors="ignore")
        if any(h in body for h in HOOKS):
            offenders.append(str(py.relative_to(root)))
    assert not offenders, f"dormant hooks referenced outside the core: {offenders}"


def test_ism_subspace_local_search_stays_disabled_in_the_frozen_profile():
    """The ISM-block subspace LS is implemented but must not be enabled."""
    for dim in (10, 30, 50, 100):
        cfg = _dt_profiles.build_pub_config(dim, seed=20240620, max_nfes=10_000 * dim)
        method = getattr(cfg, "local_search_method", None)
        if method is None:
            pytest.skip("local_search_method not exposed in this build")
        assert method == "coordinate", (
            f"D={dim}: frozen profile must run the coordinate local search; "
            f"got {method!r}. Enabling the subspace variant changes the "
            f"trajectory and requires a new evidence release."
        )
        assert getattr(cfg, "local_search_auto_subspace", False) is False, (
            f"D={dim}: auto-subspace promotion must stay off"
        )


def test_trust_region_governor_is_removed_and_its_telemetry_pinned():
    """M-024: the TR-GSK governor was removed; only a pinned telemetry column remains.

    The column `terra_trust_clip_rate` is deliberately retained so the emitted
    schema stays stable, but it must never be *computed* -- every assignment has
    to be the literal 0.0. A computed value would mean the governor is back, which
    is trajectory-affecting and needs a new evidence release.
    """
    body = (SRC / "_dt_core.py").read_text(encoding="utf-8", errors="ignore")

    # PEP8 spacing separates a real assignment ("x = 0.0") from a keyword
    # argument that merely forwards the pinned value ("x=float(x),").
    assigns = re.findall(r"^\s*terra_trust_clip_rate\s+=\s+(.+?)\s*$",
                         body, re.MULTILINE)
    assert assigns, "telemetry column vanished; update the dormant inventory"
    for rhs in assigns:
        assert rhs == "0.0", (
            f"terra_trust_clip_rate is computed ({rhs!r}) -- the trust-region "
            f"governor appears to be active again"
        )

    # no enable flag / clipping logic may reappear
    for pattern in (r"\btrust_enabled\b", r"\btrust_region\b", r"\bTR_GSK\b"):
        live = [ln for ln in body.splitlines()
                if re.search(pattern, ln) and not ln.strip().startswith("#")]
        assert not live, f"trust-region logic resurfaced ({pattern}): {live[:2]}"
