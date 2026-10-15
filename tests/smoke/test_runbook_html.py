"""runbook.html and the docs-site runbook page are generated from runbook.md.

If this fails after an edit to runbook.md, regenerate both files with
``python scripts/build_runbook_html.py`` and commit them with the edit.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

_PATH = Path(__file__).resolve().parents[2] / "scripts" / "build_runbook_html.py"
_SPEC = importlib.util.spec_from_file_location("build_runbook_html", _PATH)
_MOD = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault(_SPEC.name, _MOD)
_SPEC.loader.exec_module(_MOD)


def test_generated_runbook_files_are_up_to_date():
    for path, expected in _MOD.outputs().items():
        current = path.read_bytes().replace(b"\r\n", b"\n").decode("utf-8")
        assert current == expected, f"{path.name} is stale: run python scripts/build_runbook_html.py"


def _headings(markdown: str) -> list[str]:
    """Return the Markdown heading titles, ignoring ``#`` comment lines inside fenced code."""
    found, in_code = [], False
    for line in markdown.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        elif not in_code and (m := re.match(r"^#{1,6}\s+(.+)$", line)):
            found.append(m.group(1).strip())
    return found


def _github_slug(text: str) -> str:
    """GitHub's heading anchor: lower case, punctuation dropped, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", text.strip().lower()).replace(" ", "-")


def test_runbook_in_page_links_resolve():
    markdown = _MOD.SOURCE.read_text(encoding="utf-8")
    titles = _headings(markdown)
    anchors = set(re.findall(r"\]\(#([^)]+)\)", markdown))
    assert anchors, "expected in-page links in runbook.md"
    html_ids = {_MOD._DOCS.slugify(t) for t in titles}
    github_ids = {_github_slug(t) for t in titles}
    assert anchors <= html_ids, ("runbook.html ids", sorted(anchors - html_ids))
    assert anchors <= github_ids, ("GitHub anchors", sorted(anchors - github_ids))


def test_inbound_runbook_anchors_resolve():
    # Every "runbook.md#anchor" link in the docs must land on a real heading of
    # the file it names (the root runbook or the generated Part 1 mirror).
    root = _MOD.ROOT
    bad = []
    for md in [root / "README.md", root / "SKILL.md", *sorted((root / "docs").rglob("*.md"))]:
        if "html" in md.relative_to(root).parts:
            continue
        text = md.read_text(encoding="utf-8")
        for target, anchor in re.findall(r"\]\(([^)#\s]*runbook\.md)#([^)]+)\)", text):
            page = (md.parent / target).resolve()
            titles = _headings(page.read_text(encoding="utf-8-sig")) if page.is_file() else []
            # GitHub renders the Markdown; docs/html and runbook.html use slugify.
            github_ids = {_github_slug(t) for t in titles}
            html_ids = {_MOD._DOCS.slugify(t) for t in titles}
            if anchor not in github_ids or anchor not in html_ids:
                bad.append(f"{md.relative_to(root).as_posix()} -> {target}#{anchor}")
    assert not bad, bad


def test_runbook_html_is_self_contained():
    page = _MOD.render_html(_MOD.SOURCE.read_text(encoding="utf-8"))
    assert not re.search(r"<(?:script|link|img)[^>]+(?:src|href)=\"https?:", page)
    assert "Part 1. Run and test DT-GSK" in page
    assert page.count('class="copy"') == 0  # copy buttons are added in the browser, not baked in
    assert page.count("<pre>") >= 20
