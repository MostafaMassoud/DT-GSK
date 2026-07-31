# CR-0006 Stage 3 — Rebuild, Integrity Re-verification, and Re-freeze

**Change request:** CR-0006 (A2-004 apgsk CEC2017 D10/D30/D50 per-run data-loss correction).
**Governance:** `decision_log.md` D-0011 (2026-07-11); `change_request_register.csv` CR-0006 = **APPROVED (P1)**.
**Date:** 2026-07-11. **Determinism:** `PYTHONIOENCODING=utf-8`; `SOURCE_DATE_EPOCH=1783468800` (PDF), `1783641600` (DOCX).
**Toolchain:** MiKTeX pdflatex/bibtex; pandoc 3.9.0.2; Ghostscript 10.06.0; Python 3.10.11.

**Verdict: PASS.** Blast radius confined to apgsk CEC2017 D10/D30/D50 (+ shared provenance). All non-apgsk
outputs byte-identical. Both formats rebuild clean and validate. Main manuscript unchanged
(`main_text_changed = false`). Engineering green. The formerly disclosed-unavailable apgsk run-level cells now
carry real measured values in the released analysis bundle.

---

## 1. Rebuild — all four artifacts reproduced BYTE-IDENTICAL

Clean deterministic rebuild via the release-wired builders:

| Artifact | Builder | Epoch | Bytes | SHA-256 vs pre-CR | vs freeze manifest |
|---|---|---|---:|---|---|
| `papers/DT-GSK.pdf` | build_pdf.py | 1783468800 | 928,688 | **IDENTICAL** | MATCH (e6b2f42e…) |
| `papers/DT-GSK.docx` | build_docx.py | 1783641600 | 3,061,644 | **IDENTICAL** | MATCH (ce449b9a…) |
| `papers/supplementary.pdf` | build_supplementary.py | 1783468800 | 939,356 | **IDENTICAL** | n/a (Phase-12 ver.) |
| `papers/supplementary.docx` | build_docx.py --supplementary | 1783641600 | 12,952,965 | **IDENTICAL** | n/a (Phase-12 ver.) |

Every build exited 0. The rebuilt main PDF/DOCX match the Phase-11 freeze-manifest hashes exactly; the rebuilt
supplement matches its current (Phase-12) committed bytes exactly. Because the artifacts are byte-identical, a
rendered-text (pdftotext) diff is a fortiori empty.

**Page counts:** main `DT-GSK.pdf` = **35 pages total / B1 = 32 main-text pages (≤ 34 hard cap → PASS**, refs pp.33–35
+ back matter excluded); `supplementary.pdf` = 36 pages (Phase-12 ablation-appendix version; unchanged by CR-0006).

## 2. `main_text_changed = false`

No main-text `.tex` was edited. All eight frozen main-manuscript sources (`main.tex` + six sections +
`supplementary_content.tex`) and `references.bib`, `citation_usage_map.csv`, `artifact_binding.csv` re-verify
byte-identical to `main_manuscript_freeze_manifest.json`. The three main-text mentions of the apgsk gap remain
frozen and correct:

- **Runtime table `tab:runtime`** (`performance.tex` L754) still shows `\apgsk{} & d.u. & d.u. & d.u. & 47.11±14.43`.
  apgsk per-run **timing** at D10/30/50 stays d.u. in the manuscript ("no runtime-superiority claim is made").
- **Prose / captions** (`performance.tex` L114–121, L263–265, L685–686; `conclusions.tex` L111) keep the
  "disclosed-unavailable … function-level tests are the sole inferential basis" wording. Per the CR's no-upgrade
  rule, wording is left as-is; no claim is strengthened.

No main-text exhibit displays apgsk **run-level effect-size cells** (Table 16 shows function-level Friedman ranks;
the run-level FULL per-function tables are not built as `.tex`). Hence the d.u.→real correction reaches no built
exhibit.

## 3. Integrity verification

| Check | Result |
|---|---|
| Rebuilt main PDF/DOCX text diff vs pre-CR | **zero difference** (byte-identical) |
| `validate_docx.py DT-GSK.docx` | **ok** (0 FAIL) |
| `validate_docx.py supplementary.docx` | **ok** (0 FAIL) |
| `validate_evidence_bindings.py` | **PASS** — sampled numbers still bind in PDF **and** DOCX |
| `validate_cross_format_parity.py --doc both` | 455 rows, **2 FAIL** — both PRE-EXISTING Phase-12 ablation tables (SA01/SA02); see §5 |
| No-ablation scan (MAIN `DT-GSK.pdf` + `.docx`) | **clean** — 1 token hit each = the frozen IN-02 "component contribution" disavowal (PDF p.30), identical to Phase-11 |
| `pytest -q` | **339 passed** (2 pre-existing dim=4 warnings) |
| `ruff check .` | **All checks passed** |

**apgsk d.u.→real confirmed** in the released analysis bundle (supplement's data form), all apgsk / D10/D30/D50, e.g.
`effect_sizes_cec2017_D10.csv`: `apgsk,n/a,n/a,n/a,disclosed-unavailable` → `apgsk,51,5.0e-01,0.0e+00,negligible,ok`.

## 4. Blast radius (verified independently; matches CR-0006 register)

**Substantive DATA changes — confined to apgsk, CEC2017, D10/D30/D50** (D100 apgsk and all other suites unchanged):

- Run-level bundle CSVs `effect_sizes` / `wilcoxon_run` / `bca_ci` (D10/30/50) + `headline_bca` + `*_exploratory_bh`:
  **apgsk rows only** (0 non-apgsk changed lines).
- `cost_cec2017.csv`: apgsk runtime D10/30/50 d.u.→real (3.97 / 14.47 / 24.06); 0 non-apgsk.
- `robustness_cec2017_r02/r05/r06`: apgsk-driven; r02 floor-scan denominator +4437 = 29 funcs × 51 runs × 3 dims
  (apgsk D10/30/50 now in the pool); **verdicts unchanged**.
- `primary_stats/statistical_results.csv`: **627 substantive changes, 100% apgsk** (AN-EFF, AN-PWRUN, AN-EXP-BH,
  AN-DESC success-rate, AN-COST runtime). The ~8,000 apparent "non-apgsk" changed lines are multi-algorithm rows
  whose shared `source_checksums` list embeds the recovered apgsk file hash — after stripping the hash tokens, **0
  non-apgsk statistical results differ**.
- Provenance JSONs (`evidence_release_manifest`, `analysis_checksums`, `source_precheck`, `source_use_log` ×3,
  `run_manifest`, `environment_record`): refreshed to reflect the recovered source. cec2013/cec2011
  `source_use_log` changes are **run-timestamp only** (their reads/checksums are unchanged).
- `phase6_run_analysis.py`: Stage-1 engine change (static `APGSK_GAP_DIMS` skip → dynamic `per_run_absent()` gate).

**Unchanged / byte-identical:** `results/paper_tables/T*.csv`, all `papers/tables/*.tex` (21), `descriptive_stats_*`,
`class_ranks_cec2017.csv`, `artifact_binding.csv`, and the compiled manuscript + supplement documents.

Note (documented in CR-0006, RS-08/LM-04 evidence notes): the recompute also refreshed apgsk **success-rate**
(AN-DESC) and **runtime** (AN-COST) at D10/30/50 — broader than the three headline stats but all derived from the
same recovered `per_run.csv`, all apgsk, none reaching the frozen manuscript. See §5.

## 5. Findings / notes for the orchestrator

1. **Cross-format parity 2 FAIL is pre-existing, not CR-0006.** Both FAILs are `supplementary.docx` `table_generated`
   on `SA01 (Table A15)` and `SA02 (Table A16)` — the **Phase-12 ablation appendix** tables. The HEAD-committed
   `cross_format_consistency.csv` already records exactly these two FAILs with identical detail hashes
   (687b3743…, 7fe30bd3…). CR-0006 introduces **zero** new parity failures (the supplement is byte-identical to
   pre-CR). These belong to a separate Phase-12 workstream.

2. **Data↔manuscript divergence on apgsk runtime (by design).** `cost_cec2017.csv` now carries apgsk runtime at
   D10/30/50, while the frozen manuscript runtime table keeps `d.u.` This is the same completeness pattern as the
   effect sizes and is explicitly recorded in `claims_evidence_matrix.csv` LM-04 ("completeness correction only …
   no strengthening is licensed"). The manuscript wording is intentionally unchanged.

3. **Supplement freeze manifest note (deliberate deviation from a literal hash-overwrite).** CR-0006 does not modify
   the supplement documents. `pre_ablation_supplement_freeze_manifest.json` records the historical PRE-ablation
   supplement; its core_documents hashes were **deliberately preserved** (not overwritten with the current
   Phase-12 ablation-containing supplement), and a `cr_0006_refreeze` note was added instead. Overwriting them would
   have mis-attributed the Phase-12 delta to CR-0006 and destroyed the pre-ablation baseline.

## 6. Re-freeze actions

| Manifest | Action |
|---|---|
| `main_manuscript_freeze_manifest.json` | Manuscript artifacts byte-identical (no change). Re-hashed **only** `claims_evidence_matrix.csv` (1b7a9af2→e91e4356, 31237→32669 B; CR-0006 evidence notes on RS-07/08/09/LM-04). Added `cr_0006_refreeze` (`main_text_changed:false`). Self-verifies: all files MATCH. |
| `primary_freeze_manifest.json` | Re-hashed 6 provenance files (evidence_release_manifest, analysis_checksums, source_precheck, source_use_log ×3). artifact_binding.csv unchanged. Added `cr_0006_refreeze`. Self-verifies: all files MATCH. |
| `pre_ablation_supplement_freeze_manifest.json` | Supplement documents unchanged by CR-0006; historical pre-ablation hashes **preserved**. Added `cr_0006_refreeze` note (see §5.3). |

All three manifests are valid JSON. Main and primary manifests independently re-verified — every recorded hash
matches the working tree.
