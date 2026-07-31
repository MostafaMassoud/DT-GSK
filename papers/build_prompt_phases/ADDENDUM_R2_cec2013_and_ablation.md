# ADDENDUM R2 — CEC2013 Family Panel + CEC2017 DT-GSK Ablation

> **Status:** authoritative revision to `papers/PAPER_BUILD_PROMPT.md` and the
> `PHASE_*` files. Both evidence sources have **LANDED** in the repository:
> the CEC2013 full-family panel is committed and the ablation tooling is
> implemented and tested. This addendum documents their exact structure and
> extends every affected phase. Where this addendum and an older phase
> instruction disagree, **this addendum wins.** Everything else in the master
> prompt and phase files stands.
>
> **Ground rules unchanged.** Citations stay within the 57-key closed set
> (`liang2013cec2013` is already in it — its role is upgraded below, not added).
> Every number still traces to committed data + a commit SHA. No fabrication.
> `cec_reference_results/` remains READ-ONLY evidence.

---

## R2.0 — What changed, in one paragraph

Two datasets that the manuscript already *references* but the tree previously
*lacked* have now **landed**: (A) the **CEC2013 family panel** under
`benchmarks/cec_reference_results/cec2013/` — the **full 7-optimizer panel** is
committed (previously DT-GSK-only), which promotes CEC2013 from a
single-method hold-out to a **second comparison suite** (28 functions,
D ∈ {10, 30, 50}, 51 runs); and (B) the **CEC2017 scaffold-ablation tooling**
for DT-GSK — `scripts/run_ablation.py` (remove-one over **6 mechanisms +
baseline = 7 cells**, SGSM off in every cell, n = 25 by design) with roll-ups
to `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv`. Both
must be audited in Phase 0, turned into statistics in Phase 2, rendered in
Phase 3, written up in Phase 4, and archived in full in Phase 5. Details below.

---

## R2.A — DATASET A: CEC2013 family panel

### A.1 Location & structure (landed — verify in Phase 0)
Mirrors the CEC2017/CEC2011 flat layout already in the repo:

```
benchmarks/cec_reference_results/cec2013/<optimizer>/
    <optimizer>_cec2013_D<dim>.csv        # per-function summary (Function,Best,Median,Mean,Worst,SD)
    per_run.csv                           # per-run finals — present for ALL seven optimizers in the landed panel
    curves/Figure_F<f>_D<dim>_Run#<r>.csv  # one representative convergence curve per (function,dim)
    gen_logs/CheckpointErrors_<opt>_F<f>_D<dim>.csv
    environment.json                      # FP-regime sentinel (fp_regime.sentinel), platform
    run_config.json  seed_schedule.csv  verification.json  phase0_protocol.json
```

- **Optimizer coverage:** the **full 7-panel landed**
  (`gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk`).
  Phase 0 still enumerates and verifies it; Phase 1 sets prominence from the
  confirmed coverage.
- **CEC2013 shape:** 28 benchmark functions (no exclusion analogous to CEC2017's
  F2 unless `verification.json`/`run_config.json` says so — **check, don't
  assume**). Dimensions per the CEC2013 protocol: **D ∈ {10, 30, 50}**,
  confirmed from the summary filenames of the landed panel.
- **Run count:** **CEC2013 = 51 runs** (the CEC2013 competition standard; this is
  what the runbook campaign uses, and what the landed `run_config.json` records).
  Re-confirm against `seed_schedule.csv` (row count) during the Phase 0 audit; if
  any cell used a different count, record it in the ledger and report it — never
  silently average over a mismatched N.

### A.2 Provenance & integrity (Phase 0)
- Confirm each CEC2013 `environment.json` carries an FP-regime sentinel and that
  it matches the canonical CEC2013 regime (record the prefix — it is a *different*
  suite from CEC2017, so the sentinel value may differ; the point is internal
  consistency across the CEC2013 panel, not equality with CEC2017's `8bda40d8…`).
- Add one ledger row per `(optimizer, cec2013, dim, n_runs, seed_policy,
  source_path, commit_sha)`.
- `cec_reference_results/` is READ-ONLY. If a CEC2013 optimizer needs
  regeneration (only the runnable ones can be re-run), emit to `results/_run_all/`
  and reconcile — never edit the imported evidence.

### A.3 Aggregation-level note (carry into setup)
The landed panel carries `per_run.csv` for **all seven optimizers** (28 functions
× 3 dims × 51 runs), so run-level data exists for the comparators too. The family
**rank statistics are still computed per-function** (one representative value per
function across the 28), exactly as the loader
(`src/gsk_family/analysis/result_loader.py`) consumes them — reference-first from
the committed panel. State the aggregation level once in Experimental Setup; any
run-level effect-size/CI claim must name the `per_run.csv` cell it is computed
from.

### A.4 Scope decision (Phase 1 — PI call)
CEC2013 can serve two roles; the PI picks one in Phase 1 and records it in
`decisions.md`:
- **Secondary confirmation suite (default, budget-safe):** one compact
  per-dimension summary table + one Nemenyi CD figure in the main text; full
  per-function tables and pairwise matrices in the supplement. One short results
  paragraph: "the CEC2017 ranking is corroborated on the independent CEC2013
  suite (Friedman rank …, Nemenyi …)."
- **Co-primary suite (only if page budget allows):** full CEC2017-equivalent
  treatment. Likely forces other material into the supplement — re-check the
  Part 3 §3.4 budget before electing this.

### A.5 Citation role upgrade
`liang2013cec2013` moves from "CEC2013 hold-out defs" to **"CEC2013 evaluation
suite defs."** Cite it in Experimental Setup where the CEC2013 protocol is
described (28 functions, dims, run count), and again in Results where CEC2013
comparison is reported. Still no citation outside the 57.

---

## R2.B — DATASET B: CEC2017 DT-GSK ablation

### B.1 Location & structure (tooling landed — confirm cells in Phase 0)
The implemented pipeline uses these paths:

```
configs/_ablation/<cell>.yml                          # one config per cell, written by scripts/run_ablation.py
results/_ablation/<cell>/dt-gsk/<suite>/             # per-cell run output (summary/curves/gen_logs)
results/ablation/
    ablation_matrix_rank_summary_<suite>[_D<dim>].csv # the roll-up: mean Friedman rank, delta vs full, best-case counts, Wilcoxon+Holm
results/dt-gsk/sweeps/parametric-study/              # parameter sensitivity (runs: 3) — sensitivity, NOT the ablation
```

- **Design:** a **remove-one scaffold ablation — 6 mechanisms + baseline =
  7 cells** — on **CEC2017 (29 functions, SGSM disabled throughout)** that
  isolates the six core scaffold components (`ace_enabled` ACE, `psr_enabled`
  NLPSR, `bse_enabled` BSE, `linkage_blockwise_enabled` linkage-aware crossover,
  `local_search_enabled` Nelder–Mead endgame, `arch_enabled` elite archive;
  ARGP / eigenframe final-polish / deep-stall restart are commented-out extras in
  `scripts/run_ablation.py`). The default run count is **n = 25** (the paper's
  stated ablation design); the summary CSV reports mean rank, delta vs the full
  (baseline) cell, and best-case counts per cell. **SGSM
  (`interaction_graph_enabled`) is off in this design by construction** — it
  isolates the *scaffold*, not the interaction memory. Say this explicitly; it is
  the honest scope of this ablation.
- **The SGSM overlay is ablated separately** (the existing CEC2013 hold-out
  design: `full / no-adaptive / no-sgsm / bare-pub`, n = 25). Keep the two
  ablations distinct in the write-up: **scaffold ablation → CEC2017 (this drop);
  SGSM-overlay ablation → CEC2013 hold-out (already present).**
- **Coverage to confirm in Phase 0:** the number of cells actually present
  (target 7: `baseline` + `no_ace`, `no_psr`, `no_bse`, `no_linkage`,
  `no_localsearch`, `no_arch` — plus any add-one `only_*` cells), that all 29
  CEC2017 functions are covered per cell, the dimension(s) the ablation was run
  at (record which — the ablation need not span all four dims; report exactly
  what exists), and the run count per cell (expected 25).

### B.2 What it enables (promotes the ablation to first-class evidence)
Previously the ablation subsection leaned on the CEC2013 hold-out. With the
CEC2017 scaffold ablation present, the ablation becomes **primary evidence on the
primary suite**:
- Compute each component's **marginal contribution** = the rank/error delta
  between the full-scaffold cell and the cell with that component disabled, read
  from `ablation_matrix_rank_summary_<suite>[_D<dim>].csv` (which also carries
  the full-vs-cell Holm-corrected Wilcoxon).
- This directly answers R1's rubric item "does each mechanism earn its place
  empirically?" — the single highest-value ablation question.

### B.3 Integrity notes
- `results/ablation/` is a *generated* result directory (not imported evidence),
  so it is writable/regenerable — but treat committed cells as the source of
  truth and bind every reported delta to them + a commit SHA.
- Do **not** merge the parametric study (`sweeps/parametric-study/`, runs = 3)
  into the ablation claims: it is low-N **sensitivity**, explicitly not the
  ablation basis. Report it separately in the supplement as sensitivity, with its
  n = 3 stated.

### B.4 Tooling (implemented & tested — use these, don't hand-roll)
The ablation pipeline is three committed scripts (see the runbook's
"DT-GSK Ablation" section):
- `scripts/run_ablation.py` — writes one config per cell under
  `configs/_ablation/<cell>.yml` (baseline + one disable-one cell per mechanism —
  6 mechanisms + baseline = 7 cells; SGSM off in every cell) and runs each to
  `results/_ablation/<cell>/dt-gsk/<suite>/`. Flags:
  `--suite {cec2017,cec2011,cec2013}` (cec2011 → native dims),
  `--mode {remove-one,add-one}`, `--dimension` comma-list, `--runs` (default 25),
  `--workers`, `--only`, `--dry-run`.
- `papers/scripts/generate_ablation_matrix.py` — rolls the cells up into
  `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv` (mean
  Friedman rank, delta vs full, best-case counts, full-vs-cell Holm-corrected
  Wilcoxon), reusing `analysis/statistics.py`; flags `--suite`/`--dimension`/
  `--full-cell`.
- `gen_ablation_table()` in `papers/scripts/generate_latex_tables.py` — renders
  one `papers/tables/ablation_<tag>.tex` per matrix. And
  `papers/scripts/generate_cec2013_convergence.py`
  renders the CEC2013 convergence grids for Dataset A (28 functions, 4
  subfigures a–d).

---

## R2.C — PER-PHASE EXTENSIONS (do these in addition to the base phase tasks)

### Phase 0 (`PHASE_0_audit.md`) — add
- **0.A** Enumerate `benchmarks/cec_reference_results/cec2013/*`: optimizers,
  dims (from summary filenames), function count (confirm 28 and any exclusion),
  presence of `per_run.csv` per optimizer, curve counts, and the FP sentinel per
  `environment.json`. One ledger row per cell. Flag any optimizer missing a
  dimension.
- **0.B** Enumerate the ablation trees: per-cell runs under
  `results/_ablation/<cell>/dt-gsk/<suite>/` (target 7 cells: baseline + 6
  remove-one), confirming 29-function coverage and the run count (expected 25)
  per cell; and the roll-up matrices
  `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv`
  (header/shape, ablation dimension(s)). Enumerate
  `results/dt-gsk/sweeps/parametric-study/` separately and tag it "sensitivity,
  n=3." If either path is absent or differently named, record the actual path and
  adapt — do not assume.
- **Exit-gate add:** the ledger now covers CEC2013 panel cells and every ablation
  cell, each with a source path + commit SHA, or an explicit regeneration ticket.

### Phase 1 (`PHASE_1_scope.md`) — add
- **1.A** Record the CEC2013 role decision (A.4) in `decisions.md`.
- **1.B** Promote the ablation to a main-text results subsection (budget
  permitting) and note in `outline.md` that its evidence is the CEC2017 scaffold
  ablation, with the CEC2013 SGSM-overlay ablation as corroboration.
- **1.C** Re-check the Part 3 §3.4 page budget against the added CEC2013 exhibits;
  if it overflows, CEC2013 stays secondary (supplement-heavy).

### Phase 2 (`PHASE_2_data_stats.md`) — add
- **2.A** Run the same statistical panel on the CEC2013 panel that Phase 2 runs on
  CEC2017 (Friedman ranks across the 28 functions per dim, Nemenyi CD, pairwise
  Wilcoxon + Holm vs each present comparator, A12, and BCa on the headline gap) —
  **per-function**, via the existing loader/`gsk-stats`. Emit to the CEC2013
  analysis output dir; add to the stats bundle.
- **2.B** Compute ablation deltas with `papers/scripts/generate_ablation_matrix.py`
  (the computation of record): per-cell mean rank, the disable-one-component
  marginal deltas vs the full-scaffold cell, best-case counts, and the paired
  full-vs-cell Wilcoxon + Holm, emitted to
  `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv`. Keep
  SGSM-off scope explicit.
- **2.C** Cross-verify CEC2013 and ablation numbers table==script==prose; add both
  to the table→CSV binding map.

### Phase 3 (`PHASE_3_tables_figures.md`) — add
- **3.A** CEC2013 exhibits sized to the Phase-1 role: (secondary) one per-dim
  summary table + one Nemenyi CD figure in main, full per-function + pairwise
  matrices in supplement; (co-primary) full CEC2017-equivalent set.
- **3.B** One **ablation exhibit** in the main text: a compact table from
  `ablation_matrix_rank_summary_<suite>[_D<dim>].csv` (component | mean rank |
  Δ vs full | best-case count), best row bolded — rendered as
  `papers/tables/ablation_<tag>.tex` via `gen_ablation_table()`; optionally a
  small bar/heat figure. Full 7-cell matrix (plus any add-one cells) →
  supplement. Parametric-study sensitivity table → supplement
  (label its n = 3).
- Bind every cell to its CSV; never hand-edit a rank.

### Phase 4 (`PHASE_4_drafting.md`) — add
- **4.A** In Experimental Setup: add the CEC2013 protocol (28 functions, dims, run
  count, `liang2013cec2013`) and one sentence on per-function resolution for both
  suites' comparators.
- **4.B** In Results: add a CEC2013 confirmation paragraph (role-sized) and a
  dedicated **Ablation** subsection built on the CEC2017 scaffold ablation —
  state each component's marginal contribution, name what the ablation does *not*
  cover (SGSM is off here; the overlay is ablated on CEC2013), and read the two
  ablations together honestly.
- **4.C** In Limitations: keep the per-function-resolution caveat; if CEC2013
  shows any regime where DT-GSK's advantage narrows, report it plainly.

### Phase 5 (`PHASE_5_supplementary.md`) — add
- **5.A** Full CEC2013 per-function tables (all present dims) + full pairwise
  Wilcoxon (Holm) matrices, S-labelled and cross-linked from the main CEC2013
  paragraph.
- **5.B** The full 7-cell CEC2017 scaffold-ablation matrix (baseline + 6
  remove-one cells, plus any add-one cells), plus the CEC2013
  SGSM-overlay ablation table, plus the parametric-study sensitivity table
  (n = 3 stated). Cross-link all from the main Ablation subsection.
- **5.C** Extend the reproducibility appendix: CEC2013 FP sentinel + seed schedule
  + commit; ablation provenance (generator, cells, commit).

---

## R2.D — ACCEPTANCE-GATE ADDITIONS (fold into Part 10 / Phase 8)

- [ ] CEC2013 panel audited; every reported CEC2013 number bound to a committed
      summary + commit SHA; aggregation-level note (A.3) stated once.
- [ ] Ablation numbers bound to
      `results/ablation/ablation_matrix_rank_summary_<suite>[_D<dim>].csv` (+ SHA);
      scaffold-vs-overlay scope stated; parametric study reported separately as
      n = 3 sensitivity.
- [ ] CEC2013 role (secondary/co-primary) recorded in `decisions.md` and the page
      budget re-checked after adding CEC2013 exhibits.
- [ ] `liang2013cec2013` cited in its upgraded role; citation set still ⊆ 57.

---

## R2.E — HONESTY CAVEATS TO PRESERVE (do not smooth over)
1. Family rank statistics are computed **per-function** (the loader's
   consumption model) on CEC2013 as on CEC2017. The landed panel does carry
   `per_run.csv` for all seven optimizers, but any run-level claim must name
   the exact cell it is computed from — state the aggregation level once in
   Setup.
2. The CEC2017 scaffold ablation runs with **SGSM disabled**; it isolates the
   scaffold, not the interaction memory. The overlay's contribution is a separate
   (CEC2013 hold-out) ablation. Reporting one as if it covered the other would be
   a misattribution.
3. The parametric study is n = 3 — sensitivity signal only, never a significance
   claim.
4. Confirm CEC2013's function count and any exclusion from `verification.json`
   before tabulating; do not copy CEC2017's F2-exclusion convention onto CEC2013.

<!-- END ADDENDUM R2 -->
