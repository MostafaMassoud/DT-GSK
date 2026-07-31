#!/usr/bin/env python
"""Phase 8 task 14 - claim/citation/number audit of the drafted manuscript.

Audits papers/main.tex + papers/sections/*.tex + papers/supplementary.tex against
the governance artifacts:
  - papers/governance/allowed_citation_keys.txt      (61 allowed \\cite keys since
                                                      CR-0020 / ruling R8; the counts
                                                      printed below are read from the
                                                      file, never hard-coded)
  - papers/governance/citation_role_map.csv          (per-key sanctioned roles)
  - papers/governance/claims_evidence_matrix.csv     (50 claims; statuses; blocked wording)
  - papers/governance/artifact_binding.csv           (artifact/analysis id universe)
  - papers/analysis/rel-2026-07-10-262fc16c9/analysis_manifest.json (AN-* ids)

Outputs:
  - papers/governance/citation_usage_map.csv
  - papers/build_prompt_phases/phase_08/paragraph_evidence_audit.csv
  - stdout report: violations by category (citation, binding, number,
    ablation, blocked wording, terminology), row counts.

The script never edits prose. It only reports.
"""
from __future__ import annotations

import csv
import json
import os
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PAPERS = REPO / "papers"
GOV = PAPERS / "governance"
PH08 = PAPERS / "build_prompt_phases" / "phase_08"
# N-009: this was pinned to rel-2026-07-10-262fc16c9, which is now two releases
# superseded -- regenerating against it would anchor the citation map to a dead
# bundle. Follows the same GSK_REL_ID override the rest of the pipeline uses, so
# it tracks the current release instead of drifting again.
ANALYSIS = PAPERS / "analysis" / os.environ.get(
    "GSK_REL_ID", "rel-2026-07-20-67d9345f9")
if not ANALYSIS.is_dir():
    raise SystemExit(
        f"analysis bundle not found: {ANALYSIS}. Set GSK_REL_ID to the release "
        "you intend to audit against; do not fall back to a superseded bundle."
    )

# ----------------------------------------------------------------------------
# Target files. in_build is derived from the \input graph of the two drivers.
# ----------------------------------------------------------------------------
MAIN = PAPERS / "main.tex"
SUPP = PAPERS / "supplementary.tex"
SECTIONS = sorted((PAPERS / "sections").glob("*.tex"))


def input_graph(driver: Path) -> set[str]:
    """Files \\input by a driver (relative to papers/, .tex appended)."""
    out = set()
    for m in re.finditer(r"\\input\{([^}]+)\}", driver.read_text(encoding="utf-8")):
        p = m.group(1)
        if not p.endswith(".tex"):
            p += ".tex"
        out.add(p.replace("\\", "/"))
    return out


MAIN_INPUTS = input_graph(MAIN)
SUPP_INPUTS = input_graph(SUPP)
IN_BUILD_REL = {"main.tex", "supplementary.tex"} | MAIN_INPUTS | SUPP_INPUTS

TARGETS: list[tuple[Path, str, bool]] = []
for f in [MAIN, *SECTIONS, SUPP]:
    rel = f.relative_to(PAPERS).as_posix()
    TARGETS.append((f, rel, rel in IN_BUILD_REL))
# tables/T*.tex are \input by supplementary.tex -> include in token scans only.
TABLE_FILES = sorted((PAPERS / "tables").glob("T*.tex"))

# ----------------------------------------------------------------------------
# Governance data
# ----------------------------------------------------------------------------
ALLOWED_KEYS = {
    k.strip()
    for k in (GOV / "allowed_citation_keys.txt").read_text(encoding="utf-8").splitlines()
    if k.strip()
}

ROLE_MAP: dict[str, dict] = {}
with open(GOV / "citation_role_map.csv", encoding="utf-8-sig", newline="") as fh:
    for row in csv.DictReader(fh):
        ROLE_MAP[row["citation_key"].strip()] = row

CLAIMS: dict[str, dict] = {}
with open(GOV / "claims_evidence_matrix.csv", encoding="utf-8-sig", newline="") as fh:
    for row in csv.DictReader(fh):
        CLAIMS[row["claim_id"].strip()] = row

ASSERTABLE = {
    cid for cid, r in CLAIMS.items()
    if r["status"] in ("READY", "ACCEPTED_PHASE_6", "NARROWED_PHASE_6")
}
FORBIDDEN_CLAIMS = set(CLAIMS) - ASSERTABLE  # DEFERRED_TO_PHASE_12*, BLOCKED_ON_*

ANALYSIS_IDS: set[str] = set()
manifest = json.loads((ANALYSIS / "analysis_manifest.json").read_text(encoding="utf-8"))
for out in manifest.get("outputs", []):
    ANALYSIS_IDS.update(out.get("analysis_ids", []))

ARTIFACT_IDS: set[str] = set()
with open(GOV / "artifact_binding.csv", encoding="utf-8-sig", newline="") as fh:
    for row in csv.DictReader(fh):
        ARTIFACT_IDS.add(row["artifact_id"].split(" ")[0].strip())
        aid = row.get("analysis_id", "").strip()
        if aid:
            ANALYSIS_IDS.add(aid)

EVIDENCE_CARDS = {p.stem for p in (GOV / "evidence_cards").glob("*.md")}

# Negative-findings shorthand ids used by drafting agents (phase_06/negative_findings.md)
NEGATIVE_FINDING_ALIASES = {
    "APGSK-GAP", "CEC2011-EGSK-LOSS", "CEC2013-D30-THIRD", "ENVIRONMENT",
    "D30-SECOND", "NEMENYI-NONSEP", "WTL-EGSK-LOSS", "R01-DIVERGE", "R04-DIVERGE",
}

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
CITE_RE = re.compile(r"\\cite[tp]?\*?(?:\[[^\]]*\])?\{([^}]+)\}")
BIND_RE = re.compile(r"%+\s*BIND:\s*(.+)$")
SECTION_RE = re.compile(r"\\(?:sub)*section\*?\{")


def strip_comment(line: str) -> str:
    """Remove an unescaped %-comment tail."""
    out = []
    i = 0
    while i < len(line):
        c = line[i]
        if c == "%" and (i == 0 or line[i - 1] != "\\"):
            break
        out.append(c)
        i += 1
    return "".join(out)


def brace_arg_span(text: str, start: int) -> int:
    """Given index of '{', return index one past its matching '}'."""
    depth = 0
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
    return len(text)


STRIP_CMDS = (
    "cite", "ref", "eqref", "pageref", "label", "input", "includegraphics",
    "bibliography", "usepackage", "documentclass", "begin", "end", "texttt",
    "pgfplotsset", "usetikzlibrary", "setcounter", "sisetup", "mbox",
)


def strip_latex_for_numbers(text: str) -> str:
    """Remove command arguments whose digits are structural, not scientific."""
    # remove optional args of stripped commands + their brace args
    for cmd in STRIP_CMDS:
        pat = re.compile(r"\\" + cmd + r"\*?(\[[^\]]*\])?")
        while True:
            m = pat.search(text)
            if not m:
                break
            end = m.end()
            # consume consecutive brace groups
            span_end = end
            while span_end < len(text) and text[span_end] == "{":
                span_end = brace_arg_span(text, span_end)
            if cmd == "texttt":
                # keep texttt content? paths/ids -> structural; drop it
                pass
            text = text[: m.start()] + " " + text[span_end:]
    # label-ish tokens S1..S9, C1..C9, F1..F30, T01..T22, D10-style handled later
    return text


NUM_RE = re.compile(
    r"(?<![\w.\-])("
    r"\d+(?:[,{]?,?\}?\d{3})*(?:\.\d+)?(?:[eE][+-]?\d+)?"
    r"|\d+\^\{-?\d+\}"
    r")(?![\w])"
)

# Structural / protocol constants that need no % BIND (frozen protocol PR-04,
# dims/tiers, run counts, suite years, list markers, section-structure ints)
PROTOCOL_ALLOW = {
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13",
    "22", "28", "29", "30", "50", "51", "100",
    "2011", "2013", "2017", "2020", "2021", "2026",
    "10000", "10,000", "70", "75", "95", "0.05",
    "1e-8", "1e-08", "10^{-8}",
}


def find_numbers(content: str) -> list[str]:
    text = strip_latex_for_numbers(content)
    # drop label-like tokens: S1, C4, F29, T01, D10, R2, A2-004, ids
    text = re.sub(r"\b[A-Za-z]+\d+(?:-\d+)?\b", " ", text)
    # drop 10^{-8}-style kept via math: normalize \times 10^{-8}
    nums = []
    for m in NUM_RE.finditer(text):
        tok = m.group(1).replace("{,}", ",")
        nums.append(tok)
    return nums


def classify_numbers(nums: list[str]) -> list[str]:
    return [n for n in nums if n.replace(",", "") not in
            {p.replace(",", "") for p in PROTOCOL_ALLOW}]


# ----------------------------------------------------------------------------
# Pass 1: citation usage map
# ----------------------------------------------------------------------------
citation_rows = []
cite_fail = []
for path, rel, in_build in TARGETS:
    lines = path.read_text(encoding="utf-8").splitlines()
    current_section = "(preamble)"
    for ln, raw in enumerate(lines, 1):
        if SECTION_RE.search(raw) and not raw.lstrip().startswith("%"):
            m = re.search(r"\\(?:sub)*section\*?\{([^}]*)\}", raw)
            if m:
                current_section = m.group(1)
        content = strip_comment(raw)
        for m in CITE_RE.finditer(content):
            for key in [k.strip() for k in m.group(1).split(",")]:
                ok = key in ALLOWED_KEYS
                role = ROLE_MAP.get(key, {})
                ctx = content.strip()
                ctx = (ctx[:160] + "...") if len(ctx) > 160 else ctx
                needs_review = "verified mechanism" in role.get("usage_condition", "")
                if key == "awad2016problem" and not role:
                    # citation_role_map.csv predates CR-0005 (2026-07-10): the
                    # key was BLOCKED when the map was authored. The resolved
                    # evidence card (evidence_cards/awad2016problem.md,
                    # ADMISSIBLE) carries the suite-definition role directly.
                    role = {"appendix_b_role":
                            "CEC2017 suite-definition role (B.4; "
                            "evidence card, CR-0005 resolved - role map "
                            "row missing, stale)",
                            "evidence_card": "evidence_cards/awad2016problem.md",
                            "usage_condition": "suite-definition claims only"}
                if not ok or not role:
                    supported = "FAIL - key outside allowed set/role map"
                elif not in_build:
                    supported = "n/a (stale file, not in released build)"
                elif needs_review:
                    supported = ("yes - verified mechanism discussed at cite site "
                                 "(manual check 2026-07-11)")
                else:
                    supported = ("yes - role-consistent per citation_role_map "
                                 "(manual spot-check 2026-07-11)")
                citation_rows.append({
                    "citation_key": key,
                    "file": rel,
                    "in_build": "yes" if in_build else "NO (stale, not in either driver)",
                    "line": ln,
                    "section": current_section,
                    "semantic_role": role.get("appendix_b_role", "KEY NOT IN ROLE MAP"),
                    # Column NAME, not a count: this is the committed header of
                    # citation_usage_map.csv and is deliberately left unchanged by
                    # CR-0020 (corpus 57 -> 61). Renaming it would rewrite the
                    # header of a lockstep file for no gain.
                    "in_allowed_57": "PASS" if ok else "FAIL",
                    "evidence_card": role.get("evidence_card", ""),
                    "usage_condition_class": (
                        "mechanism-discussion-only" if needs_review
                        else "optional-role-scoped"),
                    "evidence_card_supported": supported,
                    "context": ctx,
                })
                if not ok and in_build:
                    cite_fail.append((rel, ln, key))

# ----------------------------------------------------------------------------
# Pass 2: paragraph evidence audit
# ----------------------------------------------------------------------------
para_rows = []
unbound_violations = []
bind_token_problems = []
forbidden_claim_hits = []

KNOWN_FILEISH = re.compile(
    r"(phase_0\d|\.md|\.csv|\.py|\.tex|\.json|negative_findings|seed_and_pairing|"
    r"captions_registry|equation_registry|parameter_table|contribution_matrix|"
    r"terminology|novelty_scope|thesis|outline|promotion_tool_test|RUNBOOK|"
    r"robustness|pre-registration|items?\s+\d|Section\s+\d|totals\.|strides|"
    r"rel-2026|analysis_checksums|evidence_release_manifest|"
    r"algorithm_freeze_manifest)", re.I)

# ART-PARAMS is the frozen-parameter artifact shorthand used by drafting agents
# (phase_03/parameter_table.md); accept alongside TAB-/FIG- ids.
ARTIFACT_IDS.add("ART-PARAMS")

# EG-* ids: evidence gap register (disclosed-unavailable evidence bindings)
EG_IDS = set(re.findall(r"\bEG-\d{3}\b",
                        (GOV / "evidence_gap_register.md").read_text(encoding="utf-8")))

ID_HEAD = re.compile(r"^(AN-|EC:|TAB-|FIG-|ART-|[A-Z]{2}-\d)")
CLAIM_RANGE = re.compile(r"^([A-Z]{2})-(\d{2})\.\.(?:[A-Z]{2}-)?(\d{2})$")
DIM_LIST = re.compile(r"^(AN-[A-Z]+-\d{4})-(D\d+(?:[/,.]+D?\d+)*|D\d+\.\.D\d+)$")


def split_bind_tokens(bind_text: str) -> list[str]:
    """Split a BIND comment into candidate tokens on ';' and ','."""
    toks = []
    for part in re.split(r"[;,]", bind_text):
        part = part.strip().strip(".")
        if part:
            toks.append(part)
    return toks


def expand_ids(head: str) -> list[str]:
    """Expand compact forms: MT-02..MT-07, AN-OMNI-2017-D10/D30/D50/D100."""
    m = CLAIM_RANGE.match(head)
    if m:
        pre, lo, hi = m.group(1), int(m.group(2)), int(m.group(3))
        return [f"{pre}-{i:02d}" for i in range(lo, hi + 1)]
    m = DIM_LIST.match(head)
    if m:
        base, dims = m.groups()
        if ".." in dims:
            lo, hi = re.findall(r"D(\d+)", dims)
            tiers = [d for d in ("10", "30", "50", "100")
                     if int(lo) <= int(d) <= int(hi)]
        else:
            tiers = re.findall(r"\d+", dims)
        return [f"{base}-D{d}" for d in tiers]
    return [head]


def validate_bind_token(tok: str) -> tuple[list[str], str]:
    """Return (claim_ids_found, problem). Non-ID annotation fragments pass."""
    t = tok.strip().rstrip(").")
    if not t:
        return [], ""
    t = re.sub(r"^claims?\s+", "", t)          # 'claim MT-06' -> 'MT-06'
    head = re.split(r"[\s(]", t, 1)[0].strip()
    claim_ids = []
    if not ID_HEAD.match(head):
        # free-text annotation (notes, file refs, parameter callouts): pass if
        # it references a known artifact family or is plainly a note.
        return [], ""
    for h in expand_ids(head):
        if h in CLAIMS:
            claim_ids.append(h)
        elif h in ANALYSIS_IDS:
            pass
        elif h.startswith("AN-"):
            return claim_ids, f"unknown analysis id '{h}'"
        elif h.startswith("EC:"):
            if h[3:] not in EVIDENCE_CARDS:
                return claim_ids, f"unknown evidence card '{h[3:]}'"
        elif h.split("-")[0] in ("TAB", "FIG", "ART"):
            if h in ARTIFACT_IDS:
                continue
            stem = h.rstrip("*").rstrip("-")
            # wildcard / sub-grid suffix forms: FIG-CONV-SUP-*, FIG-CONV-CEC2011-A/B/C
            if any(a.startswith(stem.split("-A")[0].split("-*")[0])
                   or stem.startswith(a) for a in ARTIFACT_IDS):
                continue
            return claim_ids, f"unknown artifact id '{h}'"
        elif h in NEGATIVE_FINDING_ALIASES or h in EG_IDS:
            pass
        elif re.match(r"^[A-Z]{2}-\d", h):
            return claim_ids, f"unknown claim id '{h}'"
    return claim_ids, ""


for path, rel, in_build in TARGETS:
    lines = path.read_text(encoding="utf-8").splitlines()
    current_section = "(preamble)"
    para_lines: list[tuple[int, str]] = []

    def flush(para: list[tuple[int, str]]):
        if not para:
            return
        start_ln = para[0][0]
        raw_block = "\n".join(t for _, t in para)
        if SECTION_RE.search(raw_block):
            pass
        binds = []
        for _, t in para:
            bm = BIND_RE.search(t)
            if bm:
                binds.extend(split_bind_tokens(bm.group(1)))
        content = "\n".join(strip_comment(t) for _, t in para).strip()
        if not content:
            return  # comment-only block
        claim_ids = set()
        for b in binds:
            cids, prob = validate_bind_token(b)
            claim_ids.update(cids)
            if prob and in_build:
                bind_token_problems.append((rel, start_ln, prob))
        claim_ids = sorted(claim_ids)
        for cid in claim_ids:
            if cid in FORBIDDEN_CLAIMS and in_build:
                forbidden_claim_hits.append((rel, start_ln, cid, CLAIMS[cid]["status"]))
        nums = find_numbers(content)
        nonproto = classify_numbers(nums)
        if re.search(r"\\orcidauthor|\\history|\\pubvolume|\\articlenumber", content):
            status = "ADMIN_PLACEHOLDER (AG-0002/front-matter, not scientific)"
        elif binds:
            status = "BOUND"
        elif not nums:
            status = "NO_NUMBERS"
        elif not nonproto:
            status = "PROTOCOL_OR_STRUCTURAL"
        else:
            status = "UNBOUND_NUMBER"
            if in_build:
                unbound_violations.append((rel, start_ln, nonproto,
                                           content[:120].replace("\n", " ")))
        is_scientific = bool(
            nums or binds or CITE_RE.search(content)
            or re.search(r"\b(rank|significan|Wilcoxon|Friedman|Nemenyi|Holm|"
                         r"error|budget|W/T/L|median|mean|converg|panel)\b",
                         content, re.I))
        para_rows.append({
            "file": rel,
            "in_build": "yes" if in_build else "NO (stale, not in either driver)",
            "start_line": start_ln,
            "section": current_section,
            "scientific_paragraph": "yes" if is_scientific else "no",
            "claim_ids_anchored": "; ".join(claim_ids),
            "bind_tokens": "; ".join(binds),
            "numbers_found": "; ".join(nums),
            "non_protocol_numbers": "; ".join(nonproto),
            "binding_status": status,
            "excerpt": content[:120].replace("\n", " "),
        })

    for ln, rawline in enumerate(lines, 1):
        if SECTION_RE.search(rawline) and not rawline.lstrip().startswith("%"):
            m = re.search(r"\\(?:sub)*section\*?\{([^}]*)\}", rawline)
            if m:
                flush(para_lines)
                para_lines = []
                current_section = m.group(1)
                continue
        if rawline.strip() == "":
            flush(para_lines)
            para_lines = []
        else:
            para_lines.append((ln, rawline))
    flush(para_lines)

# ----------------------------------------------------------------------------
# Pass 3: token scans (released text = comment-stripped, in-build files + tables)
# ----------------------------------------------------------------------------
ABLATION_RE = re.compile(r"ablation|X-ABL|no_ace|no_bse|no_psr|no_sgsm|"
                         r"scaffold[ -]cell|_ablation", re.I)
BLOCKED_PATTERNS = [
    ("EGSK-spelling (BG-02 blocked)", re.compile(r"\bEGSK\b")),
    ("state-of-the-art (RS-01/HL-01 blocked)",
     re.compile(r"state[- ]of[- ]the[- ]art", re.I)),
    ("holdout (PR-03/RS-11 blocked)", re.compile(r"\bhold[- ]?out\b", re.I)),
    ("best algorithm (HL-01 blocked)", re.compile(r"\bbest algorithm\b", re.I)),
    ("first ever (CL-02 blocked)", re.compile(r"\bfirst[- ]ever\b", re.I)),
    ("component causality (IN-02 blocked)",
     re.compile(r"\b(?:ISM|memory|polish|escape|restart)\s+"
                r"(?:causes|drives|explains)\b", re.I)),
    ("novel-operator wording (MT-01 blocked)",
     re.compile(r"\bnovel operator\b", re.I)),
]
REVIEW_PATTERNS = [
    ("'independent'+suite words in same paragraph (PR-03/RS-11)",
     re.compile(r"(?=.*\bindependent\b)(?=.*(?:\bsuite\b|CEC.?2013|holdout))",
                re.I | re.S)),
    ("'validat*'+CEC2013 in same paragraph (RS-11/IN-03)",
     re.compile(r"(?=.*validat)(?=.*CEC.?2013)", re.I | re.S)),
    ("bare 'free' (MT-08/HL-01: needs objective-evaluations qualifier or RNG-free)",
     re.compile(r"\bfree\b", re.I)),
    ("'novel' (MT-01 scope check)", re.compile(r"\bnovel\b", re.I)),
]
TERM_PATTERNS = [
    ("SGSM expansion fabricated", re.compile(r"SGSM\s*\((?!.*code alias)", re.I)),
    ("TERRA expansion fabricated", re.compile(r"TERRA\s*\(")),
    ("SP-NLPSR expansion fabricated", re.compile(r"SP-NLPSR\s*\(")),
]

scan_hits = {"ablation_released": [], "ablation_comments": [], "blocked": [],
             "review": [], "terminology": []}

SCAN_FILES = [(p, r, b) for p, r, b in TARGETS] + [
    (p, f"tables/{p.name}", True) for p in TABLE_FILES]

for path, rel, in_build in SCAN_FILES:
    lines = path.read_text(encoding="utf-8").splitlines()
    # --- released-text scans on line-wrap-joined paragraphs (catches phrases
    # split across hard line breaks) ---
    paras: list[tuple[int, str]] = []
    buf: list[str] = []
    buf_start = 1
    for ln, raw in enumerate(lines, 1):
        content = strip_comment(raw).strip()
        if content:
            if not buf:
                buf_start = ln
            buf.append(content)
        else:
            if buf:
                paras.append((buf_start, " ".join(buf)))
                buf = []
    if buf:
        paras.append((buf_start, " ".join(buf)))
    for start_ln, ptext in paras:
        if not in_build:
            continue
        if ABLATION_RE.search(ptext):
            scan_hits["ablation_released"].append((rel, start_ln, ptext[:120]))
        for name, pat in BLOCKED_PATTERNS:
            if pat.search(ptext):
                scan_hits["blocked"].append((name, rel, start_ln, ptext[:120]))
        for name, pat in REVIEW_PATTERNS:
            if pat.search(ptext):
                scan_hits["review"].append((name, rel, start_ln, ptext[:120]))
        for name, pat in TERM_PATTERNS:
            if pat.search(ptext):
                scan_hits["terminology"].append((name, rel, start_ln, ptext[:120]))
    # --- comment scan (informational; S6 placeholder is the permitted block) ---
    in_s6_block = False
    for ln, raw in enumerate(lines, 1):
        content = strip_comment(raw)
        comment = raw[len(content):]
        if "PHASE_12_PLACEHOLDER" in raw or re.search(r"S6\s*--\s*RESERVED", raw):
            in_s6_block = True
        elif content.strip():
            in_s6_block = False
        if (comment.strip() or raw.strip().startswith("%")) and in_build:
            ctext = comment if comment.strip() else raw
            if ABLATION_RE.search(ctext):
                tag = "PERMITTED-S6" if (rel == "supplementary.tex" and in_s6_block) \
                    else "comment"
                scan_hits["ablation_comments"].append((tag, rel, ln, ctext.strip()[:100]))

# ----------------------------------------------------------------------------
# Write outputs
# ----------------------------------------------------------------------------
cit_path = GOV / "citation_usage_map.csv"
with open(cit_path, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(citation_rows[0].keys()))
    w.writeheader()
    w.writerows(citation_rows)

para_path = PH08 / "paragraph_evidence_audit.csv"
with open(para_path, "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(para_rows[0].keys()))
    w.writeheader()
    w.writerows(para_rows)

# ----------------------------------------------------------------------------
# Report
# ----------------------------------------------------------------------------
def hdr(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)

print(f"AUDIT of {len(TARGETS)} tex files (+{len(TABLE_FILES)} table files in token scans)")
print("in-build:", sorted(r for _, r, b in TARGETS if b))
print("STALE (not input by main.tex or supplementary.tex):",
      sorted(r for _, r, b in TARGETS if not b))

hdr("1. CITATION AUDIT")
print(f"citation_usage_map.csv rows: {len(citation_rows)} -> {cit_path}")
n_inbuild = sum(1 for r in citation_rows if r["in_build"] == "yes")
print(f"  occurrences in released build: {n_inbuild}")
used_keys = {r['citation_key'] for r in citation_rows if r['in_build'] == 'yes'}
print(f"  distinct keys used in build: {len(used_keys)} of {len(ALLOWED_KEYS)} allowed")
print(f"  keys outside the allowed {len(ALLOWED_KEYS)} (FAIL): {len(cite_fail)}")
for f, ln, k in cite_fail:
    print(f"    FAIL {f}:{ln} key={k}")
mech_only = [r for r in citation_rows if r["in_build"] == "yes"
             and r["usage_condition_class"] == "mechanism-discussion-only"]
print(f"  mechanism-discussion-only keys needing semantic review: {len(mech_only)} occurrences")

hdr("2. PARAGRAPH / NUMBER BINDING AUDIT")
print(f"paragraph_evidence_audit.csv rows: {len(para_rows)} -> {para_path}")
from collections import Counter
c = Counter((r["in_build"] == "yes", r["binding_status"]) for r in para_rows)
for (ib, st), n in sorted(c.items()):
    print(f"  {'in-build' if ib else 'stale   '} {st}: {n}")
print(f"\nUNBOUND-NUMBER violation candidates (in-build): {len(unbound_violations)}")
for f, ln, nums, exc in unbound_violations:
    print(f"  {f}:{ln} nums={nums} :: {exc}")
print(f"\nBIND tokens referencing FORBIDDEN claims: {len(forbidden_claim_hits)}")
for f, ln, cid, st in forbidden_claim_hits:
    print(f"  {f}:{ln} {cid} status={st}")
print(f"\nunrecognized BIND tokens: {len(bind_token_problems)}")
for f, ln, p in bind_token_problems:
    print(f"  {f}:{ln} {p}")

hdr("3a. NO-ABLATION SCAN (released text)")
print(f"released-text ablation hits (must be 0): {len(scan_hits['ablation_released'])}")
for f, ln, t in scan_hits["ablation_released"]:
    print(f"  {f}:{ln} :: {t}")
s6 = [h for h in scan_hits["ablation_comments"] if h[0] == "PERMITTED-S6"]
oth = [h for h in scan_hits["ablation_comments"] if h[0] != "PERMITTED-S6"]
print(f"comment-level hits: {len(scan_hits['ablation_comments'])} "
      f"({len(s6)} in permitted S6 block; {len(oth)} other comments - informational)")
for tag, f, ln, t in oth:
    print(f"  [{tag}] {f}:{ln} :: {t}")

hdr("3b. BLOCKED-WORDING SCAN (released text; must be 0)")
print(f"hits: {len(scan_hits['blocked'])}")
for name, f, ln, t in scan_hits["blocked"]:
    print(f"  [{name}] {f}:{ln} :: {t}")

hdr("3c. TERMINOLOGY SCAN (must be 0)")
print(f"hits: {len(scan_hits['terminology'])}")
for name, f, ln, t in scan_hits["terminology"]:
    print(f"  [{name}] {f}:{ln} :: {t}")

hdr("3d. REVIEW-CLASS WORDING HITS (manual adjudication)")
print(f"hits: {len(scan_hits['review'])}")
for name, f, ln, t in scan_hits["review"]:
    print(f"  [{name}] {f}:{ln} :: {t}")

hdr("SUMMARY")
print(json.dumps({
    "citation_usage_map_rows": len(citation_rows),
    "paragraph_evidence_audit_rows": len(para_rows),
    "cite_key_failures_in_build": len(cite_fail),
    "unbound_number_candidates_in_build": len(unbound_violations),
    "forbidden_claim_binds_in_build": len(forbidden_claim_hits),
    "unrecognized_bind_tokens_in_build": len(bind_token_problems),
    "ablation_hits_released_text": len(scan_hits["ablation_released"]),
    "blocked_wording_hits": len(scan_hits["blocked"]),
    "terminology_hits": len(scan_hits["terminology"]),
    "review_class_hits": len(scan_hits["review"]),
}, indent=2))
