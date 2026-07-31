# Phase 9 — LaTeX Build Report (PDF side)

Date: 2026-07-11
Builder: Claude Code (Phase 9 dual-format production, Task A)
Canonical source: FROZEN at Phase 8 — `papers/main.tex` + `papers/sections/*.tex` + `papers/supplementary.tex`. No content edits were made.

## Environment

| Component | Version |
|---|---|
| OS | Windows 11 Home 10.0.26200 |
| Python | 3.10.11 |
| pdflatex | MiKTeX-pdfTeX 4.27 (MiKTeX 26.5) |
| bibtex | MiKTeX-BibTeX 4.2 (MiKTeX 26.5) |
| SOURCE_DATE_EPOCH | `1783468800` (set for both builds per determinism contract, Section 9.4) |

## Script audit

- `papers/scripts/build_pdf.py` — audited. Compiles the canonical `main.tex` via pdflatex → bibtex → pdflatex ×2 from `papers/`, then moves `main.pdf` → `DT-GSK.pdf` on success (locked-target fallback to `DT-GSK.new.pdf`). **No mechanical defects; no fixes required.**
- `papers/scripts/build_supplementary.py` — audited. Two pdflatex passes over the canonical `supplementary.tex` using the committed `supplementary.bbl` (MDPI class has no bibtex flow for the supplement); hard-fails on undefined references. **No mechanical defects; no fixes required.**

## Commands run

```
cd D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1
SOURCE_DATE_EPOCH=1783468800 python papers/scripts/build_pdf.py
SOURCE_DATE_EPOCH=1783468800 python papers/scripts/build_supplementary.py
```

## Build results

| Output | Pages (from log) | Size (bytes) | Result |
|---|---|---|---|
| `papers/DT-GSK.pdf` (from `main.pdf`) | 34 | 920,985 | success |
| `papers/supplementary.pdf` | 32 | 889,540 | success |

## Log scan

- **Undefined references:** 0 (no `LaTeX Warning: There were undefined references` in either log).
- **Undefined citations:** 0 (no `Citation ... undefined`; `main.blg` 40 entries / `supplementary.blg` 8 entries, both zero BibTeX warnings/errors).
- **Missing figures/files:** 0 (no `File ... not found` in either log).
- **S6 placeholder:** present in `supplementary.tex` only as the comment `% S6 -- RESERVED (ablation study).` — confirmed it does **not** render; no ablation content in either PDF.
- **Warnings recorded (benign, no action):**
  - `main.log`: 5× `Package hyperref Warning: Token not allowed in a PDF string (Unicode)` (math tokens in bookmark strings); 3× `Overfull \hbox` (2.09pt, 17.51pt, 1.43pt). *(Superseded by the Gate 9 mechanical fix below: the 17.51pt box is now 2.48pt.)*
  - `supplementary.log`: 2× `Package hyperref Warning: Token not allowed in a PDF string (Unicode)`; 0 overfull boxes.

## Recorded mechanical build fix (Gate 9 QA, 2026-07-11)

- **MF-01 (layout-only, zero content change):** the 17.51pt `Overfull \hbox` in
  Table 1 (`tab:family-review`) produced a visible glyph collision on page 4 —
  the citation `[10]` in the `p{1.7cm}` Variant column overprinted the
  "Gaussian" text of the adjacent column (`ATMALS-GSK [10]` cannot break at a
  `~` tie). Fix: `papers/sections/related_work.tex` line 158,
  `\atmals{}~\cite{alfadli2025atmals}` → `\atmals{} \cite{alfadli2025atmals}`
  (non-breaking tie → breakable space; `[10]` now wraps to the second line of
  the cell). No word, number, citation, or claim changed. Verified by 300 dpi
  render before/after; residual overfull for the row is 2.48pt (the width of
  the label word itself, invisible inside the 12pt intercolumn gutter, same
  class as the benign 2.09pt FDB-AGSK row). Post-fix `main.log` overfull
  inventory: 2.09pt / 2.48pt / 1.43pt; pages still 34; 0 undefined
  references/citations. The Word-side companion was rebuilt from the same
  source (see `word_build_report.md` Section 7 item 7).

## Build incident (environmental, not a script defect)

First supplementary run failed with `! I can't write on file 'supplementary.pdf'` — the pre-existing PDF was held by another process with a share-read/share-delete handle (write denied, rename permitted; typical PDF-viewer lock). Resolution: renamed the stale PDF aside, re-ran the build (clean success), deleted the stale copy. No source or script change involved.

## Output hashes (sha256)

Normalization per determinism contract: strip `/CreationDate`, `/ModDate`, and trailer `/ID` byte spans before hashing (normalizer: small Python regex-based stripper; raw hash is over the file as written).

| File | Raw sha256 | Normalized sha256 |
|---|---|---|
| `papers/DT-GSK.pdf` | `8fd1a83cedf3331696ce1d27035a0cdc655339117c16bfb3f8bc728f0a66fc22` | `5e47d2914f075dd1e0f7931e182537df5e1132de26c1e6f78a22cf09fc34cefa` |
| `papers/supplementary.pdf` | `e63d3480ada03ae8e4da38281819da09e0de2d42a2d503e4d6e1e33b9eb26b5c` | `f475342c8d184e2c22bb4c70d774312f38a16913de1e412cd43ee4e65a64b3a3` |

**Superseded for `DT-GSK.pdf` by the Gate 9 mechanical fix MF-01 (2026-07-11):**

| File | Raw sha256 | Bytes |
|---|---|---|
| `papers/DT-GSK.pdf` (post-MF-01) | `9ff72733934e46d1fba6914abe3d74b0ab3ffc3b8e75c4a09eb74fb704614cef` | 920,977 |

Two consecutive full rebuilds under `SOURCE_DATE_EPOCH=1783468800` are
**byte-identical** (raw-hash equality — stronger than the Section 9.4
normalized-content requirement). `papers/supplementary.pdf` was not rebuilt
(the fixed file feeds `main.tex` only); its raw hash above remains current.

## Filename mappings

- `papers/main.pdf` → `papers/DT-GSK.pdf` (MDPI class requires the `main.tex` filename; user-facing artefact renamed post-build).
- `papers/scripts/build_docx.py` → `papers/DT-GSK.docx` (Word-side companion, Task B).

Also recorded in `papers/governance/project_configuration.md` (dated Phase 9 note).

## Skipped: generate_review_pack.py

`papers/scripts/generate_review_pack.py` was **not run**. Rationale: it is an internal advisor artifact that reads the staging area; it is excluded from the publication evidence chain and produces no submission-facing output. Skip recorded here per Phase 9 Task A item 4.
