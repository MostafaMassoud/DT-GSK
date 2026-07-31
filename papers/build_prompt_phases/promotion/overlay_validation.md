# X-ABL-02 SGSM-overlay — validation & provenance (CEC2013 D50)

**Study.** X-ABL-02, the SGSM-overlay ablation (`tab:abl-sgsm-overlay`), pre-registered in
`papers/build_prompt_phases/phase_05/ablation_preregistration.md` §2. This is the **direct
SGSM isolation** reviewers R1/R6 asked for — the study X-ABL-01 (scaffold, SGSM-off in every
cell) explicitly *cannot* provide. Reference cell = `full`; 4 cells share one seed/runs/suite/dim.

**Scope.** DT-GSK · CEC2013 · **D50** · 25 runs · 28 functions (F1–F28). CEC2013's SGSM tier
gate is `interaction_graph_min_dim=50`, so **D50 is the SGSM-active tier** for CEC2013 — the
correct (and only) dimension at which a direct SGSM isolation is meaningful for this suite.
Only D50 cells exist in `results/_ablation_sgsm/`; no D100 overlay was run (the preregistration
reserves D100 as optional and it is out of scope here).

## Cells and single-toggle semantics

| Cell | `optimizer_options` (delta vs `full`) | Contrast `full` vs cell isolates |
|---|---|---|
| `full` | `interaction_graph_enabled=true` (reference) | — |
| `no_sgsm` | `interaction_graph_enabled=false` | **DIRECT SGSM contribution** (R1/R6) |
| `no_adaptive` | `interaction_confidence_adaptive=false` (SGSM on) | adaptive confidence-gate contribution |
| `no_finalpolish` | `final_polish_enabled=false` (SGSM on) | eigenframe final-polish (AN-ABL-POLISH; C2/MT-09) |

Each non-reference cell flips exactly **one** toggle relative to `full` (verified from each
cell's `summary/run_config.json` and `configs/_ablation/overlay_*.yml`).

## Validation checks — all PASS

| Check | full | no_sgsm | no_adaptive | no_finalpolish |
|---|---|---|---|---|
| `per_run.csv` data rows (28×25=700) | 700 ✓ | 700 ✓ | 700 ✓ | 700 ✓ |
| functions present | 1–28 ✓ | 1–28 ✓ | 1–28 ✓ | 1–28 ✓ |
| runs per function | 25 ✓ | 25 ✓ | 25 ✓ | 25 ✓ |
| dimension column | {50} ✓ | {50} ✓ | {50} ✓ | {50} ✓ |
| summary CSV present (`dt-gsk_cec2013_D50.csv`) | ✓ | ✓ | ✓ | ✓ |
| `base_seed` / `seed_policy` | 20240620 / unified | 20240620 / unified | 20240620 / unified | 20240620 / unified |
| per-(func,run) seed == `full` | ref | 0 mismatch ✓ | 0 mismatch ✓ | 0 mismatch ✓ |
| summary `Mean` vs mean(`per_run.error`) | max rel diff 4.2e-11 ✓ | 4.4e-11 ✓ | 2.4e-11 ✓ | 4.6e-11 ✓ |

- **Seed schedule identity across all 4 cells:** `seed_schedule.csv` is byte-identical in every
  cell — SHA-256 `b2150782a79f1abcc748b77c7144438eeae6b6d3cef6dcd0517825a234798218` (13 146 B).
  Combined with 0 per-(func,run) seed mismatches, the cells form a fair paired design: identical
  shared `X0` and RNG schedule, differing only by the single toggle.
- **Command (all cells):** `python run.py --root . --optimizer dt-gsk --suite cec2013 --runs 25
  --seed 20240620 --seed-policy unified --rand-generator threefry --benchmark-fp-mode default
  --benchmark-backend auto` on `HUAWEI-MMASOUD` (22 cores), Python 3.10.11, Windows.

**Verdict: VALID.** All 4 overlay cells are complete (700/700 rows), seed-consistent, D50, with a
verified fair paired design. Both data sources (per-run errors and the summary `Mean` column)
agree to <5e-11. `verification.json` in each cell reads `verdict: CONSISTENT`.

## Provenance note (byte-identical core; 02-valid) — do NOT re-run

The runner resolves the importable `gsk_family` package to the **07-SAGE editable install**
(`D:/AI/PhD-Projects/00-GSK-Family/07-SAGE-DT-GSK_Family_Python_v0.1/src/gsk_family`), while the
CEC2013 evaluator and suite data are **02-native** (invoked with `--root .`, `data_root=
benchmarks/cec_suite_python/cec2013/`). The overlay numbers are valid for the **frozen** DT-GSK
algorithm, on three independently confirmed grounds:

1. **Optimizer core is byte-identical to the phase-03 freeze.** SHA-256 (first 16 hex) of the four
   frozen core sources match `papers/build_prompt_phases/phase_03/algorithm_freeze_manifest.json`
   **exactly**, and are identical between the 02 tree and the 07-SAGE install actually imported:

   | source | frozen manifest | 02 tree | 07-SAGE (used) |
   |---|---|---|---|
   | `dt_gsk.py` | `a274e0f83b4efd3c` | `a274e0f83b4efd3c` | `a274e0f83b4efd3c` |
   | `_dt_core.py` | `1ef815cee5d4c9c3` | `1ef815cee5d4c9c3` | `1ef815cee5d4c9c3` |
   | `_dt_profiles.py` | `c3dcdce3a3477dca` | `c3dcdce3a3477dca` | `c3dcdce3a3477dca` |
   | `_dt_rng.py` | `db1cc028b3ebc145` | `db1cc028b3ebc145` | `db1cc028b3ebc145` |

   The `_dt_subsystems/` package (10 `.py` files) is byte-identical between the 02 tree and the
   07-SAGE install (per-file SHA-256 match). (The manifest's `_dt_subsystems_merkle32` uses the
   project's own merkle recipe in `scripts/validate_*`; the relevant cross-tree byte-identity is
   confirmed directly by per-file hashing.)
2. **Evaluator is 02-native.** The CEC2013 functions/transforms/composition modules under
   `benchmarks/cec_suite_python/cec2013/` are the 02 repo's own; they were used via `--root .`.
3. **Completion is itself an 02-execution proof.** The `no_adaptive` and `no_finalpolish` cells
   each completed all 700 runs. 07-SAGE's guard rejects those toggle combinations; their clean
   completion (25×28, `verdict: CONSISTENT`) demonstrates 02 execution semantics.

Hashing static source files is **not** a re-run and does not alter any result. Per the binding
discipline these cells are treated as immutable staging evidence and are **not** re-run; they are
promoted by deterministic copy + SHA-256 manifest (see `overlay_evidence_manifest.json`).

Per-cell `git_commit` at run time differed (`35d3ced` / `b6fd732` / `3ae0269` / `7f0ebcb`) because
the cells were executed across one day; this is immaterial given the core-hash identity above —
the *algorithm bytes*, not the working-tree commit, define the frozen optimizer.
