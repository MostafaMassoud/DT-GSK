# Phase 9 — Word pipeline build report (Task B)

Date: 2026-07-11 (build epoch normalized to SOURCE_DATE_EPOCH default
`1783641600` = 2026-07-10T00:00:00Z).
Canonical sources: FROZEN Phase-8 `papers/main.tex` + `papers/sections/*.tex`
+ `papers/supplementary.tex`. **Zero content edits were made to any canonical
LaTeX source** — every transformation happens in generated shim copies
(`papers/main_pandoc.tex`, `papers/supplementary_pandoc.tex`, overwritten per
run) and in OOXML post-processing.

## 1. Toolchain

| Tool | Version | Role |
|---|---|---|
| pandoc (CLI, subprocess) | 3.9.0.2 | LaTeX shim -> DOCX (native OMML math) |
| python-docx | 1.2.0 | `word/reference.docx` style template |
| lxml | 6.x | OOXML post-processing (fields, bookmarks, native tables, customXml) |
| Ghostscript gswin64c | 10.06.0 | PDF->PNG raster fallback for figures (220 dpi) |

pypandoc is not importable in this environment; pandoc is invoked via
`subprocess` per the Phase 9 binding constraints.

## 2. Commands

```bash
python papers/scripts/make_reference_docx.py            # -> word/reference.docx
python papers/scripts/build_docx.py                     # -> papers/DT-GSK.docx
python papers/scripts/build_docx.py --supplementary     # -> papers/supplementary.docx
python papers/scripts/build_docx.py --validate-only papers/DT-GSK.docx
python papers/scripts/build_docx.py --validate-only papers/supplementary.docx
python -m ruff check papers/scripts/build_docx.py papers/scripts/make_reference_docx.py papers/scripts/_word_ooxml.py
```

## 3. Deliverables and hashes

| File | Bytes | SHA-256 |
|---|---|---|
| `papers/DT-GSK.docx` | 3,058,596 | `c9bad9230ed6e0cb634150665d8e934d66ae07f46e4ec46d684a0a00fd24b79d` |
| `papers/supplementary.docx` | 12,837,676 | `902db38f448f2af3c27ac7b7966edb6c21e2be854bcc29256c19734cf3ee2ceb` |
| `word/reference.docx` | 11,249 | `4ba61b8252a478de8eaa57e1e03d0b9238df7ee8384af4ee1c6313d71af39dfc` |
| `word/field_registry.csv` | 472 data rows | (regenerated per build, deterministic) |

Determinism (Section 9.4 contract): two consecutive full rebuilds of each
document produced **byte-identical** output (stronger than the required
normalized-content equality). docProps timestamps are stamped from
SOURCE_DATE_EPOCH; zip entry metadata (order, timestamps, attributes,
compression) is fixed by `papers/scripts/_word_ooxml.py::write_deterministic_zip`.

## 4. Tooling built/extended

1. **`papers/scripts/_word_ooxml.py` (new)** — shared OOXML primitives:
   namespaces, run/field/bookmark factories (complex fields with cached
   results), deterministic zip writer, docProps stamping.
2. **`papers/scripts/make_reference_docx.py` (new)** — builds
   `word/reference.docx` programmatically (python-docx + lxml over pandoc's
   default style skeleton): A4; margins 2.0 cm sides / 2.5 cm top+bottom;
   Palatino Linotype 10 pt serif body (font *named only* — no font embedding);
   Heading 1–3 (12/10.5/10 pt bold family); Title/Author/Abstract; `Caption`,
   `Table Caption`, `Image Caption` (9 pt, editable); monospace `Source Code`
   + dedicated `Algorithm Line` style (Consolas 9 pt); `Bibliography` style
   with hanging indent; TOC Heading/TOC 1–3; table style `Table` with shaded
   bold header row (`firstRow` conditional format, fill `E7E6E6`).
3. **`papers/scripts/build_docx.py` (extended, full rewrite)** —
   * `--supplementary` entry point (`papers/supplementary.tex` ->
     `papers/supplementary.docx`);
   * `--reference-doc word/reference.docx` wired into the pandoc invocation;
   * marker-based shim (front-matter re-expression, input flattening, comment
     stripping, Phase-8 presentation-group removal, algorithm/equation/table
     conversion, `\ref`/`\cite`/bibliography markers, PDF-identical section
     numbers from the frozen `.aux` files);
   * OOXML post-processing stage: SEQ fields for every Figure/Table/Algorithm/
     Equation caption; REF fields + bookmarks (stable IDs
     `ref_<sanitized manuscript_label>`, seeded from
     `papers/governance/artifact_binding.csv` manuscript_label values, which
     are the LaTeX labels); native TOC field with update-on-open
     (`w:updateFields` in settings.xml); CITATION fields + customXml
     `b:Sources` store built from `papers/references.bib` filtered to cited
     keys (citation order/numbers from the frozen `.aux`/`.bbl`, tags from
     `papers/governance/word_citation_tag_map.csv`);
   * native `w:tbl` construction for T1–T16 (+`T16_bca`) from
     `papers/tables/word_sources/*.json` — exact values and precision, header
     row(s) carrying the `w:tblHeader` accessibility property +
     `w:tblCaption`/`w:tblDescription`, first-column left / other columns
     centered, column-count-scaled font size;
   * `SOURCE_DATE_EPOCH` + docProps normalization, deterministic re-zip;
   * alt text (`wp:docPr/@descr`) on every image from its adjacent
     registry-derived caption;
   * `--validate-only` package validator (see
     `papers/governance/word_validation_report.md`).

## 5. Inventory (final builds)

| Metric | DT-GSK.docx | supplementary.docx |
|---|---|---|
| Native OMML math objects (`m:oMath`) | 607 | 172 |
| Display equations numbered (SEQ Equation + bookmark) | 13 | 1 |
| Equation *images* (must be 0) | 0 | 0 |
| Tables total (`w:tbl`) | 11 | 14 |
| — native from word_sources JSON | 3 (T16→Table 7, T15→Table 8, T1→Table 9) | 13 (T2–T14 → Tables A1–A13) |
| — native from frozen `.tex` (reconciliation) | — | 1 (`T16_bca` → Table A14) |
| — pandoc-path authored tables (reference-doc `Table` style, header row marked) | 8 (family-review, notation, worked-example, parameters, panel, protocol, runtime, abbreviations) | 0 |
| SEQ fields | 38 (14 Figure + 10 Table + 1 Algorithm + 13 Equation) | 35 (14 Table + 20 Figure + 1 Equation) |
| REF fields (all cached with PDF-identical numbers) | 146 | 21 |
| CITATION fields (cached `[n]` per frozen `.bbl` order) | 85 | 9 |
| TOC fields (update-on-open) | 1 | 1 |
| Total complex fields | 270 | 66 |
| Bookmarks (total / added by post-processing) | 141 / 69 | 86 / 50 |
| Images (`w:drawing`) / with alt text | 14 / 14 | 20 / 20 |
| customXml `b:Source` entries (IEEE numbered style) | 40 | 8 |
| Unresolved markers | 0 | 0 |
| Ablation mentions / S6 rendering | 0 / none | 0 / none |
| Algorithm pseudocode lines (`Algorithm Line` style, numbered 1–26) | 26 | — |

`word/field_registry.csv`: 472 rows (every SEQ/REF/CITATION/TOC field plus
every post-processing bookmark and native table), columns
`doc,field_type,field_id,target,cached_result,location`.

## 6. T16_bca cross-format reconciliation (Phase 7/8 hand-off) — RESOLVED

* The frozen supplement (`tab:bca-ci`, Table A14) typesets the **rank-CI
  table** (`papers/tables/T16_bca.tex`: BCa 95% CIs on the CEC2017 Friedman
  mean ranks, 7 algorithms x 4 dimensions, n_boot=10,000,
  BASE_SEED=20260422).
* The Word-side semantic source `papers/tables/word_sources/T16_bca.json`
  carries a **different** table: the per-function paired-mean-error BCa
  companion (696 rows, byte-equal to the concatenation of
  `bca_ci_cec2017_D10..D100.csv`).
* **Resolution applied:** the DOCX table for `tab:bca-ci` is built by parsing
  the frozen `papers/tables/T16_bca.tex` (macros expanded: `\egsk`->eGSK,
  `\fdbagsk`->FDB-AGSK), so the DOCX renders the SAME rank-CI content as the
  PDF (verified: header "Mean [95% BCa CI]" x4 and all CI cells present, e.g.
  "5.52 [4.88, 6.02]"). The per-function companion **stays supplement-only
  data** (evidence-release/analysis-bundle CSVs `bca_ci_cec2017_D*.csv`); it
  is NOT typeset in either format. `word_sources/T16_bca.json` remains the
  registry-defined data companion and is deliberately not consumed for
  typesetting.

## 7. Fixes made during the build (tooling-side; no canonical-source edits)

1. **Phase-8 presentation groups** (`\begingroup`/`lrbox`/`[H]` wrappers
   around the frozen notation/parameter tables) are stripped in the shim;
   pandoc otherwise honors `\renewenvironment{table}` and silently drops the
   captions of *every subsequent* table (root cause of six missing table
   captions in an intermediate build; fixed by broadening the filter to
   `\renewenvironment{table|tabular}`).
2. **Comment stripping in the shim**: a `% ... \resizebox ...` build-note
   comment was being consumed by the balanced-brace `\resizebox` unwrapping
   pass, deleting the parameter-table wrapper. All LaTeX comment text is now
   removed from the shim before any transformation (pandoc drops comments
   anyway; content-neutral).
3. **Table-id normalization**: `tables/T01.tex` binds to
   `word_sources/T1.json` (leading zeros stripped).
4. **pandoc caption attributes**: pandoc mirrors table captions (including my
   markers) into `w:tblCaption`; a post-processing pass resolves marker
   tokens inside attribute values.
5. **Bold "best" cells**: the JSON semantic sources carry no emphasis
   channel, so the frozen "best in bold" convention is recomputed from the
   semantic values (first-minimum rule, matching the generator): per-row
   Mean_GSK vs Mean_ISM for T1–T5/T11–T13, per-row minimum over the seven
   `*_Mean` columns for T7–T10, per-column minimum for T16. Verified 0
   value-level mismatches against the frozen `.tex` `\bestval` cells for the
   T1/T2/T7/T16 spot set (102 bold cells compared).
6. **Bookmark-name legality (2026-07-11, revealed by
   `papers/scripts/validate_docx.py`)**: `_rename_pandoc_bookmarks` only
   rewrote pandoc bookmark names containing `:` or `-`, so the Word-illegal
   heading anchor `limitations.` (trailing period; from the
   `\paragraph{Limitations.}` run-in heading) survived in `DT-GSK.docx`.
   The pass now renames every bookmark whose name does not match
   `[A-Za-z_][A-Za-z0-9_]{0,39}` (no internal hyperlinks reference pandoc
   anchors, so the rename is side-effect-free). Both documents rebuilt:
   `supplementary.docx` byte-identical to the Section 3 hash;
   `DT-GSK.docx` re-hashed to
   `2e451769fe4f7d3d81a7982d5c62fc91efbf21a36f2c977bf116e2adc1267c9f`
   (3,058,595 bytes; two consecutive rebuilds byte-identical; the
   Section 3 table value is superseded by this entry and by
   `papers/governance/word_validation_report.md` Section 2).
7. **Gate 9 mechanical fix MF-01 follow-through (2026-07-11)**: the recorded
   layout-only fix in `papers/sections/related_work.tex` line 158
   (`\atmals{}~\cite{...}` → `\atmals{} \cite{...}`; see
   `latex_build_report.md`, "Recorded mechanical build fix") flows into the
   Table 1 cell text of the DOCX (non-breaking space → regular space; zero
   content change). `DT-GSK.docx` rebuilt:
   `5517b6318df84ad8020d352eb080d3cbab0574c111fde01a6463f9f77918844a`
   (3,058,600 bytes; two consecutive rebuilds byte-identical; supersedes
   item 6's hash). `supplementary.docx` and `word/field_registry.csv` are
   byte-identical to their prior hashes (fix touches neither). All three
   validators re-run green: `validate_docx.py` PASS 33/33 both documents,
   `validate_cross_format_parity.py` 417 rows / 0 FAIL,
   `validate_evidence_bindings.py` 721/721 tokens in both formats.

## 8. Recorded deviations / conventions

* **eGSK capitalization** applied at Word build time per the word_sources
  terminology notes: exact-token `EGSK`->`eGSK`, `FDBAGSK`->`FDB-AGSK` in all
  native-table headers/cells (0 residual `FDBAGSK`/`EGSK_` tokens in either
  document). Other header strings remain verbatim CSV identifiers by design.
* **Citation tag-map staleness**: `word_citation_tag_map.csv` still lists
  `awad2016problem` as `admissible=no / BLOCKED_do_not_generate_word_source`;
  that row predates approved CR-0005 (decision D-0009, 2026-07-10) which
  un-blocked the key. The build applies a recorded override
  (`CITATION_BLOCK_OVERRIDES` in `build_docx.py`) and generates its
  `b:Source`. The tag map itself was left untouched (governance file; update
  belongs to its owner).
* **Precision convention**: native tables render the *exact values and
  precision* of the semantic word_sources (e.g. Table 7 shows `2.879310`
  where the PDF displays `2.88`). This is the mandated semantic-source
  behavior for the Word format; the PDF remains the display-rounded
  rendering. Point values agree by construction (same frozen CSV exports).
* **JSON `notes` fields** are provenance/instruction notes (transcription
  provenance, terminology directive, panel order); the terminology directive
  is *applied*, and the notes are carried into the accessibility metadata
  path only (not typeset as visible table notes — they are not part of the
  frozen rendered content).
* **Bibliography**: the References section is the static MDPI-numbered list
  converted from the frozen `.bbl` (numbers = citation order, identical to
  the PDF); CITATION fields carry cached `[n]` / `[n,m]` / `[n–m]` results.
  No BIBLIOGRAPHY field is inserted (the static list is canonical); the
  `b:Sources` store (IEEE numbered style) enables Word-native regeneration.
* **Update-on-open**: `w:updateFields` refreshes TOC/SEQ/REF on open (values
  are cached identically, so refresh is idempotent for numbering); a Word
  field update may re-render multi-source CITATION fields per the IEEE style
  (e.g. `[1,2]` -> `[1], [2]`) — flagged for the final Word-open validation.
* **Heading number typography**: Word headings render `N<tab>Title`
  (vs. the MDPI PDF's `N. Title`) — mechanical Word convention.
* **Figures**: embedded as PNG (generator-produced sibling PNGs preferred;
  Ghostscript 220 dpi raster of the frozen PDFs as fallback);
  `height=…\textheight`/`keepaspectratio` options are dropped in the shim so
  Word sizes by width only.
* **Word-open validation**: Microsoft Word is not available in this
  environment; the open-save-open check is replaced by the documented
  fallback (see `papers/governance/word_validation_report.md`).
