# Phase 7 — Primary Tables, Figures, Equations, and Method-Artifact Production — Gate Report

- **Phase:** 7 (PAPER_BUILD_PROMPT.md lines 4381–4650)
- **Evidence:** Phase 6 bundle `rel-2026-07-10-262fc16c9` + `results/paper_tables/` staging exports (sole admissible inputs)
- **Gate date:** 2026-07-11
- **Verdict:** **APPROVED — Phase 7 FROZEN**
- **Signatories:** P2 + P3 + P5 + P7 + P8 (framework Gate 7 quorum)

## 1. Artifact inventory (all regenerated, zero hand-typed values)
| Category | Count | Location |
|---|---|---|
| LaTeX tables | **17** (T01–T16 + T16_bca; T14 LaTeX defect found+fixed) | `papers/tables/` |
| Word-native semantic table sources | **17 JSONs** (+ binding-level terminology notes) | `papers/tables/word_sources/` |
| Convergence grids (CR-0001 seven-curve) | **21 grids / 174 panels — every panel 7/7 series, ZERO absences** | `papers/figures/convergence/` |
| Nemenyi CD diagrams | 4 (bundle-wired, unrounded ranks, omnibus-gated, CD=1.673 cross-checked) | `papers/figures/nemenyi/` |
| Rank charts | 4 (rank-vs-dim, CEC2017 bars, CEC2011, legacy) | `papers/figures/ranks/` |
| Conceptual figures (approved specs, no empirical values) | 5 (+ .drawio source + Word diagram plan) | `papers/figures/concept/` |
| Method artifacts | 4 .tex (notation, pseudocode, parameters, equations E1a–E12) | `papers/build_prompt_phases/phase_03/` |
| Binding | **`papers/governance/artifact_binding.csv` — 55 rows**, §3.8 schema, full SHA-256 chains | governance |

## 2. Named tooling work completed
1. **CR-0001 seven-curve extension** — new shared `_convergence_common.py`; all three
   per-suite generators rewritten two-series → seven-curve family overlay (P1 order,
   P2 mean-across-runs, P3 Okabe-Ito map, shared legend, log-error axis, floor 1e-14
   disclosed; 4 CEC2011 negative-objective panels on disclosed linear fallback);
   main-text grids driven by the FROZEN curve selection (hard-fail if absent).
2. **Nemenyi rewire** — reads unrounded bundle `friedman_ranks_*.csv`; T16.tex-parsing
   path removed (one exhibit is never another's data source).
3. **Ablation suppression** — `--skip-ablation` flag added; assertion passed; zero
   ablation artifacts; `results/_ablation` never read.
4. **`generate_t16_bca.py`** rewired from result_loader to bundle descriptive stats.
5. **`generate_rank_charts.py`** bundle-wired; 3 pre-registered figures added.
6. Terminology normalization in table generator (EGSK→eGSK, FDBAGSK→FDB-AGSK).

## 3. Validation results
- **Value-level:** `exhibit_validation_report.md` — **4,349 comparisons, zero unexplained
  mismatches** (every .tex cell vs authoritative CSV; figure points sampled vs bundle).
- **Automated figure QA (CR-0003):** `figure_qa.py` — **135 checks over all 34 figures:
  0 critical / 0 major / 0 minor** (resolution 219–301 dpi, no overflow/clipping,
  no duplicate/empty panels, labels match filenames, no timestamps, no ablation/
  EGSK/holdout tokens).
- **Visual inspection pass:** 16 figures read directly — legible at column width,
  grayscale-distinguishable per P3 linestyles (`visual_qa_report.md`).
- **Captions:** `captions_registry.md` — 28 self-contained entries incl. the mandated
  limitation notes (apgsk per-run gap, r01/r04 robustness qualification, CEC2011
  significant loss vs eGSK, CEC2013 D30 third place).
- **Dispositions:** T21/T22 NOT generated (EG-006); trace/adaptive-params figures NOT
  generated (EG-005, no promoted GenLog release); T17–T20 never created; stale legacy
  artifacts flagged as superseded.

## 4. Adversarial QA (Gate 7)
**PASS — 2 major + 3 minor, ALL FIXED during QA:** (1) matplotlib `/CreationDate`
timestamps in 26 PDFs → stripped via `metadata={"CreationDate": None}`, all regenerated;
(2) T14 `p_holm` bare-underscore LaTeX defect → `$p_{\text{Holm}}$` mapping, other 16
tables byte-identical on regeneration; (3) Word-source terminology notes added;
(4) grid-count typo corrected; (5) supplement sub-grid shared-label risk recorded as a
**Phase 8 hand-off requirement** (subfigure environments or suffixed labels).

## 5. Carry-forward for Phase 8/9
- Supplement sub-grid labels (fig:sconv-*) need subfigure/suffixed labels at render.
- `T16_bca` semantic divergence (tex = rank-CI table; word_source = per-function BCa
  companion) disclosed in binding — Phase 9 must reconcile cross-format.
- Figures' `word_location` = pending-phase9 (DrawingML plan exists).

## 6. Sign-off
- **P2:** APPROVED — method artifacts faithful to the frozen phase_03 canon.
- **P3:** APPROVED — statistical marks/captions match the bundle; limitation notes present.
- **P5:** APPROVED — generators authoritative-input-only; bindings + checksums complete.
- **P7:** APPROVED — final-size visual inspection recorded; figure QA clean.
- **P8:** APPROVED — Word-native semantic sources exist for all tables + diagram plan.

**Gate 7 APPROVED. Phase 7 FROZEN 2026-07-11.** A later changed analysis output requires
exhibit regeneration and revalidation. Phase 8 (manuscript drafting) unblocked.
