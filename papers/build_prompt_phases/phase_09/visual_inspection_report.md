# Phase 9 — Gate 9 Adversarial QA: Visual Inspection Report (Task 18)

Date: 2026-07-11.
Scope: `papers/DT-GSK.pdf` (34 pp), `papers/supplementary.pdf` (32 pp),
`papers/DT-GSK.docx`, `papers/supplementary.docx`, against the FROZEN
canonical sources (`papers/main.tex` + `sections/*.tex` +
`supplementary.tex`).
Verdict: **PASS** — one major visual defect found and fixed via recorded
mechanical build fix MF-01 (see Section 3); zero unfixed major defects;
zero Gate 9 hard failures.

## 1. Method

All checks below are **independent re-derivations** (fresh scripts over the
artifacts), not re-runs of the project validators; the project validators
were additionally re-executed after the fix (Section 3).

- **PDF**: pymupdf 1.27.2 text + layout extraction (imaging available, so
  the text-layer-only fallback was NOT needed); page renders at 110 dpi for
  12 selected pages (title, math-dense p9/p12, Tables 1/7/9, back matter
  p31, references p32/p34, supplement p1/p8/p9/p10/p31); 300 dpi zooms of
  suspect regions; word-box margin-overflow scan over every page of both
  PDFs; `main.log`/`supplementary.log` overfull/undefined scans.
- **DOCX**: direct unzip + `document.xml` structural walk (lxml): field
  stacks, bookmark pairing, REF-target resolution, caption adjacency,
  media census, alt text, customXml store; full-text extraction from
  `w:t`+`m:t`; pandoc 3.9.0.2 round-trip of both documents to markdown for
  spot reading (title/abstract, equation registry, Table 7, Table A14, GenAI
  block, references).

## 2. PDF findings (both documents)

| Check | DT-GSK.pdf | supplementary.pdf |
|---|---|---|
| Pages / outline entries | 34 / 32 (all levels nest correctly) | 32 / 16 |
| Equation wrapping | Eqs (1)–(13) display cleanly, right-numbered, no overflow (visual + word-box scan) | Eq (1) clean |
| Margin overflow (word-box scan, every page) | 0 words beyond type area | 0 |
| Table breaks | No table splits across pages; Tables 1–10 each intact | A1–A14 paginate at row boundaries with repeated structure; no orphan captions |
| Caption placement | Tables: caption above; Figures: caption below (MDPI convention) — verified on renders p4/p12/p20/p25 | Same, verified p8/p9/p10 |
| Headings | MDPI submit layout, line numbers present (submission requirement), section numbering matches outline | Same |
| References section | 40 MDPI-numbered entries with DOIs, hanging layout, no dangling numbers | 8 entries |
| Rasterized math | None — only page-1 logo images exist (4); all math is vector text | Same |
| Overfull boxes (`main.log`) | 2.09pt / **17.51pt (visible collision — fixed, Section 3)** / 1.43pt; post-fix 2.09/2.48/1.43 (all invisible) | 0 |

## 3. Defect found and fixed (recorded mechanical build fix MF-01)

**Defect (major, visual):** Table 1 (`tab:family-review`, p4), row
ATMALS-GSK: the citation `[10]` overprinted the adjacent column's
"Gaussian" ("[1Ǥaussian" collision), because `\atmals{}~\cite{...}` cannot
break at the `~` tie inside the `p{1.7cm}` Variant column (17.51pt overfull
> 12pt intercolumn gutter). Verified by 300 dpi zoom render.

**Fix:** `papers/sections/related_work.tex` line 158 — `~` tie → breakable
space (1 character; zero content change; no word/number/citation/claim
altered). `[10]` now wraps to line 2 of the cell; 300 dpi re-render clean.
Logged in `latex_build_report.md` ("Recorded mechanical build fix") and
`word_build_report.md` Section 7 item 7.

**Rebuilds + re-validation after the fix:**
- `DT-GSK.pdf` rebuilt (SOURCE_DATE_EPOCH=1783468800): 34 pp, 920,977 B,
  raw sha256 `9ff72733…614cef`; two consecutive rebuilds **byte-identical**.
- `DT-GSK.docx` rebuilt: 3,058,600 B, sha256 `5517b631…18844a`; two
  consecutive rebuilds **byte-identical**; `supplementary.docx`,
  `supplementary.pdf`, `word/field_registry.csv`, `word/reference.docx`
  byte-identical to their recorded hashes (fix does not reach them).
- Validators re-run green: `validate_docx.py` PASS 33/33 (both),
  `validate_cross_format_parity.py` 417 rows / 0 FAIL,
  `validate_evidence_bindings.py` 721/721 tokens found in both formats.
- Independent structural QA re-run post-rebuild: all counts unchanged
  (Section 5).

## 4. DOCX findings (both documents)

| Check | DT-GSK.docx | supplementary.docx |
|---|---|---|
| Caption placement | Tables 1–10: "Table N." caption paragraph immediately before each `w:tbl`; 14 figures: "Figure N." immediately after each drawing; abbreviations table correctly uncaptioned (intro sentence above) | A1–A14 captions before tables; B1–B20 captions after figures |
| Heading structure | Headings 1–3 styled, cached numbers, TOC field `TOC \o "1-3" \h \z \u` + `w:updateFields` | Same |
| References | Heading + 40 entries in `Bibliography` style, numbered identically to PDF | 8 entries |
| Equation rendering | 607 `m:oMath`, 0 equation images (14 media = 14 canonical `\includegraphics`, all PNG figures) | 172 / 0 (20 = 20) |
| Algorithm 1 | 26 `Algorithm Line` paragraphs, numbered 1–26, monospace | — |
| Table A14 reconciliation | — | Rank-CI table matches PDF exactly (spot: "GSK 5.52 [4.88, 6.02]…" via round-trip) |
| Terminology | 0 residual `EGSK`/`FDBAGSK` tokens; `eGSK` ×65 | 0; `eGSK` ×27 |
| GenAI block | Renders (see Section 6) | Correctly absent (back matter is main-paper-only in BOTH formats — consistent) |

## 5. Gate 9 hard-failure checklist (independent verification, post-fix)

| Hard failure | Result | Independent evidence |
|---|---|---|
| Rasterized math (equation images) | **NONE** | Media census: 14/20 PNGs = figure count exactly; no formula/eq/OLE-named media; 0 `w:object`/OLEObject; PDF body pages contain 0 images (only p1 logos) |
| Image tables | **NONE** | 11/14 real `w:tbl` elements; every PDF table extracts as text |
| Static required fields w/o justification | **NONE** | 270/66 complex fields all live with cached results (0 missing caches); sole static element = References list, justified in `word_validation_report.md` Section 1 with customXml `b:Sources` (40/8) preserving regenerability |
| Broken cross-references | **NONE** | All 146+21 REF targets present in bookmark sets (independent walk); bookmarks paired 141/141, 86/86, 0 duplicates, 0 Word-illegal names |
| PDF/Word content divergence | **NONE** | cross_format_consistency.csv: 417 rows = 380 PASS + 37 PASS_FORMAT_DIFF, 0 FAIL; every FMT_DIFF row inspected — all are the four recorded intentional classes (TOC existence, heading-number typography, semantic-precision tables, OMML-vs-glyph extraction) |
| Ablation content | **NONE** | 0 hits for ablation/ablat/phase_12_placeholder/do-not-release over every XML part of both DOCX packages and both PDFs' full text; S6 renders nowhere (outline ends at S5; no `S6` line in any format) |

## 6. AG-0007 — GenAI disclosure (Phase 8 hand-off) — VERIFIED, placement judgment recorded

- **Renders in both formats:** PDF p31 carries the dedicated block "**Use of
  Generative Artificial Intelligence.**" (methods-level HOW: evidence-locked
  pipeline, AI designed no experiments / produced no data / computed no
  statistics) followed by "**Acknowledgments:** … Claude Fable 5
  (Anthropic) …". The DOCX carries both blocks with identical text (pandoc
  round-trip spot-read). The supplement carries neither, in both formats —
  consistent (back matter belongs to the main paper).
- **MDPI-placement judgment:** MDPI policy (AG-0007 register row, verified
  2026-07-10) requires (i) declaration at submission, (ii) a methods-level
  HOW description, (iii) tool name/version in Acknowledgments. (i) is in the
  rewritten cover letter (final sentence of the confirmation paragraph);
  (iii) is in Acknowledgments with tool + vendor. For (ii): this manuscript
  has no Materials-and-Methods section (algorithms-paper structure), so the
  HOW description is placed as a dedicated back-matter declaration block
  between Data Availability and Acknowledgments — the position MDPI's
  template uses for declaration statements. Judged **compliant placement**;
  folding it into Section 4 would misplace pipeline-disclosure prose inside
  experimental content. AG-0007 remains formally open in the register only
  for author sign-off (drafted-unconfirmed), an author-side item.

## 7. R-0004 — cover letter — VERIFIED RESOLVED (pending author review)

- `papers/cover_letter.tex`/`.md` rewritten 2026-07-11 for *Algorithms*
  (MDPI): addressee "Editorial Office, Algorithms (MDPI)"; scientific core
  bound to CL-02 wording (2.48-of-7 descriptive aggregate, eGSK 2.96
  second), C1–C4 contribution scopes, family-panel-only claims; GenAI
  submission declaration included; suggested reviewers left as AUTHOR-FILL
  (no fabricated names).
- `papers/cover_letter.pdf` rebuilt from the new source (2 pp; text
  extraction confirms Algorithms/MDPI, zero SWEVO mentions).
- Stale letter neutralized: retained only as
  `papers/cover_letter_STALE_swevo.pdf` (audit copy, clearly labeled).
- `papers/governance/risk_register.csv` R-0004 row updated: mitigation
  records the 2026-07-11 rewrite; status `resolved-pending-author-review`.

## 8. Integrity sampling (P9)

- **15 numbers** sampled from the frozen `.tex` across
  introduction/proposed-algorithm/performance/conclusions/supplement
  (2.48; 2.96; 150,000; 1,000,037; 2,147,483,646; 10^-8; 0.137; 42.40;
  2.88; 3.29; 11–2–16; 9.5×10^-3; 5D; 10,000 [n_boot]; 20260422; 1.673
  [supp]): **all found identically in the DOCX** (normalized for `{,}`,
  unicode minus, OMML spacing) and cross-confirmed in the tex source.
- **10 citations** (mohamed2020gaining[5], awad2016problem[1],
  mohamed2020agsk[6], apgsk2021[7], fdbagsk2023[8], jawad2024egsk[9],
  alfadli2025atmals[10], tanabe2013shade[21], omidvar2014dg[22],
  hansen2001cmaes[23]): for each, the frozen `main.aux` number matches the
  cached `[n]` of every corresponding CITATION field in the DOCX, the tag
  exists in the customXml `b:Sources` store, and reference-list entry *n*
  opens with the correct first author (round-trip check); PDF list spots
  [5]/[9]/[10] agree. **10/10 PASS.**

## 9. Recorded observations (not Gate 9 failures)

1. **D-WORD-01 stays open** (documented deviation): Microsoft Word is not
   available here; final Word-open validation (field refresh, TOC pages,
   CITATION re-render form) is required before submission.
2. **Native-table headers** show verbatim semantic identifiers in the DOCX
   (e.g. `D10_MeanRank` vs PDF `D10`) and full semantic precision — the
   recorded word_sources convention (parity CSV `PASS_FORMAT_DIFF`).
   A Word reader sees more verbose headers than the PDF reader; acceptable
   per the mandated semantic-source behavior.
3. **Typography close-out pending by design**
   (`phase_09/docx_typography_requirement.md` orders it AFTER the Phase 9
   workflow reports): `word/reference.docx` already uses the locked
   Palatino Linotype 10 pt body + 9 pt captions, but Title/Heading sizes
   (16/12/10.5/10 bold) do not yet match the mdpi.cls-exact spec
   (18 pt title; 10 pt bold/italic/regular headings; justified Normal), and
   the DOCX→PDF export comparison has not run. Out of Gate 9 scope; must be
   executed with a further DOCX rebuild + re-validation before Phase 11.
4. `word_citation_tag_map.csv` staleness for `awad2016problem`
   (CR-0005/D-0009 override recorded in `word_build_report.md` Section 8) —
   governance-file update belongs to its owner.
5. Benign residual overfulls (2.09/2.48/1.43pt) sit inside the intercolumn
   gutter/margin tolerance and are invisible at 300 dpi.
