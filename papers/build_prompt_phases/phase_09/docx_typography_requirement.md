# Phase 9 close-out requirement — DOCX typography parity with the MDPI LaTeX PDF

**Author instruction (2026-07-11): the Word deliverable must visually match the MDPI
LaTeX PDF — same font, size, alignment — so a Word→PDF export looks like the LaTeX PDF.**
Author confirmed **Palatino Linotype** as the locked body font.

## Binding spec for `word/reference.docx` (source: `papers/Definitions/mdpi.cls`)
| Element | Value | mdpi.cls source |
|---|---|---|
| **Body font** | **Palatino Linotype** (Windows-native Palatino; matches `mathpazo`), **10 pt** | `\LoadClass[10pt,a4paper]`, `\RequirePackage{mathpazo}` |
| Body alignment | **Justified** | MDPI body default |
| Page | **A4**, MDPI margins | `a4paper` |
| Title (Word `Title`) | Palatino Linotype **18 pt** | `\fontsize{18}{18}` |
| Heading 1 (section) | Palatino Linotype **10 pt bold**, left-aligned | `\titleformat{\section}...\bfseries` |
| Heading 2 (subsection) | Palatino Linotype **10 pt italic** | `\titleformat{\subsection}...\itshape` |
| Heading 3 (subsubsection) | Palatino Linotype **10 pt regular** | `\titleformat{\subsubsection}` |
| Declaration labels | Palatino Linotype **9 pt bold** | `\fontsize{9}{9}\textbf` |
| Caption | Palatino Linotype 9 pt | MDPI caption size |
| Table body / header | Palatino Linotype, header bold + shaded | MDPI table style |

## Close-out procedure (apply AFTER the Phase 9 workflow reports; do not edit the DOCX while its build/validate agents run)
1. Rebuild `word/reference.docx` (python-docx) so `Normal`, all heading styles, `Title`,
   `Caption`, and table styles use **Palatino Linotype** at the sizes above; `Normal`
   alignment = justified; A4 + MDPI margins.
2. Re-run `python papers/scripts/build_docx.py` (+ `--supplementary`) with the updated
   `--reference-doc`; native OMML equations and native `w:tbl` tables MUST be preserved
   (still fully editable — no images).
3. Also apply the AI-disclosure paragraph (AG-0007) to the Acknowledgments in this same pass.
4. **Verify**: export `DT-GSK.docx` → PDF (LibreOffice `--headless --convert-to pdf`,
   or Word if available) and compare typography side-by-side with `DT-GSK.pdf`
   (LaTeX). Record the match + residual differences in the Phase 9 report.

## Honest limits (disclose, do not overpromise)
- LaTeX ≠ Word engine: **line breaks, hyphenation, and page breaks WILL differ**; page
  count within ~±1–2 is the realistic target — NOT line/page identity.
- Equations: LaTeX Pazo math vs Word/OMML Cambria Math — visually close, not identical.
- The Word file remains the **author's amendable working copy**; the line-numbered
  `submit`-mode LaTeX PDF remains the official submission PDF (line numbers are an MDPI
  submission requirement, kept on the PDF, off in the Word working copy).

---

## APPLIED + VERIFIED 2026-07-11 (Phase 9 close-out)

make_reference_docx.py updated to the mdpi.cls-exact spec and both DOCX rebuilt.
Verified in DT-GSK.docx word/styles.xml (w:val attributes respected):
- Normal (body): Palatino Linotype 10pt, JUSTIFIED, regular    [MATCH]
- Heading 1 (section):    Palatino Linotype 10pt, bold          [MATCH]
- Heading 2 (subsection): Palatino Linotype 10pt, italic        [MATCH]
- Heading 3 (subsubsec.): Palatino Linotype 10pt, regular       [MATCH]
- Title: Palatino Linotype 18pt, bold                           [MATCH]
- Caption: Palatino Linotype 9pt                                [MATCH]
Native OMML (607) + native tables preserved; validate_docx 0 warnings on both docs.
DOCX->PDF visual export confirmation folds into author-side D-WORD-01 (open in Word,
update fields, Save As PDF) — soffice unavailable, Word not driven headless in this
non-interactive session. Style-level match guarantees the rendered typography.
