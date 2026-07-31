"""Union strict-inventory semantics of papers/scripts/check_manifest.py.

The evidence tree legitimately holds more than one release (the frozen primary
plus per-suite releases minted later). Checked against any single manifest, the
other release's files would all read as unlisted, so strict inventory must
accept the UNION of every supplied manifest for a shared evidence root -- while
each manifest's own byte checks stay per-manifest.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "check_manifest",
    Path(__file__).resolve().parents[2] / "papers" / "scripts" / "check_manifest.py",
)
check_manifest = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(check_manifest)


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@pytest.fixture()
def evidence(tmp_path: Path):
    """A tiny evidence root with two 'releases' and one manifest for each."""
    root = tmp_path / "evidence"
    (root / "suite_a" / "alg").mkdir(parents=True)
    (root / "suite_b" / "alg").mkdir(parents=True)
    (root / "_underscore").mkdir()

    a = root / "suite_a" / "alg" / "per_run.csv"
    b = root / "suite_b" / "alg" / "per_run.csv"
    a.write_bytes(b"a-rows\n")
    b.write_bytes(b"b-rows\n")
    # Underscore trees are outside inventory scope (own manifests).
    (root / "_underscore" / "extra.txt").write_bytes(b"ignored\n")

    def manifest(path: Path, files: list[Path]) -> Path:
        payload = {
            "evidence_root": str(root),
            "files": [
                {
                    "path": f.relative_to(root).as_posix(),
                    "sha256": _sha(f.read_bytes()),
                    "bytes": f.stat().st_size,
                }
                for f in files
            ],
        }
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    ma = manifest(tmp_path / "manifest_a.json", [a])
    mb = manifest(tmp_path / "manifest_b.json", [b])
    return root, ma, mb


def test_single_manifest_strict_flags_other_release_as_unlisted(evidence, capsys) -> None:
    _, ma, _ = evidence
    rc = check_manifest.main(["--manifest", str(ma), "--strict-inventory"])
    out = capsys.readouterr().out
    assert rc == 1
    assert "1/1 match" in out
    assert "UNLISTED" in out and "suite_b" in out


def test_union_of_both_manifests_passes_strict_inventory(evidence, capsys) -> None:
    _, ma, mb = evidence
    rc = check_manifest.main(
        ["--manifest", str(ma), "--manifest", str(mb), "--strict-inventory"]
    )
    out = capsys.readouterr().out
    assert rc == 0
    # Multi-manifest output labels each count line by manifest basename.
    assert "manifest_a.json: 1/1 match" in out
    assert "manifest_b.json: 1/1 match" in out
    assert "UNLISTED" not in out


def test_union_still_fails_on_genuinely_unlisted_file(evidence, capsys) -> None:
    root, ma, mb = evidence
    stray = root / "suite_a" / "stray.txt"
    stray.write_bytes(b"nobody lists me\n")
    rc = check_manifest.main(
        ["--manifest", str(ma), "--manifest", str(mb), "--strict-inventory"]
    )
    out = capsys.readouterr().out
    assert rc == 1
    assert "stray.txt" in out


def test_byte_checks_stay_per_manifest(evidence, capsys) -> None:
    """A corrupted file fails its OWN manifest even when the union lists it."""
    root, ma, mb = evidence
    (root / "suite_b" / "alg" / "per_run.csv").write_bytes(b"tampered\n")
    rc = check_manifest.main(["--manifest", str(ma), "--manifest", str(mb)])
    out = capsys.readouterr().out
    assert rc == 1
    assert "manifest_a.json: 1/1 match" in out
    assert "manifest_b.json: 0/1 match" in out
    assert "changed" in out
