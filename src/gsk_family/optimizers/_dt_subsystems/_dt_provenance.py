"""Minimal provenance helpers for the migrated DT-GSK core.

Vendored from the source DT-GSK ``profile_locking.py`` but trimmed to the only
two symbols the optimizer core needs — :func:`current_git_commit` and
:func:`stable_hash` — both used for non-algorithmic result/telemetry stamping.
The source's config/profile-coupled hashing functions (which imported the
experiment-level ``Config`` and ``profiles``) are intentionally omitted, so this
module has no intra-package dependencies and cannot affect optimizer numerics.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import asdict, is_dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import numpy as np


def _json_ready(obj: Any) -> Any:
    """Return a JSON-stable representation (paths->str, dataclasses expanded)."""
    if isinstance(obj, Path):
        return str(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    if isinstance(obj, np.generic):
        return obj.item()
    if is_dataclass(obj):
        return _json_ready(asdict(obj))
    if isinstance(obj, dict):
        return {str(k): _json_ready(v) for k, v in sorted(obj.items(), key=lambda kv: str(kv[0]))}
    if isinstance(obj, (list, tuple)):
        return [_json_ready(v) for v in obj]
    return obj


def stable_hash(obj: Any, *, prefix_len: int = 16) -> str:
    """Return a stable SHA-256 prefix hash of a JSON-stable view of ``obj``."""
    payload = json.dumps(_json_ready(obj), sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[: int(prefix_len)]


@lru_cache(maxsize=1)
def current_git_commit(*, repo_root: str | None = None) -> str:
    """Return a short git commit hash when available, else ``"unknown"``."""
    root = Path(repo_root).resolve() if repo_root is not None else Path(__file__).resolve().parents[2]
    git_dir = root / ".git"
    if not git_dir.exists():
        return "unknown"
    try:
        out = subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return out or "unknown"
    except (OSError, subprocess.SubprocessError):
        return "unknown"


__all__ = ["current_git_commit", "stable_hash"]
