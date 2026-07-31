# Phase 2 — Immutable Empirical Evidence, Benchmark, and Provenance Audit — Gate Report

- **Phase:** 2 — Immutable empirical evidence, benchmark, and provenance audit
- **Master framework:** `papers/PAPER_BUILD_PROMPT.md` (Phase 2, lines 3166–3406)
- **Anchor commit:** `262fc16c91fbe5608a1a0b0c5df3cbcd009edc21`
- **Release bound:** `rel-2026-07-10-262fc16c9` → `papers/analysis/rel-2026-07-10-262fc16c9/`
- **Gate date:** 2026-07-10
- **Verdict:** **APPROVED — Phase 2 FROZEN**
- **Signatories:** P3 + P4 + P5 + P9 (framework Gate 2 quorum; the register seed `P2;P5;P9`
  is corrected to the master Review-gate signatories, exactly as Gate 1 corrected its seed list).

---

## 1. Scope and evidence source

Phase 2 audits the sole immutable empirical evidence source
`benchmarks/cec_reference_results/` (the "reference tree"), freezes evaluator
versions/hashes, binds the release id, and certifies that no downstream artifact
may draw empirical values from anywhere else. `results/` remains staging-only and
enters the pipeline only through the Section 2.4 controlled promotion in Phase 12.

The frozen release is `rel-2026-07-10-262fc16c9` (evidence_root
`benchmarks/cec_reference_results`, anchor `262fc16c9…`), recorded in
`evidence_release_manifest.json` and `data_ledger.csv`.

## 2. Evidence artifacts (all present, parsed, non-empty)

| Artifact | Role | Certified this session |
|---|---|---|
| `evidence_release_manifest.json` | per-file SHA-256 immutability manifest | **3,409** file entries, **3,409** `sha256` values, `totals.files=3409`, 712,038,425 bytes; class-counts sum to 3,409 |
| `data_ledger.csv` | dataset-level ledger (algorithm × suite × dim) | 174 data rows (+header) with `n_runs`, `pairing_design`, `function_set`, `suite_version`, `algorithm_version` |
| `phase2_anomaly_register.csv` | anomaly taxonomy + disposition | present (16 KB); apgsk cec2017 partial-provenance defect logged + dispositioned |
| `benchmark_protocol_audit.md` (+ part2) | protocol / budget / run-count audit | present (32 KB) |
| `comparability_audit.md` | cross-algorithm comparability | present (16 KB) |
| `seed_and_pairing_audit.md` | seed schedule + pairing design | present (10 KB) |
| `fp_environment_audit.md` | floating-point regime / sentinel | present (10 KB) |
| `reference_inventory.csv` | reference-tree inventory | present (43 KB) |
| `reproducibility_manifest.json` | determinism / environment record | present (23 KB) |
| `staging_inventory.md` | staging-vs-reference separation | present (5 KB) |
| strict-source guard | tooling enforcement | `result_loader.set_strict_source`, `StrictSourceViolation`, source audit |

## 3. Independent re-verification performed at gate time

These checks were re-executed this session (not accepted on the producing agent's word):

1. **Immutability-manifest coverage.** Walked `benchmarks/cec_reference_results/`:
   **3,409** files on disk == `totals.files` (3,409) == `sha256` entry count (3,409).
   File-class decomposition (curve_csv 1554, gen_log_csv 1554, summary_csv 174,
   per_run 21, environment_json 21, run_config_json 21, seed_schedule 21,
   phase0_protocol_json 21, verification_json 21, tree_readme 1) sums to 3,409.
2. **Evidence-tree cleanliness.** Manifest records
   `git status --porcelain -- benchmarks/cec_reference_results` empty at hash time;
   HEAD verified == anchor `262fc16c9…`.
3. **Traceability consistency (backbone debt cleared).** `PAPER_BUILD_PROMPT.md` is
   7,759 total / 6,146 non-blank lines; `source_line_traceability.csv` carries
   **6,146** rows == non-blank count, `line_no` unique, `min=1`, `max=7,759`==total.
   The CR-0003 re-patch flagged "OUTSTANDING" in the Phase 1 note is therefore
   **DONE** (verified this session); `requirements_traceability_matrix.csv` = 2,153 rows.
4. **Engineering gate.** `pytest -q` → **339 passed**, 2 benign warnings
   (`dim=4` linkage-block smoke edge; not a scientific path). `ruff check .` →
   **clean** after removing 5 unused-import `F401`s in
   `papers/governance/audit_evidence/{phase2_tasks678_audit,seed_env_audit}.py`.
5. **Strict-source guard.** `tests/unit/test_strict_source_guard.py` → 15 passed;
   guard blocks staging paths under `GSK_STRICT_SOURCE`, default OFF preserves
   legacy behaviour; `scripts/promote_evidence.py` present with working `--help`.

## 4. Dispositioned anomaly (disclosed, non-blocking)

- **A2 / group H1 — apgsk cec2017 partial auxiliary provenance.** `apgsk`'s
  cec2017 `per_run.csv`, `seed_schedule.csv`, `environment.json`, and
  `run_config.json` cover **D100 only**; the per-dimension **summary CSVs**
  (the empirical values used for ranking) are complete. This is a
  provenance-completeness gap on one comparator's auxiliary files, **not** an
  empirical-value mismatch and **not** a comparability defect. It is recorded in
  `phase2_anomaly_register.csv` and `benchmark_protocol_audit.md`, disclosed in the
  release manifest `known_defect_note`, and **dispositioned NON-BLOCKING at Gate 2**
  with the requirement that any apgsk cec2017 provenance claim be qualified to D100.
  No silent repair was performed; the release is hashed exactly as frozen.

## 5. Gate 2 hard-failure checks (framework line 3404)

| Blocking condition | Status |
|---|---|
| Any empirical source outside `cec_reference_results` | **NONE** — strict-source guard enforces; loader is reference-first |
| Unexplained run mismatch | **NONE** — the sole mismatch (apgsk aux provenance) is explained + dispositioned |
| Invalid evaluation budget | **NONE** — budget/run-count audit clean in `benchmark_protocol_audit.md` |
| Unresolved comparability defect | **NONE** — `comparability_audit.md` resolved |

## 6. Acceptance

All Phase 2 acceptance criteria PASS on the evidence above. The release
`rel-2026-07-10-262fc16c9` is frozen and bound to `papers/analysis/<release_id>/`;
evaluator versions/hashes and the SHA-256 ledger are frozen; downstream phases
MUST source empirical values only from this release.

## 7. Sign-off

- **P3 (method/data):** APPROVED — evidence source single, immutable, hash-locked.
- **P4 (statistics/accounting):** APPROVED — run-count/budget/pairing ledger valid;
  apgsk aux-provenance gap dispositioned with a binding qualification.
- **P5 (reproducibility/integrity):** APPROVED — 3,409/3,409 hashes, tree clean at
  anchor, engineering gate green, strict-source guard enforced.
- **P9 (evidence/traceability):** APPROVED — traceability consistent with the master
  (6,146 rows == non-blank), anomaly disclosed not repaired.

**Gate 2 APPROVED. Phase 2 FROZEN 2026-07-10.** Reopening requires a
`change_request_register.csv` row per Section 12.2. Phase 3 entry criterion
("Phases 0–2 are frozen") is now satisfied.
