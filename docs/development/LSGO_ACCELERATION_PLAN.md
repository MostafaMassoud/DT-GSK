# CEC2013LSGO Acceleration Plan — all 7 GSK-family algorithms, bit-identically

**Status:** ACTIVE. Autonomous-resumable — read §0 to find where to continue.
**Opened:** 2026-07-25. **Scope:** CEC2013LSGO (D=1000, D=905) primary.

## ⚠⚠ FULL UNFREEZE — author ruling 2026-07-25

**The bit-identity constraint is LIFTED.** Results may change; reruns are
authorised. This supersedes the "Hard constraint" this document opened with, and
supersedes the byte-lock on the optimizer core
(`_dt_core.py`, `_dt_subsystems/`, `_dt_rng.py`, `_dt_profiles.py`, `dt_gsk.py`)
and the "no comparator edit" rule.

Newly permitted: `fastmath=True`, reordered reductions, replaced kernels, changed
data layouts, ISM gating, archive resizing, algorithmic substitutions.

**Consequences that MUST be planned for — this is not a free hand:**

1. **All frozen evidence becomes stale.** `benchmarks/cec_reference_results`
   (cec2011 / cec2013 / cec2017) no longer describes the shipped code once any
   result-changing edit lands. Every affected cell needs re-running: 7 algorithms
   × 4 suites × 25–51 runs. LSGO alone is ~100 CPU-hours; the full matrix is
   substantially more.
2. **The manuscript's bound numbers change.** Every value in the paper traces to
   `rel-2026-07-20-67d9345f9` — including the abstract's headline
   (**Friedman mean rank 2.48**, `AN-RANKAGG-2017-OVERALL`), all T01–T16 tables,
   every p-value, every Holm/Nemenyi decision, and the S6.5 ISM isolation null.
   These are **not** editorial text; they are evidence-bound claims.
3. **A new evidence release must be minted** and the whole
   claims/evidence/manifest chain re-pointed (`papers/governance/`), then all four
   artifacts rebuilt and all three manifests re-minted.
4. **Sequencing risk.** The paper currently sits submission-ready with 12
   author-blocking items open (ORCIDs, GenAI disclosure, H.S.M.R. e-mail, …).
   Landing result-changing optimisations now restarts the evidence chain and
   invalidates the submission-ready state until the full rerun + re-analysis
   completes.

**Therefore: strongly prefer bit-identical wins first** (they cost nothing and
need no rerun), and batch every result-changing change into ONE campaign so the
rerun is paid once, not repeatedly. Record each result-changing edit in the CR
register with its rerun scope before landing it.

This plan is LSGO-specific and **subordinate to**
`docs/development/ACCELERATION_CAMPAIGN_PROMPT.md` (the family-wide campaign
document, 89 KB) — read that for the governance overlay (§5), the R1/R2/R3
rulings, and Appendix A's profiling discipline. This file records only what is
LSGO-specific plus the live work-state.

---

## 0. RESUME POINT — update this section on every phase transition

| Phase | State | Evidence / artifact |
|---|---|---|
| P0 Baseline measured | **DONE** | §2 table (from completed campaign `per_run.csv`) |
| P1 Attribution ledger, all 7 | **DONE 2026-07-25** | §2.1 below; `scratchpad/phase1_ledger.json` |
| P1b Contention / worker scaling | **IN PROGRESS** | §2.2 below |
| P1c RNG re-measure at 300 k | **DONE** | §2.3 — RNG share holds, does NOT fall |
| P2 T3 Threefry unroll | **CLOSED — already done** (`61dc84bd8`, 4.19×) | §0 note below |
| **P3-RNG scalar fast path** | **DONE — CR-0010** (1.85× / 1.46× / 1.33×, bit-identical) | §0 table below |
| P2 T1 wrapper ceremony | ❌ **REJECTED — measured 0.03 s/run** (§4.1a) | §4.1a |
| P2 T2 duplicate `isfinite` scan | ✅ **DONE — CR-0011**, 1.06–1.17× on all 7, bit-identical | §4.1b |
| P2 worker knee (4/6/8) | **NEXT** — zero code risk, ~30 % efficiency at 12 | §7 |
| P3 dt-gsk archive scan (29 %) | ready — **result-changing**, batch into one rerun | §4.2 |
| P4 Bit-identity certification | not started | §5 checklist |
| P5 Governance (CR + manifests) | not started | — |

### ✅ T3 IS ALREADY DONE — do not attempt it (verified 2026-07-25)

`ACCELERATION_CAMPAIGN_PROMPT.md §3.3` states the Threefry fill kernel is **NOT**
unrolled and that §6.1's 3.9× lever is "AVAILABLE", citing an adversarial
verification against `threefry_rng.py:113-130`. **That claim is STALE.** The
kernel was unrolled and committed:

```
61dc84bd8  perf(P3): unroll the Threefry-4x64-20 fill kernel - 4.19x, bit-identical (R1)
```

Evidence in the current source (`src/gsk_family/common/threefry_rng.py`):
**20 explicit `# --- round N (rot a/b) ---` blocks** with literal rotation
constants; literal key injection (`x3 = x3 + parity  # k[4] @ s=1, word 3`);
and **zero** hits for the anti-patterns the doc described
(`for r in range(20)`, `r % 8`, `rot_x1[...]`, `(r+1) % 4`, `s % 5`).

**Consequence for the ledger:** the 26–39 % RNG share measured in §2.1/§2.3 is the
cost of an **already 4.19×-optimised** kernel. `_fill_doubles_kernel` is at or
near its floor — treat it as a **ceiling line**, not a target. Fix
`ACCELERATION_CAMPAIGN_PROMPT.md §3.3` so it stops directing work here.

### ✅ P3-RNG LANDED — CR-0010, 2026-07-25 (bit-identical, no rerun)

The atmals-gsk 47 % target below is **DONE**. Fix applied: index-based reservoir
+ `random_scalar()` fast path in `ThreefryGenerator`, with scalar dispatch in the
shared `DoublesStreamGenerator.random`.

| Algorithm | before | after | speedup | `best_fitness` |
|---|---|---|---|---|
| atmals-gsk | 46.42 s | 25.10 s | **1.85×** | identical |
| gsk | 17.37 s | 11.92 s | **1.46×** | identical |
| egsk | 16.35 s | 12.28 s | **1.33×** | identical |

(F1 D1000, MaxFES = 300 000, threefry.) Certified: 60 randomised trials × 120
mixed scalar/batch calls vs an independent reimplementation of the OLD buffering
semantics (0 mismatches); state round-trip; column-major order (trap T2); 37 RNG
KATs; full suite 488 passed; end-to-end `best_fitness` identity. Benefits **all
seven algorithms and all five suites** — the generator is shared.

**Next action — revised work order (post-unfreeze, T3 closed, P3-RNG landed):**
1. **atmals-gsk `_draw` = 47 % — ROOT CAUSE ISOLATED 2026-07-25.**
   It is **not** kernel time and **not** a missing batch. `_draw`
   (`threefry_rng.py:327`) already buffers: a scalar request generates a 4-double
   block and keeps 3 in `self._buffer`, so the njit kernel is already amortised
   4×. The 47 % is **per-call Python overhead**, paid on every scalar draw:
   - `out = np.empty(count)` — a fresh 1-element array allocation;
   - `self._buffer = self._buffer[take:]` — **builds a new ndarray view object
     every call** (the expensive part);
   - `float(...)` boxing at the two call sites.

   Call sites: `atmals_gsk.py:98` (`if float(rng.random()) < pls/dim`) and `:100`
   (`2.0*float(rng.random()) - 1.0`), both inside `_local_search`, executed
   per-dimension per-elite. Lines `:136` and `:191` are already batched
   (`rng.random((3, pop_size, dim))`) and are fine.

   **⚠ Naive batching is NOT bit-identical.** The draw count is *data-dependent*:
   `:100` only draws when `:98`'s test passes. Pre-drawing `2*dim` consumes more
   stream than the original consumed, shifting every subsequent draw. Likewise,
   drawing all tests first and then all values reorders the stream mapping. Either
   approach changes results.

   **The bit-identical fix — a scalar fast path, not batching.** Add
   `random_scalar()` to the generator that returns the next double from a
   **fixed preallocated buffer indexed by an integer pointer**, refilling in
   large blocks (e.g. 4096) when the pointer hits the end. This consumes the
   **same sequence in the same order**, so it is bit-identical by construction,
   while removing the per-call allocation and the view-object churn. Keep
   `_draw(count)` semantics unchanged for the batched call sites and make both
   share one buffer + pointer so the interleaved stream stays consistent.

   **Gate:** `tests/unit/test_rng.py` (threefry known-answer draws) **and** an
   end-to-end atmals-gsk seeded run reproducing `best_fitness` exactly.
2. **dt-gsk `_archive_consider_batch_nb` = 29 %** — previously blocked at its
   bit-identical floor (naive-order, order-dependent scan). **The unfreeze makes
   it optimisable** (early-exit, spatial pruning, or a smaller cap).
   *Result-changing → batch into the single rerun campaign.*
3. **T1 wrapper ceremony** — 5–10 % across the classics, now unblocked.

**Author rulings — BOTH CLEARED 2026-07-25:**

1. **T1 (`_kernels.py`, comparator-shared) — UNBLOCKED.** The standing "no
   comparator edit (MATLAB-faithful ports)" constraint is lifted for this change.
   T1 changes no arithmetic. §5 certification still applies in full: all six
   comparators must reproduce their frozen cec2017 / cec2011 / cec2013 cells
   byte-for-byte.

2. **`_rng_3buf` dead fast path — AUTHORISED** (`_dt_core.py:2573`; guards at
   `:993-1001`, `:1064-1077`). Refreeze authority granted, so the largest known
   unrealised DT-GSK saving is now a live target, no longer a ceiling line.
   ⚠ Still inside the byte-locked core, and the reference matrix order the guard
   protects is **load-bearing (T2′)**, not incidental:
   `ReferenceRNG.uses_reference_matrix_order` is a CLASS attribute set `True` for
   **every** generator (`_dt_rng.py:85`), which is why production always takes the
   three-draw branch. Realising the pre-allocated buffer requires **proving** the
   single-fill path reproduces the three separate column-major
   `(NP,D)` draws — `reference_rng.py:59`
   (`flat.reshape(..., cols, rows).swapaxes(-1,-2)`) — in exactly the same order,
   per substream. **Gate: `tests/unit/test_dt_rng.py` (13-substream KAT vs
   `fixtures/dt_rng_kat.json`).** Treat that KAT as the acceptance test, not a
   formality — if it fails, the transformation is wrong, not the KAT.

---

## 1. The constraint that shapes this plan

**Objective evaluation is only 2–9 % of LSGO wall time** (measured 2026-07-25,
two-budget differencing, F1/F4/F8/F13/F15).

This **inverts** the priority in `ACCELERATION_CAMPAIGN_PROMPT.md §3.1`, whose
headline lever — the serial-kernel twins — was validated on **cec2017
(D=10–100)** where per-launch overhead is large relative to a small batch. At
D=1000 a `parallel=True` launch amortises over 100 rows of 1000 doubles, so the
launch tax is ~1 % of batch cost, not 60–90 %.

**Consequence: all objective-side work is capped at ~9 % for LSGO.** Do not port
the serial-twin lever here expecting 3–10×. 91–98 % of LSGO time is
optimizer-side.

## 2. Measured baseline (3×10⁶ FEs, completed campaign runs)

| Algorithm | min/run | µs/FE | × floor |
|---|---|---|---|
| agsk | 17.0 | 341 | 1.00 |
| gsk | 17.1 | 343 | 1.01 |
| fdb-agsk | 17.5 | 350 | 1.03 |
| apgsk | 18.2 | 364 | 1.07 |
| egsk | 19.8 | 396 | 1.16 |
| dt-gsk | 27.5 | 550 | 1.61 |
| atmals-gsk | 31.6 | 633 | 1.86 |

Full 7-algorithm campaign ≈ **100 CPU-hours**. Each 10 % saved ≈ 10 hours.

**Correction to an earlier finding in this session:** the six classics *are*
numba-accelerated — via the shared `_kernels.py:154`
(`njit(cache=True, fastmath=False)(_gsk_build_trial_loop)`). A grep for `numba`
in the per-algorithm files returns 0 and is **misleading**; the acceleration
lives in the shared kernel module.

### 2.1 P1 attribution ledger (measured 2026-07-25, F1 D1000, threefry, 20k/40k differencing)

Steady-state single-process cost, and self-time share of the top contributors:

| Algorithm | ss µs/FE | **RNG total** | objective | `ascontiguousarray` (T1) | trial kernel |
|---|---|---|---|---|---|
| gsk | 30 | **39.1 %** | 20.4 % | 10.5 % | 10.0 % |
| agsk | 40 | **28.3 %** | 25.6 % | 5.7 % | 7.5 % |
| apgsk | 40 | **28.8 %** | 24.9 % | 5.6 % | 7.7 % |
| fdb-agsk | 45 | **25.9 %** | 23.3 % | 5.1 % | 7.1 % |
| egsk | 43 | **39.9 %** | 17.5 % | 9.5 % | 12.1 % |
| atmals-gsk | 125 | **68.3 %** | 5.2 % | — | — |
| dt-gsk | 171 | (ISM/archive-dominated — see §4.2) | 6.1 % | — | — |

RNG total = `threefry_rng._fill_doubles_kernel` + `threefry_rng._draw`
(+ `reference_rng.random` / `rng.random` scalar wrappers where present).

**Three findings that set the work order:**

1. **Threefry is the dominant shared cost — T3 is the #1 lever**, not the
   objective and not the wrapper ceremony. 26–40 % across the five classics.
2. **atmals-gsk is confirmed RNG-CALL-BOUND** exactly as
   `ACCELERATION_CAMPAIGN_PROMPT.md §3.3` predicted: `_draw` alone is **47.4 %**,
   plus `reference_rng.random` 8.6 % and `rng.random` 5.7 % — scalar
   `rng.random()` paying a full Python → wrapper → njit round trip *per double*.
   Batching those draws is a large bit-identical win and explains why atmals-gsk
   is the slowest family member.
3. **T1 is real but second-order**: 5.1–10.5 %.

### 2.2 ⚠ UNRESOLVED: a 10× gap between single-process and campaign cost

P1 measures **30–171 µs/FE single-process**; the completed campaign recorded
**341–633 µs/FE** (§2). That is a **~3–11× discrepancy that is not yet explained.**

Two candidate causes, and the discriminating test:

- **(a) Worker contention / memory bandwidth.** The campaign ran 13 workers, each
  churning 800 KB population arrays at D=1000. A first scaling probe at 30 000
  evals was **invalid** — fixed per-worker setup (spawn, imports, FP-regime
  sentinel probe) dominated compute, so all worker counts returned ~35 s
  (efficiency fell to 8 %, an artifact, not contention). **Retest at ≥300 000
  evals so compute dominates.**
- **(b) Late-budget phases.** Costs that only activate deep into a 3×10⁶ budget:
  the BSE archive filling to 200 entries (its distance scan is O(K·|A|·D)), the
  ISM graph accumulating, deep-stall restarts, and end-of-run polish
  (`local_search_start_frac = 0.95`, egsk late-stage). A 40 000-eval probe reaches
  ~1.3 % of the budget and **never enters these phases at all.**

**RESOLVED 2026-07-25 — cause (b) CONFIRMED: cost per FE grows with budget.**
Same algorithm (gsk), same cell (F1 D1000), single process, three budgets:

| budget | µs/FE | vs 40 k |
|---|---|---|
| 40 000 | 30 | 1.0× |
| 300 000 | 99 | 3.3× |
| 3 000 000 (campaign) | 343 | 11.4× |

Roughly **3.4× per 10× budget** — cost is superlinear in the budget, not
constant. Mechanisms: the BSE archive fills toward 200 entries (its distance scan
is O(K·|A|·D), so it grows as the archive grows), the ISM graph accumulates, and
end-of-run phases activate (`local_search_start_frac = 0.95`, egsk late-stage,
deep-stall restarts).

**Methodological consequence — this invalidates short-budget profiling for
ranking:**
- A 40 000-eval probe reaches ~1.3 % of the budget and **never enters the
  expensive regime at all**.
- Therefore the §2.1 percentages describe the **early regime only**. RNG cost per
  generation is roughly *constant*, so as budget-dependent costs grow, **RNG's
  share must fall** at full budget. The 26–40 % / 68 % figures are upper bounds,
  not full-run shares.
- **Before committing to T3, re-measure RNG share at ≥300 000 evals** (ideally
  3×10⁶ on one cell). If RNG falls to single digits at full budget, T3 stops
  being the #1 lever and the archive/ISM growth terms take over.

**Do not rank optimisation targets from short-run profiles in this suite.**

## 3. Already banked

- **CR-0009** — `_split_component` row-sum kernel (`interaction_graph.py`),
  certified bit-identical, **2.3–3× on DT-GSK LSGO**. This removed a
  pathological O(n³)-ish Python hot spot that was 61–70 % of DT-GSK runtime.
- **Linkage block size** matched to the suite group structure (config, LSGO-only)
  and `strict_profile_dims` fail-closed: `configs/dtgsk_cec2013lsgo.yml`.

**Nothing of CR-0009's magnitude is known to remain.** Treat any claim of
another 3× as unproven until measured.

## 4. Targets

### 4.1 Shared (one fix lands for six or seven algorithms)

Pre-located and adversarially reviewed in `ACCELERATION_CAMPAIGN_PROMPT.md §3.2`.

| ID | Target | Location | Why it bites at D=1000 | Risk |
|---|---|---|---|---|
| **T1** | Wrapper ceremony: 8 `ascontiguousarray` + 4 `np.full` NP-vector allocations **per call** | `_kernels.py:194-214` | every generation ×30 000, on 100×1000 arrays (800 KB each) | low — pre-resolve outside the loop; no arithmetic touched |
| **T2** | **Duplicate** adapter/dispatcher ceremony: contiguity coercion **and** a full `np.all(np.isfinite)` scan, done **twice** | `benchmark_adapter/problem.py:48-63`, `factory.py:103-110` | 2 × 10⁵-element scans/generation ×30 000 | low — hoist/dedupe validation |
| **T3** | Threefry fill kernel **not unrolled** (adversarially confirmed: 3 modulos, rotation-table lookups, branchy key injection) | `threefry_rng.py:113-130` | LSGO draws ~3×10⁵ doubles/generation | low — **R1 bit-identical by construction** (integer ops, same order) |

**T3 caveat:** already `njit(cache=True, fastmath=False)`; LLVM may *already*
unroll a constant-trip `range(20)`. Reference measured 3.9×; realised win may be
far less. **Measure before committing.** Generate unrolled code mechanically,
never hand-transcribed.

### 4.1a ❌ T1 REJECTED — negative result, measured 2026-07-25

**Do not re-attempt T1.** It was implemented (pass-through guards for the 8
`ascontiguousarray` + 4 `_as_f64_vector` calls), certified **bit-identical on all
7 algorithms** (end-to-end `best_fitness` at 300 k), then **reverted** because the
gain is negligible:

| normalisation path | µs / generation |
|---|---|
| original ceremony | 9.63 |
| guarded fast path | 8.71 |

0.92 µs/generation × 30 000 generations = **0.028 s per run**, against runs of
10–30 s → **~0.1 %**. Not worth three extra helpers on a code path shared by every
algorithm.

#### ⚠ The methodological lesson — cProfile self-time misled the triage

`ascontiguousarray` showed **5.1–10.5 % self-time** in the §2.1/§2.3 ledgers. That
was an **artifact of call count, not cost**: ~240 000 tiny calls per run, each
carrying cProfile's per-call instrumentation overhead. The real cost is 0.1 %.

Two corollaries, both learned the hard way here:

1. **Never accept a cProfile self-time share for a high-call-count, low-cost
   function without a microbenchmark.** Profile to *locate* candidates; measure
   the candidate in isolation to *size* them.
2. **Whole-run A/B on this machine cannot resolve small effects.** Matched-condition
   runs swung gsk 10.88 → 6.57 s and atmals-gsk 10.75 → 13.17 s *in opposite
   directions* from a change worth 0.03 s — i.e. pure drift. Run-to-run spread
   reached **22 %** (gsk: 8.92–10.89 s). Anything under ~1.3× must be measured by
   microbenchmark, not by whole-run timing.

`ACCELERATION_CAMPAIGN_PROMPT.md §3.2` lists T1 and T2 as located targets on the
strength of *static* inspection (call counts and allocation shapes). T1 is now
falsified empirically; **T2 (`as_population` contiguity + the duplicated
`np.all(np.isfinite)` scan) rests on the same reasoning and should be
microbenchmarked before any code is written.** An `isfinite` scan over 10⁵
elements is ~50–100 µs; twice per generation over 30 000 generations is ~3–6 s per
run, which *is* worth checking — but check it, do not assume it.

### 4.1b ✅ T2 CONFIRMED REAL — measured 2026-07-25, ready to implement

Microbenchmarked first (per the §4.1a lesson), NP=100 D=1000, 5×20 000 iterations:

| operation | µs/call | s/run @ 30 000 gens |
|---|---|---|
| `as_population` (full) | 18.60 | 0.558 |
| **`np.all(np.isfinite(pop))` alone** | **18.42** | **0.553** |
| `np.ascontiguousarray(pop)` alone | 0.12 | 0.004 |
| `pop.sum()` (reference, 10⁵ elems) | 23.14 | 0.694 |

**The `isfinite` scan is 99 % of `as_population`.** It costs about as much as a full
reduction over the population — unsurprising, it *is* a full pass over 10⁵ doubles.

**The scan is genuinely duplicated**, confirmed in source:
- `benchmark_adapter/problem.py:62` — `if not np.all(np.isfinite(pop))`
- `benchmarks/cec_suite_python/cec2013lsgo/functions.py:202` — the same check again
  on the same array.

(The `np.sum(~np.isfinite(...))` on the following line in each is the *error* path
only — it does not run in the happy path, so each function costs one scan.)

**Total: ~1.1 s per run = 4–10 %** of a 10–30 s LSGO run. Unlike T1, this is worth
doing. `ascontiguousarray` at 0.12 µs independently re-confirms T1's rejection.

#### ✅ LANDED — CR-0011, 2026-07-25 (bit-identical, no rerun)

`as_population` gained `check_finite: bool = True`; the two real-suite adapter call
sites pass `False` (the sphere site keeps the default). Shape/dtype/emptiness checks
always run.

| Algorithm | pre-T2 | post-T2 | gain |
|---|---|---|---|
| gsk | 2.28 s | 2.01 s | 1.13× |
| agsk | 2.53 s | 2.33 s | 1.09× |
| apgsk | 2.71 s | 2.45 s | 1.11× |
| fdb-agsk | 3.01 s | 2.67 s | 1.13× |
| atmals-gsk | 4.45 s | 4.19 s | 1.06× |
| egsk | 2.59 s | 2.31 s | 1.12× |
| dt-gsk | 11.59 s | 9.90 s | 1.17× |

(F1 D1000, seed 20240620, MaxFES = 60 000.) **All 7 bit-identical, hex-exact.**
**All 7 improved** — 7/7 in one direction is p ≈ 0.016 by chance, so the effect is
real; per §4.1a the *magnitude* still carries this machine's ±22 % spread, so treat
1.06–1.17× as indicative, not precise. Safety re-verified: non-finite input raises
on the adapter path (via the dispatcher) **and** the direct path; 1-D / empty /
wrong-D still raise under `check_finite=False`; full suite 488 passed.

**Original implementation note (kept for rationale) — remove the redundancy, not
the validation.** These are safety
checks; deleting one outright would weaken the boundary. Preferred shape: give the
suite dispatcher a private `_validated: bool = False` parameter that skips its scan,
and have the adapter (which has already scanned) pass `True`. Direct callers of the
suite function — tests, ad-hoc use — keep full validation.

**Certification:** trivially bit-identical (a *check* is removed, no arithmetic
touched) but verify anyway: end-to-end `best_fitness` identity on one seeded cell
per algorithm, plus a test asserting a non-finite population **still raises** on
both the adapter path and the direct suite path.

⚠ **Design tradeoff to accept explicitly:** the adapter becomes the single point
that guarantees finiteness for the campaign path. If a future refactor bypasses the
adapter, the suite's own scan is the safety net — hence the opt-out flag rather than
deleting the check.

### 4.2 Per-algorithm (rank by P1 ledger)

- **atmals-gsk (1.86× floor)** — largest unknown. `ACCELERATION_CAMPAIGN_PROMPT`
  flags it **RNG-call-bound**: scalar `rng.random()` costs a full
  Python → wrapper → njit round trip *per double*. If P1 confirms, batching those
  draws is a large bit-identical win.
- **dt-gsk (1.61×)** — post-CR-0009 leaders are the BSE archive distance scan
  (`_archive_consider_batch_nb`, ~14 ms/gen) and the CR-0009 row-sum kernel
  (~13 ms/gen). **Both at their bit-identical floor**: naive-order reductions,
  already numba, and the archive scan is order-dependent by construction (each
  candidate sees the archive as mutated by earlier ones). ~1.05–1.1 % left via a
  full `_split_component` numba fusion, but it is **tie-fragile**
  (`np.lexsort`/`setdiff1d` tie-breaking must be reproduced exactly).
  **Recommendation: do not pursue.**
- **egsk (1.16×)** — scipy-SLSQP polish is a separate cost class; measure first.

### 4.3 Ceiling lines — record, do not touch

- ~~`_rng_3buf` dead fast path~~ — **no longer a ceiling line; AUTHORISED
  2026-07-25** and promoted to a live P3 target (see §0 ruling 2 for the
  bit-identity obligation and the KAT gate).
- `eigh` — **one call per run** (2.1 s); amortises to <1 % at 3×10⁶ FEs. Looks
  large in short profiles. **Not a steady-state target.**

## 5. Certification — every change, no exceptions

Adapted from the CR-0009 precedent:

1. **Provable bit-identity argument** first (not a tolerance): state why the new
   code performs the same operations in the same order.
2. **Frozen-suite cells** — cec2017 / cec2011 / cec2013 cells backing the paper
   must reproduce byte-for-byte.
3. **FP-regime sentinel unchanged** for every affected suite
   (`gsk_family.runners.fp_regime.canonical_fp_regime`).
4. **KATs green** — `tests/unit/test_rng.py` (threefry known-answer),
   `tests/unit/test_dt_rng.py` (13-substream KAT).
5. **End-to-end** — identical `best_fitness` on a seeded run per affected
   algorithm.
6. **Full test suite** green.

A change that cannot satisfy (1) is not an R1 change and is out of scope here.

## 6. Honest ceiling

- Objective-side: capped at ~9 % (§1).
- T1+T2: allocation/validation overhead, not arithmetic → plausibly
  **10–25 % family-wide**, not multiples.
- T3: **0–15 %**, depending on whether LLVM already unrolls.
- dt-gsk: near its floor post-CR-0009.

**Realistic expectation: ~1.2–1.5× family-wide, bit-identically**
(≈ 20–35 CPU-hours per full campaign). Beyond ~1.5× requires either refreeze
authorisation (`_rng_3buf`) or **accepting result changes** (ISM gating, archive
shrink) — both out of scope under "without impacting logic".

**Stopping is a deliverable.** If the P1 ledger shows only ceiling lines, write
the ceiling proof and stop. Do not manufacture work.

## 7. Operational notes (learned the hard way, 2026-07-25)

- **Worker count: use 12. There is no throughput knee — memory is the limit.**
  Measured 2026-07-25 (gsk F1 D1000, 200 000 evals, `functions:[1], runs:N` so all
  tasks are in one parallelisable group):

  | workers | total s | speedup | throughput | ~memory |
  |---|---|---|---|---|
  | 1 | 176.5 | 1.00× | 4.1/min | 0.4 GB |
  | 2 | 99.8 | 1.77× | 7.2/min | 0.8 GB |
  | 4 | 68.7 | 2.57× | 10.5/min | 1.5 GB |
  | 6 | 62.5 | 2.83× | 11.5/min | 2.3 GB |
  | 8 | 55.7 | 3.17× | 12.9/min | 3.0 GB |
  | **12** | **39.3** | **4.50×** | 18.3/min | **4.6 GB** |
  | 16 | — | +2 % vs 12 | 18.1/min | 6.1 GB |
  | 20 | — | +20 % vs 12 | 21.4/min | 7.6 GB |

  Efficiency falls monotonically (88 % → 37 %) but **absolute throughput never
  stops rising**, so the classic "pick the knee" advice does not apply: the only
  reason to stop adding workers here is memory. 12 → 20 buys 20 % throughput for
  67 % more memory, and an OOM costs the entire campaign (see the next bullet —
  0/375 runs completed). **Recommendation: `--workers 12` as the default; 16 only
  with >12 GB free; 20 only on an otherwise-idle machine.** At ~380 MB/worker,
  budget ≈ 0.4 GB × workers plus headroom for the D=1000 working arrays.
- **Parallelism is contention-bound at ~30 % efficiency** (measured 2026-07-25,
  gsk F1 D1000, 300 000 evals, 12 runs of one function): 1 worker 254.6 s →
  12 workers 69.7 s = **3.65× from 12 workers**. Per-run wall inflates **3.3×**
  under 12-way concurrency (21.2 s → 69.7 s). So the campaign's 341–633 µs/FE is
  *both* budget growth (§2.2) *and* contention. **Open question: locate the
  throughput knee** — test 4 / 6 / 8 workers; more workers still buys absolute
  throughput here, but with sharply diminishing returns and much higher memory
  risk.
- **Probe design trap (cost me two invalid measurements).** The runner dispatches
  **function by function**, parallelising the *runs within* each function group.
  A probe with `runs: 1` therefore has **nothing to parallelise** and shows 0.99×
  at every worker count — an artifact, not contention. Always probe scaling with
  `functions: [1], runs: N`, never `functions: [1..N], runs: 1`.
- **Memory, not compute, is the LSGO failure mode.** 13 workers at D=1000 on a
  31 GB / 64 GB-commit machine exhausted memory: allocations as small as
  **1.10 MiB** failed, 25 runs were logged as `skipped`, and **0 of 375
  completed** while the campaign *looked* healthy for ~25 min. Use
  `--workers 4-6` at D=1000 and free browser/Dropbox/AnyDesk first (~5 GB).
- **A campaign that skips every run still reports "running".** Check
  `summary/per_run.csv` row count (not just process liveness) within the first
  few minutes. A fail-fast guard for this is an open item (CAMPAIGN-GUARD).
- **`run.py --config` now composes with CLI flags** (fixed 2026-07-25). Before
  that fix, `--max-evaluations` / `--functions` / `--runs` were **silently
  ignored** whenever `--config` was given.
- **The numba cache is real and shared** (117 `.nbi` / 135 `.nbc`, ~7 MB, in
  `__pycache__`). A serial warm pass over all 15 functions × both dims populates
  every signature the campaign needs; workers then load from disk instead of each
  invoking LLVM.
- **Profile with the production generator (`threefry`).** GSK's own default is
  `twister`; profiling the wrong stream makes RNG numbers meaningless.
- **Strip one-time cost by two-budget differencing.** A single short profile
  attributes JIT + `eigh` + init to the steady state and misleads badly.
