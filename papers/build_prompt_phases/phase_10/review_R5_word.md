# Review R5 — Word (.docx) Deliverable

**Reviewer:** R5 (word)
**Artifact under review:** `papers/DT-GSK.docx` (3.06 MB), cross-checked against `papers/DT-GSK.pdf` (34 pp) and `papers/styles.xml` inside the package.
**Method:** package opened read-only via Python `zipfile`; `word/document.xml`, `word/styles.xml`, `word/settings.xml`, `word/footnotes.xml`, `word/comments.xml`, `customXml/item1.xml`, `docProps/*` inspected directly. PDF float inventory extracted with PyMuPDF; page 1 rendered at 2x for typographic parity. No files edited.

**Recommendation:** minor_revision.

---

## Summary

This is a genuinely well-built OMML Word deliverable, not a rasterized or degraded export. Equations are native, editable Office Math (594 `m:oMath` blocks with real `m:sSub`/`m:sSup`/`m:f`/`m:nary` structure); zero equations are embedded as images. All 11 tables are native `w:tbl` with grids and styles. All 270 complex fields (146 `REF`, 85 `CITATION`, 38 `SEQ`, 1 `TOC`) are structurally balanced (270 begin / 270 separate / 270 end) and carry cached results, so cross-references, figure/table numbers and citation brackets display correctly even before a field update. Typography matches the frozen spec: `Normal`/`BodyText` styles set Palatino Linotype at `sz=20` (10 pt) with `jc="both"` (justified), inherited cleanly (zero hard-coded per-run fonts or justifications in the body). `settings.xml` carries `<w:updateFields w:val="true"/>`, which is the correct mitigation for the acknowledged D-WORD-01 author-side finalization step.

The defects found are all minor/editorial: (1) the DOCX carries a "Contents" TOC that the submitted PDF does not, a version-of-record divergence; (2) the citation database is stamped `StyleName="IEEE"` on an MDPI-numeric manuscript, and the printed reference list is static text rather than a live bibliography field — a hybrid that is currently correct but fragile; (3) figure images carry only generic "Picture" alt text; (4) `footnotes.xml.rels` carries orphaned DOI hyperlink relationships. None are rejection-grade. Full rendered-layout parity could not be machine-verified without Word, which is exactly the scope the D-WORD-01 deferral reserves to the author.

---

## Category assessments

### 1. OMML equation editability — 5/5
Explicit evidence of native, editable Office Math:
- 594 `<m:oMath>` blocks; 0 `<m:oMathPara>` (inline placement, consistent with the PDF).
- Structured operators present: 208 `m:sSub`, 119 `m:sSup`, 5 `m:f` (fractions), 2 `m:nary`, 3040 math runs.
- First block decodes to genuine editable markup: `<m:oMath><m:r><m:t>D</m:t></m:r>...<m:t>=</m:t>...<m:t>30</m:t></m:oMath>` (i.e. *D* = 30, fully re-typeable in the Word equation editor).
- 14 raster images (`a:blip`) all map 1:1 to the 14 numbered PDF figures (taxonomy tree, mean-rank/Friedman/Nemenyi plots, convergence, concept diagrams). None is an equation. Confirmed: **no equation is rasterized.**

### 2. Native tables — 4/5
- 11 native `<w:tbl>` elements, each with a `<w:tblGrid>` and an applied `<w:tblStyle>` (11 grids / 11 styles). Tables are fully editable, not images.
- PDF has 10 numbered tables; DOCX has 11 native tables. The one extra is unexplained (plausibly the author/affiliation or a keywords/algorithm block rendered as a layout table) and is not a defect, but the count mismatch and the MDPI booktabs rule parity (top/mid/bottom rules) rely on the paragraph/table *style* rather than explicit `<w:tblBorders>` and were not visually confirmable without Word. Minor verification ticket filed.

### 3. Fields / bookmarks / citations / bibliography — 4/5
- Fields are healthy: 270 fields, all balanced (270 begin/separate/end), all carrying cached results. Spot checks: a `REF ref_sec_related` field is cached to "2"; a figure `SEQ` field is cached to "1"; `CITATION awad2016problem \m das2011cec2011` is cached to "[1,2]". 141 bookmark starts anchor the cross-references.
- Citations are Word-native `CITATION` fields (85) bound to a real source database: `customXml/item1.xml` holds 40 `<b:Source>` entries.
- `<w:updateFields w:val="true"/>` is set, so Word prompts to refresh all fields on open.
- Caveats (minor): the source DB is stamped `SelectedStyle="\IEEE2006OfficeOnline.xsl" StyleName="IEEE"` on an MDPI-numeric paper; the printed reference list is *static* MDPI-formatted text (no `BIBLIOGRAPHY` field), so in-text `CITATION` fields and the reference list are not mechanically linked. This is currently consistent (IEEE numeric brackets happen to equal MDPI `[n]`) but is fragile if the author regenerates or inserts a bibliography. Also `footnotes.xml.rels` carries a block of DOI hyperlink `Relationship` entries that the empty `footnotes.xml` never references (orphaned package bloat). Ticket filed.
- Clean: `comments.xml` contains no comments (no stray reviewer annotations); `footnotes.xml` holds only the two default separators (the 13 `\footnote*` hits in LaTeX source are all `\footnotesize`, so zero real footnotes were dropped — no content loss).

### 4. Table of contents — 4/5
- Native TOC field present and correct: `TOC \o "1-3" \h \z \u`, with the heading tree cached (Introduction, Related Work, 2.1/2.2/2.3, Proposed Algorithm, 3.1–3.3.2, ...). `updateFields=true` will populate page numbers on open (0 `PAGEREF` currently cached, so page numbers are absent until the author refreshes — expected).
- Parity divergence (minor): the submitted **PDF has no Table of Contents** ("Contents" absent from the first four pages; no dotted-leader TOC pattern), whereas the DOCX front-matter includes one. An editor comparing the two deliverables will see front matter in the Word file that is not in the version-of-record PDF. Ticket filed.

### 5. Visual parity / typography — 4/5
- Typographic spec confirmed at the style level: `Normal`, `BodyText`, `FirstParagraph`, `Abstract`, headings all set `Palatino Linotype`; body `sz=20` (10 pt) with `jc="both"`; heading styles carry Palatino. Font and justification are inherited from styles (0 hard-coded `Palatino`/`jc=both` in body runs) — clean, portable styling.
- PDF page 1 (rendered) shows the MDPI submit-mode layout — Palatino, justified body, line numbers, MDPI logo/footer — consistent with the style definitions.
- Limits (honest, and covered by D-WORD-01): full rendered layout (float placement, table rules, header/footer, title setting) cannot be machine-verified without Word; the DOCX-vs-PDF TOC divergence (above) is a visible parity gap; figure `wp:docPr` names are all generic "Picture" (no descriptive alt text — accessibility minor). Tickets filed.

---

## Verdict
The Word deliverable meets Q1 expectations for a native-format submission: editable OMML math, native tables, live and balanced fields tied to a citation DB, and correct Palatino/10pt/justified typography, with the field-finalization caveat honestly deferred to the author (D-WORD-01) via `updateFields=true`. The open tickets are minor/editorial and do not touch any frozen number or the algorithm. Recommend **minor_revision**.
