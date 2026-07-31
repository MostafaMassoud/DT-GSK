# Phase 11 — No-Ablation Prohibition Scan (Task 10)

**Phase / task:** Phase 11, task 10 (PAPER_BUILD_PROMPT.md §Phase 11) — prove that
no ablation content of any kind is rendered in the shipped primary artifacts before
the Phase-12 ablation is authorized.

- **Anchor commit:** `cffcbb48153fd6395c67bb35ece0107269c15694`
- **Evidence release in force:** `rel-2026-07-10-262fc16c9`
- **Scanner:** `scratchpad/phase11_scan.py` (PyMuPDF `page.get_text` = pdftotext-equivalent
  for PDFs; `zipfile` over every `word/*.xml` stream for DOCX; UTF-8 read for `.tex`).
- **Token set (case-insensitive regex):** `ablation | X-ABL | no_ace | scaffold cell |
  component contribution`.
- **Surfaces scanned:** `DT-GSK.pdf`, `supplementary.pdf` (rendered text); `DT-GSK.docx`,
  `supplementary.docx` (all `word/*.xml` streams — body, headers, footers, foot/endnotes);
  `main.tex` + the five built section sources + `supplementary.tex`; all `tables/*.tex`
  captions; `cover_letter.tex` + `cover_letter.pdf`.

---

## Verdict — PASS: ZERO rendered ablation-content hits

**No ablation number, rank, p-value, effect size, cell result, component-efficacy claim,
or component-causality claim is rendered in any shipped artifact.** The only permitted
source-comment hit (the reserved S6 slot) is present and renders nothing. All other token
occurrences are either (a) governance disclaimers that *disavow* component attribution,
(b) source-only `% No ablation content` provenance comments, or (c) inside the **unbuilt
orphan** `sections/supplementary_content.tex`, which is not `\input` by any build root and
therefore renders nowhere.

---

## 1. Rendered artifacts (the binding surfaces)

| Rendered artifact | Token hits | Adjudication |
|---|---:|---|
| `DT-GSK.pdf` | 1 | **Disclaimer, not ablation content** (see §1.1) |
| `supplementary.pdf` | 0 | clean |
| `DT-GSK.docx` | 1 | **Same disclaimer sentence** as the PDF (see §1.1) |
| `supplementary.docx` | 0 | clean |
| `cover_letter.pdf` | 0 | clean |

### 1.1 The single rendered token occurrence is a required *negation* (IN-02 permitted wording)

Both rendered hits (`DT-GSK.pdf` and `DT-GSK.docx`) are the **same frozen sentence** in
Section 4 (from `sections/performance.tex`, `% BIND: IN-02 permitted wording`):

> "… it is stated here as plausibility, **not as a measured component contribution** — the
> mechanisms of Section 3 are proposed and fully specified, and per-component causal
> attribution is **deliberately not claimed** in this paper."

This is the opposite of ablation content: it is the manuscript **explicitly disavowing** any
measured component contribution and deferring per-component causality. The regex over-matches
the bigram "component contribution" inside a negation. Under the substantive test — *does any
ablation result, number, or component-efficacy/causality claim render?* — the count is **zero**.
This disclaimer is mandated by the claims matrix (IN-02) and by
`ablation_correction_triggers.md` G0 (the shipped text must contain zero component-causality
statements so no Phase-12 result can retroactively justify a claim). Its presence is a
compliance signal, not a violation.

---

## 2. Source-only occurrences (not rendered — informational)

| Source file | Hits | Nature |
|---|---:|---|
| `main.tex` | 1 | `% … no ablation …` provenance comment (LaTeX comment; not typeset) |
| `sections/introduction.tex` | 1 | `% … No ablation content …` comment |
| `sections/related_work.tex` | 1 | `% … No ablation content.` comment |
| `sections/proposed_algorithm.tex` | 1 | `% NO ablation content; component causality deferred …` comment |
| `sections/conclusions.tex` | 1 | `% … No ablation content …` comment |
| `sections/performance.tex` | 2 | one `% … No ablation …` comment; one is the §1.1 rendered disclaimer body line |
| `sections/literature_review.tex` | 0 | clean |
| `supplementary.tex` | 2 | line 2 `%% … non-ablation supplement …` comment; **line 947 the reserved S6 comment** |
| `tables/*.tex` | 0 | clean |
| `cover_letter.tex` | 0 | clean |

All `.tex` hits above except the §1.1 disclaimer body line are LaTeX **comments** (`%`-prefixed),
which are never typeset. They are governance provenance markers asserting the absence of ablation
content, and are themselves evidence of the discipline.

### 2.1 Reserved S6 slot — the sole *permitted* placeholder (renders nothing)

`supplementary.tex` lines 947–954 is a pure-comment reserved block:

```
% S6 -- RESERVED (ablation study).
% PHASE_12_PLACEHOLDER - DO NOT RELEASE
% … no heading, no text, and no exhibit in any released build. …
% BIND: AB-01; AB-02; AB-03 (all DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY)
```

Every line is `%`-commented → **renders nothing** (confirmed: `supplementary.pdf` and
`supplementary.docx` scans returned 0 hits). This is the single permitted hit per the task
specification and matches the Phase-12 insertion point recorded in
`pre_ablation_supplement_freeze_manifest.json`.

---

## 3. The orphan `sections/supplementary_content.tex` (renders NOWHERE)

`sections/supplementary_content.tex` contains ~30 token occurrences (a 16-cell scaffold
ablation, a 4-cell SGSM overlay, `results/ablation/…` paths, "scaffold cell", etc.). **It is an
unbuilt orphan:** `grep supplementary_content papers/main.tex papers/supplementary.tex`
returns **nothing** (exit 1) — no build root `\input`s it. This is the same file three Phase-10
reviewers mistakenly opened (revision tickets → REJECTED-INVALID; the *shipped* supplement is
`supplementary.tex`, which is compliant). Because it is never compiled, **none of its ablation
content reaches any released PDF or DOCX.** It carries no `X-ABL`/AB binding to the shipped
build and is scheduled for disposition inside Phase 12.

---

## 4. Reproduction

```
cd D:/AI/PhD-Projects/00-GSK-Family/02-GSK_Family_Python_v1.1
PYTHONIOENCODING=utf-8 python scratchpad/phase11_scan.py
```

**Result:** rendered PDFs/DOCX contain **zero** ablation-content hits (the two token
occurrences are the single IN-02 disavowal sentence); the reserved S6 comment is the only
permitted source-comment hit; the orphan `supplementary_content.tex` renders nowhere.
**Scan verdict: PASS (no blocker).**
