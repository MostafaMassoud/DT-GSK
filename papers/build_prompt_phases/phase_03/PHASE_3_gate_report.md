# Phase 3 — Method Reconstruction, Code Correspondence, and Algorithm Freeze — Gate Report

- **Phase:** 3 (PAPER_BUILD_PROMPT.md lines 3410–3628)
- **Anchor commit:** `708a927bf525a74eaec41c7efc10820a4af6442b`
- **Evidence release:** `rel-2026-07-10-262fc16c9` (Phase 2 FROZEN)
- **Gate date:** 2026-07-10
- **Verdict:** **APPROVED — Phase 3 FROZEN** (algorithm + parameters frozen; residual
  format-renderings and high-D dynamic traces tracked, and cannot alter the frozen definition)
- **Signatories:** P2 + P4 + P5 + P9 (framework Gate 3 quorum)

## 1. Deliverables produced (`papers/build_prompt_phases/phase_03/`)
| Output (framework) | File | Status |
|---|---|---|
| Contribution decomposition | `contribution_matrix.md` | ✅ 16 mechanisms classified INH/MOD/ORI with code anchors |
| Ablation toggle audit | `ablation_toggle_audit.md` | ✅ 6 toggles verified single-component (2 documented couplings) |
| Evaluation accounting | `evaluation_accounting_report.md` | ✅ single cap, all calls charged, budget-safe |
| Notation (canonical) | `notation_table.md` | ✅ every pseudocode/equation symbol defined |
| Pseudocode (canonical) | `algorithm_pseudocode.md` | ✅ order/gating match `dt_gsk_optimize` |
| Equation registry | `equation_registry.csv` | ✅ E1–E12 with labels + code anchors + class |
| Parameter freeze | `parameter_table.md` | ✅ `pub` tier-resolved values |
| Complexity | `complexity_analysis.md` | ✅ per-mechanism, O(D²)/O(D³) code-substantiated + amortised |
| Implementation correspondence | `implementation_correspondence.md` | ✅ eq↔code, no prose-only mechanism |
| Deterministic trace | `deterministic_trace/` | ✅ real fixed-seed run + witness JSON + README |
| Algorithm freeze manifest | `algorithm_freeze_manifest.json` | ✅ source hashes + change-control rule |

## 2. Independent verification performed
- **Code correspondence (P2 basis):** all 16 contribution-matrix mechanisms traced to
  executing code; **no prose-only mechanism** (`implementation_correspondence.md` §Findings).
  GSK junior/senior index selection read directly (`gained_shared_{junior,senior}.py`);
  main-loop order confirmed against `dt_gsk_optimize:1974` and the byte-locked spec.
- **Evaluation accounting (P4):** `BudgetController` is the single cap; `nfes_used += n`
  then bound-checked; truncation gives budget-safe final batch. Verified live by the
  deterministic trace: **`nfes_used == 3000 == MaxFES`**, best-so-far **monotone**,
  **repeat-identical** — all true.
- **Freeze integrity (P5):** core source SHA-256 recorded; byte-identity enforced by
  `validate_profile_lock.py` + `test_dt_gsk_byte_stable.py`; profile oracle by
  `test_dt_profiles.py`. Engineering gate green at this anchor (pytest 339, ruff clean).
- **Contribution boundaries (P9):** INH/MOD/ORI each cite the closest approved evidence
  card; novelty scoped to control/budget/structure-memory/polish — **no new-operator claim**;
  "free" wording dispositioned to "no extra *objective* evaluations."

## 3. QA checkpoints (framework §Quality-assurance)
- No undefined symbol ✅ (notation covers all) · No mechanism without purpose/timing/cost/
  fallback ✅ · No prose-only mechanism ✅ · No material code behaviour omitted ✅ ·
  No unsupported "free"/"negligible" wording ✅ (complexity states O(D²)/O(D³) amortised).

## 4. Residual items (tracked; do NOT affect the frozen algorithm definition)
1. **`.tex` / `.omml.xml` renderings** of notation/pseudocode/parameter tables — deferred to
   **Phase 7/9**, generated from the canonical `.md` sources here (framework routes Word/LaTeX
   production to those phases). Renderings cannot change the frozen definition.
2. **High-D dynamic trace (D≥50 SGSM/polish; D≤30 deep-stall)** — the Phase-3 micro-trace
   (D=10, 3000 NFE) validates the base loop; SGSM/polish/deep-stall are **statically**
   code-verified here and will get **dynamic** witnesses in **Phase 6** against the frozen
   release. Documented in `deterministic_trace/README.md`.
3. **P2 line-by-line replay** of one full high-D iteration — the structural walk is done;
   the exhaustive replay is scheduled with the Phase 6 trace.

## 5. Sign-off
- **P2 (method/code):** APPROVED — reconstruction reimplementable; code↔pseudocode agree.
- **P4 (accounting):** APPROVED — MaxFES-exact, budget-safe (live-verified).
- **P5 (integrity):** APPROVED — algorithm + parameters hash-frozen; profile-lock enforced.
- **P9 (evidence/claims):** APPROVED — contribution boundaries evidence-based; wording guards set.

**Gate 3 APPROVED. Phase 3 FROZEN 2026-07-10.** Any change to the frozen core, `pub`
profile, or mechanism inventory invalidates Phases 3+ and requires a
`change_request_register.csv` row (Section 12.2). Phase 4 entry (thesis/claims freeze) is
unblocked and inherits the contribution matrix + novelty statement as its claim source.
