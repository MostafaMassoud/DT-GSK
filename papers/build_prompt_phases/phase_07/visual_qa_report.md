# Gate 7 — adversarial figure/exhibit QA report (CR-0003)

Scope: every Phase 7 produced exhibit — 17 regenerated tables
(`papers/tables/T01–T16, T16_bca.tex`), 17 Word-source JSONs
(`papers/tables/word_sources/`), 34 figure PNG+PDF pairs (21 convergence
grids, 4 Nemenyi CD diagrams, 4 rank charts, 5 conceptual figures), and
4 method artifacts (`phase_03/*.tex`). Empirical ground truth restricted to
the Phase 6 bundle `papers/analysis/rel-2026-07-10-262fc16c9/`, the staging
export `results/paper_tables/`, and (P2) `benchmarks/cec_reference_results/`
gen_logs. No `results/_run_all`, no `results/_ablation`, no rendered `.tex`
read as a data source.

## Verdict

**PASS** — after the fixes recorded in §3: **0 critical, 0 major, 0 minor**
open findings. Automated QA (`figure_qa.py`, final run): **135 pass checks,
0 findings** over all 34 produced figures.

---

## 1. Automated figure QA (figure_qa.py)

Tool: `papers/build_prompt_phases/phase_07/figure_qa.py` (new, this gate;
`ruff check` clean). Per figure it verifies, from the PNG raster and the
PDF text/content layer:

| Check | Method | Result (final run) |
|---|---|---|
| Overflow / clipped text | non-background density on all 4 PNG border rows/cols (>30% flags) | 0 flagged |
| Empty figure | non-white pixel fraction < 0.1% | 0 flagged |
| Duplicate figures | sha256 over all 34 PNGs | 34/34 unique |
| Duplicate panels in a grid | repeated `Fk (D=d)` titles in PDF text | 0 |
| 7-series per convergence panel | companion `*_missing.log` cross-check (174 panels) + all 7 P3 stroke colours present in each grid's PDF content stream | 174/174 panels 7/7; colours present in all 21 grids |
| Legend presence + P1 order | exact legend line `GSK AGSK APGSK FDB-AGSK ATMALS-GSK eGSK DT-GSK` in PDF text | present in all 21 convergence grids; P1-ordered entries in rank charts |
| P3 colour map | stroke ops matched to Okabe-Ito {#E69F00,#56B4E9,#009E73,#CC79A7,#0072B2} + grey 0.6 + black | all series figures pass |
| Function/dimension labels vs filename | panel-title set extracted from PDF == set derived from the companion missing.log for that grid; dim token cross-checked against filename | all 21 grids exact; CD diagrams carry `D = {10|30|50|100}` matching filename |
| Axis scaling sanity | power-of-ten tick tokens (log-error y) per grid; CEC2011 linear fallback disclosures counted (`linear scale (negative objectives)`: a=3 [F2,F5,F6], b=1 [F10], c=0) | all pass |
| CD diagram content | 7 algorithm names, 7 two-decimal rank labels, `CD = 1.67`, `k = 7, N = 29` annotation | 4/4 pass |
| Raster resolution | PNG pixels vs PDF MediaBox: >=200 dpi | 299–301 dpi (convergence/nemenyi/ranks), 219–220 dpi (concept) |
| Determinism | no `/CreationDate` bytes in any produced PDF | clean after fix (§3.1) |
| Forbidden tokens | `ablation`, standalone `EGSK`, `hold(-)out` in any produced figure text layer | zero |

P5 conformance re-checked: main-grid panels are exactly the frozen
`phase_05/curve_selection.csv` selection (D30: F3, F10, F12, F26;
D100: F1, F5, F12, F26) — read, never re-derived.

## 2. Visual inspection pass (16 figures read at rendered size)

Viewed directly and judged for column-width legibility and grayscale
distinguishability (P3 linestyles):

1–2. `main_cec2017_D30.png`, `main_cec2017_D100.png` — 4 panels each,
   7 distinguishable curves (distinct dash patterns; DT-GSK thick solid
   black on top), log-error axes, single shared legend in P1 order, F3-D30
   shows the documented 1e-14 display floor. Legible at column width.
3–6. `nemenyi_cd_cec2017_D{10,30,50,100}.png` — rank-sorted bars, value at
   bar end, CD scale bar anchored at best rank; cohorts match the
   tables_figures_report (D10 {DT-GSK,AGSK,FDB-AGSK,APGSK,eGSK}; D30 best
   eGSK {eGSK,DT-GSK}; D50 {DT-GSK,eGSK}; D100 {DT-GSK,eGSK,ATMALS-GSK}).
   DT-GSK highlighted (fill), works in grayscale (position + labels).
7–10. `rank_vs_dim_cec2017.png` (7 lines, P3 styles, distinguishable in
   grayscale via dash patterns), `cec2017_mean_ranks.png` (grouped bars, P1
   order per group), `cec2011_ranks.png` (sorted barh, eGSK first, DT-GSK
   highlighted — consistent with the mandated [CEC2011-EGSK-LOSS]
   disclosure), `friedman_gsk_family.png` (overall bars, DT-GSK best).
11–15. Conceptual: `fig_architecture.png` (8 numbered subsystems, GSK core,
   gate badges, RNG + BudgetController rails, restart-never-loses-ground
   loop, returns global best), `fig_sgsm_mechanism.png` (3 stages, E10
   formula, confidence gate, 3 exploitation channels; "ISM; code alias
   SGSM" terminology), `fig_dim_gating.png` (filled-vs-empty ON/OFF,
   grayscale-safe, frozen tier values, D>=50 / D>=100 threshold callouts,
   freeze footnote), `fig_taxonomy.png` (4 comparison dimensions vs
   DG/CMA-ES/eigenvector-DE, card-bounded citations, "never worded free"
   footnote), `fig_nlpsr_schedule.png` (4 tiers + linear LPSR reference,
   analytic only).
16. `cec2011_a.png` — supplement grid sample: 7/7 series everywhere; the
   three negative-objective panels (F2, F5, F6) carry the in-panel
   "linear scale (negative objectives)" disclosure; F3 (D=1) panel has an
   extremely narrow y-range (all algorithms coincide at ~1.15e-5) — curves
   overlap by data, not a rendering defect.

## 3. Findings and fixes applied (all fixes verified by re-run)

### 3.1 FIXED (major) — timestamps inside 26 produced PDFs
21 convergence PDFs + 5 conceptual PDFs embedded matplotlib
`/CreationDate` metadata, violating the determinism contract ("no
timestamps in artifact content"). The Task-B artifacts (tables, Nemenyi,
rank charts) were already clean; the claim in `tables_figures_report.md`
§5 ("verified 0 occurrences ... in every produced PDF") held only for the
Task-B outputs. Fix: added `metadata={"CreationDate": None}` to the PDF
`savefig` in `papers/scripts/_convergence_common.py`,
`generate_flowchart.py`, `generate_sgsm_mechanism.py`,
`generate_dim_gating.py`, `generate_taxonomy_figure.py`,
`generate_nlpsr_trajectory.py`, then regenerated all 26 figures with their
recorded generator commands (admissible inputs only). Verification: all 26
paired PNGs are **byte-identical** to the pre-fix versions (content
unchanged; only the PDF timestamp dropped); companion missing.logs
unchanged; `/CreationDate` scan now clean over every bound PDF. The 26
changed PDF checksums were updated in
`papers/governance/artifact_binding.csv`.

### 3.2 FIXED (major) — LaTeX-breaking bare underscore in T14.tex
`papers/tables/T14.tex` row label `p_holm` (bare underscore in text mode —
compile error / malformed row in the CEC2013 Wilcoxon table). Fix: label
mapping `p_holm -> $p_{\text{Holm}}$` in
`papers/scripts/generate_latex_tables.py` (`_fmt_metric`), regenerated with
`--skip-ablation`. All other 16 `.tex` outputs byte-identical after the
re-run (determinism re-confirmed); only `T14.tex` changed; binding checksum
updated.

### 3.3 FIXED (minor) — terminology trap in Word-source JSONs
`word_sources/T{7..10,15,16}.json` carry verbatim CSV identifiers `EGSK` /
`FDBAGSK` with no glossary note, risking an eGSK-capitalization breach at
the Phase 9 Word build. Fix: `generate_word_sources.py` now emits an
explicit note in every JSON ("display names at Word build time MUST apply
the frozen Phase 4 glossary: EGSK -> eGSK, FDBAGSK -> FDB-AGSK ..."); all
17 JSONs regenerated (values verbatim-unchanged).

### 3.4 FIXED (trivial) — report arithmetic
`convergence_validation.md` total said "17 grid figures"; the enumerated
table sums to 21 (2 main + 12 CEC2017 supplement + 3 CEC2011 + 4 CEC2013).
Corrected to 21.

### 3.5 Script-calibration notes (not artifact defects)
First `figure_qa.py` run produced 6 false positives (CD-diagram numeric
filter counted the alpha=0.05 annotation; two concept keyword probes used
wording not present in the art). Fixed in the QA script itself; final run
is the record.

## 4. Gate checks (adversarial re-verification)

- **Zero hand-typed values — independent spot-check** (beyond
  `exhibit_validation_report.md`): T03.tex F12/F26 rows re-derived from
  `results/paper_tables/T3.csv` (Best/Median/Worst/Mean/SD order, 2-dp
  scientific, `\bestval` on the smaller unrounded mean) — exact; T16.tex
  all 35 rank cells vs `T16.csv` at 2 dp with per-column best markers —
  exact; T01.tex F21/F22 vs `T1.csv` — exact (F22 bold resolved on
  unrounded means 14.169 < 14.242); T15.tex eGSK row vs `T15.csv` (D30
  p 0.1987 = 0.1986745 at 4 dp) — exact; T14.tex R+/R-/p/p_holm columns vs
  `T14.csv` — exact. Confirms the validation report's PASS (4349
  comparisons, 0 mismatches).
- **No-ablation scan**: `grep -ri ablation` over `papers/tables/`
  (including word_sources and the stale T21/T22) and `papers/figures/`
  (all text layers + PDF-extracted text) — **zero matches**. No ablation
  artifact of any kind exists in the build.
- **Terminology scan**: no standalone `EGSK`, no `FDBAGSK`, no
  `hold(-)out` misuse in any produced `.tex`, figure text layer, or
  phase_03 method artifact (the only "holdout" strings are the mandated
  negations "never worded independent/holdout/validation" in CEC2013
  word-source notes; CEC2013 is consistently "second comparison suite").
- **Binding coverage**: all 55 `artifact_binding.csv` rows point at
  existing files; every Phase 7 produced output under `papers/tables/` and
  `papers/figures/{convergence,nemenyi,ranks,concept}` is bound. Unbound
  files on disk are exactly the disclosed stale/superseded legacy set:
  `F{01,04,15,22}_D{30,50}.png` (pre-Phase-7 two-series PNGs),
  `ranks/nemenyi_cd_d50.pdf` (superseded), `T21.tex`/`T22.tex` (stale,
  EG-006), plus legacy `figures/{flowchart,taxonomy,traces}/` (superseded
  per method_artifacts_report) — none may be `\input`/`\includegraphics`'d
  by Phase 8.
- **Caption completeness**: every bound manuscript label resolves to a
  caption in `captions_registry.md` (grouped shorthand headings cover the
  per-dimension families `tab:cec2017-d10/-d30/-d50/-d100`,
  `tab:cec2013-d10/-d30/-d50`, `fig:sconv-cec2017-d10..d100`, and the
  equation set `eq:junior-idx ... eq:rng-substreams`). Mandated limitation
  notes ([APGSK-GAP], [RANK-ROBUSTNESS], [CEC2011-EGSK-LOSS],
  [CEC2013-D30-THIRD]) are attached where required.
- **Label uniqueness**: unique across exhibits; the only shared labels are
  the intentional a/b/c(/d) sub-grids of one supplement exhibit family
  (`fig:sconv-*`). **Phase 8 must** render these as subfigures or suffix
  the `\label`s — flagged as a hand-off requirement, not a Phase 7 defect
  (their `latex_location` is `pending-phase8-rewire`).
- **Validation verdict**: `exhibit_validation_report.md` PASS confirmed;
  T16_bca cross-format note (word source carries the per-function BCa
  companion, the .tex carries rank CIs) remains correctly disclosed in the
  binding CSV and captions registry for Phase 9 reconciliation.

## 5. Dispositions re-confirmed (unchanged by this gate)

- T21/T22: NOT-GENERATED (EG-006); `generate_parametric_tables.py` not
  run; stale legacy files remain excluded from binding.
- `generate_trace_figures.py` / `generate_adaptive_params_panel.py`:
  diagnostic-release-GATED, not run (no promoted GenLog release; EG-005).
- Ablation exhibits: none (P6, DEFERRED_TO_PHASE_12_SUPPLEMENT_ONLY).

## 6. Inventory (validated in this gate)

- Tables: 17 `.tex` (T01–T16, T16_bca) — value-validated, terminology
  clean, T14 repaired.
- Word sources: 17 JSON — regenerated with glossary note; values verbatim.
- Figures: 34 PNG+PDF pairs (21 convergence grids / 174 panels, 4 Nemenyi
  CD, 4 rank charts, 5 conceptual) — all pass automated + visual QA;
  timestamps purged; checksums re-recorded.
- Method artifacts: 4 (`notation_table.tex`, `algorithm_pseudocode.tex`,
  `parameter_table.tex`, `equations.tex`) — terminology scan clean.
