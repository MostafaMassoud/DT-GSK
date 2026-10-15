"""Generate ``runbook.html`` and the docs-site runbook page from ``runbook.md``.

``runbook.md`` at the repository root is the single source. This script writes:

* ``runbook.html``: a standalone, self-contained page (no external assets)
  with a contents sidebar, light and dark themes, and a copy button on every
  command, so anyone can open it in a browser;
* ``docs/getting-started/runbook.md``: the docs-site copy of Part 1 (the
  run-and-test guide), with links re-pointed from ``docs/getting-started/``.
  ``scripts/build_docs_html.py`` then renders it into ``docs/html/``.

Run from the repository root after every edit to ``runbook.md``::

    python scripts/build_runbook_html.py           # write both files
    python scripts/build_runbook_html.py --check   # exit 1 if either is stale

The Markdown renderer is the one ``scripts/build_docs_html.py`` uses, so the
two HTML outputs agree on what each construct means.
"""

from __future__ import annotations

import argparse
import html
import importlib.util
import posixpath
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "runbook.md"
HTML_OUT = ROOT / "runbook.html"
MIRROR_OUT = ROOT / "docs" / "getting-started" / "runbook.md"
MIRROR_DIR = "docs/getting-started"
PART2_HEADING = "## Part 2. Maintainer and paper-pipeline reference"

_SPEC = importlib.util.spec_from_file_location("build_docs_html", Path(__file__).with_name("build_docs_html.py"))
assert _SPEC is not None and _SPEC.loader is not None
_DOCS = importlib.util.module_from_spec(_SPEC)
sys.modules.setdefault(_SPEC.name, _DOCS)  # dataclasses resolve annotations through sys.modules
_SPEC.loader.exec_module(_DOCS)

_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
_LIST_ITEM = re.compile(r"^\s*(?:[-*]|\d+\.)\s+")
_SELF_LINK = re.compile(r"\s*A formatted copy of this page,.*?open it in any web browser\.", re.S)


def _drop_self_link(part1: str) -> str:
    """Drop the intro sentence that sends readers to runbook.html; both outputs already link or are it."""
    text, count = _SELF_LINK.subn("", part1, count=1)
    if count != 1:
        raise SystemExit("runbook.md intro sentence about runbook.html changed; update _SELF_LINK")
    return text


def join_wrapped_lines(markdown: str) -> str:
    """Join wrapped list items and blockquotes into single lines.

    The shared renderer reads one line per list item and per quote line; a
    wrapped item would otherwise split into a list item plus a stray paragraph.
    Fenced code blocks are left untouched.
    """
    out: list[str] = []
    in_code = False
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code = not in_code
            out.append(line)
            continue
        if in_code or not out or not stripped:
            out.append(line)
            continue
        previous = out[-1]
        prev_stripped = previous.strip()
        if prev_stripped.startswith(">") and stripped.startswith(">"):
            out[-1] = f"{previous.rstrip()} {stripped[1:].strip()}"
            continue
        if (
            prev_stripped
            and _LIST_ITEM.match(previous)
            and line.startswith((" ", "\t"))
            and not _LIST_ITEM.match(line)
        ):
            out[-1] = f"{previous.rstrip()} {stripped}"
            continue
        out.append(line)
    return "\n".join(out) + "\n"


def split_parts(markdown: str) -> tuple[str, str]:
    """Split the runbook into (title + Part 1, Part 2) at the Part 2 heading."""
    head, sep, tail = markdown.partition(PART2_HEADING)
    if not sep:
        raise SystemExit(f"runbook.md has no '{PART2_HEADING}' heading")
    head = re.sub(r"\n---\s*\n*$", "\n", head.rstrip() + "\n")
    return head, sep + tail


def _is_relative(target: str) -> bool:
    return not (re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith(("#", "/")))


def identity_link_map(markdown: str) -> dict[str, str]:
    """Map every repository-relative link target to itself (root-level output)."""
    targets = {}
    for _, target in _LINK.findall(markdown):
        path = target.split("#", 1)[0]
        if path and _is_relative(path):
            targets[path] = path
    return targets


def render_html(markdown: str) -> str:
    """Render ``runbook.md`` into the standalone ``runbook.html`` page."""
    part1, part2 = split_parts(join_wrapped_lines(markdown))
    part1 = _drop_self_link(part1)
    link_map = identity_link_map(markdown)
    body1, toc1 = _DOCS.render_markdown(part1, link_map)
    body2, toc2 = _DOCS.render_markdown(part2, link_map)
    title = next((t for level, t, _ in toc1 if level == 1), "Runbook")
    nav = []
    for level, text, anchor in toc1 + toc2:
        if level == 1:
            continue
        cls = "nav-part" if anchor.startswith("part-") else "nav-step"
        nav.append(f'<a class="{cls}" href="#{anchor}">{html.escape(_strip_md(text))}</a>')
    return TEMPLATE.format(
        title=html.escape(f"DT-GSK {title}"),
        nav="\n        ".join(nav),
        part1=body1,
        part2=body2,
    )


def _strip_md(text: str) -> str:
    return re.sub(r"[`*]", "", text)


def mirror_markdown(markdown: str) -> str:
    """Build ``docs/getting-started/runbook.md``: Part 1, links re-pointed."""
    part1, _ = split_parts(join_wrapped_lines(markdown))
    part1 = _drop_self_link(part1)
    anchors = {_DOCS.slugify(m.group(1)) for m in re.finditer(r"^#{1,6}\s+(.+)$", part1, re.M)}

    def repoint(match: re.Match[str]) -> str:
        label, target = match.group(1), match.group(2)
        if target.startswith("#"):
            if target[1:] in anchors:
                return match.group(0)
            return f"[{label}](../../runbook.md{target})"
        if not _is_relative(target):
            return match.group(0)
        path, _, anchor = target.partition("#")
        rel = posixpath.relpath(path, MIRROR_DIR)
        return f"[{label}]({rel}{'#' + anchor if anchor else ''})"

    lines = part1.splitlines()
    body = "\n".join(lines[1:]).lstrip("\n")  # drop the source H1; the mirror has its own
    in_code = False
    out = []
    for line in body.splitlines():
        if line.strip().startswith("```"):
            in_code = not in_code
        out.append(line if in_code else _LINK.sub(repoint, line))
    header = (
        "# Runbook\n\n"
        "> Generated from the root [runbook.md](../../runbook.md) by "
        "`scripts/build_runbook_html.py`; edit that file, not this one. This page "
        "is Part 1, the run-and-test guide. Part 2, the maintainer and "
        "paper-pipeline reference, is in the [root runbook](../../runbook.md#part-2-maintainer-and-paper-pipeline-reference), "
        "and a standalone formatted copy is [runbook.html](../../runbook.html).\n\n"
    )
    return header + "\n".join(out).rstrip() + "\n"


def outputs() -> dict[Path, str]:
    """Return every generated file and its expected content."""
    markdown = SOURCE.read_text(encoding="utf-8")
    return {HTML_OUT: render_html(markdown), MIRROR_OUT: mirror_markdown(markdown)}


def main(argv: list[str] | None = None) -> int:
    """Write the generated files, or with ``--check`` report whether they are stale."""
    parser = argparse.ArgumentParser(description="Generate runbook.html and the docs-site runbook page.")
    parser.add_argument("--check", action="store_true", help="Exit 1 if a generated file is out of date.")
    args = parser.parse_args(argv)
    stale = []
    for path, content in outputs().items():
        data = content.encode("utf-8")
        current = path.read_bytes() if path.is_file() else b""
        # Compare ignoring CRLF vs LF: Git for Windows may check text out as CRLF.
        if current.replace(b"\r\n", b"\n") == data:
            continue
        stale.append(path.relative_to(ROOT).as_posix())
        if not args.check:
            path.write_bytes(data)
    if args.check:
        if stale:
            print("stale (run python scripts/build_runbook_html.py): " + ", ".join(stale))
            return 1
        print("runbook outputs are up to date")
        return 0
    print("wrote " + (", ".join(stale) if stale else "nothing (already up to date)"))
    if MIRROR_OUT.relative_to(ROOT).as_posix() in stale:
        print("docs/getting-started/runbook.md changed: run python scripts/build_docs_html.py to refresh docs/html/")
    return 0


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<!-- Generated from runbook.md by scripts/build_runbook_html.py. Do not edit by hand. -->
<style>
:root {{
  --bg: #fbfbfa; --surface: #ffffff; --text: #1f2328; --muted: #59636e;
  --border: #d8dee4; --accent: #0b6bcb; --accent-soft: #e8f1fb;
  --code-bg: #f3f4f6; --code-text: #1f2328; --callout: #fff8e6; --callout-border: #e0a800;
  --part2: #6e7781;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    --bg: #0f1216; --surface: #161b22; --text: #e6edf3; --muted: #9da7b3;
    --border: #30363d; --accent: #58a6ff; --accent-soft: #132339;
    --code-bg: #1c2128; --code-text: #e6edf3; --callout: #2a2410; --callout-border: #b08800;
    --part2: #8b949e;
  }}
}}
:root[data-theme="dark"] {{
  --bg: #0f1216; --surface: #161b22; --text: #e6edf3; --muted: #9da7b3;
  --border: #30363d; --accent: #58a6ff; --accent-soft: #132339;
  --code-bg: #1c2128; --code-text: #e6edf3; --callout: #2a2410; --callout-border: #b08800;
  --part2: #8b949e;
}}
* {{ box-sizing: border-box; }}
html {{ scroll-behavior: smooth; scroll-padding-top: 16px; }}
body {{ margin: 0; background: var(--bg); color: var(--text);
  font: 16px/1.65 system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }}
.layout {{ display: grid; grid-template-columns: 290px minmax(0, 1fr); max-width: 1280px; margin: 0 auto; }}
nav.toc {{ position: sticky; top: 0; height: 100vh; overflow-y: auto; padding: 28px 18px 28px 24px;
  border-right: 1px solid var(--border); font-size: 14px; }}
nav.toc .brand {{ font-weight: 700; font-size: 17px; margin-bottom: 4px; }}
nav.toc .sub {{ color: var(--muted); margin-bottom: 18px; }}
nav.toc a {{ display: block; color: var(--muted); text-decoration: none; padding: 4px 10px; border-radius: 6px;
  border-left: 3px solid transparent; }}
nav.toc a:hover {{ color: var(--text); background: var(--accent-soft); }}
nav.toc a.active {{ color: var(--accent); border-left-color: var(--accent); background: var(--accent-soft); }}
nav.toc a.nav-part {{ margin-top: 14px; font-weight: 650; color: var(--text); }}
nav.toc a.nav-step {{ padding-left: 20px; }}
nav.toc summary {{ cursor: pointer; font-weight: 650; color: var(--muted); margin-bottom: 6px; }}
@media (min-width: 1001px) {{ nav.toc summary {{ display: none; }} }}
main {{ padding: 36px 48px 80px; min-width: 0; }}
.content {{ max-width: 860px; }}
h1 {{ font-size: 34px; line-height: 1.2; margin: 0 0 12px; letter-spacing: -0.01em; }}
h2 {{ font-size: 26px; line-height: 1.25; margin: 48px 0 12px; padding-bottom: 8px; border-bottom: 1px solid var(--border); }}
h3 {{ font-size: 20px; margin: 36px 0 10px; color: var(--accent); }}
h4 {{ font-size: 17px; margin: 24px 0 8px; }}
p, ul, ol {{ margin: 0 0 14px; }}
li {{ margin: 6px 0; }}
p, li, blockquote {{ overflow-wrap: anywhere; }}
td, th {{ overflow-wrap: break-word; }}
td:first-child code {{ white-space: nowrap; overflow-wrap: normal; }}
a {{ color: var(--accent); }}
code {{ font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace; font-size: 0.88em;
  background: var(--code-bg); color: var(--code-text); padding: 1px 6px; border-radius: 5px; overflow-wrap: anywhere; }}
pre {{ position: relative; background: var(--code-bg); border: 1px solid var(--border); border-radius: 10px;
  padding: 14px 16px; margin: 0 0 18px; overflow-x: auto; }}
pre code {{ background: none; padding: 0; font-size: 13.5px; line-height: 1.55; white-space: pre; overflow-wrap: normal; }}
.copy {{ position: absolute; top: 8px; right: 8px; font: 12px/1 system-ui, sans-serif; padding: 6px 10px;
  border-radius: 6px; border: 1px solid var(--border); background: var(--surface); color: var(--muted); cursor: pointer; }}
.copy:hover {{ color: var(--text); border-color: var(--accent); }}
.copy.done {{ color: var(--accent); border-color: var(--accent); }}
.table-wrap {{ overflow-x: auto; margin: 0 0 18px; border: 1px solid var(--border); border-radius: 10px; }}
table {{ border-collapse: collapse; width: 100%; font-size: 15px; background: var(--surface); }}
th, td {{ text-align: left; vertical-align: top; padding: 9px 12px; border-bottom: 1px solid var(--border); }}
th {{ background: var(--code-bg); font-weight: 650; }}
tr:last-child td {{ border-bottom: none; }}
blockquote {{ margin: 0 0 18px; padding: 12px 16px; background: var(--callout); border-left: 4px solid var(--callout-border);
  border-radius: 0 8px 8px 0; }}
.part {{ background: var(--surface); border: 1px solid var(--border); border-radius: 14px; padding: 8px 36px 28px;
  margin-bottom: 28px; }}
.part.maintainer {{ border-style: dashed; }}
.part.maintainer > h2:first-child {{ color: var(--part2); }}
.part > h1:first-child, .part > h2:first-child {{ margin-top: 28px; }}
.badge {{ display: inline-block; font-size: 12px; font-weight: 650; letter-spacing: 0.04em; text-transform: uppercase;
  padding: 3px 10px; border-radius: 999px; background: var(--accent-soft); color: var(--accent); margin: 24px 0 0; }}
.badge.maint {{ background: var(--code-bg); color: var(--part2); }}
.theme {{ margin-top: 18px; font: 13px system-ui, sans-serif; padding: 6px 10px; border-radius: 6px;
  border: 1px solid var(--border); background: var(--surface); color: var(--muted); cursor: pointer; }}
.top {{ position: fixed; right: 18px; bottom: 18px; padding: 8px 12px; border-radius: 999px; background: var(--surface);
  border: 1px solid var(--border); color: var(--muted); text-decoration: none; font-size: 13px; }}
@media (max-width: 1000px) {{
  .layout {{ display: block; }}
  nav.toc {{ position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); padding: 20px 16px; }}
  main {{ padding: 20px 16px 64px; }}
  .part {{ padding: 4px 16px 20px; }}
}}
@media print {{
  nav.toc, .copy, .top, .theme {{ display: none; }}
  .layout {{ display: block; }}
  .part {{ border: none; padding: 0; }}
  pre {{ white-space: pre-wrap; }}
}}
</style>
</head>
<body>
<div class="layout">
  <nav class="toc" aria-label="Contents">
    <div class="brand">DT-GSK Runbook</div>
    <div class="sub">Install, test and run</div>
    <details id="contents" open>
      <summary>Contents</summary>
        {nav}
    </details>
    <button class="theme" type="button" id="theme">Switch light / dark</button>
  </nav>
  <main>
    <div class="content">
      <section class="part">
        <span class="badge">For everyone</span>
{part1}
      </section>
      <section class="part maintainer">
        <span class="badge maint">For maintainers</span>
{part2}
      </section>
    </div>
  </main>
</div>
<a class="top" href="#">Back to top</a>
<script>
(function () {{
  document.querySelectorAll("pre").forEach(function (pre) {{
    var button = document.createElement("button");
    button.className = "copy"; button.type = "button"; button.textContent = "Copy";
    button.addEventListener("click", function () {{
      var text = pre.querySelector("code") ? pre.querySelector("code").innerText : pre.innerText;
      function done() {{ button.textContent = "Copied"; button.classList.add("done");
        setTimeout(function () {{ button.textContent = "Copy"; button.classList.remove("done"); }}, 1500); }}
      if (navigator.clipboard && window.isSecureContext) {{
        navigator.clipboard.writeText(text).then(done);
      }} else {{
        var area = document.createElement("textarea"); area.value = text; document.body.appendChild(area);
        area.select(); try {{ document.execCommand("copy"); done(); }} catch (e) {{}} document.body.removeChild(area);
      }}
    }});
    pre.appendChild(button);
  }});
  var links = Array.prototype.slice.call(document.querySelectorAll("nav.toc a[href^='#']"));
  var byId = {{}};
  links.forEach(function (a) {{ byId[a.getAttribute("href").slice(1)] = a; }});
  if ("IntersectionObserver" in window) {{
    var observer = new IntersectionObserver(function (entries) {{
      entries.forEach(function (entry) {{
        if (entry.isIntersecting && byId[entry.target.id]) {{
          links.forEach(function (a) {{ a.classList.remove("active"); }});
          byId[entry.target.id].classList.add("active");
        }}
      }});
    }}, {{ rootMargin: "0px 0px -75% 0px" }});
    Object.keys(byId).forEach(function (id) {{ var el = document.getElementById(id); if (el) observer.observe(el); }});
  }}
  var contents = document.getElementById("contents");
  var narrow = window.matchMedia("(max-width: 1000px)");
  function syncContents() {{
    if (narrow.matches) {{ contents.removeAttribute("open"); }} else {{ contents.setAttribute("open", ""); }}
  }}
  syncContents();
  if (narrow.addEventListener) {{ narrow.addEventListener("change", syncContents); }} else {{ narrow.addListener(syncContents); }}
  var root = document.documentElement;
  try {{ var saved = localStorage.getItem("runbook-theme"); if (saved) root.setAttribute("data-theme", saved); }} catch (e) {{}}
  document.getElementById("theme").addEventListener("click", function () {{
    var dark = root.getAttribute("data-theme") === "dark" ||
      (!root.getAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
    var next = dark ? "light" : "dark";
    root.setAttribute("data-theme", next);
    try {{ localStorage.setItem("runbook-theme", next); }} catch (e) {{}}
  }});
}})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    sys.exit(main())
