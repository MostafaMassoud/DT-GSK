# X-ABL-02 SGSM-overlay — validation & provenance (51-run regeneration, `abl-rel-2026-07-16`)

> **Release note.** This validation record covers the **51-run post-fix regeneration**
> (C006 final-polish incumbent + M038 graph-backend corrections applied, commit
> `af7efc534`; run 2026-07-16). It supersedes the 25-run validation of
> `abl-rel-2026-07-13`, recoverable via git history. Every check below was re-executed
> against the promoted 51-run cells on 2026-07-17.

**Study.** X-ABL-02, the SGSM-overlay ablation, pre-registered in
`papers/build_prompt_phases/phase_05/ablation_preregistration.md` §2. This is the **direct
SGSM isolation** reviewers R1/R6 asked for — the study X-ABL-01 (scaffold, SGSM-off in every
cell) explicitly *cannot* provide. Reference cell = `full`; within each suite the 4 cells share
one seed schedule, run count, suite, and dimension set.

**Scope.** DT-GSK · **CEC2017 D50/D100** (29 functions, F2 excluded) and **CEC2013 D50**
(28 functions) · **51 runs per (cell, function, dimension)** — matching the primary panel's
power. Both suites gate the SGSM tier at `interaction_graph_min_dim=50`, so these are the
SGSM-active tiers; no CEC2013 D100 overlay exists (the preregistration reserves it as optional).

## Cells and single-toggle semantics (verified from each cell's `run_config.json`)

| Cell | `optimizer_options` (delta vs `full`) | Contrast `full` vs cell isolates |
|---|---|---|
| `full` | `interaction_graph_enabled=true` (reference) | — |
| `no_sgsm` | `interaction_graph_enabled=false` | **DIRECT SGSM contribution** (R1/R6) |
| `no_adaptive` | `interaction_confidence_adaptive=false` (SGSM on) | adaptive confidence-gate contribution |
| `no_finalpolish` | `final_polish_enabled=false` (SGSM on) | eigenframe final-polish (AN-ABL-POLISH; C2/MT-09) |

Each non-reference cell flips exactly **one** toggle relative to `full` (re-verified 2026-07-17
from the promoted `summary/run_config.json` of all 8 cells).

## Validation checks — all PASS (re-executed 2026-07-17)

**CEC2017 (per cell):**

| Check | full | no_sgsm | no_adaptive | no_finalpolish |
|---|---|---|---|---|
| `per_run.csv` rows D50 (29×51=1479) | 1479 ✓ | 1479 ✓ | 1479 ✓ | 1479 ✓ |
| `per_run.csv` rows D100 (29×51=1479) | 1479 ✓ | 1479 ✓ | 1479 ✓ | 1479 ✓ |
| functions present | 29 (F1, F3–F30) ✓ | ✓ | ✓ | ✓ |
| runs per (function, dim) | 51 ✓ | 51 ✓ | 51 ✓ | 51 ✓ |
| `base_seed` / `seed_policy` | 20240620 / unified | same ✓ | same ✓ | same ✓ |
| summary `Mean` vs mean(`per_run.error`) | max rel diff 3.7e-11 ✓ | 4.0e-11 ✓ | 3.4e-11 ✓ | 4.4e-11 ✓ |
| `verification.json` verdict | CONSISTENT | CONSISTENT | CONSISTENT | CONSISTENT |

**CEC2013 (per cell):** 1428/1428 rows (28×51) at D50 only, functions F1–F28, 51 runs per
function, same seed/policy, summary-vs-per-run max rel diff ≤ 3.7e-11, verdict CONSISTENT —
all four cells.

- **Seed-schedule identity across cells:** `seed_schedule.csv` is byte-identical in all four
  cells of each suite — CEC2017 SHA-256
  `c0bf724160e97f1165ddb84ae1c5be09512c640ca4da0732ade4e735b0ff34b3`, CEC2013
  `7566bc78ea7d586cf5831afd7b1cb594bc4d9f9756686fee409cee3090a375b2`. The cells therefore
  form a fair paired design: identical shared RNG schedule, differing only by the single toggle.
- **Runner:** `scripts/run_overlay_ablation_51.py --workers 15` (drives `run.py --config
  configs/_ablation/_51run/overlay_*.yml --root .`, thread-pinned environment); per-cell
  host/environment details are recorded in each cell's `summary/environment.json`.

**Verdict: VALID.** All 8 overlay cells are complete, seed-consistent, single-toggle, and
internally agreeing to < 5e-11 between the per-run and summary data sources.

## Provenance

The 51-run cells were executed entirely in this repository (source checkout, `--root .`,
native evaluators under `benchmarks/cec_suite_python/`), with the post-fix optimizer whose
frozen-core byte identity is enforced by `scripts/validate_profile_lock.py` and the
regression tests `tests/regression/test_dt_polish_incumbent_consistent.py` and
`test_dt_graph_backend_parity.py` (both fail on the pre-fix binary). The historical 25-run
release's cross-tree provenance argument (07-SAGE editable install) does not apply to this
regeneration — no external install was involved. Promotion into this release was a
deterministic copy with SHA-256 re-hash, recorded in `_ablation/manifest.json`
(`abl-rel-2026-07-16`).

## Analysis panels (reproduce Supplement S6.5 exactly)

Friedman over the 4 cells on per-function means; paired Wilcoxon signed-rank per contrast;
Holm over the pre-registered 3-comparison family:

| Panel | Friedman χ² / p | `no_sgsm` Δrank / Holm p | `no_adaptive` Holm p | `no_finalpolish` Δrank / Holm p |
|---|---|---|---|---|
| CEC2017 D50 | 14.43 / 2.4e-03 | +0.05 / **0.983** (n.s.) | 0.283 (n.s.) | +1.14 / **0.002** (sig) |
| CEC2017 D100 | 12.76 / 5.2e-03 | +0.16 / **0.897** (n.s.) | 0.079 (n.s.) | +0.98 / **0.005** (sig) |
| CEC2013 D50 | 13.40 / 3.8e-03 | +0.20 / **0.647** (n.s.) | 0.235 (n.s.) | +1.18 / **0.002** (sig) |

**Finding (consistent across all three panels).** The direct SGSM isolation shows **no
significant standalone benefit** at any active tier; the adaptive gate is directional but not
significant; only the ISM-dependent **final polish** is Holm-significant — measured here
un-handicapped (post-C006). This is the honest null Supplement S6.5 reports. Detailed
narrative: `overlay_findings.md` (CEC2013) and the contrasts JSONs (all three panels).
