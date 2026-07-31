# DT-GSK — Complexity Analysis

**Phase 3 deliverable** (Phase 3 task 11). Time/memory by mechanism, derived from the
**actual data-structure dimensions** in the source; `O(D^2)`/`O(D^3)` terms are claimed
only where the code supports them, and amortised by cadence. Per-generation costs are stated
for population size `NP` (≤ `5D`, shrinking under NLPSR) and dimension `D`. Objective-call
cost is separated from algorithmic overhead.

## Per-generation overhead (excluding objective evaluations)
| Mechanism | Time | Memory | Basis |
|---|---|---|---|
| GSK trial construction (junior+senior, KR mask) | `O(NP·D)` | `O(NP·D)` | vectorised over population×dims |
| Fitness sort / ranking | `O(NP·log NP)` | `O(NP)` | argsort each gen |
| NLPSR target + worst-cull | `O(NP)` (`O(NP·log NP)` if re-sorted) | `O(1)` | `_psr_target_size` is `O(1)`; cull is a partition |
| ACE sample + EMA update | `O(NP + M)`, `M`=5 arms | `O(M)` | per-individual arm draw + arm-credit EMA |
| ARGP prune | `O(M·W)` | `O(M·W)` | window bookkeeping |
| Linkage block mask | `O(NP·D)` | `O(D)` | block assignment |
| Bound repair | `O(NP·D)` | — | elementwise |
| Elite archive update | `O(|A|·D)` distance check | `O(|A|·D)`, `|A|≈1.5·NP_init` | distance-thresholded insert |
| BSE (when fired) | `O(r_rst·NP·D)` | `O(NP·D)` | Cauchy perturb + archive seed |

## Dimension-gated mechanisms
| Mechanism | Time | Memory | Basis / cadence |
|---|---|---|---|
| **SGSM interaction graph update** (D≥50) | `O(D^2)` per refresh (dense `D×D` accumulation) | **`O(D^2)`** for `G` | `interaction_graph.py` holds a `D×D` signed matrix; refreshed every `interaction_graph_refresh_period=5` gens → **amortised `O(D^2/5)`/gen**. Thinning (`interaction_update_period`, `interaction_update_max_samples`) can reduce further. |
| **Eigenframe polish** (D≥50, one-shot) | **`O(D^3)`** eigendecomposition of the `D×D` signed matrix, **once** near end of run | `O(D^2)` | `_final_polish_basis` diagonalises `G`; single occurrence ⇒ negligible amortised cost over the whole run |
| Subspace local search (D≥50) | `O(k·b)` per LS, `k`=top blocks, `b`≤`interaction_ls_dim_cap=20` | `O(k·b)` | bounded subspace, not full-D |
| D≥100 controllers (A1/A2/FC4, basin, SP-NLPSR) | `O(NP·D)` aggregate | `O(basin_max_size·D)`=`O(64·D)` | scalar controllers + bounded basin memory |

## Whole-run cost model
- **Dominant algorithmic term:** at D≥50, the SGSM `O(D^2)` refresh (amortised `O(D^2/5)`/gen)
  plus the **single** `O(D^3)` eigendecomposition. For D<50 no `D^2`/`D^3` interaction
  structures are allocated: the sub-20 tier is `O(NP·D)`/gen like GSK, and at 20≤D<50 the
  optional DE arm adds a vectorised donor selection — an `O(n_DE·NP)` partial select (up to
  `O(NP^2)` when most rows draw DE) — which is bounded compute, not budget.
- **Objective-cost separation:** with MaxFES=`10^4·D`, total objective work is
  `10^4·D · cost(f)`, **independent of the overhead above**. The overhead is sub-dominant to
  objective cost for any non-trivial `f`, and the SGSM/polish `D^2`/`D^3` terms are the price
  paid for the **zero-extra-evaluation** structure learning (they cost compute, not budget).
- **Memory:** the `O(NP·D)` population family (population + trial + 3-buffer RNG workspace,
  `NP_init=5D`) dominates at **every** tier — a few MB at D=100. The `O(D^2)` interaction
  state (three D×D accumulators + reusable scratch ≈ 0.5 MB at D=100) is a minority of the
  live footprint even where it is largest (a single D×D float64 matrix is 80 KB).

## Wording guards (QA)
- Report SGSM/polish as `O(D^2)`/`O(D^3)` **compute** cost, explicitly amortised (per-5-gen
  refresh; one-shot eigendecomposition) — never as "free."
- Do not claim overall complexity better than GSK; DT-GSK adds bounded overhead for
  structure learning, justified by dimension-gating so low-D runs pay none of the
  `D^2`/`D^3` structure-learning overhead (the 20≤D<50 DE-arm donor term is separate).
