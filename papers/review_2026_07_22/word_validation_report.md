# Stage 17 — Microsoft Word / OOXML validation and DOCX→PDF typographic-parity report

**Seat:** `s17_journal_production` (PROD-WORD lead; teams T4-SOFT, T7-VENUE)
**Review date:** 2026-07-22
**Objects under test:** `papers/DT-GSK.docx` (1,037,004 B, sha256 `1ad8c3b2129b1f65…`),
`papers/supplementary.docx` (8,735,071 B, sha256 `a9a64295278f67db…`), `word/reference.docx`,
against `papers/DT-GSK.pdf` (**39 pp**) and `papers/supplementary.pdf` (**61 pp**).

> **This report supersedes `papers/governance/word_validation_report.md` for the current build.**
> That file audits a superseded package (see §0) and is itself a Major finding (**S17-04**).

All statements are **CONFIRMED** unless marked **SUSPECTED**.

---

## 0. **S17-04 (Major, P1, CONFIRMED)** — the governance Word-validation record is stale in every measurable field

`papers/governance/word_validation_report.md` is the artifact Stage 17 and profile §10.12
designate as the place where Word deviations are recorded. It is dated **Phase 9, 2026-07-11**
and describes a package that no longer exists. Every count in it is now wrong:

| Field | `word_validation_report.md` (Phase 9) | Measured 2026-07-22 | |
|---|---|---|---|
| Scope line: main PDF pages | "34 pp" | **39 pp** | stale |
| Scope line: supplement PDF pages | "32 pp" | **61 pp** | stale |
| `m:oMath` main / supp | 607 / 172 | **753 / 640** | stale |
| Images main / supp | 14 / 20 | **7 / 27** | stale |
| `w:tbl` main / supp | 11 / 14 | **17 / 26** | stale |
| SEQ fields main / supp | 38 / 35 | **37 / 54** | stale |
| REF fields main / supp | 146 / 21 | **171 / 40** | stale |
| CITATION fields main / supp | 85 / 9 | **86 / 16** | stale |
| **TOC fields main / supp** | **1 / 1** | **0 / 0** | **contradicted** |
| Bookmarks main / supp | 141 / 86 | **140 / 170** | stale |
| Total complex fields main / supp | 270 / 66 | **294 / 110** | stale |
| Parity rows | 417 | **579** | stale |
| Recorded `DT-GSK.docx` sha256 | `5517b6318df84ad8…` | `1ad8c3b2129b1f65…` | stale |
| Recorded `supplementary.docx` sha256 | `902db38f448f2af3…` | `a9a64295278f67db…` | stale |

Two consequences are more than bookkeeping:

1. **Deviation D-WORD-01 item 1 instructs the author to confirm something that cannot happen.**
   It reads: *"TOC populates with page numbers (field `TOC \o "1-3" \h \z \u`; `w:updateFields` is
   set, Word updates on open)."* Neither clause holds. `validate_docx.py` on the current
   packages reports `toc_field_absent: PASS — 0 TOC fields (expected 0: DOCX matches the no-TOC
   PDF)` and `no_update_fields_on_open: PASS — w:updateFields=false`. The removal of the TOC is
   deliberate and correct (the MDPI submission PDF carries none) and the validator was updated to
   expect it — but the governance record was not.
2. **The report contains no Stage 17 T1–T5 typographic-parity specification at all.** §§1–8 cover
   OOXML structure, parity counts, and evidence bindings; nothing records the body font, size,
   alignment, page geometry, or heading weights that the DOCX must match, and no DOCX→PDF export
   comparison or its deviation is recorded. That specification is supplied below.

**Required correction:** replace or amend `papers/governance/word_validation_report.md` with the
current counts, hashes and page numbers; delete or rewrite D-WORD-01 item 1; and incorporate the
T1–T5 specification from §§1–5 below.

---

## 1. T1 — Parity specification extracted from `papers/Definitions/mdpi.cls`

Read from the class, not assumed:

| Attribute | Class value | Source |
|---|---|---|
| Base size / paper | **10 pt, A4** | L29 `\LoadClass[10pt,a4paper]{article}` |
| Body font | **Palatino** (`mathpazo` → URW Palladio; confirmed as the embedded `URWPalladioL-Roma/-Ital/-Bold` subsets in the PDF) | L43 `\RequirePackage{mathpazo}` |
| Body alignment | **justified** (`article` default; no `\raggedright` in the body) | class default |
| Line spacing | `\linespread{1.13}` | L983 |
| Paragraph indent | 0.75 cm | L984 |
| Margins | **left 2.7 cm, right 2.7 cm, top 1.8 cm, bottom 1.5 cm** (`includehead`, `includefoot`) | L975–L980 `\RequirePackage[left=2.7cm,right=2.7cm,top=1.8cm,bottom=1.5cm,…]{geometry}` |
| Title | 18 pt | L577 `\fontsize{18}{18}` |
| `\section` | **10 pt bold**, ragged-right | L836 `\titleformat{\section}…\bfseries` |
| `\subsection` | **10 pt italic** | L839 `…\itshape` |
| `\subsubsection` | **10 pt regular** | L842 |
| Caption | `small` (9 pt) text, **bold** label, `labelsep=period`, justified | L994–L1004 `\captionsetup…labelfont={bf, small,…}` |
| Back-matter declarations | 9 pt, bold `Label:` run-in | L850–L868 |
| Hyphenation | **disabled** (`\RequirePackage[none]{hyphenat}`, L209) | L209 |

## 2. T2 — `word/styles.xml` measured against the specification

Bold/italic read from the `w:val` attribute, not element presence (`<w:b w:val="0"/>` = **not**
bold). Identical results for `DT-GSK.docx` and `supplementary.docx`.

| Style | `w:rFonts` (ascii/hAnsi/cs) | `w:sz` (half-pt) | `w:jc` | bold | italic | vs T1 |
|---|---|---|---|---|---|---|
| `Normal` | Palatino Linotype (all three set) | 20 → **10 pt** | `both` | – | – | **MATCH** |
| `BodyText` | Palatino Linotype | 20 → 10 pt | `both` | – | – | **MATCH** |
| `FirstParagraph` | Palatino Linotype | 20 → 10 pt | `both` | – | – | **MATCH** |
| `Title` | Palatino Linotype | 36 → **18 pt** | `left` | `<w:b/>` (true) | – | **MATCH** |
| `Heading1` (≙ `\section`) | Palatino Linotype | 20 → 10 pt | – | `<w:b/>` **true** | `w:val="0"` **false** | **MATCH** (bold) |
| `Heading2` (≙ `\subsection`) | Palatino Linotype | 20 → 10 pt | – | `w:val="0"` **false** | `<w:i/>` **true** | **MATCH** (italic) |
| `Heading3` (≙ `\subsubsection`) | Palatino Linotype | 20 → 10 pt | – | `w:val="0"` false | `w:val="0"` false | **MATCH** (regular) |
| `Caption` | Palatino Linotype | 18 → **9 pt** | `both` | false | false | **MATCH** on size/alignment |
| `Bibliography` | Palatino Linotype | 18 → 9 pt | `both` | – | – | **MATCH** |

**Font, size, weight and alignment mapping is correct throughout — including the subtle
bold-vs-italic heading distinction that a naive presence check would have misread.**

### 2.1 **S17-03 (Major, P1, CONFIRMED)** — page margins do not match the class

`w:sectPr` in both DOCX (and in `word/reference.docx`, which is the origin):

```
pgSz  w=11906 h=16838 twips              → A4 210 × 297 mm      MATCH
pgMar left=1134 right=1134               → 2.00 cm / 2.00 cm    vs class 2.70 / 2.70  MISMATCH
      top=1417  bottom=1417              → 2.50 cm / 2.50 cm    vs class 1.80 / 1.50  MISMATCH
      header=709 footer=709              → 1.25 cm / 1.25 cm
```

| Measure | LaTeX PDF | Word | Δ |
|---|---|---|---|
| Text width | 21.0 − 5.4 = **15.6 cm** | 21.0 − 4.0 = **17.0 cm** | **+9.0 %** |
| Text height | 29.7 − 3.3 = **26.4 cm** | 29.7 − 5.0 = **24.7 cm** | −6.4 % |

This is a **typography defect in the Stage 17 defect list** ("wrong page size or margins"), not an
unavoidable engine difference: a Word `Save As PDF` export will show visibly wider side margins
that are *narrower at the sides and deeper top and bottom* than the submitted LaTeX PDF, and a
~9 % longer line measure. Net text area differs by only ~2 %, so the page-count delta should stay
small — the visible mismatch is the page geometry itself, not the length.

**Required correction:** set `word/reference.docx` `w:pgMar` to
`left=1531 right=1531 top=1021 bottom=850` twips (2.70 / 2.70 / 1.80 / 1.50 cm) and rebuild both
DOCX. **Post-revision verification:** `w:pgMar` in both packages equals those values; a re-export
shows the same text measure as the LaTeX PDF.

## 3. T3 — reference template and font availability

* `word/reference.docx` encodes the same specification as the deliverables — Palatino Linotype at
  `sz=20`, `jc=both`, Title 36, Caption/Bibliography 18, the same heading weights — so the style
  mapping is centrally defined and reproducible. It also carries the **same non-conforming
  margins** (§2.1); that is where the defect originates and where it must be fixed.
* **Font availability:** *Palatino Linotype* is a Windows-bundled font, so the deliverables render
  as intended on the build platform and on any Windows editor's machine. **Substitution risk:** it
  is **not** present by default on macOS (which ships *Palatino* / *Palatino Linotype* only with
  Office) or on Linux. An editor opening the DOCX without it will get a substituted face and the
  typographic parity will break silently. Naming the required font in the submission notes is the
  cheap mitigation. Recorded as a risk, not a ticket — the font choice is correct.

## 4. T4 — DOCX→PDF export comparison: **ATTEMPTED, NOT COMPLETED**

Microsoft Word **is** available in this environment
(`C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE`); LibreOffice is not. An export was
attempted via Word COM automation, opening `papers/DT-GSK.docx` read-only and calling
`ExportAsFixedFormat` to a scratch path (no repository file was written or modified):

```
$word = New-Object -ComObject Word.Application ; $word.Visible = $false ; $word.DisplayAlerts = 0
$doc  = $word.Documents.Open($src, $false, $true)   # ReadOnly
$doc.ExportAsFixedFormat($dst, 17)                  # wdExportFormatPDF
```

The process ran for **more than 85 minutes** without producing the PDF (WINWORD.EXE resident at
~183 MB, no output file, no error) and was terminated. The most likely cause is a non-visible
modal during pagination of a 753-equation, 294-field document, but that is **SUSPECTED**, not
confirmed. **No repository file was touched; the document was opened read-only and never saved.**

The page-count delta, per-page appearance comparison, and rendered side-by-side inspection are
therefore **not available from this review**.

## 5. T5 — documented deviation (Stage 17 sole-exception mechanism)

> **DEVIATION D-WORD-02 (open, this review, 2026-07-22).** The DOCX→PDF export comparison
> (T4) could not be completed: Microsoft Word is installed but did not finish
> `ExportAsFixedFormat` on `papers/DT-GSK.docx` within 85 minutes, and no headless converter
> (LibreOffice `soffice`) is available. Parity is therefore established at the **style level**
> (T1–T3) only: font family, font size, body justification, page size, title/heading/caption
> sizes and heading weights are verified byte-level against `word/styles.xml`, and **one
> mismatch is confirmed — the page margins (S17-03).**
>
> **A style-level match is a strong but incomplete substitute for the rendered comparison.**
> It cannot detect pagination pathologies, table column collapse, figure placement drift,
> equation-baseline problems, or field-update side effects. The author-side
> **open-in-Word → update fields → `Save As PDF` → page-by-page visual comparison against
> `papers/DT-GSK.pdf`** is a **required pre-submission step** and is recorded here as such.
>
> This deviation is in addition to the still-open **D-WORD-01** (Word open/save/reopen
> validation never executed, `papers/governance/word_validation_report.md` §1). Both must be
> closed by the same author-side Word session.

---

## 6. OOXML / editability review — PASS on every mandated item

`python papers/scripts/validate_docx.py <file>` → **33 PASS / 0 FAIL** for both packages
(exit 0), re-run in this review. Independently re-verified items:

| Stage 17 requirement | Verdict | Evidence (measured 2026-07-22) |
|---|---|---|
| All equations native OMML | **PASS** | `m:oMath` 753 (main) / 640 (supplement); `m:oMathPara` 0; `zero_equation_images`: "7 drawings + 0 OLE vs 7 canonical `\includegraphics`; formula-named media: []" |
| **No equations rasterised** (Stage 17 *critical* class) | **PASS** | drawing count equals the canonical `\includegraphics` count in both packages; no formula-named media parts |
| **No tables rasterised** (Stage 17 *critical* class) | **PASS** | 17 `w:tbl` vs 17 canonical table environments (main); 26 vs 26 (supplement); `table_structure_sane` PASS |
| Tables are native `w:tbl` | **PASS** | as above; `tblGrid`/`gridSpan` consistent, no empty rows/cells |
| Captions editable paragraphs | **PASS** | 23 (main) + 50 (supplement) caption artifacts matched as paragraphs by the parity validator; none is an image |
| Live numbering fields | **PASS** | SEQ 37 (main, names `Algorithm/Equation/Figure/Table`) + 54 (supplement); all carry cached results |
| Cross-references via bookmarks + REF | **PASS** | REF 171 (main) / 40 (supplement), all targets exist; bookmarks 140 / 170, paired, unique ids **and** unique names, all Word-legal `[A-Za-z0-9_]`, ≤40 chars, letter-initial |
| Updateable citations | **PASS** | CITATION fields 86 / 16; `customXml` `b:Sources` store present and fully wired, 40 sources vs 40 cited keys in the frozen `.aux` |
| Static bibliography deviation | **DOCUMENTED, ACCEPTED** | References are a static MDPI-numbered list converted from the frozen `.bbl`; recorded in `papers/governance/word_validation_report.md` §1 with justification. Profile §10.12's exception clause applies — **verify the record, do not fail Gate P** |
| TOC and lists | **N/A, correctly** | 0 TOC fields, matching the no-TOC PDF; `toc_field_absent` PASS. See §0 for the stale record that says otherwise |
| Section numbering via styles | **PASS** | `Heading1/2/3` used throughout; 21 referenced style ids all defined |
| Alt text present | **PASS** | 7/7 (main) and 27/27 (supplement) images carry `descr` |
| Opens without repair | **PARTIAL** | `python-docx` opens both; zip CRC, content types, relationship targets, `r:id` resolution, field `fldChar` begin/separate/end balance (294/294/294), duplicate `docPr` ids, and XML-1.0 control characters all clean — i.e. every documented Word-repair trigger class is covered. Actual Word open/save/reopen remains D-WORD-01 |
| **No tracked changes** | **PASS** | XML-parsed counts (not substring matches): `w:ins` 0, `w:del` 0, `w:moveFrom` 0, `w:moveTo` 0 in both |
| **No comments** | **PASS** | `word/comments.xml` present but contains **0** `w:comment` elements (625 B empty part); `commentRangeStart` 0, `commentReference` 0 |
| **No hidden text** | **PASS** | `w:vanish` 0, `w:highlight` 0 |
| No placeholders / unresolved markers | **PASS** | 0 `@@` markers; no `TODO`/`TBD`/`FIXME` in any part |
| Ablation-token hygiene | **PASS** | main: tokens absent from all 26 parts, no rendered S6; supplement: S6 correctly rendered, release-block tokens absent from all 46 parts |

**Diagram editability (profile §10.17.3):** flowchart *diagrams* ship as images, which the control
permits. Their step content is additionally available as native text — the supplement's
`Table A19`-class parameter tables and the algorithm listing are `w:tbl`/paragraph content, not
pictures. No table or figure-table appears in Word only as a picture.

### 6.1 **S17-10 (Minor, P3, CONFIRMED)** — Word figures below MDPI's recommended resolution

Effective DPI computed from `wp:extent` (EMU) against the embedded PNG pixel dimensions:

| Package | Images | Effective DPI range | Worst cases |
|---|---|---|---|
| `DT-GSK.docx` | 7 | **219 – 527** | `media/rId20.png` 909×1619 px placed 298.2×531.2 pt → **219 dpi**; `media/rId24.png` → 219 dpi |
| `supplementary.docx` | 27 | **235 – 384** | `media/rId123.png` 1335×760 px placed 408.9×232.8 pt → **235 dpi** |

MDPI's stated guidance is a minimum of **600 dpi**. Every Word figure is below it. The PDF is
unaffected (its figures are vector). This is both a journal-requirement shortfall in the Word
deliverable and a PDF↔Word quality divergence.

**Required correction:** raise the rasterisation DPI in `papers/scripts/build_docx.py` (or emit
EMF/vector where pandoc permits) so every embedded image reaches ≥600 dpi at its placed size.

---

## 7. Ticket register (schema §5.4) — Word tickets

```text
ticket_id: S17-03
review_stage: 17
reviewer_role: PROD-WORD / T4-SOFT
severity: Major
priority: P1
confidence: Confirmed
issue_type: production
manuscript_location: word/reference.docx w:sectPr/w:pgMar; propagated to papers/DT-GSK.docx and papers/supplementary.docx
claim_id_or_artifact_id: Stage 17 T1-T3 typographic parity; profile 10.12 final bullet
concise_issue: The Word page margins do not match the mdpi.cls page geometry, so a Word-exported PDF will not match the submitted LaTeX PDF.
exact_evidence_or_observation: mdpi.cls L975-L980 sets left=2.7cm right=2.7cm top=1.8cm bottom=1.5cm. Both DOCX and word/reference.docx carry w:pgMar left=1134 right=1134 top=1417 bottom=1417 twips = 2.00/2.00/2.50/2.50 cm. Text measure 17.0 cm vs 15.6 cm (+9.0 percent); text height 24.7 cm vs 26.4 cm.
root_cause: word/reference.docx was authored with default 2 cm / 2.5 cm margins rather than transcribed from the class geometry; every build inherits it.
scientific_or_editorial_justification: Stage 17 lists "wrong page size or margins" as a ticketable typography defect and profile 10.12 requires the Word document to reproduce the LaTeX page geometry.
impact_on_validity_or_acceptance: No effect on content. A Word-exported PDF looks materially different from the submitted PDF - the exact failure mode Stage 17 T1-T5 exists to catch.
required_correction: Set w:pgMar to left=1531 right=1531 top=1021 bottom=850 twips in word/reference.docx and rebuild both DOCX deterministically.
acceptable_alternatives: None - the class geometry is the specification.
additional_evidence_needed: None. A confirming DOCX-to-PDF export requires the D-WORD-02 author-side step.
dependencies: D-WORD-02 (T5) for the rendered confirmation.
expected_improvement: Word export becomes visually consistent with the LaTeX PDF; closes the only confirmed T1-T3 mismatch.
post_revision_verification: w:pgMar equals the specified twip values in reference.docx and both deliverables; author-side Save As PDF shows the same line measure as DT-GSK.pdf.
status: open
```

```text
ticket_id: S17-04
review_stage: 17
reviewer_role: PROD-WORD / T4-SOFT
severity: Major
priority: P1
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/governance/word_validation_report.md (whole file; scope line L5, section 1 item 1, section 3 count table, section 4 parity table)
claim_id_or_artifact_id: profile 10.12 Word-deviation record; Stage 17 required output
concise_issue: The governance Word-validation record describes a superseded package, asserts a TOC field that no longer exists, and contains no T1-T5 typographic-parity specification.
exact_evidence_or_observation: The file audits "papers/DT-GSK.pdf (34 pp)" and "papers/supplementary.pdf (32 pp)" against the current 39 pp / 61 pp; it records m:oMath 607/172 (now 753/640), images 14/20 (now 7/27), w:tbl 11/14 (now 17/26), REF 146/21 (now 171/40), TOC 1/1 (now 0/0), 417 parity rows (now 579), and DOCX hashes 5517b631../902db38f.. (now 1ad8c3b2../a9a64295..). Deviation D-WORD-01 item 1 asks the author to confirm a TOC populates and that w:updateFields is set; validate_docx.py reports toc_field_absent PASS "0 TOC fields (expected 0)" and no_update_fields_on_open PASS "w:updateFields=false".
root_cause: The record was written at Phase 9 and never refreshed through the Phase-12, 2026-07-18 remediation, the 2026-07-21 freeze, or the R-01..R-14 re-freeze.
scientific_or_editorial_justification: This file is the designated location for the journal-approved static-field deviation and for the Stage 17 T1-T5 record; a stale record cannot discharge either duty, and an instruction to verify a non-existent field wastes the one author-side Word session that closes D-WORD-01.
impact_on_validity_or_acceptance: No effect on reported science. It defeats the audit trail Gate P depends on.
required_correction: Refresh the file with current counts, hashes and page numbers; delete or rewrite D-WORD-01 item 1; incorporate the T1-T5 specification from sections 1-5 of this report; retain the static-bibliography deviation record unchanged.
acceptable_alternatives: Supersede it by reference to this report, provided the governance path remains the single point of truth.
additional_evidence_needed: None.
dependencies: S17-03 (the refreshed record must carry the corrected margins).
expected_improvement: Restores a truthful deviation record and gives the author one correct pre-submission Word checklist.
post_revision_verification: Every count, hash and page number in the refreshed file reproduces from the shipped artifacts; no D-WORD-01 item references a non-existent field.
status: open
```

```text
ticket_id: S17-10
review_stage: 17
reviewer_role: PROD-WORD
severity: Minor
priority: P3
confidence: Confirmed
issue_type: production
manuscript_location: papers/DT-GSK.docx word/media/*; papers/supplementary.docx word/media/*; generator papers/scripts/build_docx.py
claim_id_or_artifact_id: MDPI figure-resolution guidance
concise_issue: Every figure in the Word deliverables is rasterised below MDPI's recommended 600 dpi minimum.
exact_evidence_or_observation: Effective DPI from wp:extent versus PNG pixel size - main 219-527 dpi over 7 images (worst media/rId20.png 909x1619 px at 298.2x531.2 pt = 219 dpi); supplement 235-384 dpi over 27 images (worst media/rId123.png = 235 dpi). The PDFs are unaffected: their figures are vector.
root_cause: The DOCX build rasterises figures at a fixed pixel budget independent of placed size.
scientific_or_editorial_justification: MDPI recommends a minimum of 600 dpi for figures; the Word deliverable is a required submission artifact.
impact_on_validity_or_acceptance: Low. Production would request higher-resolution originals if the Word file were used for typesetting.
required_correction: Raise the rasterisation DPI in build_docx.py so every embedded image reaches at least 600 dpi at its placed size, or emit vector where pandoc permits.
acceptable_alternatives: Supply the original vector figures separately at submission.
additional_evidence_needed: None.
dependencies: None.
expected_improvement: Word deliverable meets the stated figure-resolution guidance and matches the PDF's quality.
post_revision_verification: Minimum effective DPI over all w:drawing images >= 600 in both packages.
status: open
```

---

## 8. Gate P — Word axis verdict

**PASS on OOXML editability and native content; FAIL on typographic parity (S17-03); the
governance deviation record is Major-stale (S17-04); the DOCX→PDF rendered comparison is a
documented deviation (D-WORD-02).**

Nothing in the Word deliverables is rasterised that must be native, nothing is tracked, commented
or hidden, and the Eq. (4) `s_J`/`s_S` correction from ticket R-01 is present in the OMML
(verified independently — see `cross_format_consistency_report.md` §3). The two open items are
the page geometry and the record that should have caught it.
