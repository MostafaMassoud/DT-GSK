# EGSK — Algorithm Spec & Porting Verdict

Algorithm specification and porting verdict for the EGSK optimizer (now shipped
as `optimizers/egsk.py`). Source of truth for the port:
`01-GSK_Family_MATLAB_v1.0/gsk_family/src/optimizers/egsk/`.

> **Outcome (post-Phase 0): Option A was implemented.** EGSK is now a runnable optimizer
> (`src/gsk_family/optimizers/egsk.py`) — a faithful port whose interior-point refinement uses
> `scipy`-SLSQP in place of MATLAB `fmincon`, validated by a paired per-run test. See
> [egsk.md](../algorithms/egsk.md) and
> [egsk_validation_appendix.md](../research/egsk_validation_appendix.md). The options below are the
> original Phase 0 analysis; Option A is the one that shipped.

## 1. What EGSK is (Enhanced GSK)
Base GSK (junior/senior gaining-sharing over a fixed population of NP=100) **plus three enhancements**:
1. **Dual adaptive knowledge factors KF1 (junior) & KF2 (senior).** Constant `0.5` until late stage
   (`g >= 0.75·G_Max`), then recomputed **per individual** via a triangular membership function over
   ranked-fitness anchors (KF1: `fitness(Rg1,Rg3,Rg2)`; KF2: scalar `fitness(min R1,min R2,min R3)`),
   clamped to `[0,1)`.
2. **Fixed 10/90 senior partition** — `round(NP·0.1)` / `round(NP·0.9)` hardcoded in
   `egsk_gained_shared_senior.m` (the base GSK helper is parameterized `P`; **must not be reused as-is**).
3. **Interior-point local refinement `egsk_ip_refine`** — MATLAB **`fmincon` (algorithm='sqp')**,
   budget `ceil(0.002·max_nfes)`, fired in late stage when `std([a2 b2 c2])·1e-2 <= 1` and best-so-far
   is above target; refines the incumbent and writes it back to row `NO_i`.

Key constants: `NP=100`, `KR=1`, `K=10`, junior schedule `ceil(D·(1-g/G_Max)^K)`, `G_Max=fix(max_nfes/NP)`,
midpoint bound repair, **asymmetric population selection** (compare `sum(fitness)` vs `sum(children)` to
pick the base, then greedy per-individual), termination at `nfes>=max_nfes` (no early stop).
Per-generation random draws (order matters): 3 mask draws `rand(NP,D)` + the senior R1/R2/R3 index
sampling in `egsk_gained_shared_senior`.

## 2. RNG verdict — byte-identity is **INFEASIBLE** (for the published reference)
- ✅ **RNG/seed are byte-reproducible.** The EGSK reference CSVs were generated with **threefry** (not the
  code's default `twister`); the seed formula is identical to Python's `get_cec_seed`; and
  `common/threefry_rng.py` already reproduces MATLAB's `rng(seed,'threefry')` stream **bit-for-bit**
  (validated to machine epsilon — the basis of the existing family ports). So the GSK population search
  *can* be byte-faithful.
- ❌ **`fmincon` breaks it.** `egsk_optimize.m:21` — *"the published eGSK reference **always** calls
  fmincon"* — and the code errors if it's unavailable. MATLAB's `fmincon` SQP has **no byte-identical
  Python equivalent** (scipy `SLSQP`/`trust-constr` is a different algorithm with a different iteration
  path and floating-point trajectory). The reference CSVs are visibly SQP-polished (F1/F3/F6 best = 0.0).
- **Conclusion:** because the reference always ran `fmincon` and `fmincon` can't be reproduced in Python,
  **full byte-identity is impossible.** Validation must be **Tier B — statistical equivalence**.

## 3. Helper reuse map (Python `common/`)
- **Reuse directly:** `gained_shared_junior_r1r2r3` (donors.py:24), `gsk_bound_repair` (bounds.py:12),
  `gsk_initial_population_from_options` + `gsk_init_population` (population.py:53/66),
  `gsk_restore_rng_after_initialization` (population.py:94). (`reduction` exists but EGSK keeps NP fixed.)
- **Must create:** (1) **EGSK senior partition** (fixed 10/90 — *not* the parameterized `P` version);
  (2) **`egsk_ip_refine`** wrapping `scipy.optimize.minimize(method='SLSQP', bounds=…, maxiter/maxfun
  capped)` as the `fmincon` substitute; (3) inline **KF triangular-membership adaptation**; (4) inline
  **asymmetric selection** twist.
- **As shipped (`optimizers/egsk.py`):** (1) turned out **not** to need a new partition — the shared
  `gained_shared_senior_r1r2r3` is reused with `p = 0.1` (`_SENIOR_P = 0.1`), because
  `round(NP·0.9) == round(NP·(1−0.1))` for every `NP`, so the fixed 10/90 split *is* the parameterized
  helper at `p = 0.1`. (2) `_egsk_ip_refine` wraps `scipy.optimize.minimize(method="SLSQP")` (details in
  §6). (3) `_triangular_membership` + `_clamp_kf` perform the KF adaptation. (4) the asymmetric
  `sum(fitness)` vs `sum(children)` selection is written inline in the generation loop.

## 4. Python contract & registration
- `src/gsk_family/optimizers/egsk.py` mirrors `agsk.py`: `optimize(problem, options) -> OptimizerResult`,
  `_option_value`, `gsk_initial_population_from_options`, `RandomContext`, `_scan_best`,
  `_append_convergence`, budget tracking, the result fields + `params`/`notes`.
- Register: add `'egsk'` to `OPTIMIZER_IDS` (`optimizers/__init__.py`) and make it RUNNABLE in
  `analysis/project_policy.py` (it is currently `REFERENCE_COMPARATORS`-only) — keeping the comparator
  semantics consistent.
  - **As shipped:** `'egsk'` is in `OPTIMIZER_IDS` and now appears in **both** `RUNNABLE_OPTIMIZERS`
    **and** `REFERENCE_COMPARATORS` (`analysis/project_policy.py`) — runnable locally while still
    available as committed reference statistics. It is one of the **seven** runnable family optimizers.
- **Smoke oracle** (`test_egsk_smoke.m`): sphere F1, D10, `max_nfes=10000`, `seed=777`, target `1e-8` —
  the first parity check.

## 5. Recommended validation strategy (Tier B) + the decision you must make
Because of `fmincon`, there are three honest options — **this is the Phase-0 decision gate:**

- **Option A (recommended): port EGSK faithfully *with* a scipy-SLSQP `ip_refine`, validate
  statistically.** Algorithm-faithful; the GSK part is byte-exact; document the `fmincon→SLSQP`
  substitution. Accept that on the SQP-polished functions exact agreement with the reference is **not**
  expected — report the achieved per-function statistical agreement (paired Wilcoxon, mean/median within
  tolerance) honestly. Risk: may *not* statistically match the `fmincon` reference where SQP dominates.
- **Option B: port the GSK core *without* `ip_refine` (the `use_fmincon=false` mode).** This **is**
  byte-reproducible — but it does **not** match the committed (fmincon) reference; you'd have to
  regenerate the EGSK reference in no-fmincon mode (a different, weaker algorithm than published EGSK).
- **Option C: keep EGSK reference-only** and document why (the `fmincon` dependency makes a clean,
  reproducible Python port impossible without an SQP substitution).

## 6. Phase-1 questions — **resolved in the shipped port** (`optimizers/egsk.py`)
- **Triangular-membership convention & the `min(R1)` index quirk — confirmed intentional.**
  `_triangular_membership` vectorizes the reference `y = (x−a)/(b−a)` on `[a, b]`, `(c−x)/(c−b)` on
  `[b, c]`, else `0`; `_clamp_kf` then applies the reference clamp (`y ≥ 1 → 0`, `y ≤ 0 → 0`, and
  non-finite `→ 0`, a no-move that keeps the parent). The senior anchors take `min` over the **index**
  vector — `a2 = fitness[min(r1)]`, `b2 = fitness[min(r2)]`, `c2 = fitness[min(r3)]` — reproduced
  verbatim and flagged in-code as a deliberate reference quirk.
- **The IP budget is honoured and counted into `nfes`.** `_egsk_ip_refine` sets
  `budget = min(ceil(2e-3·max_nfes), max_nfes − nfes)` and calls
  `minimize(method="SLSQP", bounds=…, options={"maxiter": budget, "ftol": 1e-12})`. SLSQP has no
  `MaxFunEvals`/`maxfun` option, so the budget is enforced by a **hard per-call counter** that raises a
  `_BudgetExceeded` sentinel; every objective call (value + finite-difference gradient) is then added to
  `nfes`, exactly as `details.funcCount` is in the reference. The refinement draws **no** RNG.
- **IP trigger thresholds are hardcoded per reference** — the late stage begins at `g ≥ 0.75·G_Max`
  (`_LATE_STAGE_FRAC`), and refinement fires only when `std([a2, b2, c2])·1e-2 ≤ 1` **and** best-so-far
  is above `optimum + val_2_reach`. The refined incumbent is written back to its producing row `NO_i`.
