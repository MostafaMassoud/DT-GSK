#!/usr/bin/env python3
"""Gate: CITATION.cff must declare the version of the tag it ships inside.

Why this exists
---------------
Zenodo reads ``CITATION.cff`` when it archives a GitHub Release, and it takes
the ``version:`` field from that file rather than from the tag name.  If the
file says ``2.4`` inside a tag named ``v2.5``, the permanent archive records
2.4 and the DOI points at a version that never existed.

This defect (registered as S8-01) recurred three times in this project --- at
v2.3, at v2.4, and again at v2.5 --- because the rule lived only in prose, in a
review register nobody re-reads at release time.  Prose did not hold, so this
is a gate.

What it checks
--------------
1. For every ``vN.M`` tag, the ``CITATION.cff`` committed *inside* that tag
   declares exactly ``N.M``.  This is the invariant Zenodo actually consumes.
2. The working tree's ``CITATION.cff`` is not behind the newest tag, so the
   next tag starts from a correct file.
3. No comment in ``CITATION.cff`` references a stale version, which is how the
   "doi: added after the ... v2.4 release" line survived into v2.5.

Exit code 0 on pass, 1 on any failure.  Read-only; touches nothing.
"""
from __future__ import annotations

import re
import subprocess
import sys

CFF = "CITATION.cff"

# Published tags are never re-pointed in this project, so historical mismatches
# are immutable facts rather than actionable defects.  Each is exempted here
# ONLY with a reason, so the gate fails on new mismatches instead of staying
# permanently red.  Never add an entry to silence a tag you could still fix.
KNOWN_HISTORICAL_MISMATCHES = {
    "v2.2": ("embeds 2.1; found by this gate on 2026-08-01, after the tag was "
             "already published. No GitHub Release or Zenodo archive was ever "
             "cut from it, so nothing external records the wrong version."),
    "v2.5": ("embeds 2.4; the defect that motivated this gate. Superseded by "
             "v2.6, which carries the correct version and is the Release basis. "
             "No Release or Zenodo archive was cut from v2.5."),
}

TAG_RE = re.compile(r"^v(\d+)\.(\d+)$")
VERSION_RE = re.compile(r"^version:\s*[\"']?(\d+\.\d+)[\"']?\s*$", re.MULTILINE)
# a comment naming a version, e.g. "# doi: added after ... the v2.4 release"
COMMENT_VERSION_RE = re.compile(r"^\s*#.*?\bv?(\d+\.\d+)\b.*$", re.MULTILINE)


def git(*args: str) -> str:
    out = subprocess.run(["git", *args], capture_output=True, text=True)
    if out.returncode != 0:
        raise SystemExit("git %s failed: %s" % (" ".join(args), out.stderr.strip()))
    return out.stdout


def declared_version(text: str, where: str) -> str:
    m = VERSION_RE.search(text)
    if not m:
        raise SystemExit("FAIL: no 'version:' field in %s" % where)
    return m.group(1)


def version_tags() -> list[tuple[tuple[int, int], str]]:
    tags = []
    for line in git("tag").splitlines():
        m = TAG_RE.match(line.strip())
        if m:
            tags.append(((int(m.group(1)), int(m.group(2))), line.strip()))
    tags.sort()
    return tags


def main() -> int:
    failures: list[str] = []
    tags = version_tags()
    if not tags:
        print("PASS: no vN.M tags yet; nothing to check.")
        return 0

    # (1) every tag must embed its own version
    for _, tag in tags:
        try:
            blob = git("show", "%s:%s" % (tag, CFF))
        except SystemExit:
            failures.append("%s does not contain %s" % (tag, CFF))
            continue
        got = declared_version(blob, "%s:%s" % (tag, CFF))
        want = tag.lstrip("v")
        if got == want:
            status = "ok"
        elif tag in KNOWN_HISTORICAL_MISMATCHES:
            status = "MISMATCH (exempt: immutable published tag)"
        else:
            status = "MISMATCH"
        print("  %-8s embeds version %-6s expected %-6s %s" % (tag, got, want, status))
        if got != want and tag not in KNOWN_HISTORICAL_MISMATCHES:
            failures.append(
                "%s embeds CITATION.cff version %s but the tag is %s. Zenodo would "
                "archive %s. Fix: bump %s and cut a superseding tag (published tags "
                "are never re-pointed in this project)." % (tag, got, want, got, CFF))

    newest_ver, newest_tag = tags[-1]
    newest_str = "%d.%d" % newest_ver

    # (2) the working tree must not be behind the newest tag
    with open(CFF, encoding="utf-8") as fh:
        tree_text = fh.read()
    tree_ver = declared_version(tree_text, "working tree %s" % CFF)
    tree_tuple = tuple(int(p) for p in tree_ver.split("."))
    print("  working tree embeds version %s; newest tag is %s" % (tree_ver, newest_tag))
    if tree_tuple < newest_ver:
        failures.append(
            "working-tree %s declares %s, behind the newest tag %s. The next tag "
            "would inherit a stale version." % (CFF, tree_ver, newest_tag))

    # (3) no comment may name a version other than the current one
    for m in COMMENT_VERSION_RE.finditer(tree_text):
        named = m.group(1)
        if named != tree_ver:
            failures.append(
                "%s comment names version %s while the file declares %s: %r"
                % (CFF, named, tree_ver, m.group(0).strip()))

    if failures:
        print("\nFAIL: %d problem(s)" % len(failures))
        for f in failures:
            print("  - %s" % f)
        return 1
    print("\nPASS: CITATION.cff version is consistent with every tag (%d checked)."
          % len(tags))
    return 0


if __name__ == "__main__":
    sys.exit(main())
