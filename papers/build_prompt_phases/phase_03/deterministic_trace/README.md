# Phase 3 — Deterministic Trace

**Source constraint (Phase 3 task 12 / mitigation).** The ISM core sources are
profile-locked (`scripts/validate_profile_lock.py` enforces byte-identity; even
semantics-preserving in-file instrumentation fails the clean profile-lock exit
criterion). This trace is therefore captured at the **result/telemetry layer** —
`OptimizerResult.convergence` (best-so-far vs. nfes) plus the returned
`best_fitness`/`nfes` — **without touching the locked core**.

## Reproduce
```bash
python papers/build_prompt_phases/phase_03/deterministic_trace/make_trace.py
```
Fixed inputs: CEC2017 F1 (shifted-rotated sphere), D=10, MaxFES=3000, seed=20240620,
threefry. Output: `trace_cec2017_F1_D10_S20240620.json`.

## What it validates (pseudocode ↔ execution)
| Claim (algorithm_pseudocode.md) | Trace field | Result |
|---|---|---|
| Budget-exact accounting (`evaluation_accounting_report.md`) | `budget_exact` / `nfes_used` | **true** / 3000 == MaxFES |
| Returns monotone global-best (steps 10–13) | `best_so_far_monotone_nonincreasing` | **true** |
| Same seed → identical result (E12 substreams) | `determinism_repeat_identical` | **true** |
| Self-init fair-start exception (contribution row 16) | `notes` | `self-init (fair-start exception)` |

MaxFES=3000 is below `deep_stall_min_budget=20000`, so the deep-stall restart is inert
here (byte-safe small-budget path) — the trace exercises the base loop + NLPSR + ACE +
accept without restart perturbation, matching the pseudocode's non-restart branch.
Larger-budget traces (which do exercise SGSM/polish at D≥50 and deep-stall at D≤30) are
produced in Phase 6 against the frozen release; this micro-trace is the Phase-3 freeze
witness.
