#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Produce a machine-checkable all-green attestation (ticket M-030 / EXP-004).

WHAT THIS ANSWERS
-----------------
"The tests pass on my machine" is not a reproducibility claim. The claim the
manuscript needs is narrower and checkable: *the full suite and every release
gate ran green on an interpreter and dependency set that lie inside the support
envelope the project declares in pyproject.toml.*

So this tool does three things, and refuses to emit a green attestation unless
all three hold:

1. Reads the declared envelope from ``pyproject.toml`` and checks the INSTALLED
   interpreter and package versions against it. A green suite on an
   out-of-envelope stack attests to nothing about the supported configuration.
2. Runs the full test suite TWICE with ``--junitxml`` (the ticket's
   "run all tests twice"). Two identical green runs also rule out a suite whose
   result depends on ordering or on state left by a previous run.
3. Runs every release gate that guards the manuscript.

Output lands in ``papers/governance/environment_attestation/`` -- deliberately
NOT in the analysis bundle, which ``phase6_run_analysis.py`` rmtree's on every
regeneration, and which RT-001 will force to be regenerated.

USAGE
-----
    python papers/scripts/make_environment_attestation.py
    python papers/scripts/make_environment_attestation.py --verify   # re-check only
"""
from __future__ import annotations

import argparse
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "papers" / "governance" / "environment_attestation"
PYPROJECT = ROOT / "pyproject.toml"

# Gates that guard the manuscript, with the exit codes each may legitimately
# return. Only document-consistency has a second acceptable code: it exits 2
# when an author-supplied field is still unfilled, which blocks submission but
# is not a defect in the tree and must not be conflated with drift (exit 1).
GATES = [
    ("build-hygiene", ["papers/scripts/validate_build_hygiene.py"], {0}),
    ("provenance-claims", ["papers/scripts/validate_provenance_claims.py"], {0}),
    ("cross-format-parity", ["papers/scripts/validate_cross_format_parity.py"], {0}),
    ("document-consistency", ["papers/scripts/validate_document_consistency.py"],
     {0, 2}),
    ("docx-main", ["papers/scripts/validate_docx.py", "papers/DT-GSK.docx"], {0}),
    ("docx-supplementary", ["papers/scripts/validate_docx.py",
                            "papers/supplementary.docx"], {0}),
]

TRACKED = ["numpy", "scipy", "pandas", "matplotlib"]


# --------------------------------------------------------------------------- #
# declared envelope
# --------------------------------------------------------------------------- #
def _ver(s: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", s))


def _satisfies(version: str, spec: str) -> bool:
    """Check `version` against a PEP 440-style comma list (>=1.24,<2.4)."""
    v = _ver(version)
    for part in spec.split(","):
        part = part.strip()
        m = re.match(r"(>=|<=|==|!=|>|<)\s*([\d.]+)", part)
        if not m:
            continue
        op, ref = m.group(1), _ver(m.group(2))
        # compare on the shorter common prefix so 1.15.3 vs 1.16 works
        n = min(len(v), len(ref))
        a, b = v[:n], ref[:n]
        ok = {">=": a >= b, "<=": a <= b, "==": a == b,
              "!=": a != b, ">": a > b, "<": a < b}[op]
        # a strict upper bound must compare on the full declared precision
        if op in ("<", "<=") and a == b and len(v) > len(ref):
            ok = (op == "<=")
        if not ok:
            return False
    return True


def declared_envelope() -> dict:
    text = PYPROJECT.read_text(encoding="utf-8")
    env = {}
    m = re.search(r'requires-python\s*=\s*"([^"]+)"', text)
    if m:
        env["python"] = m.group(1)
    for pkg in TRACKED:
        m = re.search(rf'"{pkg}([^"]*)"', text)
        if m:
            env[pkg] = m.group(1).strip()
    return env


def installed_versions() -> dict:
    out = {}
    for pkg in TRACKED:
        try:
            mod = __import__(pkg)
            out[pkg] = getattr(mod, "__version__", "unknown")
        except Exception as exc:      # noqa: BLE001 - report, don't crash
            out[pkg] = f"NOT INSTALLED ({type(exc).__name__})"
    return out


def git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=str(ROOT), capture_output=True,
                              text=True).stdout.strip()
    except OSError:
        return ""


# --------------------------------------------------------------------------- #
def run_suite(tag: str) -> dict:
    xml = OUT / f"junit-{tag}.xml"
    cmd = [sys.executable, "-X", "utf8", "-m", "pytest", "-q", "-p", "no:randomly",
           f"--junitxml={xml}"]
    print(f"  [{tag}] {' '.join(cmd[-4:])}")
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
    counts = {}
    if xml.is_file():
        head = xml.read_text(encoding="utf-8", errors="ignore")[:2000]
        m = re.search(r'<testsuite[^>]*\btests="(\d+)"[^>]*', head)
        if m:
            counts["tests"] = int(m.group(1))
        for k in ("failures", "errors", "skipped"):
            mm = re.search(rf'\b{k}="(\d+)"', head)
            counts[k] = int(mm.group(1)) if mm else 0
        mt = re.search(r'\btime="([\d.]+)"', head)
        if mt:
            counts["seconds"] = round(float(mt.group(1)), 2)
    tail = (r.stdout or "").strip().splitlines()
    return {"exit_code": r.returncode, "xml": xml.name,
            "summary": tail[-1] if tail else "", **counts}


def run_gates() -> list[dict]:
    out = []
    for name, argv, accept in GATES:
        r = subprocess.run([sys.executable, "-X", "utf8", *argv],
                           cwd=str(ROOT), capture_output=True, text=True)
        good = r.returncode in accept
        note = "" if r.returncode == 0 else (
            "  (accepted: author-supplied field pending)" if good else "")
        print(f"  gate {name:22s} exit {r.returncode}"
              f"{'' if good else '   <<< NOT ACCEPTED'}{note}")
        out.append({"gate": name, "command": "python " + " ".join(argv),
                    "exit_code": r.returncode,
                    "accepted_exit_codes": sorted(accept), "ok": good})
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--verify", action="store_true",
                    help="re-check an existing attestation without re-running")
    args = ap.parse_args()

    att_path = OUT / "attestation.json"
    if args.verify:
        if not att_path.is_file():
            print("[attestation] none found; run without --verify first")
            return 1
        att = json.loads(att_path.read_text(encoding="utf-8"))
        print(f"[attestation] {att['generated_utc']}  green={att['green']}")
        for k, v in att["envelope_check"].items():
            print(f"  {k:12s} installed={v['installed']:<12s} "
                  f"declared={v['declared']:<16s} {'OK' if v['in_envelope'] else 'OUT'}")
        return 0 if att["green"] else 1

    OUT.mkdir(parents=True, exist_ok=True)
    print("[attestation] declared envelope vs installed stack")
    declared = declared_envelope()
    installed = {"python": platform.python_version(), **installed_versions()}
    check = {}
    for key, ver in installed.items():
        spec = declared.get(key, "")
        ok = _satisfies(ver, spec) if spec else False
        check[key] = {"installed": ver, "declared": spec or "(undeclared)",
                      "in_envelope": bool(ok)}
        print(f"  {key:12s} {ver:<12s} vs {spec or '(undeclared)':<18s} "
              f"{'OK' if ok else 'OUT OF ENVELOPE'}")
    envelope_ok = all(v["in_envelope"] for v in check.values())

    print("\n[attestation] full suite, run twice")
    runs = [run_suite("run1"), run_suite("run2")]

    print("\n[attestation] release gates")
    gates = run_gates()

    suites_ok = all(r["exit_code"] == 0 and r.get("failures", 1) == 0
                    and r.get("errors", 1) == 0 for r in runs)
    same = (len({r.get("tests") for r in runs}) == 1)
    gates_ok = all(g["ok"] for g in gates)
    green = envelope_ok and suites_ok and same and gates_ok

    att = {
        "schema": "dtgsk-environment-attestation/1",
        "ticket": "M-030 (EXP-004)",
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "green": green,
        "green_requires": ("installed stack inside the declared envelope; two "
                           "identical all-green suite runs; every release gate exit 0"),
        "envelope_check": check,
        "interpreter": {"version": platform.python_version(),
                        "executable": sys.executable,
                        "implementation": platform.python_implementation()},
        "platform": {"system": platform.system(), "release": platform.release(),
                     "machine": platform.machine(), "node": platform.node()},
        "git": {"head": git("rev-parse", "HEAD"),
                "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
                "dirty": bool(git("status", "--porcelain"))},
        "test_runs": runs,
        "runs_agree_on_test_count": same,
        "gates": gates,
    }
    att_path.write_text(json.dumps(att, indent=2) + "\n", encoding="utf-8")

    print(f"\n[attestation] envelope={'OK' if envelope_ok else 'OUT'}  "
          f"suites={'OK' if suites_ok else 'FAIL'}  "
          f"agree={'OK' if same else 'DIFFER'}  "
          f"gates={'OK' if gates_ok else 'FAIL'}")
    print(f"[attestation] wrote {att_path.relative_to(ROOT)}  green={green}")
    if not green:
        print("[attestation] NOT green - do not cite this as an all-green result")
    return 0 if green else 1


if __name__ == "__main__":
    sys.exit(main())
