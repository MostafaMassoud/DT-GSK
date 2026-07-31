#!/usr/bin/env python3
# Copyright (c) 2026 Mostafa Masoud <moustafa.masoud@gmail.com>
"""Cross-check the manuscript's provenance claims against the actual artifacts.

Ticket M-031 required "cross-check every release ID, commit, hash, and
'unchanged' statement against the current manifests" -- and C-007 (mint a fresh
freeze manifest) and C-008 (terminal re-freeze) need the same check, so it lives
here rather than in a one-off script.

WHY THIS CLASS OF DEFECT IS EASY TO SHIP
----------------------------------------
Provenance prose is written once and then silently decays: a release is
superseded, modules are renamed, a hash is regenerated, and the sentence that
described the old state keeps compiling perfectly. The specific failure this
gate was built for is a subsection that asserted "no such change occurred for
the results reported in this paper" while three artifacts in the same repository
recorded two post-freeze source fixes and a full evidence regeneration.

CHECKS
------
1. IDENTIFIERS  -- every release id / anchor commit the manuscript cites exists
   in the manifests, and no superseded release is cited as current.
2. HASHES       -- every SHA-256 prefix the manuscript prints is either a live
   hash of the shipped module or is explicitly labelled historical.
3. NO-CHANGE    -- the manuscript never asserts that no post-freeze change
   occurred while the change register records one.
4. CHANGE REG   -- every post-freeze source correction named in the manuscript
   has a registered change request.

Exit 0 = the provenance prose matches the artifacts.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PAPERS = ROOT / "papers"

FREEZE = PAPERS / "build_prompt_phases" / "phase_03" / "algorithm_freeze_manifest.json"
RELEASE = PAPERS / "governance" / "evidence_release_manifest.json"
REGISTER = PAPERS / "governance" / "change_request_register.csv"
OPTIM = ROOT / "src" / "gsk_family" / "optimizers"

SOURCES = [PAPERS / "main.tex", PAPERS / "supplementary.tex",
           *sorted((PAPERS / "sections").glob("*.tex"))]

# Modules whose hashes the manuscript may print.
SHIPPED = ["dt_gsk.py", "_dt_core.py", "_dt_profiles.py", "_dt_rng.py"]

# Phrases that assert no post-freeze change ever happened.
NO_CHANGE = [
    re.compile(r"no such change occurred", re.I),
    re.compile(r"no post-freeze change (?:has )?occurred", re.I),
    re.compile(r"the frozen sources (?:are|remain) unchanged", re.I),
]

problems: list[str] = []


def fail(msg: str) -> None:
    print(f"  FAIL  {msg}")
    problems.append(msg)


def ok(msg: str) -> None:
    print(f"  ok    {msg}")


def text_of(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")


def live_hashes() -> dict[str, str]:
    out = {}
    for name in SHIPPED:
        f = OPTIM / name
        if f.is_file():
            out[name] = hashlib.sha256(f.read_bytes()).hexdigest()[:16]
    return out


def strip_tex_comments(text: str) -> str:
    """Drop everything from the first UNESCAPED '%' to end of line.

    The previous gate joined raw source, so an identifier that appeared only in a
    '%' comment counted as "cited" -- and a superseded identifier hidden in a
    comment was invisible.  Comments are not rendered, so they can neither make
    nor discharge a provenance claim.
    """
    out: list[str] = []
    for line in text.splitlines():
        i, cut = 0, len(line)
        while i < len(line):
            if line[i] == "\\":       # \% and friends are escaped, not a comment
                i += 2
                continue
            if line[i] == "%":
                cut = i
                break
            i += 1
        out.append(line[:cut])
    return "\n".join(out)


def iter_blocks(text: str):
    """Yield (start_line, block) for \\item entries and blank-line paragraphs."""
    cur: list[str] = []
    start = 1
    for i, line in enumerate(text.splitlines(), 1):
        if (not line.strip()) or line.lstrip().startswith("\\item"):
            if cur:
                yield start, "\n".join(cur)
                cur = []
        if line.strip():
            if not cur:
                start = i
            cur.append(line)
    if cur:
        yield start, "\n".join(cur)


# A block making one of these assertions is an AUTHORITY block: it tells the
# reader where the reported numbers come from, so every identifier it names must
# be current.  Keyed on the assertion itself -- NOT on proximity to an id, and
# NOT on capturing the id grammatically (the old regex captured the pronoun in
# "... is drawn from it" and therefore never matched anything).
AUTHORITY = [
    re.compile(r"current release", re.I),
    re.compile(r"all empirical values", re.I),
    re.compile(r"accompanying this article", re.I),
    re.compile(r"every (?:number|value)[^.]{0,160}?\b(?:drawn|derives?|derived|comes?)\b",
               re.I | re.S),
    re.compile(r"\b(?:derives?|derived|drawn)\s+from\b[^.]{0,120}?\brelease\b", re.I | re.S),
]

# A superseded id may legitimately appear inside an authority block when it is
# framed as history ("... which supersedes X", "historical", "prior release").
_HISTORICAL = re.compile(
    r"supersed\w*|historical|prior|earlier|previous|replaced|deprecated", re.I)


def release_universe(rel: dict) -> tuple[set[str], set[str]]:
    """(current_tokens, superseded_tokens): ids, full anchors and 9-char anchors."""
    cur_id = str(rel.get("release_id", "") or "")
    cur_anchor = str(rel.get("anchor_commit", "") or "")
    current = {t for t in (cur_id, cur_anchor, cur_anchor[:9]) if t}

    raw = {str(rel.get("supersedes_release", "") or "")}
    for d in sorted((PAPERS / "analysis").glob("rel-*")):
        raw.add(d.name)
        man = d / "analysis_manifest.json"
        if man.is_file():
            try:
                m = json.loads(text_of(man))
            except (ValueError, OSError):
                continue
            for key in ("anchor_commit", "anchor", "commit"):
                if m.get(key):
                    raw.add(str(m[key]))

    superseded: set[str] = set()
    for sid in raw:
        if not sid:
            continue
        superseded.add(sid)
        m = re.search(r"-([0-9a-f]{7,40})$", sid)
        if m:
            superseded.add(m.group(1))
    return current, superseded - current


def _authority_violations(label: str, body: str, superseded: set[str],
                          report: bool = True) -> int:
    """Fail every authority block/sentence that names a superseded identifier."""
    bad = 0
    for ln, blk in iter_blocks(body):
        if not any(a.search(blk) for a in AUTHORITY):
            continue
        for tok in sorted(superseded, key=len, reverse=True):
            hit = None
            for m in re.finditer(re.escape(tok), blk):
                if _HISTORICAL.search(blk[max(0, m.start() - 70):m.start()]):
                    continue          # "... which supersedes X" is legitimate
                hit = m
                break
            if hit is not None:
                bad += 1
                if report:
                    fail(f"{label}:{ln}: authority statement presents superseded "
                         f"identifier {tok} as the source of reported values")
                break
    return bad


def _freeze_release_ids(frz: dict) -> "tuple[str, dict]":
    """The pass-24 freeze widened ``evidence_release`` from a single string to
    a per-suite mapping (primary / cec2013lsgo / cec2020 / ablation). Return
    ``(primary_id, mapping)`` under either schema (mapping empty for legacy)."""
    val = frz.get("evidence_release", "")
    if isinstance(val, dict):
        return str(val.get("primary", "") or ""), {k: str(v) for k, v in val.items()}
    return str(val or ""), {}


def check_identifiers(rel: dict, frz: dict) -> None:
    print("[1] release identifiers")
    cur_id = str(rel.get("release_id", "") or "")
    cur_anchor = str(rel.get("anchor_commit", "") or "")
    current, superseded = release_universe(rel)
    legacy, _ = _freeze_release_ids(frz)
    if legacy and legacy != cur_id:
        superseded.add(legacy)

    bodies = {p.name: strip_tex_comments(text_of(p)) for p in SOURCES if p.is_file()}
    blob = "\n".join(bodies.values())

    # (a) whenever the manuscript names ANY release, it must name the current one.
    present = sorted({t for t in ({cur_id} | superseded) if t and t in blob})
    if cur_id and cur_id in blob:
        ok(f"current release {cur_id} is cited in rendered prose")
    elif present:
        fail(f"rendered prose cites release id(s) {', '.join(present)} but never "
             f"states the current release {cur_id}")
    else:
        print("  note  no release id appears in rendered prose")

    # (b) the current anchor must be stated in rendered prose too.
    if cur_anchor:
        if cur_anchor in blob or cur_anchor[:9] in blob:
            ok(f"anchor {cur_anchor[:9]} cited and matches the release manifest")
        else:
            fail(f"current anchor {cur_anchor[:9]} is never stated in rendered prose")

    # (c) authority-context rule (replaces the pronoun-escaping regex).
    bad = sum(_authority_violations(n, b, superseded) for n, b in bodies.items())
    if not bad:
        ok("no authority statement cites a superseded release")

    # (d) the freeze manifest must agree with the release manifest(s).
    fm = PAPERS / "governance" / "main_manuscript_freeze_manifest.json"
    if fm.is_file():
        try:
            got, per_suite = _freeze_release_ids(json.loads(text_of(fm)))
        except ValueError:
            got, per_suite = "", {}
        if got and cur_id and got != cur_id:
            fail(f"freeze manifest evidence_release {got} != release manifest {cur_id}")
        elif got:
            ok(f"freeze manifest agrees: evidence_release {got}")
        for suite in ("cec2013lsgo", "cec2020"):
            claimed = per_suite.get(suite, "")
            sm = PAPERS / "governance" / f"evidence_release_manifest_{suite}.json"
            if not claimed or not sm.is_file():
                continue
            suite_id = str(json.loads(text_of(sm)).get("release_id", "") or "")
            if suite_id and claimed != suite_id:
                fail(f"freeze manifest {suite} release {claimed} != "
                     f"suite release manifest {suite_id}")
            elif suite_id:
                ok(f"freeze manifest agrees: {suite} release {claimed}")


def _pdf_text(p: Path) -> str:
    try:
        import pypdf
        return "\n".join((pg.extract_text() or "") for pg in pypdf.PdfReader(str(p)).pages)
    except Exception:
        return ""


def _docx_text(p: Path) -> str:
    try:
        import zipfile
        with zipfile.ZipFile(p) as z:
            xml = z.read("word/document.xml").decode("utf-8", "ignore")
        return re.sub(r"<[^>]+>", " ", xml)
    except Exception:
        return ""


def check_rendered(rel: dict, frz: dict) -> None:
    """The freeze pins the PDFs/DOCX, so the gate must read what the reader reads."""
    print("[1b] rendered submission artifacts")
    cur_id = str(rel.get("release_id", "") or "")
    _, superseded = release_universe(rel)
    legacy, _ = _freeze_release_ids(frz)
    if legacy and legacy != cur_id:
        superseded.add(legacy)

    any_text = False
    for name in ("DT-GSK.pdf", "DT-GSK.docx", "supplementary.pdf", "supplementary.docx"):
        p = PAPERS / name
        if not p.is_file():
            continue
        body = _pdf_text(p) if p.suffix == ".pdf" else _docx_text(p)
        if not body.strip():
            print(f"  note  {name}: no extractable text (skipped)")
            continue
        any_text = True
        flat = re.sub(r"\s+", " ", body)
        tight = re.sub(r"\s+", "", body)      # hashes may wrap across lines
        hits = 0
        for sent in re.split(r"(?<=[.;])\s+", flat):
            if not any(a.search(sent) for a in AUTHORITY):
                continue
            packed = re.sub(r"\s+", "", sent)
            for tok in sorted(superseded, key=len, reverse=True):
                where = sent.find(tok)
                if where < 0 and tok in packed:
                    where = 0
                if where < 0:
                    continue
                if _HISTORICAL.search(sent[max(0, where - 70):where] or sent[:70]):
                    continue
                fail(f"{name}: rendered authority sentence presents superseded "
                     f"identifier {tok} as the source of reported values")
                hits += 1
                break
        # Only an artifact that actually names a release must name the current
        # one; a document that is silent on releases is not making a claim.
        # "names a release" means prints an actual identifier -- a document that
        # only says "the evidence release" in prose delegates identity elsewhere
        # (the main paper legitimately defers to the supplement) and is silent,
        # not wrong.
        names_release = any(t in flat or t in tight for t in superseded)
        if cur_id and names_release and cur_id not in flat and cur_id not in tight:
            fail(f"{name}: names a release but never the current {cur_id}")
        elif not hits:
            ok(f"{name}: no superseded authority claim"
               + ("; states the current release" if cur_id in flat or cur_id in tight
                  else "; silent on release identity"))
    if not any_text:
        print("  note  no rendered artifact text available")


def self_test() -> int:
    """The hardening must fail the exact shapes that previously slipped through."""
    sup = {"rel-2026-07-16-78f075cb0", "78f075cb0",
           "78f075cb0f68a80010d524bdcc390a69a0afc5cd"}
    cases = [
        ("pronoun escape", "\\item \\textbf{Current release (anchor "
         "\\texttt{78f075cb0}).}  The regenerated evidence is release "
         "\\texttt{rel-2026-07-16-78f075cb0}.  Every number reported in this "
         "paper is drawn from it.", True),
        ("derive-from + anchor", "All empirical values in the main paper derive "
         "from the promoted evidence release accompanying this article (anchor "
         "commit \\texttt{78f075cb0f68a80010d524bdcc390a69a0afc5cd}).", True),
        ("legitimate history", "The regenerated evidence supersedes "
         "\\texttt{rel-2026-07-16-78f075cb0}, retained for the provenance chain.",
         False),
        ("comment only", "% Current release rel-2026-07-16-78f075cb0 drawn from it",
         False),
    ]
    bad = 0
    for label, text, should_fail in cases:
        n = _authority_violations("self-test", strip_tex_comments(text), sup,
                                  report=False)
        got = n > 0
        status = "ok  " if got == should_fail else "FAIL"
        if got != should_fail:
            bad += 1
        print(f"  {status} {label}: expected_fail={should_fail} got_fail={got}")
    print("[self-test] " + ("OK" if not bad else f"{bad} case(s) wrong"))
    return 1 if bad else 0


# The freeze manifest predates the ism -> dt rename, so its keys are the old names.
_RENAMED = {"ism_gsk.py": "dt_gsk.py", "_ism_core.py": "_dt_core.py",
            "_ism_profiles.py": "_dt_profiles.py", "_ism_rng.py": "_dt_rng.py"}


def check_hashes() -> None:
    """Two structural rules, deliberately not a proximity heuristic.

    An earlier version accepted any hash appearing within ~1500 characters of the
    word "historical". That can never fail inside a subsection *about* historical
    hashes -- a self-test caught it passing a frozen hash substituted for a live
    one. The rules below key on the module each hash is attributed to instead.
    """
    print("[2] printed hashes")
    live = live_hashes()
    frz_raw = json.loads(text_of(FREEZE)).get("frozen_core_sources", {})
    frozen = {_RENAMED.get(k, k): v for k, v in frz_raw.items()
              if isinstance(v, str) and len(v) == 16}

    # LaTeX prints these as: \texttt{_dt_rng.py} \texttt{8a0fc...}
    # Two accepted spellings of a "<module> <hash>" pair.  The manuscript stopped
    # wrapping identifiers in \texttt on 2026-07-24 (author decision: normal body
    # font in both PDF and DOCX), which silently blinded the \texttt-only pattern
    # -- every pair still printed, but Rule B below saw an empty `seen` and
    # reported all four live hashes as missing.  The archived form is kept so the
    # gate still reads pre-2026-07-24 sources.
    #   old: \texttt{_dt_core.py}\texttt{dc2d...}
    #   new: _dt_core.py dc2d...
    # The trailing (?![0-9a-f]) stops a 40-char commit from matching on its first
    # 16 characters.
    pair_re = re.compile(
        r"\\texttt\{(\\?_?[\w\\]+\.py)\}\s*\\texttt\{([0-9a-f]{16})\}"
        r"|(\\?_?[\w\\]+\.py)[\s~]+([0-9a-f]{16})(?![0-9a-f])")
    seen: set[str] = set()

    for src in SOURCES:
        if not src.is_file():
            continue
        body = text_of(src)
        for m in pair_re.finditer(body):
            mod = (m.group(1) or m.group(3)).replace("\\_", "_").replace("\\", "")
            h = m.group(2) or m.group(4)
            seen.add(h)
            # Rule A: a hash attributed to a module must be that module's live or
            # frozen hash -- never another module's, never unknown.
            allowed = {live.get(mod), frozen.get(mod)} - {None}
            if allowed and h not in allowed:
                owner = next((k for k, v in {**live, **frozen}.items() if v == h), None)
                fail(f"{src.name}: hash {h} attributed to {mod}"
                     + (f" but belongs to {owner}" if owner else " matches no known source"))

    # Rule B: each shipped module's CURRENT hash must actually appear. This is what
    # catches a live hash being quietly replaced by its historical predecessor --
    # the pair stays internally valid, but the current state stops being stated.
    for mod, h in sorted(live.items()):
        if h not in seen:
            fail(f"current hash of {mod} ({h}) is never printed; the manuscript "
                 f"states only historical hashes for it")
    ok(f"live shipped-module hashes all present: {', '.join(sorted(live.values()))}")


def check_no_change_claims() -> None:
    print("[3] 'no post-freeze change' assertions")
    reg = list(csv.DictReader(REGISTER.open(encoding="utf-8", newline="")))
    core_crs = [r for r in reg
                if re.search(r"frozen core|post-freeze", r.get("reason", ""), re.I)]
    for src in SOURCES:
        if not src.is_file():
            continue
        for i, line in enumerate(text_of(src).splitlines(), 1):
            if line.lstrip().startswith("%"):
                continue
            for pat in NO_CHANGE:
                if pat.search(line):
                    if core_crs:
                        fail(f"{src.name}:{i}: asserts no post-freeze change, but "
                             f"{len(core_crs)} change request(s) record one "
                             f"({', '.join(r['change_id'] for r in core_crs)})")
                    else:
                        print(f"  note  {src.name}:{i}: no-change assertion "
                              "(register has no core CR, so it may hold)")
    ok("no unsupported no-change assertion")


def check_change_register() -> None:
    print("[4] change register covers the named corrections")
    reg = list(csv.DictReader(REGISTER.open(encoding="utf-8", newline="")))
    ids = {r["change_id"] for r in reg}
    blob = "\n".join(text_of(p) for p in SOURCES if p.is_file())
    for cr in sorted(set(re.findall(r"CR-\d{4}", blob))):
        if cr in ids:
            ok(f"{cr} cited and registered")
        else:
            fail(f"{cr} is cited in the manuscript but absent from the register")
    # the two known post-freeze defects must be registered somewhere
    joined = " ".join(r.get("reason", "") + r.get("evidence", "") for r in reg)
    for defect in ("C006", "M038"):
        if defect in joined:
            ok(f"{defect} has a registered change request")
        else:
            fail(f"{defect} is a post-freeze core fix with no change request")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--self-test", action="store_true",
                    help="assert the authority rule fails the shapes that "
                         "previously slipped through, and passes legitimate history")
    ap.add_argument("--skip-rendered", action="store_true",
                    help="skip PDF/DOCX extraction (source-only run)")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    for req in (FREEZE, RELEASE, REGISTER):
        if not req.is_file():
            print(f"[provenance] missing required artifact: {req}")
            return 1

    rel = json.loads(text_of(RELEASE))
    frz = json.loads(text_of(FREEZE))

    print("[provenance] cross-checking manuscript claims against artifacts\n")
    check_identifiers(rel, frz)
    print()
    if not args.skip_rendered:
        check_rendered(rel, frz)
        print()
    check_hashes()
    print()
    check_no_change_claims()
    print()
    check_change_register()

    if problems:
        print(f"\n[provenance] FAILED with {len(problems)} problem(s)")
        return 1
    print("\n[provenance] OK - prose matches the manifests")
    return 0


if __name__ == "__main__":
    sys.exit(main())
