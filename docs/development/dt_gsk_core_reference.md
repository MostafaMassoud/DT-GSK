# DT-GSK Core Reference — the vendored core and its byte-identity lock

> The single authoritative description of DT-GSK's vendored core: what is locked, why,
> which tests hold the line, and the facts most often got wrong. The
> [Developer Guide](developer_guide.md), [Contributor Guide](contributor_guide.md),
> [Extension Guide](extension_guide.md) and [Maintenance Guide](maintenance_guide.md)
> all link here rather than restating it.
>
> The **rules** live in [PROJECT_RULES.md](../../PROJECT_RULES.md) §4–§5 and
> [CODING_STANDARD.md](../../CODING_STANDARD.md) §5. This page explains them.

## What DT-GSK is (and what the letters mean)

**DT-GSK = Dimension-Tiered Gaining-Sharing Knowledge.** The mechanisms it activates are
gated by problem dimension, and that tiering is the method's defining property.

**ISM = Interaction-Structure Memory.** This is the name of *one subsystem inside*
DT-GSK — the accepted-move coordinate-pair graph — **not** an expansion of DT-GSK, and
not the algorithm's name. The project was renamed `ISM-GSK` → `DT-GSK` and only the
component name survives. Glossing the algorithm as "DT-GSK (Interaction-Structure
Memory GSK)" --- as several pages of this documentation once did --- is wrong: the
**D** and the **T** stand for *Dimension-Tiered*.

ISM is a **specified negative result**, not a contribution — and it has been dropped from
the paper's keywords. The paper's three contributions are the **deterministic** final
polish (C1), the dimension-tiered adaptive scaffold (C2), and the controlled
seven-algorithm family evaluation (C3); C1 is claimed **basis-neutrally** — the endgame is
what is claimed, not the basis it searches along. Two isolations bound the memory. The
`no_sgsm` ablation cell, which toggles the graph off at its active tiers, finds **no
statistically significant standalone benefit** under Holm correction. The three-arm basis
isolation added in revision (Supplementary Section S9.1) goes further: at fixed enablement
the plain coordinate axes **outperform** the learned eigenframe at D=50 (Holm 1.4e-4, 25
of 29 functions) and, under the canonical 1e-8 tie rule, at D=100 as well (Holm
0.0489) — while the polish itself beats no
refinement at both active dimensions (22/2/5 at D=50, 23/1/5 at D=100; the coordinate arm
28/1/0 and 25/1/3). Never describe either result as an improvement or a gain from ISM.

Describing what the code *does* — computing an eigenbasis of the signed interaction matrix
and polishing along it — is **correct**, and that is what the rest of this page does.
Presenting that eigenbasis as a contribution, as a benefit, or as an open question is not.

## The locked surface

These files are **vendored**: they were migrated byte-identically from the source
DT-GSK v2.1 project and **must not be edited for behavior** — no refactors, no renames,
no reformatting, no "improvements".

| Path | Role |
|---|---|
| `optimizers/_dt_core.py` | the algorithm (~5,000 lines) |
| `optimizers/_dt_subsystems/` | `bound_constraint.py`, `budget.py`, `budget_policy.py`, `basin_memory.py`, `gained_shared_junior.py`, `gained_shared_senior.py`, `interaction_graph.py`, `_numba_accel.py`, `_dt_provenance.py` |
| `optimizers/_dt_rng.py` | the 13-substream RNG layer |
| `optimizers/_dt_profiles.py` | `build_pub_config` — **data, not logic; never hand-edit a value** |
| `optimizers/dt_gsk.py` | the adapter onto the runner's optimizer contract |

New DT-GSK functionality is added **around** the core, never inside it. The adapter is
the correct place for anything the runner needs.

**The docstring gate deliberately exempts `_dt_core.py` and `_dt_subsystems/*`**
(`tests/unit/test_docstrings.py`). Do **not** add docstrings to vendored code to satisfy
the gate — that perturbs the vendored bytes, which is the very thing the lock exists to
prevent.

## What holds the line

| Gate | Test | What it locks |
|---|---|---|
| Config KAT | `tests/unit/test_dt_profiles.py` | `build_pub_config` output, per tier |
| RNG KAT | `tests/unit/test_dt_rng.py` | the 13 substreams and their seeds |
| Byte-stable golden | `tests/regression/test_dt_gsk_byte_stable.py` | the trajectory itself |
| Curve monotonicity | `tests/regression/test_dt_gsk_curve_monotone.py` | the best-so-far convergence contract |
| Graph backend parity | `tests/regression/test_dt_graph_backend_parity.py` | compiled kernels are bound, and bit-identical to the NumPy path |
| Polish incumbent | `tests/regression/test_dt_polish_incumbent_consistent.py` | the polish receives a self-consistent incumbent |

The golden values were validated **byte-identical against the source project** at
`seed=12345`, `max_nfes=3000`, `pub` profile.

**If a golden goes red, investigate the drift — never edit the golden to silence it.**

> ### The byte-stable KAT does not cover everything
> Its cells are **D ≤ 30**, which is *below* the tier where the interaction graph and the
> final polish activate. It therefore cannot see a defect in either. This is not
> hypothetical: an interaction-graph import typo silently selected the NumPy fallback for
> the entire released campaign, and the KAT stayed green throughout. The two D≥50
> regression tests above exist to close that gap. **When you touch a D≥50 mechanism, the
> byte-stable KAT passing tells you nothing.**

## Dimension tiers

The `pub` profile switches mechanisms on by dimension. Know which tier your change lives in:

| Tier | Adds |
|---|---|
| `D < 20` | base scaffold (+ escape overrides) |
| `20 <= D < 50` | D30 best-status handling |
| **`D >= 50`** | **SGSM interaction graph, adaptive confidence gate, eigenframe final polish** |
| **`D >= 100`** | **TERRA, budget policy, basin memory, SP-NLPSR, late-accept clipping** |

Consequence: a change to the interaction graph or the polish **cannot** affect D10/D30,
and a D≤30 test **cannot** exercise them.

## Facts that are routinely got wrong

**Initial population is always `5*D`.** `np_init_mult = 5` and is *never overridden* at
any dimension. DT-GSK self-initializes and **ignores any injected `X0`** — a documented
fair-start exception (PROJECT_RULES §4.5). Do not "fix" it.

> Earlier revisions of these guides claimed `5*D` below D=40 and `10*D` above. **That was
> false.** The 5-below/10-above split belongs to `_DEFAULT_BLOCK_SIZES`, the linkage
> **block-size** schedule in `_dt_profiles.py` — a different parameter entirely.

**Deep-stall restart ships default-ON** (`deep_stall_restart_enabled=True`,
`deep_stall_frac=0.25`, `deep_stall_min_budget=20000`). It draws RNG **only when it
fires**, and the min-budget guard keeps it inert at the golden's `max_nfes=3000`, which is
why it is byte-safe. Every real CEC run (`>= 10000*D`) clears the guard.

**Seeding is unified and non-negotiable.** `dt-gsk` is the sole member of
`UNIFIED_ONLY_OPTIMIZERS`: it is forced onto `threefry` + `get_cec_seed` under *every*
seed policy. The 13 substreams (`init, core, ace, kexp, div, bse, arch, link, de,
control, flow, basin, trust`) are **append-only** and the first nine are prefix-locked.

**Supplying a callback does not change results.** The FC4 lift-EMA is the only
fitness-affecting quantity in the per-generation telemetry block, and it is updated
*above* the callback guard on purpose. A run with no callback, a curve callback, or a
full generation callback produces bit-identical results — verified at D=100, where FC4 is
actually live (it is disabled at D=50). If you relocate that update, you break this
property.

**The local search that runs is coordinate descent, not the ISM subspace search.**
`local_search_method` defaults to `"coordinate"`, and the `pub` profile keeps it there at
every tier — defaulted at `50 <= D < 100`, and set *explicitly* to `"coordinate"` at
`D >= 100`. The ISM top-k **subspace** local search (`subspace_nm`, which would restrict the
polish to the interaction graph's strongest blocks) is **implemented but not enabled** in
the frozen configuration — the core states this at its own definition site. The interaction
graph still *informs* linkage and block selection at `D >= 50`
(`interaction_use_for_local_search=True`), but the search that executes is coordinate-wise.
Do not claim DT-GSK runs a graph-guided subspace polish; it does not.

## Determinism at D 50 and above

SGSM uses `prange`, so thread count changes floating-point reduction order. For any
byte-identity work, export all six variables **before Python imports numpy/numba** —
setting them inside Python has no effect — and run `--serial` or `--workers 1`:

```powershell
$env:OMP_NUM_THREADS=1; $env:MKL_NUM_THREADS=1; $env:OPENBLAS_NUM_THREADS=1
$env:VECLIB_MAXIMUM_THREADS=1; $env:NUMEXPR_NUM_THREADS=1; $env:NUMBA_NUM_THREADS=1
```

For a *campaign* (rather than a parity check), process-level parallelism is still safe
with `--numba-threads 1`: each cell's seed is a pure function of
`(base_seed, dim, func, run)`, independent of worker count or execution order.

## If you must change core behavior

You cannot do it silently. A behavior change at `D >= 50` invalidates the evidence
produced by the old binary, so it forces a regeneration campaign. The procedure — the
affected-cell inventory, the determinism setup, and the manuscript edits that follow —
is in the [Evidence Re-run Runbook](evidence_rerun_runbook.md).
