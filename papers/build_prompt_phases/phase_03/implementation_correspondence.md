# DT-GSK — Implementation Correspondence

**Phase 3 deliverable** (Phase 3 task 9). Maps each equation / pseudocode block to code
files, functions, and stable symbols; flags dead code, undocumented behaviour, and any
prose-only mechanism. Line numbers are at anchor `262fc16c9`; symbols are stable across
minor line drift.

## Equation ↔ code
| Eq | Pseudocode step | File : function | Notes |
|---|---|---|---|
| E1a | junior indices | `gained_shared_junior.py:56 gained_shared_junior_r1r2r3` | Numba `junior_r1r2r3_core_fast`; pure-Python fallback shares the same r3_pool draws |
| E1b | senior indices | `gained_shared_senior.py:59/132` | `_round_away_from_zero` group boundaries; requires `0<p<0.5` |
| E2 | junior dim schedule | `_dt_core.py` Kexp path | `(1−x)^Kexp` |
| E3 | gaining-sharing update | `_numba_accel.py` gsk kernel | vectorised trial build |
| E4 | crossover mask | `_dt_core.py:926 _build_phase4_masks`, `:908 _make_linkage_groups`, `:839 _resolve_linkage_block_size` | per-coord KR OR block mask |
| E5 | NLPSR | `_dt_core.py:790 _psr_target_size`; `_numba_accel.py:909 _psr_target_nb` (`nl=frac**(1.0-frac)` @933) | round-half-up |
| E6 | ACE update | `_dt_core.py:1193 _ace_update_probs`, `:1163 _ace_sample_indices`; ARGP `:1261/:1304` | EMA + floor projection `_ace_project_probs:684` |
| E7 | bound repair | `bound_constraint.py:1` | L-SHADE midpoint |
| E8 | greedy accept | `dt_gsk_optimize:1974` accept block | strictly `<` |
| E9 | BSE | `_dt_core.py:1813 StagnationDetector`, `:1412 cauchy_like`, `:1640 EliteArchive` | triple trigger at D≥20 |
| E10 | SGSM graph | `_dt_subsystems/interaction_graph.py` (862 lines) | decay 0.95; confidence gate |
| E11 | eigenframe polish | `_dt_core.py:1882 _final_polish_basis`, `:1907 _final_polish_compass` | RNG-free; strict budget |
| E12 | RNG substreams | `_dt_rng.py` | 13 named, prefix-locked |

## Config-toggle ↔ mechanism (freeze targets)
`psr_enabled:153`, `ace_enabled:192`, `bse_enabled:193`, `arch_enabled:194`,
`linkage_blockwise_enabled:183`, `local_search_enabled:304`, `interaction_graph_enabled:324`,
`deep_stall_restart_enabled:444`, `final_polish_enabled:427`. All resolved by
`_dt_profiles.build_pub_config`.

## Findings
1. **No prose-only mechanism found** — every mechanism named in `docs/algorithms/dt-gsk.md`
   and the contribution matrix maps to executing code (verified for all 16 rows).
2. **Numba/pure-Python dual paths** (`gained_shared_*`, `_numba_accel`) are numerically
   convergent by construction (shared pre-drawn pools) — not dead code; the pure-Python path
   is the graceful fallback when Numba is unavailable. Byte-stability at D≥50 requires
   single-threaded Numba/BLAS (thread pinning) so SGSM reductions have fixed order.
3. **Default-OFF fields that the `pub` profile turns ON** (`linkage_blockwise_enabled`,
   `local_search_enabled`, `interaction_graph_enabled`) — dataclass default `False` is the
   bare fallback; not dead, activated per tier. Reviewers must read the *resolved* profile,
   not the dataclass, to see what runs.
4. **Experimental/off-by-default scalars** (`ace_coverage_weighted`, `terra_*`,
   `init_oversample`, `init_method="lhs"`, V4 A1/A2/FC4 defaults) are **no-ops in the locked
   headline** and excluded via `_ALGORITHM_EXCLUDE_KEYS`; they must NOT be described as part
   of the shipped method. Flagged for the Phase 4 claim freeze.
5. **Profile-lock constraint:** `scripts/validate_profile_lock.py` enforces byte-identical
   ISM core sources; any in-file instrumentation (even semantics-preserving) fails the clean
   profile-lock exit criterion. Traces MUST come from `ISMTrace_*.jsonl` telemetry or
   runner/evaluator wrappers (see `deterministic_trace/README.md`).

## Prose-code conflicts
**None unresolved.** The one wording risk (SGSM/polish "free") is dispositioned in
`contribution_matrix.md` and `evaluation_accounting_report.md`: free of extra *objective
evaluations*, not free of *compute*.
