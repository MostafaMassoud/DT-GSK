# Phase 11 — Final Primary Integrity Audit

- **Phase:** 11 (Primary manuscript finalization + pre-ablation freeze)
- **Date:** 2026-07-11
- **Evidence release (immutable):** `rel-2026-07-10-262fc16c9`
- **Anchor / core-source freeze:** Phase-3 `algorithm_freeze_manifest.json`
- **Artifacts audited (all re-built clean this phase):**
  `papers/DT-GSK.pdf`, `papers/supplementary.pdf`, `papers/DT-GSK.docx`, `papers/supplementary.docx`
- **Overall verdict:** **PASS** — all nine categories PASS; zero FAIL. No blocker.
  Two major figure-label defects (R4-T1/T2) remain **deferred-non-blocking** (pre-rendered
  checksum-bound assets; scheduled for the post-Phase-12 figure-refresh) per Gate-10 change control.

## 0. Build reproducibility (determinism precondition)

Clean-aux rebuild under the determinism contract (`PYTHONIOENCODING=utf-8`;
`SOURCE_DATE_EPOCH=1783468800` for PDF, `1783641600` for DOCX). Every artifact reproduced the frozen
Phase-9/10 byte size exactly:

| Artifact | Pages | Bytes | Frozen bytes | Match |
|---|---|---|---|---|
| `DT-GSK.pdf` | 35 | 928,688 | 928,688 | byte-identical |
| `supplementary.pdf` | 32 | 889,540 | 889,540 | byte-identical |
| `DT-GSK.docx` | — | 3,061,644 | 3,061,644 | byte-identical |
| `supplementary.docx` | — | 12,837,665 | 12,837,665 | byte-identical |

`main.log`: 0 undefined references, 0 undefined citations, 0 multiply-defined labels, 0 missing files,
2 benign overfull `\hbox` (2.48pt/2.09pt/1.43pt class, MF-01 already applied). `supplementary.log`: all
zero. (Supplement PDF hit the documented environmental viewer-lock on the pre-existing file — resolved
by the Phase-9 rename-aside procedure; not a script defect.)

## 1. Category verdicts

| # | Category | Verdict | Evidence |
|---|---|---|---|
| 1 | Citations (subset of 57) | **PASS** | §2 |
| 2 | Claims (ACCEPTED/NARROWED/READY; none PENDING) | **PASS** | §3 |
| 3 | Numbers bind to `rel-2026-07-10-262fc16c9` | **PASS** | §4 |
| 4 | Source-only (no `results/` leak) | **PASS** | §5 |
| 5 | Equations / pseudocode / code correspondence | **PASS** | §6 |
| 6 | Tables / figures bound | **PASS** (figure-label cosmetics deferred, non-blocking) | §7 |
| 7 | Cross-format consistency (`validate_cross_format_parity.py`) | **PASS** | §8 |
| 8 | Word native fields (`validate_docx.py`) | **PASS** | §9 |
| 9 | Journal compliance | **PASS** | §10 |

## 2. Citations — PASS

- Compiled bibliographies: `main.bbl` = **40** `\bibitem` entries, `supplementary.bbl` = **8**.
- Both are a strict subset of the 57-key admissible pool (`allowed_citation_keys.txt`, 57 keys):
  `main.bbl subset=True extras=[]`; `supplementary.bbl subset=True extras=[]`.
- 0 undefined citations in either log; `main.blg` 40 entries / `supplementary.blg` 8 entries with 0
  real BibTeX warnings (the lone `warning$` grep hit is a `.bst` function name, not a warning).
- Consistent with Gate-10 "40/40 in-build ⊆ 57-key pool, usage-map symmetric."

## 3. Claims — PASS

`claims_evidence_matrix.csv` (50 rows) `status` distribution:

| Status | Count |
|---|---|
| READY | 29 |
| ACCEPTED_PHASE_6 | 16 |
| NARROWED_PHASE_6 | 2 |
| DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY | 3 |
| **PENDING / BLOCKED** | **0** |

Every claim is READY, ACCEPTED, or NARROWED; the only deferrals are the 3
`DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY` ablation claims (S6, Phase-12 scope) — legitimately deferred,
not PENDING. Matches Phase-6 adjudication (16 ACCEPTED + 2 NARROWED + 0 BLOCKED, 0 PENDING).

## 4. Numbers bind to the release — PASS

- `validate_evidence_bindings.py`: the full sampled set returns `[PASS] … pdf=yes docx=yes` for every
  probed number (exit 0), across main and supplement, each traced to a named analysis id / bound source
  (e.g. `AN-RANKAGG-2017-OVERALL`, `AN-OMNI-2013-D30`, `TAB-T16-BCA`, `PR-02/PR-04`).
- Spot-bound headline values, all present in the rendered PDF and unchanged from the release:
  CEC2017 overall Friedman mean rank **2.48** of 7 (RS-01 NARROWED, `% BIND`);
  eGSK D30 **3.07**; CEC2011 second; Nemenyi non-separable; per-run cost 8.69/0.55.
- Byte-identical rebuild (§0) is the strongest possible evidence that no bound number moved.
- Release id `rel-2026-07-10-262fc16c9` is unchanged (config Section 5).

## 5. Source-only (no `results/` leak) — PASS

- Rendered-text scan of both PDFs: **no** `results/_ablation`, `results/_analysis`, `results/_run_all`,
  `results/dt-gsk`, `results/ablation`, `D:/AI`, or `/home/` string in either PDF.
- Shipped `.tex` sources reference `results/` only in:
  (a) `performance.tex:139` — a `% BIND` **comment** (not rendered) pointing to the *immutable*
  `benchmarks/cec_reference_results/` tree (correct provenance, not staging); and
  (b) `supplementary.tex:920` — **intentional prose** describing the promotion rule ("new … runs land
  in the `results/` staging area, which is never citable; staging data enters evidence only through …
  `scripts/promote_evidence.py`"). This is the reproducibility-discipline statement, not a data leak.
- The only file carrying real `results/…` data paths, `sections/supplementary_content.tex`, is an
  **unbuilt orphan**: `supplementary.tex` does **not** `\input` it and `main.tex` inputs only
  `sections/{introduction,related_work,proposed_algorithm,performance,conclusions}`. It renders in no
  shipped artifact (re-confirmed this phase).

## 6. Equations / pseudocode / code correspondence — PASS

- **Frozen core source SHA-256 (first 16 hex) vs Phase-3 freeze manifest — all MATCH:**
  `dt_gsk.py` a274e0f83b4efd3c · `_dt_core.py` 1ef815cee5d4c9c3 · `_dt_profiles.py` c3dcdce3a3477dca ·
  `_dt_rng.py` db1cc028b3ebc145. The frozen algorithm is byte-identical to the Phase-3 freeze.
- `validate_profile_lock.py --root .`: **passed for 3 configs** (byte-identity of the pub profile).
- `pytest -q`: **339 passed** (includes the byte-stability KAT `test_dt_gsk_byte_stable` and the
  profile oracle `test_dt_profiles`), 2 benign warnings (a `dim=4` test-only block-size fallback).
- Equation↔pseudocode↔code agreement was proven at Gate 3 (16 mechanisms traced to executing code, a
  live fixed-seed deterministic trace); nothing in the frozen canon changed since, so the
  correspondence holds. **Note (cosmetic, deferred):** the *conceptual figures* mislabel equation
  numbers (R4-T1) — an asset-label defect, not a body equation/code defect; the manuscript equations
  and pseudocode themselves are correct.

## 7. Tables / figures bound — PASS

- `artifact_binding.csv`: **55** exhibit rows, each with `source_checksums` + `output_checksum` SHA-256
  chains to the immutable release.
- `validate_cross_format_parity.py` table checks: `table_pdf_spot` PASS (main 3, supplement 14);
  `table_generated`/`table_value_precision` show only non-failing `FMT_DIFF` (format-only), 0 FAIL.
- Phase-7 value-level validation (4349 comparisons, 0 unexplained mismatch; 135 automated figure QA
  checks, 0 findings) stands unchanged under the byte-identical rebuild.
- **Deferred-non-blocking:** figure-label cosmetics (R4-T1 equation labels, R4-T2 raw BibTeX keys,
  R4-T3 repo paths, R4-T4 SGSM alias, R4-T6 CD-diagram titles) are pre-rendered checksum-bound assets
  scheduled for the post-Phase-12 figure-refresh (see `residual_ticket_disposition.md`). The bound
  *values* are correct; only baked labels are affected.

## 8. Cross-format consistency — PASS

`validate_cross_format_parity.py --doc both`: **TOTAL rows = 423, FAIL = 0** (exit 0). Residual
`FMT_DIFF` rows (TOC, equation_display, table_generated, heading-number typography) are expected
format-representation differences, not content failures. No-ablation scan PASS on both PDFs.

## 9. Word native fields — PASS

`validate_docx.py` reports `"ok": true` on both documents:

| DOCX | oMath | oMathPara(img) | tables | images/alt | fields | markers_left |
|---|---|---|---|---|---|---|
| `DT-GSK.docx` | 607 | 0 | 12 | 14 / 14 | 274 | 0 |
| `supplementary.docx` | 172 | 0 | 14 | 20 / 20 | 66 | 0 |

All equations native OMML (0 equation images), all tables native `w:tbl`, alt text on every image, all
SEQ/REF/CITATION/TOC fields balanced, 0 unresolved markers, 0 warnings.

## 10. Journal compliance — PASS

- **Venue wiring:** `\documentclass[algorithms,article,submit,moreauthors,pdftex]{Definitions/mdpi}`
  (main.tex line 9; shifted from the Phase-0/4 "line 5" only by Phase-8 header comments — journal
  option `algorithms` and the vendored `Definitions/mdpi.cls` are unchanged). MDPI *Algorithms* is
  FROZEN at Phase 4 (D-0010); no change request has re-opened the venue (see
  `journal_reverification_note.md`).
- **Page budget (Section 1.5 / `page_budget.md` §8 gate condition `B1 ≤ 34`):**
  total PDF **35 pp**; references occupy pp.33–35, back matter (Author Contributions, Funding, Data
  Availability, Acknowledgments, Conflicts of Interest) occupies lower p.32–p.33; **B1 (main text +
  exhibits, EXCLUDING references and back matter) = 32 pp ≤ 34 hard cap → PASS** (2 pp headroom). The
  +1 vs the Phase-8/9 measurement (34 pp total / B1 31) is entirely the **frozen Phase-10** additions
  (Table 11 CEC2013 Friedman + Limitations Sixth/Seventh + statistical-protocol sentences), not a
  Phase-11 change. Supplement **32 pp** (unchanged).
- **Abstract:** ~197–199 words ≤ 200 MDPI cap.
- **No ablation** in either format (S6 renders nowhere; ablation-token scan clean in both PDFs and via
  `validate_docx` no-ablation guard).
- **Required sections present:** Abstract, Keywords, Introduction, Methods (Proposed DT-GSK),
  Results (Experimental Study), Conclusions, Author Contributions, Funding, Data Availability,
  Conflicts of Interest, References.
- **Residual (author-side, non-blocking):** `verified_online = false` (official Instructions page
  returned HTTP 403 to the automated fetcher on 2026-07-10). Live-page re-verification of the
  length/style/figure rules is an explicit author pre-submission step; it does not block content
  freeze.

## 11. Word open-save-open validation — D-WORD-01 (author-side deferral)

`validate_docx.py` (static/programmatic validation) PASSES on both DOCX. Microsoft Word is unavailable
in this non-interactive environment, so the **open-in-Word → update fields → Save-As → re-open**
round-trip (and the DOCX→PDF typography-match export) remains the documented **Gate-9 exception
D-WORD-01**, owned by the author at pre-submission. Recorded, not attempted here.

## 12. Sign-off summary

All nine integrity categories PASS with zero FAIL; the frozen algorithm, evidence release, and every
bound number are intact and byte-reproducible; deferred residuals are change-controlled and
non-blocking. The manuscript is integrity-clean for the Phase-11 pre-ablation freeze.
