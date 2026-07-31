# Staging Inventory and Quarantine Note — Phase 2, Task 13

| Field | Value |
|---|---|
| Phase | Phase 2, task 13 — audit staging data without admitting it |
| Anchor commit | `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21` |
| Snapshot date | 2026-07-10 (counts are a point-in-time snapshot; `results/_ablation/` is being written by a live campaign and its numbers change) |
| Admissibility | **Every path in this inventory is NON-ADMISSIBLE as publication evidence** (Sections 0.3, 2.1-E, 2.3). Staging enters the paper only via the Section 2.4 controlled promotion into `benchmarks/cec_reference_results/` with a release manifest. |
| Method | Directory walk with file/byte counts only. No result file was opened for value interpretation; no ablation outcome was inspected (Section 6.10). |

## 1. `results/` inventory (counts only)

| Path | Files | Bytes | Content class | Admissibility |
|---|---:|---:|---|---|
| `results/_ablation/baseline/dt-gsk/cec2017/` (`curves/`, `gen_logs/`, `summary/`) | 152 | 49,572,361 | live ablation staging cell | NON-ADMISSIBLE; quarantined (Section 6.10) |
| `results/_ablation/no_ace/dt-gsk/cec2017/` | 152 | 49,319,610 | live ablation staging cell | NON-ADMISSIBLE; quarantined |
| `results/_ablation/no_bse/dt-gsk/cec2017/` | 103 | 31,631,694 | live ablation staging cell (in progress) | NON-ADMISSIBLE; quarantined |
| `results/_ablation/no_psr/dt-gsk/cec2017/` | 152 | 13,565,071 | live ablation staging cell | NON-ADMISSIBLE; quarantined |
| `results/_analysis/publication_polish/` | 1 | 15,926 | historical review note (`project_review_findings.md`) | NON-ADMISSIBLE (rank-6 prose) |
| `results/_run_all/_analysis/cec2017/` | 4 | — | historical stats-pass bundle (`cec2017_{statistical_report.txt, friedman_ranks.csv, friedman_ranks.tex, wilcoxon_summary.tex}`) | NON-ADMISSIBLE; superseded by the Phase 5/6 controlled analysis bundle |
| `results/_run_all/_analysis/cec2013/` | 4 | — | historical stats-pass bundle | NON-ADMISSIBLE |
| `results/_run_all/_analysis/cec2011/` | 4 | — | historical stats-pass bundle | NON-ADMISSIBLE |
| *(total `results/_run_all/_analysis/`)* | 12 | 134,416 | | |

Notable absences (all legitimate; record-as-`missing`, non-failing per Section 4.4):

- `results/_run_all/<optimizer>/<suite>/` reproduction trees — **absent**
  (raw logs thinned by the storage campaign; commit `e2cddd3b0`). The loader
  fallback surface is therefore empty at the anchor, which reduces — but does
  not remove — the need for the task 10 strict-source guard.
- `results/paper_tables/` — **absent**; materialized only by the Phase 6
  task 23 export (see `asset_map.md` Section 3 and `instruction_precedence.md`
  C-11).
- `results/ablation/` aggregate CSVs — **absent** (Phase-12-only).
- `results/dt-gsk/sweeps/parametric-study/` — **absent**; blocks T21/T22
  (asset_map.md F-12.3; `evidence_gap_register.md` owner).

## 2. Quarantine note — live `results/_ablation/` campaign

A live ablation staging campaign (runbook "Full Paper Pipeline" sequencing,
recorded as conflict C-09) is writing cells `baseline`, `no_ace`, `no_bse`,
`no_psr` under `results/_ablation/<cell>/dt-gsk/cec2017/` during Phase 2
(uncommitted churn visible in `git status` at session start). Per Sections
0.3, 6.10 and the C-09 disposition:

1. the churn is **NON-BLOCKING** for Phase 2 — `results/` is staging-only;
2. these outputs are **quarantined from the primary workflow**: they MUST NOT
   be read to shape the primary paper, MUST NOT feed any table, figure,
   statistic, or claim, and MUST NOT be promoted before the Phase 12
   pre-ablation gate (Gate 11);
3. permitted uses before Phase 12 are archival and parser tests **with values
   masked** only;
4. this inventory recorded directory/file counts only and did not read any
   contained value;
5. any future evidentiary use requires the full Section 2.4 promotion through
   `scripts/promote_evidence.py` into a versioned immutable release, after the
   pre-registered Phase 12 design is frozen — the existing cells' outcomes do
   not pre-commit that design.

## 3. Reproducibility notes for later final-ablation staging

- Cell layout observed (names only): `results/_ablation/<cell>/dt-gsk/cec2017/{curves,gen_logs,summary}/`
  — matches the Section 4.4 expected working layout and the
  `generate_ablation_matrix.py --ablation-root results/_ablation` interface.
- Cell names present (`baseline`, `no_ace`, `no_psr`, `no_bse`) follow the
  `no_<mechanism>` convention expected by `_ABLATION_LABELS` in
  `generate_latex_tables.py`.
- `configs/_ablation/<cell>.yml` remains the config staging pattern for
  Phase 12 dry-run regeneration.

*Every path above is staging. None of it is evidence.*

---

## Dated note — 2026-07-11: ablation campaign COMPLETE; baseline F25-D100 shortfall + repair

- The 7-cell scaffold ablation campaign (baseline + no_ace/no_psr/no_bse/no_linkage/
  no_localsearch/no_arch; CEC2017 D10/30/50/100; 25 runs; SGSM off in every cell)
  finished 2026-07-11 ~03:13.
- **Completeness check:** 6 of 7 cells have exactly 2,900 per_run rows (29 funcs x 4
  dims x 25 runs). **baseline has 2,894 — six runs of F25 at D100 are missing**
  (19/25); all other (dim,func) cells exactly 25.
- **Repair (in progress):** deterministic re-run of the full baseline D100 slice into
  the SEPARATE root `results/_ablation_repair/baseline/` (command:
  `python scripts/run_ablation.py --only baseline --dimension 100 --runs 25 --workers 12
  --output-root results/_ablation_repair`). Seeds are per (dim,func,run) via
  get_cec_seed(20240620,...), so re-computed runs are byte-identical to the originals;
  the 719 overlapping D100 rows MUST byte-match the original per_run rows — this serves
  as the repair-validation check at Phase 12 promotion.
- **Phase 12 promotion instruction:** compose baseline = original D10/30/50 (+ the
  byte-match-verified D100 from the repair root); document the composition in the
  promotion record; never silently merge. All quarantine rules unchanged — no outcome
  has been inspected (only row counts / run accounting, which is provenance, not outcome).

- **REPAIR VALIDATED 2026-07-11 (exit 0).** `results/_ablation_repair/baseline/` D100
  slice = 725 rows (29 funcs x 25 runs). Byte-match against the 719 original D100 rows:
  **0 mismatches on every scientific column** (optimizer, suite, function, dimension,
  run, seed, best_fitness, error, nfes, termination) — deterministic seeds reproduced
  the originals exactly. The **6 missing F25-D100 runs recovered** (runs 6, 8, 11, 12,
  14, 15). The ONLY differing column is `runtime_seconds` (repair ~2x slower under the
  12-worker load) — wall-clock is environment-dependent and is NOT an ablation endpoint
  (ablation uses error/best_fitness), so it does not affect any ablation delta.
  **Composition decision:** at Phase 12, the authoritative baseline D100 slice is the
  REPAIR slice (complete + internally runtime-consistent); baseline D10/30/50 stay from
  the original campaign. Disclose in the promotion record that baseline-D100 wall-clock
  derives from the repair environment (irrelevant to the error-based ablation; the cost
  analysis is comparability-qualified regardless). Validation script + full output in the
  session scratchpad.
