# Phase 9 — Dual-Format LaTeX/PDF and Native Microsoft Word Production — Gate Report

- **Phase:** 9 (PAPER_BUILD_PROMPT.md lines 4901–5204)
- **Gate date:** 2026-07-11
- **Verdict:** **APPROVED — Phase 9 FROZEN**
- **Signatories:** P5 + P6 + P7 + P8 + P9 (framework Gate 9 quorum)

## 1. The four deliverables
| File | Format | Measure |
|---|---|---|
| `papers/DT-GSK.pdf` | LaTeX PDF (submit mode) | **34 pp**, 0 undefined refs/cites, vector math, line-numbered for review |
| `papers/supplementary.pdf` | LaTeX PDF | **32 pp**, standalone, S6 not rendered |
| `papers/DT-GSK.docx` | native Word | **607 OMML equations, 0 equation images**; 11 native tables; 270 live fields; fully editable |
| `papers/supplementary.docx` | native Word | 172 OMML, 14 native tables, 66 fields |
| `word/reference.docx` | Word template | **Palatino Linotype 10 pt justified, MDPI-exact styles** |
| `papers/cover_letter.{md,tex,pdf}` | cover letter | **rewritten for MDPI Algorithms (R-0004 resolved)** |

## 2. Native Word production (Gate-9 hard requirements met)
- **Zero rasterized math** (607+172 native `m:oMath`), **zero table images** (11+14 native
  `w:tbl` from semantic sources); all captions editable.
- **Live fields**: SEQ 38+35, REF 146+21 (every target bookmark resolves), CITATION 85+9
  (cached `[n]` identical to the frozen `.bbl`, MDPI numbered order), TOC 1+1 update-on-open;
  141+86 Word-legal bookmarks; 40+8 `customXml b:Sources` entries; 14+20 images with alt text.
- **Tooling built**: `_word_ooxml.py`, `make_reference_docx.py`, extended `build_docx.py`
  (`--supplementary`, `--reference-doc`, OOXML post-processor), and the three D.6 validators
  (`validate_docx.py`, `validate_cross_format_parity.py`, `validate_evidence_bindings.py`).

## 3. Validation
- `validate_docx.py`: **33/33 checks PASS** on both DOCX (0 warnings after typography rebuild).
- `validate_cross_format_parity.py`: **417 artifact rows — 0 FAIL** (380 PASS + 37 recorded
  intentional format-only differences) → `cross_format_consistency.csv`.
- `validate_evidence_bindings.py`: **721/721 `% BIND` numeric tokens found identically in
  both PDF and DOCX**; 0 FAIL.
- **Determinism**: two consecutive rebuilds byte-identical with `SOURCE_DATE_EPOCH` set
  (normalized-content contract, Section 9.4).
- **No-ablation scan**: clean in both formats; S6 renders nowhere.

## 4. Author-requested typography (DOCX ↔ PDF visual match)
Applied the **mdpi.cls-exact** typography to `word/reference.docx` and rebuilt both DOCX;
verified in `styles.xml`: body **Palatino Linotype 10 pt justified**, H1 10 pt bold,
H2 10 pt italic, H3 10 pt regular, Title 18 pt bold, Caption 9 pt — all MATCH
(`docx_typography_requirement.md`). Native equations/tables preserved (still editable).
Honest limit recorded: LaTeX≠Word engines, so line/page breaks differ; typography and look
match, not pixel/line identity.

## 5. R-0004 resolved
Cover letter rewritten for **Editorial Office, Algorithms (MDPI)**; scientific core bound to
CL-02 + C1–C4 scopes + the family-panel bound; originality/no-simultaneous-submission +
AG-0007 GenAI sentence; suggested reviewers = author-fill placeholder; stale SWEVO letter
renamed `cover_letter_STALE_swevo.pdf`. Risk register R-0004 →
`resolved-pending-author-review`; claims CL-01 → READY.

## 6. Adversarial QA and resolution
**PASS — 0 critical; 1 major fixed; 3 minor resolved/deferred:**
- ~~Table 1 `[10]`↔"Gaussian" glyph collision (17.5 pt overfull)~~ → 1-char breakable-space
  fix MF-01, re-rendered clean.
- Typography close-out → **applied + verified this pass** (§4).
- `word_citation_tag_map.csv` stale `awad2016problem` row → **updated to admissible=yes**
  (CR-0005 / D-0009).
- **D-WORD-01 (documented Gate-9 exception)**: Microsoft Word unavailable in this
  non-interactive environment → the prescribed open-save-open validation + the DOCX→PDF
  visual export are an **author-side pre-submission step** (open both DOCX in Word, allow
  update-fields-on-open, verify TOC/SEQ/REF/CITATION, Save As PDF). Recorded in
  `word_validation_report.md` per the Gate-9 static/fallback exception clause.

## 7. Sign-off
- **P5:** APPROVED — deterministic builds, normalized-content hashes, both formats.
- **P6:** APPROVED — wording/structure equal across formats.
- **P7:** APPROVED — PDF build quality; MF-01 collision fixed.
- **P8:** APPROVED — DOCX fully editable, native OMML/tables, MDPI typography; D-WORD-01
  author step documented.
- **P9:** APPROVED — citation + number integrity identical across formats (721/721).

**Gate 9 APPROVED. Phase 9 FROZEN 2026-07-11.** Any later content revision requires
rebuilding and revalidating both formats. Phase 10 (adversarial review) unblocked.
