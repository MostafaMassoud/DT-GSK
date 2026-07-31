# DT-GSK — Ablation Toggle Audit

**Phase 3 deliverable** (PAPER_BUILD_PROMPT.md Phase 3, task 13: *define ablation
toggles without running them*). Audits `scripts/run_ablation.py` and the config
keys it flips, verifies each toggle's semantics against
`src/gsk_family/optimizers/_dt_core.ISMGSKConfig`, and confirms each toggle
disables **only** its intended component. **No ablation outcomes are inspected here.**

## 1. Cell design (from `run_ablation.py`)
- **Driver:** `scripts/run_ablation.py`; aggregator `papers/scripts/generate_ablation_matrix.py`.
- **Default mode `remove-one`:** `baseline` (full scaffold) + one `no_<m>` cell per
  mechanism that sets that mechanism's flag `False`. Six mechanisms → **7 cells**.
- **Alt mode `add-one` (ATMALS-style):** `base` (all six off) + one `only_<m>` cell each.
- **SGSM held OFF in every scaffold cell** via `_SGSM_OFF = {"interaction_graph_enabled": False}`
  (`run_ablation.py:52`) — the SGSM overlay is ablated separately on the CEC2013 hold-out
  (`full`/`no-adaptive`/`no-sgsm`), not here. This is a deliberate design choice, disclosed.

## 2. The six audited toggles (`MECHANISMS`, `run_ablation.py:59`)

| Cell flag | Config field (default) | Component disabled | Verified single-component? | Code anchor |
|---|---|---|---|---|
| `ace_enabled` | `ace_enabled=True` (`:192`) | ACE bandit; falls back to fixed `(KF,KR,Kexp)` + heterogeneous-Kexp path | **Yes** — gates only the ACE sampling/update; operator core untouched | `_ace_sample_indices:1163`, `_ace_update_probs:1193` |
| `psr_enabled` | `psr_enabled=True` (`:153`) | NLPSR population reduction; population stays at `NP_init` | **Yes** — gates only `_psr_target_size`; note paired `sp_nlpsr_enabled` is a **separate** D≥100 subspace floor (independent) | `_psr_target_size:790` |
| `bse_enabled` | `bse_enabled=True` (`:193`) | Budget-safe escape (Cauchy rescue + archive restart) | **Yes** — gates the StagnationDetector-driven escape; **note distinctness from `deep_stall_restart_enabled`** (a separate restart, NOT disabled by this flag) | `StagnationDetector:1813` |
| `linkage_blockwise_enabled` | `linkage_blockwise_enabled=False`* (`:183`) | Linkage-aware block crossover; reverts to per-coordinate KR mask | **Yes** — gates only the block-mask path in `_build_phase4_masks` | `_build_phase4_masks:926` |
| `local_search_enabled` | `local_search_enabled=False`* (`:304`) | Nelder–Mead / coordinate endgame local search | **Yes** — gates only the LS block | `_final_polish_*`/LS path |
| `arch_enabled` | `arch_enabled=True` (`:194`) | Elite archive (also removes BSE archive-seed source) | **Partial** — disabling the archive also removes BSE's archive-injection seed. Documented coupling: `arch` and `bse` interact by design (BSE `bse_archive_inject_prob`). Flag still disables exactly the archive object; the coupling is a real algorithmic dependency, not a toggle leak. | `EliteArchive:1640` |

\* Dataclass default is `False`; the **`pub` profile enables these at the appropriate
tiers**. In the ablation, cells are built on top of the `pub` profile (the runner resolves
`pub` then applies `optimizer_options`), so `no_linkage`/`no_localsearch` genuinely turn OFF
a component the baseline had ON at that dimension. Confirm per-dimension that the `pub`
profile enabled the mechanism before reporting a "disable" delta (e.g. `local_search` and
SGSM-dependent polish are only ON at D≥50).

## 3. Toggle-semantics findings
1. **Each of the six flags gates exactly one component** in `_dt_core`, with two
   **documented, intended couplings** that MUST be disclosed in the ablation write-up:
   - `arch_enabled=False` also removes BSE's archive-seed source (BSE still fires Cauchy).
   - `bse_enabled` does **not** disable the deep-stall restart (`deep_stall_restart_enabled`)
     — they are distinct stagnation responses. A "no escape" reading of `no_bse` is therefore
     **incomplete**; the deep-stall multi-start remains active.
2. **SGSM (`interaction_graph_enabled`)** is off in all scaffold cells; any SGSM contribution
   is quantified only in the separate CEC2013 SGSM-overlay ablation. Do not attribute SGSM
   effects to any scaffold cell.
3. **Excluded extras** (`run_ablation.py:67`): `argp_enabled` (minor control),
   `final_polish_enabled` (SGSM-dependent → belongs to the SGSM ablation), and
   `deep_stall_restart_enabled` (overlaps BSE stagnation) are intentionally **not** in the
   6-mechanism scaffold set. This exclusion is a reportable scope limit, not an omission.
4. **Determinism guarantee:** because every subsystem draws from its own append-only RNG
   substream (`_dt_rng.py`, 13 streams), toggling one flag does not disturb the others'
   draw order — the ablation deltas are attributable to the disabled component, not to RNG
   drift. This is the precondition that makes the ablation valid.

## 4. Verdict
The six-mechanism scaffold ablation is **toggle-valid** for isolating ACE, NLPSR, BSE,
linkage crossover, local search, and archive, **provided** the two intended couplings
(arch↔BSE seed; BSE↔deep-stall distinctness) and the SGSM-held-off scope are disclosed in
the manuscript, and provided per-dimension baseline-ON status is checked before claiming a
disable delta. No toggle disables more than its intended component beyond the documented
archive→BSE-seed dependency. **Recorded without running any cell** (Phase 3 constraint).
