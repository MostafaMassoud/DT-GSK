"""Build a static HTML documentation site from Markdown and Python docstrings."""

from __future__ import annotations

import argparse
import ast
import html
import json
import posixpath
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


PROJECT_TITLE = "GSK Family Python Documentation"
SOURCE_GLOBS = ("*.md",)
SKIP_DIR_NAMES = {"html"}


@dataclass(frozen=True)
class Page:
    """One Markdown-backed documentation page."""

    source: Path
    output: Path
    title: str
    group: str
    relative_key: str


@dataclass(frozen=True)
class ApiMember:
    """One function, class, or method extracted from Python source."""

    kind: str
    name: str
    signature: str
    docstring: str
    lineno: int
    children: tuple["ApiMember", ...] = ()


@dataclass(frozen=True)
class ApiModule:
    """One generated Python API module page."""

    module_name: str
    source: Path
    output: Path
    docstring: str
    members: tuple[ApiMember, ...]


def slugify(value: str) -> str:
    """Return a stable lower-case HTML id."""
    cleaned = re.sub(r"[^A-Za-z0-9]+", "-", value.strip().lower()).strip("-")
    return cleaned or "section"


def page_output_name(relative: Path) -> str:
    """Return a stable flattened HTML name for a Markdown source path."""
    if relative.as_posix().lower() == "index.md":
        return "index.html"
    stem = relative.with_suffix("").as_posix().replace("/", "_")
    return f"{stem}.html"


def title_from_markdown(path: Path) -> str:
    """Read the first H1 from a Markdown file, falling back to the filename."""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("_", " ").replace("-", " ").title()


def group_for(relative: Path) -> str:
    """Return the sidebar group for a Markdown source path (keyed by folder)."""
    top = relative.parts[0] if len(relative.parts) > 1 else ""
    return {
        "getting-started": "Getting Started",
        "reference": "Reference",
        "algorithms": "Algorithm Guides",
        "development": "Development",
        "research": "Research",
        "prompt": "Prompts",
    }.get(top, "Reference")


def discover_markdown_pages(docs_root: Path, output_root: Path, _project_root: Path) -> list[Page]:
    """Discover Markdown documentation files that should become HTML pages."""
    pages: list[Page] = []
    for path in sorted(docs_root.rglob("*.md")):
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(docs_root).parts):
            continue
        relative = path.relative_to(docs_root)
        output = output_root / page_output_name(relative)
        pages.append(
            Page(
                source=path,
                output=output,
                title=title_from_markdown(path),
                group=group_for(relative),
                relative_key=relative.as_posix(),
            )
        )
    return pages


def inline_markdown(text: str, link_map: dict[str, str], current_dir: str = "") -> str:
    """Render the small inline Markdown subset used by project docs."""
    escaped = html.escape(text)

    def replace_code(match: re.Match[str]) -> str:
        return f"<code>{match.group(1)}</code>"

    escaped = re.sub(r"`([^`]+)`", replace_code, escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)

    def replace_link(match: re.Match[str]) -> str:
        label = match.group(1)
        target = html.unescape(match.group(2))
        href = rewrite_link(target, link_map, current_dir)
        return f'<a href="{html.escape(href, quote=True)}">{label}</a>'

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace_link, escaped)


def rewrite_link(target: str, link_map: dict[str, str], current_dir: str = "") -> str:
    """Rewrite Markdown documentation links to generated HTML links."""
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target) or target.startswith("#"):
        return target
    anchor = ""
    if "#" in target:
        target, anchor = target.split("#", 1)
        anchor = f"#{anchor}"
    # Strip only a leading "./" prefix; str.lstrip("./") would strip characters
    # and destroy "../" parent-relative links from nested doc pages.
    normalized = target.replace("\\", "/")
    while normalized.startswith("./"):
        normalized = normalized[2:]
    if normalized.startswith("html/"):
        return f"{normalized.removeprefix('html/')}{anchor}"
    candidates = [normalized]
    if normalized.startswith("../"):
        collapsed = normalized
        while collapsed.startswith("../"):
            collapsed = collapsed[3:]
        candidates.append(collapsed)
    if current_dir:
        candidates.append(posixpath.normpath(posixpath.join(current_dir, normalized)).lstrip("./"))
    if normalized.startswith("docs/"):
        candidates.append(normalized.removeprefix("docs/"))
    if normalized.startswith("../") and current_dir:
        candidates.append(posixpath.normpath(posixpath.join(current_dir, normalized)).lstrip("./"))
    for candidate in candidates:
        if candidate in link_map:
            return f"{link_map[candidate]}{anchor}"
        if candidate.endswith(".md") and candidate in link_map:
            return f"{link_map[candidate]}{anchor}"
    if normalized in link_map:
        return f"{link_map[normalized]}{anchor}"
    if normalized.endswith(".md") and normalized in link_map:
        return f"{link_map[normalized]}{anchor}"
    # No generated page for this target, so the link points at a real file that
    # is NOT rewritten: a root document (REVISION_STATUS.md, README.md), or an
    # artifact under papers/. Such a link was authored relative to its Markdown
    # SOURCE under docs/, but every Markdown page is emitted flattened into
    # docs/html/ -- one directory deeper than docs/ -- so passing the link
    # through unchanged leaves it exactly one hop short. Resolve it against the
    # source's own directory to get a path relative to docs/, then add the hop
    # back out of html/.
    if normalized.startswith("/"):
        return f"{target}{anchor}"
    resolved = posixpath.normpath(posixpath.join(current_dir, normalized))
    return f"../{resolved}{anchor}"


def render_table(lines: list[str], link_map: dict[str, str], current_dir: str = "") -> str:
    """Render a GitHub-style pipe table."""
    headers = [cell.strip() for cell in lines[0].strip().strip("|").split("|")]
    rows = lines[2:]
    out = ["<div class=\"table-wrap\"><table>", "<thead><tr>"]
    for header in headers:
        out.append(f"<th>{inline_markdown(header, link_map, current_dir)}</th>")
    out.append("</tr></thead><tbody>")
    for row in rows:
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        out.append("<tr>")
        for cell in cells:
            out.append(f"<td>{inline_markdown(cell, link_map, current_dir)}</td>")
        out.append("</tr>")
    out.append("</tbody></table></div>")
    return "".join(out)


def is_table_start(lines: list[str], index: int) -> bool:
    """Return True when the current line starts a Markdown pipe table."""
    if index + 1 >= len(lines):
        return False
    return "|" in lines[index] and re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*", lines[index + 1]) is not None


def collect_table(lines: list[str], index: int) -> tuple[list[str], int]:
    """Collect contiguous table lines from a Markdown document."""
    table = [lines[index], lines[index + 1]]
    cursor = index + 2
    while cursor < len(lines) and "|" in lines[cursor] and lines[cursor].strip():
        table.append(lines[cursor])
        cursor += 1
    return table, cursor


def render_code_block(language: str, code_lines: list[str]) -> str:
    """Render a fenced code block; emit Mermaid diagrams as renderable nodes."""
    code = "\n".join(code_lines)
    if language == "mermaid":
        return f'<pre class="mermaid">{html.escape(code)}</pre>'
    language_class = f" language-{html.escape(language)}" if language else ""
    return f'<pre><code class="code-block{language_class}">{html.escape(code)}</code></pre>'


def render_markdown(
    markdown: str,
    link_map: dict[str, str],
    current_dir: str = "",
) -> tuple[str, list[tuple[int, str, str]]]:
    """Render project Markdown to HTML and return headings for a page TOC."""
    lines = markdown.splitlines()
    out: list[str] = []
    toc: list[tuple[int, str, str]] = []
    paragraph: list[str] = []
    list_stack: list[str] = []
    in_code = False
    code_language = ""
    code_lines: list[str] = []
    cursor = 0

    def flush_paragraph() -> None:
        if paragraph:
            text = " ".join(part.strip() for part in paragraph).strip()
            if text:
                out.append(f"<p>{inline_markdown(text, link_map, current_dir)}</p>")
            paragraph.clear()

    def close_lists() -> None:
        while list_stack:
            out.append(f"</{list_stack.pop()}>")

    while cursor < len(lines):
        line = lines[cursor]
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                out.append(render_code_block(code_language, code_lines))
                code_lines.clear()
                code_language = ""
                in_code = False
            else:
                code_lines.append(line)
            cursor += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            close_lists()
            in_code = True
            code_language = stripped[3:].strip()
            cursor += 1
            continue

        if not stripped:
            flush_paragraph()
            close_lists()
            cursor += 1
            continue

        if is_table_start(lines, cursor):
            flush_paragraph()
            close_lists()
            table, cursor = collect_table(lines, cursor)
            out.append(render_table(table, link_map, current_dir))
            continue

        heading_match = re.match(r"^(#{1,6})\s+(.+)$", stripped)
        if heading_match:
            flush_paragraph()
            close_lists()
            level = len(heading_match.group(1))
            title = heading_match.group(2).strip()
            anchor = slugify(title)
            toc.append((level, title, anchor))
            out.append(
                f'<h{level} id="{anchor}">{inline_markdown(title, link_map, current_dir)}</h{level}>'
            )
            cursor += 1
            continue

        unordered = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        if unordered or ordered:
            flush_paragraph()
            tag = "ul" if unordered else "ol"
            if not list_stack or list_stack[-1] != tag:
                close_lists()
                out.append(f"<{tag}>")
                list_stack.append(tag)
            item = unordered.group(1) if unordered else ordered.group(1)
            out.append(f"<li>{inline_markdown(item, link_map, current_dir)}</li>")
            cursor += 1
            continue

        quote = re.match(r"^>\s?(.*)$", stripped)
        if quote:
            flush_paragraph()
            close_lists()
            out.append(
                f"<blockquote>{inline_markdown(quote.group(1), link_map, current_dir)}</blockquote>"
            )
            cursor += 1
            continue

        paragraph.append(line)
        cursor += 1

    if in_code:
        out.append(render_code_block(code_language, code_lines))
    flush_paragraph()
    close_lists()
    return "\n".join(out), toc


def nav_html(pages: list[Page], api_modules: list[ApiModule], current: str, depth: int = 0) -> str:
    """Build the left navigation HTML."""
    prefix = "../" * depth
    groups = [
        "Getting Started",
        "Reference",
        "Algorithm Guides",
        "Development",
        "Research",
        "Prompts",
    ]
    by_group: dict[str, list[Page]] = {group: [] for group in groups}
    for page in pages:
        by_group.setdefault(page.group, []).append(page)

    out = [
        '<aside class="sidebar">',
        f'<div class="brand"><a href="{prefix}index.html">GSK Family Python</a></div>',
        '<input class="nav-search" type="search" placeholder="Filter docs" aria-label="Filter docs">',
        '<nav class="nav-list" aria-label="Documentation">',
    ]
    for group in groups:
        items = sorted(by_group.get(group, []), key=lambda page: page.title.lower())
        if not items:
            continue
        out.append(f"<section><h2>{html.escape(group)}</h2>")
        for page in items:
            href = f"{prefix}{page.output.name}"
            active = " active" if href == current else ""
            out.append(f'<a class="nav-link{active}" href="{href}">{html.escape(page.title)}</a>')
        out.append("</section>")

    out.append("<section><h2>Python API</h2>")
    api_active = " active" if current == "api_index.html" else ""
    out.append(f'<a class="nav-link{api_active}" href="{prefix}api_index.html">API Module Index</a>')
    for module in sorted(api_modules, key=lambda item: item.module_name):
        href = f"{prefix}api/{module.output.name}"
        active = " active" if href.endswith(current) else ""
        out.append(f'<a class="nav-link api-link{active}" href="{href}">{html.escape(module.module_name)}</a>')
    out.append("</section>")
    out.append("</nav></aside>")
    return "\n".join(out)


def toc_html(toc: list[tuple[int, str, str]]) -> str:
    """Build an in-page table of contents."""
    usable = [item for item in toc if item[0] <= 3]
    if len(usable) <= 1:
        return ""
    out = ['<aside class="page-toc" aria-label="On this page">', "<h2>On This Page</h2>"]
    for level, title, anchor in usable:
        out.append(f'<a class="toc-level-{level}" href="#{anchor}">{html.escape(title)}</a>')
    out.append("</aside>")
    return "\n".join(out)


def page_template(
    *,
    title: str,
    body: str,
    nav: str,
    toc: str,
    depth: int = 0,
    description: str = "",
) -> str:
    """Wrap page body content in the site layout."""
    asset_prefix = "../" * depth
    desc = description or f"{title} - {PROJECT_TITLE}"
    mermaid_script = ""
    if 'class="mermaid"' in body:
        mermaid_script = (
            "\n  <script type=\"module\">"
            "import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';"
            " mermaid.initialize({ startOnLoad: true, securityLevel: 'loose', theme: 'neutral' });"
            "</script>"
        )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{html.escape(desc, quote=True)}">
  <title>{html.escape(title)} | {PROJECT_TITLE}</title>
  <link rel="stylesheet" href="{asset_prefix}assets/site.css">
</head>
<body>
  <div class="site-shell">
    {nav}
    <main class="content">
      <article class="doc-card">
        {body}
      </article>
    </main>
    {toc}
  </div>
  <script src="{asset_prefix}assets/search.js"></script>{mermaid_script}
</body>
</html>
"""


def annotation_text(annotation: ast.AST | None) -> str:
    """Return source-like annotation text."""
    if annotation is None:
        return ""
    return ast.unparse(annotation)


def default_text(default: ast.AST | None) -> str:
    """Return source-like default-value text."""
    if default is None:
        return ""
    return ast.unparse(default)


def signature_for(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> str:
    """Return a readable signature for a function or class node."""
    if isinstance(node, ast.ClassDef):
        bases = [ast.unparse(base) for base in node.bases]
        return f"{node.name}({', '.join(bases)})" if bases else node.name

    args = node.args
    parts: list[str] = []
    positional = list(args.posonlyargs) + list(args.args)
    defaults = [None] * (len(positional) - len(args.defaults)) + list(args.defaults)
    for arg, default in zip(positional, defaults):
        part = arg.arg
        annotation = annotation_text(arg.annotation)
        if annotation:
            part += f": {annotation}"
        if default is not None:
            part += f" = {default_text(default)}"
        parts.append(part)
    if args.vararg:
        part = f"*{args.vararg.arg}"
        annotation = annotation_text(args.vararg.annotation)
        if annotation:
            part += f": {annotation}"
        parts.append(part)
    elif args.kwonlyargs:
        parts.append("*")
    for arg, default in zip(args.kwonlyargs, args.kw_defaults):
        part = arg.arg
        annotation = annotation_text(arg.annotation)
        if annotation:
            part += f": {annotation}"
        if default is not None:
            part += f" = {default_text(default)}"
        parts.append(part)
    if args.kwarg:
        part = f"**{args.kwarg.arg}"
        annotation = annotation_text(args.kwarg.annotation)
        if annotation:
            part += f": {annotation}"
        parts.append(part)
    returns = annotation_text(node.returns)
    suffix = f" -> {returns}" if returns else ""
    return f"{node.name}({', '.join(parts)}){suffix}"


def api_member_from_node(node: ast.AST) -> ApiMember | None:
    """Convert an AST class/function node into API member metadata."""
    if isinstance(node, ast.ClassDef):
        methods: list[ApiMember] = []
        for child in node.body:
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                methods.append(
                    ApiMember(
                        kind="method",
                        name=child.name,
                        signature=signature_for(child),
                        docstring=ast.get_docstring(child) or "",
                        lineno=int(child.lineno),
                    )
                )
        return ApiMember(
            kind="class",
            name=node.name,
            signature=signature_for(node),
            docstring=ast.get_docstring(node) or "",
            lineno=int(node.lineno),
            children=tuple(methods),
        )
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return ApiMember(
            kind="function",
            name=node.name,
            signature=signature_for(node),
            docstring=ast.get_docstring(node) or "",
            lineno=int(node.lineno),
        )
    return None


def module_name_for(path: Path, source_root: Path) -> str:
    """Return import-style module name for a source file."""
    relative = path.relative_to(source_root.parent).with_suffix("")
    return ".".join(relative.parts)


def discover_api_modules(source_root: Path, output_root: Path) -> list[ApiModule]:
    """Parse source files and return API module pages."""
    modules: list[ApiModule] = []
    for path in sorted(source_root.rglob("*.py")):
        # Vendored DT-GSK modules are byte-identical copies of the upstream
        # project and are excluded from the generated API documentation.
        if path.name == "_dt_core.py" or "_dt_subsystems" in path.parts:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        module_name = module_name_for(path, source_root)
        members = tuple(
            member
            for child in tree.body
            if (member := api_member_from_node(child)) is not None
        )
        modules.append(
            ApiModule(
                module_name=module_name,
                source=path,
                output=output_root / "api" / f"{module_name}.html",
                docstring=ast.get_docstring(tree) or "",
                members=members,
            )
        )
    return modules


def render_docstring(text: str) -> str:
    """Render a docstring as escaped paragraphs."""
    if not text:
        return '<p class="muted">No docstring provided.</p>'
    paragraphs = [part.strip() for part in re.split(r"\n\s*\n", text.strip()) if part.strip()]
    return "\n".join(f"<p>{html.escape(part)}</p>" for part in paragraphs)


def render_api_member(member: ApiMember) -> str:
    """Render one API member and any child methods."""
    anchor = slugify(f"{member.kind}-{member.name}-{member.lineno}")
    out = [
        f'<section class="api-member" id="{anchor}">',
        f'<div class="member-kind">{html.escape(member.kind)}</div>',
        f"<h2>{html.escape(member.name)}</h2>",
        f"<pre><code>{html.escape(member.signature)}</code></pre>",
        render_docstring(member.docstring),
    ]
    if member.children:
        out.append('<div class="method-list"><h3>Methods</h3>')
        for child in member.children:
            out.append(render_api_member(child))
        out.append("</div>")
    out.append("</section>")
    return "\n".join(out)


def render_api_module(module: ApiModule) -> tuple[str, list[tuple[int, str, str]]]:
    """Render a Python module API page body and table of contents."""
    source_parts = module.source.parts
    if "src" in source_parts:
        source_rel = Path(*source_parts[source_parts.index("src"):]).as_posix()
    else:
        source_rel = module.source.name
    body = [
        f"<h1>{html.escape(module.module_name)}</h1>",
        f'<p class="source-path">Source: <code>{html.escape(source_rel)}</code></p>',
        render_docstring(module.docstring),
    ]
    toc = [(1, module.module_name, slugify(module.module_name))]
    if module.members:
        body.append("<h2 id=\"members\">Members</h2>")
        toc.append((2, "Members", "members"))
        for member in module.members:
            toc.append((2, member.name, slugify(f"{member.kind}-{member.name}-{member.lineno}")))
            body.append(render_api_member(member))
    else:
        body.append('<p class="muted">No top-level classes or functions.</p>')
    return "\n".join(body), toc


def render_api_index(api_modules: list[ApiModule]) -> tuple[str, list[tuple[int, str, str]]]:
    """Render the Python API module index."""
    groups: dict[str, list[ApiModule]] = {}
    for module in api_modules:
        prefix = ".".join(module.module_name.split(".")[:2])
        groups.setdefault(prefix, []).append(module)
    body = [
        "<h1>Python API Module Index</h1>",
        "<p>This generated section publishes Python source docstring pages for active modules and public helpers.</p>",
    ]
    toc = [(1, "Python API Module Index", "python-api-module-index")]
    for group, modules in sorted(groups.items()):
        anchor = slugify(group)
        body.append(f'<h2 id="{anchor}">{html.escape(group)}</h2>')
        toc.append((2, group, anchor))
        body.append("<ul>")
        for module in sorted(modules, key=lambda item: item.module_name):
            href = f"api/{module.output.name}"
            summary = module.docstring.splitlines()[0] if module.docstring else ""
            body.append(
                f'<li><a href="{html.escape(href)}">{html.escape(module.module_name)}</a>'
                f'<span class="api-summary">{html.escape(summary)}</span></li>'
            )
        body.append("</ul>")
    return "\n".join(body), toc


def write_assets(output_root: Path) -> None:
    """Write CSS and JavaScript assets for the static site."""
    assets = output_root / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    (assets / "site.css").write_text(
        """* {
  box-sizing: border-box;
}

:root {
  --bg: #f6f7f9;
  --panel: #ffffff;
  --ink: #17202a;
  --muted: #5f6b7a;
  --line: #d9e0ea;
  --accent: #0d6efd;
  --accent-dark: #084298;
  --code-bg: #101923;
  --code-ink: #e8edf2;
  --sidebar: #111827;
  --sidebar-ink: #e5e7eb;
  --sidebar-muted: #a8b0bd;
}

body {
  margin: 0;
  background: var(--bg);
  color: var(--ink);
  font-family: "Segoe UI", Arial, sans-serif;
  font-size: 16px;
  line-height: 1.62;
}

a {
  color: var(--accent-dark);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.site-shell {
  display: grid;
  grid-template-columns: 300px minmax(0, 1fr) 240px;
  min-height: 100vh;
}

.sidebar {
  background: var(--sidebar);
  color: var(--sidebar-ink);
  height: 100vh;
  overflow-y: auto;
  padding: 22px 18px;
  position: sticky;
  top: 0;
}

.brand a {
  color: #fff;
  display: block;
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 16px;
}

.nav-search {
  background: #0b1220;
  border: 1px solid #2c384a;
  border-radius: 6px;
  color: #fff;
  margin-bottom: 18px;
  padding: 10px 12px;
  width: 100%;
}

.nav-list section {
  border-top: 1px solid #2c384a;
  padding: 14px 0;
}

.nav-list h2 {
  color: var(--sidebar-muted);
  font-size: 12px;
  letter-spacing: .08em;
  margin: 0 0 8px;
  text-transform: uppercase;
}

.nav-link {
  border-radius: 6px;
  color: var(--sidebar-ink);
  display: block;
  font-size: 14px;
  padding: 6px 8px;
}

.nav-link.api-link {
  font-family: Consolas, "Liberation Mono", monospace;
  font-size: 12px;
}

.nav-link:hover,
.nav-link.active {
  background: #243044;
  text-decoration: none;
}

.content {
  min-width: 0;
  padding: 32px;
}

.doc-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 8px;
  box-shadow: 0 10px 26px rgba(15, 23, 42, .06);
  margin: 0 auto;
  max-width: 1040px;
  padding: 42px 52px;
}

.doc-card h1 {
  border-bottom: 1px solid var(--line);
  font-size: 34px;
  line-height: 1.2;
  margin: 0 0 24px;
  padding-bottom: 18px;
}

.doc-card h2 {
  font-size: 24px;
  margin-top: 34px;
}

.doc-card h3 {
  font-size: 19px;
  margin-top: 26px;
}

.doc-card p,
.doc-card li {
  color: #263241;
}

.doc-card code {
  background: #eef2f7;
  border-radius: 4px;
  color: #0f3b63;
  font-family: Consolas, "Liberation Mono", monospace;
  font-size: .92em;
  padding: 2px 5px;
}

.doc-card pre {
  background: var(--code-bg);
  border-radius: 8px;
  color: var(--code-ink);
  overflow-x: auto;
  padding: 16px 18px;
}

.doc-card pre code {
  background: transparent;
  color: inherit;
  padding: 0;
}

.doc-card pre.mermaid {
  background: transparent;
  border: 1px solid var(--line);
  color: var(--ink);
  padding: 14px;
  text-align: center;
}

.table-wrap {
  overflow-x: auto;
}

table {
  border-collapse: collapse;
  margin: 18px 0;
  width: 100%;
}

th,
td {
  border: 1px solid var(--line);
  padding: 9px 11px;
  text-align: left;
  vertical-align: top;
}

th {
  background: #f0f4f8;
  font-weight: 700;
}

blockquote {
  border-left: 4px solid var(--accent);
  color: var(--muted);
  margin: 20px 0;
  padding: 8px 18px;
}

.page-toc {
  align-self: start;
  max-height: 100vh;
  overflow-y: auto;
  padding: 34px 18px 24px 0;
  position: sticky;
  top: 0;
}

.page-toc h2 {
  color: var(--muted);
  font-size: 13px;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.page-toc a {
  color: #415166;
  display: block;
  font-size: 13px;
  padding: 4px 0;
}

.toc-level-3 {
  padding-left: 14px !important;
}

.source-path,
.muted,
.api-summary {
  color: var(--muted);
}

.api-summary {
  display: block;
  font-size: 13px;
}

.api-member {
  border: 1px solid var(--line);
  border-radius: 8px;
  margin: 18px 0;
  padding: 18px;
}

.member-kind {
  color: var(--muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.method-list {
  border-top: 1px solid var(--line);
  margin-top: 16px;
  padding-top: 10px;
}

@media (max-width: 1100px) {
  .site-shell {
    grid-template-columns: 260px minmax(0, 1fr);
  }

  .page-toc {
    display: none;
  }
}

@media (max-width: 760px) {
  .site-shell {
    display: block;
  }

  .sidebar {
    height: auto;
    position: relative;
  }

  .content {
    padding: 16px;
  }

  .doc-card {
    padding: 26px 22px;
  }
}

@media print {
  .sidebar,
  .page-toc,
  .nav-search,
  script {
    display: none;
  }

  .site-shell {
    display: block;
  }

  .doc-card {
    border: 0;
    box-shadow: none;
    max-width: none;
  }
}
""",
        encoding="utf-8",
    )
    (assets / "search.js").write_text(
        """const input = document.querySelector('.nav-search');
if (input) {
  input.addEventListener('input', () => {
    const query = input.value.trim().toLowerCase();
    document.querySelectorAll('.nav-link').forEach((link) => {
      const visible = !query || link.textContent.toLowerCase().includes(query);
      link.style.display = visible ? '' : 'none';
    });
  });
}
""",
        encoding="utf-8",
    )


def clean_output(output_root: Path) -> None:
    """Remove the generated HTML directory before rebuilding it."""
    if output_root.exists():
        resolved = output_root.resolve()
        if resolved.name.lower() != "html" or resolved.parent.name.lower() != "docs":
            raise ValueError(f"Refusing to remove unexpected output directory: {resolved}")
        shutil.rmtree(output_root)
    (output_root / "api").mkdir(parents=True, exist_ok=True)


def write_markdown_pages(pages: list[Page], api_modules: list[ApiModule], link_map: dict[str, str]) -> None:
    """Render all Markdown pages."""
    for page in pages:
        current_dir = str(Path(page.relative_key).parent).replace("\\", "/")
        current_dir = "" if current_dir == "." else current_dir
        body, toc = render_markdown(
            page.source.read_text(encoding="utf-8"),
            link_map,
            current_dir,
        )
        nav = nav_html(pages, api_modules, page.output.name)
        html_text = page_template(title=page.title, body=body, nav=nav, toc=toc_html(toc))
        page.output.write_text(html_text, encoding="utf-8")


def write_api_pages(output_root: Path, pages: list[Page], api_modules: list[ApiModule]) -> None:
    """Render API index and per-module API pages."""
    body, toc = render_api_index(api_modules)
    nav = nav_html(pages, api_modules, "api_index.html")
    (output_root / "api_index.html").write_text(
        page_template(title="Python API Module Index", body=body, nav=nav, toc=toc_html(toc)),
        encoding="utf-8",
    )
    for module in api_modules:
        body, toc = render_api_module(module)
        nav = nav_html(pages, api_modules, f"api/{module.output.name}", depth=1)
        module.output.write_text(
            page_template(
                title=module.module_name,
                body=body,
                nav=nav,
                toc=toc_html(toc),
                depth=1,
                description=f"Python API documentation for {module.module_name}",
            ),
            encoding="utf-8",
        )


def write_search_index(output_root: Path, pages: list[Page], api_modules: list[ApiModule]) -> None:
    """Write a small machine-readable page index for external tools."""
    records = [
        {"title": page.title, "href": page.output.name, "group": page.group}
        for page in sorted(pages, key=lambda item: item.title.lower())
    ]
    records.append({"title": "Python API Module Index", "href": "api_index.html", "group": "Python API"})
    records.extend(
        {
            "title": module.module_name,
            "href": f"api/{module.output.name}",
            "group": "Python API",
        }
        for module in sorted(api_modules, key=lambda item: item.module_name)
    )
    (output_root / "search_index.json").write_text(
        json.dumps(records, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def copy_static_doc_assets(docs_root: Path, output_root: Path) -> None:
    """Copy non-Markdown documentation assets referenced by generated pages."""
    for path in sorted(docs_root.rglob("*.csv")):
        if any(part in SKIP_DIR_NAMES for part in path.relative_to(docs_root).parts):
            continue
        target = output_root / path.relative_to(docs_root)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def build_html_docs(docs_root: Path, source_root: Path, output_root: Path) -> tuple[int, int]:
    """Build the static HTML documentation site and return page counts."""
    docs_root = docs_root.resolve()
    source_root = source_root.resolve()
    output_root = output_root.resolve()
    project_root = docs_root.parent
    clean_output(output_root)
    pages = discover_markdown_pages(docs_root, output_root, project_root)
    link_map = {page.relative_key: page.output.name for page in pages}
    for page in pages:
        if page.source.is_relative_to(docs_root):
            link_map[f"docs/{page.relative_key}"] = page.output.name
    api_modules = discover_api_modules(source_root, output_root)
    write_assets(output_root)
    write_markdown_pages(pages, api_modules, link_map)
    write_api_pages(output_root, pages, api_modules)
    write_search_index(output_root, pages, api_modules)
    copy_static_doc_assets(docs_root, output_root)
    return len(pages), len(api_modules)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description="Build static HTML documentation.")
    parser.add_argument("--docs-root", default="docs", help="Markdown docs root.")
    parser.add_argument("--source-root", default="src/gsk_family", help="Python package source root.")
    parser.add_argument("--output-root", default="docs/html", help="Generated HTML output root.")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    """Build docs/html and print a compact summary."""
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    pages, modules = build_html_docs(
        Path(args.docs_root),
        Path(args.source_root),
        Path(args.output_root),
    )
    print(f"HTML docs written to {Path(args.output_root)}")
    print(f"Markdown pages: {pages}")
    print(f"API modules: {modules}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
