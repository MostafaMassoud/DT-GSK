# Word validation report — Phase 9 (Gate 9 documented fallback)

Date: 2026-07-11; **refreshed 2026-07-22 (SE-032)** -- see Section 9, which supersedes every count, hash and page number in Sections 1-8.
Scope: `papers/DT-GSK.docx`, `papers/supplementary.docx`, `word/reference.docx`
against `papers/DT-GSK.pdf` and `papers/supplementary.pdf`. **The 34 pp / 32 pp figures originally recorded here are stale; the shipped build is 40 pp / 61 pp (Section 9).**

## 1. Recorded deviation (Gate 9 sole-exception rule)

Microsoft Word is **not available** in the build environment, so the
prescribed open-save-open check could not be executed.  Per the Phase 9
binding constraints, the DOCUMENTED FALLBACK was applied instead: OOXML
schema/package-level validation (Sections 2–3) plus this recorded deviation.

> **DEVIATION D-WORD-01 (executed 2026-07-23; confirmation pending):** The
> author performed the desktop-Word open-save of DT-GSK.docx on 2026-07-23
> (recorded in the freeze manifest, fourteenth pass; the shipped file remains
> the deterministic build output, since Word re-writes bytes on save). The
> residual author-side step is the visual confirmation checklist below
> (fields, TOC/SEQ/REF/CITATION rendering, landscape sections) on re-open.

Items to confirm at the Word-open pass:

1. TOC populates with page numbers (field `TOC \o "1-3" \h \z \u`;
   `w:updateFields` is set, Word updates on open).
2. SEQ/REF refresh is idempotent — cached values were written from the frozen
   `main.aux`/`supplementary.aux`, so numbering must not change.
3. CITATION fields re-render under the stored IEEE numbered style
   (customXml `b:Sources`); multi-source fields may reformat from the cached
   MDPI form `[1,2]` to `[1], [2]` — cosmetic, record the observed form.
4. Native OMML equations render (no equation images exist in the packages).
5. Table A14 (`tab:bca-ci`) shows the rank-CI table (BCa CIs on Friedman mean
   ranks) — cross-format reconciliation with the PDF supplement.

Related recorded convention (static-field exception, Gate 9 rule): the
References section is a **static** MDPI-numbered list converted from the
frozen `.bbl` — no `BIBLIOGRAPHY` field is inserted.  Justification: the
`.bbl` citation numbering is the canonical cross-format numbering; in-text
`CITATION` fields carry cached `[n]` results identical to the PDF, and the
customXml `b:Sources` store (40/8 entries) preserves Word-native
regenerability.  No other static-field fallback is used — TOC, SEQ, REF and
CITATION are all live complex fields with cached results.

## 2. Validator suite (Appendix D.6) — commands and verdicts

```bash
python papers/scripts/validate_docx.py papers/DT-GSK.docx        # exit 0
python papers/scripts/validate_docx.py papers/supplementary.docx  # exit 0
python papers/scripts/validate_cross_format_parity.py             # exit 0
python papers/scripts/validate_evidence_bindings.py               # exit 0
```

| Validator | Verdict | Evidence |
|---|---|---|
| `validate_docx.py` (OOXML package inspection) | **PASS 33/33 checks, both documents** | JSON report on stdout (Section 3 counts) |
| `validate_cross_format_parity.py` (PDF vs DOCX per logical artifact) | **417 artifact rows: 380 PASS, 37 PASS_FORMAT_DIFF, 0 FAIL** | `papers/governance/cross_format_consistency.csv` |
| `validate_evidence_bindings.py` (BIND-carrying numbers) | **267 BIND comments; 721 numeric tokens; 721/721 found in BOTH formats; 0 FAIL** | `papers/build_prompt_phases/phase_09/evidence_binding_verification.csv` |

One `build_docx.py` defect was revealed and fixed (tooling only, canonical
sources untouched): the pandoc-bookmark rename pass only rewrote names
containing `:` or `-`, letting the Word-illegal heading anchor
`limitations.` (trailing period) survive in `DT-GSK.docx`.  The pass now
renames every bookmark not matching `[A-Za-z_][A-Za-z0-9_]{0,39}`.  Both
documents were rebuilt and re-validated; `supplementary.docx` is
byte-identical to the pre-fix build (fix touches nothing there).  Current
hashes (two consecutive rebuilds byte-identical, `SOURCE_DATE_EPOCH=1783641600`):

| File | SHA-256 |
|---|---|
| `papers/DT-GSK.docx` | `2e451769fe4f7d3d81a7982d5c62fc91efbf21a36f2c977bf116e2adc1267c9f` |
| `papers/supplementary.docx` | `902db38f448f2af3c27ac7b7966edb6c21e2be854bcc29256c19734cf3ee2ceb` |
| `word/field_registry.csv` | `a0f0d2458b4a5d4948cdf4d2e15ea99ccf7227ed25b67335b18f463f3b591a94` |

**Update (Gate 9 QA, 2026-07-11, mechanical fix MF-01):** after the recorded
layout-only fix in `sections/related_work.tex` (Table 1 `[10]` glyph
collision; see `phase_09/latex_build_report.md`), `DT-GSK.docx` was rebuilt
and re-validated (PASS 33/33; parity 417 rows / 0 FAIL; bindings 721/721):

| File | SHA-256 |
|---|---|
| `papers/DT-GSK.docx` (post-MF-01, current) | `5517b6318df84ad8020d352eb080d3cbab0574c111fde01a6463f9f77918844a` |
| `papers/supplementary.docx` (unchanged) | `902db38f448f2af3c27ac7b7966edb6c21e2be854bcc29256c19734cf3ee2ceb` |
| `word/field_registry.csv` (unchanged) | `a0f0d2458b4a5d4948cdf4d2e15ea99ccf7227ed25b67335b18f463f3b591a94` |

## 3. OOXML package inspection (`validate_docx.py`) — counts

Checks: zip integrity/unique part names; every XML part well-formed;
required parts; `[Content_Types].xml` coverage; relationship-target
resolution + unique Ids (package, document, customXml); every `r:id` used by
`document.xml` resolves; root/body/sectPr sanity; no XML-1.0-invalid control
characters; OMML presence; zero-equation-image proof (drawing count ==
canonical `\includegraphics` count, no formula-named media); `w:tbl` count
vs canonical table environments; `w:tbl` structure (tblGrid/gridSpan
consistency, no empty rows/cells); fldChar begin/separate/end stack balance;
cached results present on every SEQ/REF/CITATION; SEQ name whitelist; single
TOC; bookmark pairing/unique ids/unique names/Word-legal names; REF targets
exist; field counts vs `word/field_registry.csv`; customXml `b:Sources`
present + fully wired + count vs frozen `.aux`; `w:updateFields`; referenced
styles defined; zero unresolved `@@` markers; no-ablation scan over every
part; S6 non-rendering; python-docx opens.

| Count | DT-GSK.docx | supplementary.docx |
|---|---|---|
| Verdict | PASS 33/33 | PASS 33/33 |
| `m:oMath` (native math) | 607 | 172 |
| `m:oMathPara` | 0 | 0 |
| Equation images | **0** (14 drawings == 14 canonical `\includegraphics`) | **0** (20 == 20) |
| Images / with alt text | 14 / 14 | 20 / 20 |
| `w:tbl` (vs canonical table envs) | 11 / 11 | 14 / 14 |
| SEQ fields | 38 | 35 |
| REF fields (all targets exist) | 146 | 21 |
| CITATION fields | 85 | 9 |
| TOC fields | 1 | 1 |
| Total complex fields (balanced) | 270 | 66 |
| Bookmarks (paired, unique, Word-legal) | 141 | 86 |
| customXml `b:Source` entries (== `.aux` cites) | 40 | 8 |
| Unresolved `@@` markers | 0 | 0 |
| Field-registry agreement | PASS (against 472-row registry) | PASS |

## 4. Cross-format parity (`validate_cross_format_parity.py`)

Per-artifact statuses (`papers/governance/cross_format_consistency.csv`,
417 rows, sha1 content hash per artifact):

| Artifact class | DT-GSK pair | supplementary pair |
|---|---|---|
| Numbered headings (vs PDF outline + text) | 38 PASS | 16 PASS |
| Outline coverage (every PDF outline entry matched) | PASS (32/32) | PASS (16/16) |
| Run-in paragraph headings | 12 PASS | — |
| Captions (figure/table/algorithm) | 25 PASS | 34 PASS |
| Generated tables (word_sources exact + display precision + PDF spot) | 3 FMT_DIFF + 3 spot PASS | 1 PASS + 13 FMT_DIFF + 14 spot PASS |
| Authored tables (canonical LaTeX row-sets) | 4 PASS + 4 FMT_DIFF | — |
| Body paragraphs | 121 PASS + 4 FMT_DIFF | 52 PASS + 1 FMT_DIFF |
| Display equations (OMML; eq numbers verified in PDF) | 6 FMT_DIFF | 1 FMT_DIFF |
| Citation keys == canonical `\cite` inventory | PASS (40 keys / 85 fields) | PASS (8 keys / 9 fields) |
| Citation cached numbers == frozen `.aux` | PASS | PASS |
| Citation rendered forms found in PDF | PASS | PASS |
| Bibliography entries (count + per-entry text in PDF) | 1 + 40 PASS | 1 + 8 PASS |
| No-ablation scan (extracted PDF text) | PASS | PASS |
| **FAIL rows** | **0** | **0** |

Intentional format-only differences recorded in the CSV (all
`PASS_FORMAT_DIFF`, none content-bearing):

1. **TOC** exists only in the DOCX (native update-on-open field); the MDPI
   submission PDF carries none.
2. **Heading-number typography**: Word renders `N<tab>Title`; the PDF
   renders `N. Title`.
3. **Native-table value precision**: DOCX renders the semantic word_sources
   precision (e.g. `2.879310`); the PDF renders display-rounded (`2.88`).
   The parity validator proves every frozen `.tex` display string is
   derivable from the semantic value at display precision (exact-format
   reproduction), so the underlying values are identical.
4. **Math rendering**: OMML linear text vs PDF glyph extraction
   (display-equation paragraphs, math-heavy table rows/captions);
   equation numbers and prose context are verified in both formats.

## 5. Evidence bindings (`validate_evidence_bindings.py`)

Every `% BIND:` comment in the frozen canonical sources was located
(267 total: 184 main + 83 supplement), its annotated visible text collected
(inline: own line + 2 preceding; standalone: up to 6 preceding lines,
paragraph-bounded), and every numeric token extracted (`\cite`/`\ref`/
`\label` arguments excluded): 721 tokens — 464 integers, 166 decimals,
78 powers of ten, 13 comma-grouped integers.

**All 721 tokens were found identically in both rendered formats**
(PDF text extraction and DOCX `w:t`+`m:t` text; whitespace/ligature/
unicode-minus-normalized channels).  Full record with per-token verdicts:
`papers/build_prompt_phases/phase_09/evidence_binding_verification.csv`.

Deterministic 30-token detail sample (round-robin over token kinds, most
distinctive first; all PASS, `pdf=yes docx=yes`):

| # | Doc | Source | Kind | Token | BIND ids |
|---|---|---|---|---|---|
| 1 | supp | supplementary.tex:613 | pow10 | 10^-14 | FIG-CONV-SUP-2017-D50-C |
| 2 | supp | supplementary.tex:168 | decimal | 0.05 | AN-PW-2017-D10..D100 |
| 3 | main | performance.tex:92 | group_int | 1,000,037 | seed_and_pairing_audit |
| 4 | main | related_work.tex:145 | int | 100 | EC:mohamed2020gaining |
| 5 | supp | supplementary.tex:168 | pow10 | 10^-8 | AN-PW-2017 protocol |
| 6 | main | performance.tex:353 | decimal | 0.21 | negative_findings item 4 |
| 7 | main | performance.tex:61 | group_int | 150,000 | PR-02, PR-04 |
| 8 | main | performance.tex:399 | int | 2026 | FIG-CD-D100 |
| 9 | main | performance.tex:601 | pow10 | 2.7x10^2 | AN-DESC-2017-D30 |
| 10 | main | performance.tex:500 | decimal | 0.137 | TAB-T06 |
| 11 | supp | supplementary.tex:429 | group_int | 10,000 | TAB-T16-BCA (n_boot) |
| 12 | main | performance.tex:399 | int | 100 | FIG-CD-D100 |
| 13 | main | performance.tex:92 | pow10 | 10^-8 | seed_and_pairing_audit |
| 14 | main | performance.tex:198 | decimal | 1.80 | AN-CLASS-2017 |
| 15 | main | performance.tex:92 | group_int | 2,147,483,646 | seed_and_pairing_audit |
| 16 | main | conclusions.tex:102 | int | 100 | LM-05 |
| 17 | supp | supplementary.tex:682 | pow10 | 4.2x10^-2 | FIG-CONV-CEC2011-A |
| 18 | main | performance.tex:407 | decimal | 2.21 | AN-TREND-2017 |
| 19 | supp | supplementary.tex:155 | group_int | 150,000 | PR-02; PR-04 |
| 20 | main | performance.tex:554 | int | 340 | TAB-T14; AN-PW-2013 |
| 21 | main | performance.tex:554 | pow10 | 3.1x10^-2 | TAB-T14 |
| 22 | main | performance.tex:705 | decimal | 42.40 | AN-COST-2017 (2-dp) |
| 23 | supp | supplementary.tex:934 | group_int | 5,916 | seed_and_pairing_audit §6 |
| 24 | supp | supplementary.tex:874 | int | 100 | ART-PARAMS |
| 25 | main | performance.tex:601 | pow10 | 9.85x10^2 | AN-DESC-2017-D30 |
| 26 | supp | supplementary.tex:367 | decimal | 3.07 | CEC2013-D30-THIRD |
| 27 | supp | supplementary.tex:853 | group_int | 70,813 | seed_and_pairing_audit §2,5 |
| 28 | main | related_work.tex:233 | int | 1000 | novelty_scope non-claim #4 |
| 29 | main | performance.tex:554 | pow10 | 1.9x10^-4 | TAB-T14 |
| 30 | main | performance.tex:198 | decimal | 1.60 | AN-CLASS-2017 |

(No scientific-`E`-notation tokens exist in BIND-annotated prose — that
notation appears only inside generated tables, which are covered by the
parity validator's exact value checks.)

## 6. No-ablation scan (both DOCX, all parts + both PDFs)

* **DOCX**: every text-bearing part of each package (document.xml, styles,
  settings, numbering, footnotes, theme, docProps, customXml, rels — 19
  XML/rels parts of the 33 [main] / 39 [supplementary] total parts; the
  remainder are PNG media) scanned for `ablation`/`ablat`/
  `phase_12_placeholder`/`do not release` (case-insensitive):
  **0 hits in both packages**.
* **PDF**: extracted full text of `DT-GSK.pdf` and `supplementary.pdf`
  scanned for the same tokens: **0 hits**.
* **S6 placeholder**: `supplementary.tex` line 947 keeps S6 as a LaTeX
  comment; validators confirm **no rendered S6 heading/caption/paragraph**
  in either PDF (outline ends at S5; no `S6`-prefixed line) or either DOCX
  (no paragraph text matching `^S6\b`).

## 7. OOXML fallback methodology note

Validator: `papers/scripts/validate_docx.py` (zipfile + lxml structural
validation; full ECMA-376 XSD validation is not available offline — recorded
as part of deviation D-WORD-01).  The narrower legacy check
`build_docx.py --validate-only` remains available and agrees.  python-docx
1.2.0 opens both packages.  Word-repair-trigger classes explicitly covered:
malformed XML, missing content types, dangling relationships, duplicate
bookmark ids/names, illegal bookmark names, unbalanced field characters,
tblGrid/gridSpan inconsistencies, empty table rows/cells, duplicate
drawing `docPr` ids, invalid control characters.

## 8. Related recorded items

* `word_citation_tag_map.csv` staleness for `awad2016problem`
  (CR-0005/D-0009 override) — see
  `papers/build_prompt_phases/phase_09/word_build_report.md` Section 8.
* T16_bca reconciliation record — same report, Section 6; re-verified here
  by the parity validator (T16_bca row-set equality vs the frozen
  `T16_bca.tex`: PASS).
* Build-fix log (bookmark-name legality) — same report, Section 7 item 6.
* Validator commands recorded in
  `papers/governance/project_configuration.md` Section 11.


---

## 9. Refresh against the shipped build (2026-07-22, SE-032)

SE-032 found every count, hash and page number in Sections 1-8 stale, and no
typographic specification anywhere. This section is measured against the build
shipped on 2026-07-22 and is authoritative where it disagrees with anything above.

### 9.1 Shipped artifacts

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| `papers/DT-GSK.docx` | 1,020,946 | `106c479d254362320ef54ab0e9dbbe00d4e09df6f7ab3b24785adf1066f457f0` |
| `papers/supplementary.docx` | 8,507,097 | `7c4ba7a2d28047ad59207c594f797cb17739f87c34bf421394fe28c7adc3f78a` |
| `word/reference.docx` | 11,244 | `5c4d8f79403112f00580441fb350316c614b27903f1edd25c735c0ad71297c89` |

Companion PDFs: `DT-GSK.pdf` 40 pp, `supplementary.pdf` 61 pp, `cover_letter.pdf` 2 pp.

### 9.2 Object counts (from `build_docx.py` post-process validation)

| Object | DT-GSK.docx | supplementary.docx |
|---|---:|---:|
| `m:oMath` (native math) | 794 | 642 |
| Tables (`w:tbl`) | 17 | 26 |
| Drawings (embedded figures) | 7 | 27 |
| Bookmarks | 141 | 170 |
| Field starts (`w:fldChar begin`) | 296 | 110 |
| `SEQ` / `REF` / `CITATION` fields | 37 / 172 / 87 | 54 / 40 / 16 |
| `TOC` fields | 0 | 0 |
| Unresolved build markers | 0 | 0 |

`validate_docx.py`: **33 PASS / 0 FAIL / 0 warnings** on both documents.
`validate_cross_format_parity.py`: **582 rows, 0 FAIL**.

### 9.3 Typographic specification

Measured from `word/reference.docx` (`word/styles.xml`, 53 style ids). Sizes are
half-points in OOXML; points are given for readability.

| Element | Style id | Typeface | Size | Weight |
|---|---|---|---|---|
| T1 Title | `Title` | Palatino Linotype | 36 half-pt = **18 pt** | bold |
| T2 Author block | `Author` | Palatino Linotype | 22 half-pt = **11 pt** | bold |
| T3 Headings 1-3 | `Heading1`/`2`/`3` | Palatino Linotype | 20 half-pt = **10 pt** | H1 bold; H2/H3 regular |
| T4 Body text | `BodyText` (document default) | Palatino Linotype | 20 half-pt = **10 pt** | regular |
| T5 Captions | `Caption` | Palatino Linotype | 18 half-pt = **9 pt** | regular |

Abstract: `Abstract`, 19 half-pt = 9.5 pt, regular. Paragraph default spacing
`w:after=200` twips. The typeface matches the LaTeX build, which sets Palatino
via the MDPI class -- so the two deliverables agree on family and on the 10 pt
body size; they differ only in measure (Section 9.4).

### 9.4 Page geometry (SE-031 decision)

`w:pgSz w:w=11906 w:h=16838` (A4) with `w:pgMar w:left=1134 w:right=1134`, giving a
text measure of **9,638 twips (170.1 mm)** against the LaTeX class's **8,845 twips
(156.0 mm)** -- the Word line measure is **9.0% wider**.

**Disposition: APPROVED DEVIATION, not a defect to be silently carried.** The full
rationale, the measurement method, and what a future revision must change together
if it wants the geometries unified, are recorded in
[`production_deviation_record.md`](production_deviation_record.md) item D-4. That file
also records the three LaTeX-class deviations (D-1 dated class, D-2 suppressed
submit-mode line numbering, D-3 suppressed branding) raised by SE-048.

### 9.5 Deviation D-WORD-01 status

**EXECUTED 2026-07-23 (author-side; visual confirmation pending).** The author
opened and saved DT-GSK.docx in desktop Word without error (freeze manifest,
fourteenth pass). The shipped artifact remains the deterministic build output
(Word re-writes bytes on save, so the re-saved file is a compatibility probe,
not the deliverable). Remaining before submission: the visual checklist of
Section 1 on re-open (fields, TOC/SEQ/REF/CITATION, landscape sections).
