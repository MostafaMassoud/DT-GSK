# Phase 11 — Phase-12 Entry Prerequisites Verification (Task 11)

**Phase / task:** Phase 11, task 11 — verify, before signing the Gate-11 certificate, that
every artifact Phase 12 depends on is intact, complete, and leak-free.

- **Anchor commit:** `cffcbb48153fd6395c67bb35ece0107269c15694`
- **Evidence release in force:** `rel-2026-07-10-262fc16c9` (primary; immutable, read-only)
- **Overall result: ALL GREEN (6/6).**

---

## Checklist

| # | Prerequisite | Result | Evidence |
|---|---|:---:|---|
| P1 | `algorithm_freeze_manifest.json` intact (hash matches phase_03 record) | **PASS** | §1 |
| P2 | `ablation_preregistration.md` complete + PHASE_12_ONLY | **PASS** | §2 |
| P3 | `ablation_toggle_audit.md` complete | **PASS** | §3 |
| P4 | `scripts/promote_evidence.py` operational (`--help`) | **PASS** | §4 |
| P5 | `results/_ablation` campaign present (7 cells) + `_ablation_repair` baseline D100 validated | **PASS** | §5 |
| P6 | No historical-result leakage | **PASS** | §6 |

---

## 1. P1 — Algorithm freeze manifest intact

- File: `papers/build_prompt_phases/phase_03/algorithm_freeze_manifest.json`
- Computed SHA-256: `88dbabd40a3b1c37b62b25287661c36db26efa46fa309a44066fabf07a314c7c`
- Recorded SHA-256 (Phase-3, `papers/governance/artifact_binding.csv`, row ART-PARAMS):
  `88dbabd40a3b1c37b62b25287661c36db26efa46fa309a44066fabf07a314c7c`
- **MATCH → PASS.** The manifest still pins the frozen core hashes
  (`dt_gsk.py` a274e0f8, `_dt_core.py` 1ef815ce, `_dt_profiles.py` c3dcdce3,
  `_dt_rng.py` db1cc028, subsystems merkle e532fc44) that Phase 12 must ablate against.

## 2. P2 — Ablation pre-registration complete + PHASE_12_ONLY

- File: `papers/build_prompt_phases/phase_05/ablation_preregistration.md`
- Header and every section carry the **`PHASE_12_ONLY`** status marker; explicit no-inspection
  attestation present ("no statistical outcome, rank, p-value, mean, or curve … was computed,
  read, or viewed"). Design is complete: X-ABL-01 scaffold remove-one (7 cells, CEC2017,
  D10/30/50/100, 25 runs), X-ABL-02 SGSM overlay (4 cells, CEC2013, D50/100), X-ABL-03
  statistical family (Wilcoxon+Holm, Friedman ranks, A12, BCa), overhead/convergence/sensitivity
  requirements, the §5 execution gate + Section-2.4 promotion, and secondary designs 6.1–6.3.
- **PASS.** Nothing in the document may execute before an all-green
  `phase12_entry_certificate.md`.

## 3. P3 — Ablation toggle audit complete

- File: `papers/build_prompt_phases/phase_03/ablation_toggle_audit.md` (5,438 bytes)
- Documents the driver `scripts/run_ablation.py`, the 7-cell remove-one design, the six audited
  toggles verified single-component against `ISMGSKConfig`, `_SGSM_OFF` scope, and the two
  mandatory couplings (arch→BSE seed source; BSE vs deep-stall distinctness). No outcomes inspected.
- **PASS.**

## 4. P4 — Promotion tool operational

- `python scripts/promote_evidence.py --help` returns usage (args:
  `--staging --suite --optimizer --release-id [--dest] [--dry-run]`), described as "Promote an
  accepted staging bundle into a new versioned subtree under the immutable evidence root
  (Section 2.4)." Exit 0.
- **PASS.** This is the sole sanctioned path from `results/_ablation` staging into a versioned
  immutable ablation release.

## 5. P5 — Ablation staging present + repair validated

**Seven remove-one cells present** under `results/_ablation/<cell>/dt-gsk/cec2017/`:
`baseline, no_ace, no_arch, no_bse, no_linkage, no_localsearch, no_psr`.

Per-run provenance (row counts only — **outcome never inspected**):

| Cell | per_run rows | Expected (29×4×25) |
|---|---:|---:|
| baseline | 2,894 | 2,900 (six F25-D100 runs short) |
| no_ace / no_arch / no_bse / no_linkage / no_localsearch / no_psr | 2,900 each | 2,900 ✓ |

**Baseline D100 repair VALIDATED** (`results/_ablation_repair/baseline/dt-gsk/cec2017/`, 725
per_run rows = 29×25): per `staging_inventory.md` dated note 2026-07-11 (exit 0), the repair
byte-matched all 719 overlapping original D100 rows on every scientific column
(optimizer/suite/function/dimension/run/seed/best_fitness/error/nfes/termination), **0
mismatches**, and recovered the 6 missing F25-D100 runs; the only differing column is
`runtime_seconds` (environment-dependent; not an ablation endpoint). Phase-12 composition
decision recorded there: baseline D100 = repair slice; baseline D10/30/50 = original campaign;
disclose in the promotion record.
- **PASS.** (Consistency with `staging_inventory.md` confirmed.)

## 6. P6 — No historical-result leakage

- `benchmarks/cec_reference_results/ablation/` — **absent** (no promoted ablation release exists;
  Phase-12-only).
- `results/ablation/` aggregate CSVs — **absent** (Phase-12-only per `staging_inventory.md`).
- All `results/_ablation*` trees are **quarantined staging**, non-admissible until the Section-2.4
  promotion in Phase 12; the Phase-6 analysis bundle was produced under the strict-source guard
  (`GSK_STRICT_SOURCE`) with **zero ablation reads** (Gate-6 record). The no-ablation scan
  (`no_ablation_scan.md`) confirms zero rendered ablation content in the shipped artifacts.
- **PASS.**

---

**Prerequisites verdict: ALL GREEN (6/6). Phase 12 entry is unblocked on the artifact-integrity
axis; the Gate-11 certificate may be signed.**
