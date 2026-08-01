# Family-wide acceleration plan — 7 algorithms x 5 suites, bit-identical only

**Status:** CLOSED 2026-07-25 (CR-0013..CR-0017; see the CAMPAIGN COMPLETE row in
the table below, which this header previously contradicted). Supersedes the
campaign-state sections of `LSGO_ACCELERATION_PLAN.md` (whose measured lessons —
T1 rejection, budget-scaling, worker knee, probe traps — remain authoritative).
**Opened:** 2026-07-25. **Closed:** 2026-07-25.

**Hard constraint:** every change bit-identical — same arithmetic, same operation
order, same RNG stream consumption, same seeded `best_fitness`. Result-changing
levers are flagged in §5 and never silently applied.

**Evidence base:** 6-agent static-analysis workflow (`wf_607c2359-7a3`,
47 findings, full detail in `scratchpad/wf_findings.json` and the workflow
transcript) + the cross-suite attribution ledger
(`scratchpad/ledger_all_suites.json`, 84 cells: 7 algs x {cec2017 D10/30/50/100,
cec2013 D10/50, cec2020 D10/20, cec2011 native x3, lsgo D1000}; each cell records
ss µs/FE, category shares, and hex `best_fitness`).

---

## 0. RESUME POINT

| Step | State |
|---|---|
| Static analysis, 6 lenses, 47 findings | **DONE** |
| Attribution ledger, 84 cells | **DONE** — 84/84 good (`ledger_all_suites.json`; pass 1 voided by a `create_stats` bug, rerun clean) |
| Golden-values matrix (Wave 0) | **DONE — 42 hex pins minted from pre-Wave-1 HEAD, green twice** |
| **Wave 1 (W1.1–W1.4) — CR-0013** | **DONE, bit-identical certified** (42 goldens + full-budget hex + 575-test suite). Interleaved A/B: 1.07× median, variance sharply reduced; microbenched ~15 µs/FE removed at D=1000 |
| **W2.1 `_rng_3buf` fused draw — CR-0014** | **DONE, bit-identical certified** (13-substream KAT + 42 goldens + full-budget hex at D50/D100/LSGO; interleaved A/B 1.07×; dead buffer plumbing removed — the old out= path would have filled C-order, so the guard it deleted was load-bearing) |
| **W2.3/2.4/2.6 — CR-0015** | **DONE, bit-identical certified** (consumer claims re-verified in source; 124 targeted tests + full-budget hex at D10/D50/LSGO + 575 suite). Note: the lens's "telemetry-only" claim for coverage_i needed NARROWING — mean_dim_coverage is consumed whenever generation_callback is set, so the gate is `ace_coverage_weighted or generation_callback` |
| **W2.2 fused trial assembly — CR-0016** | **DONE, bit-identical certified.** Real-data microbench 71.5% of the assembly surface (436→124 µs/gen at production densities D_J 0.1%/D_S 76.6%); ~2% whole-run at LSGO so the interleave was correctly unresolvable — claimed from isolated measurement |
| ~~W2.5 linkage-flatten cache~~ | **REJECTED by inspection** — <0.5% surface, identity-caching medium-risk; ceiling line |
| Wave 2 | **CLOSED** |
| ~~Wave 3~~ | **REJECTED by measurement (CR-0017)** — W3.1 delta 1.7 µs/gen (~0.1%); W3.2's whole evaluate is 0.44–2.81 µs/FE. Ceiling lines |
| **Classics leftovers — CR-0017** | **DONE** — atmals dead snapshot (~506 µs/gen at D=1000) + egsk single buffer/complement scatter + egsk rand buffer; ~~W1.5~~ rejected (~2 µs/gen) |
| **CAMPAIGN COMPLETE** | **CLOSED (CR-0013..0017).** 84/84 cells hex-identical; paired A/B **1.280× median** (the sequential re-measure's 0.79-0.90× was machine drift — proven by fixed workloads slowing 1.43× in the same period). Result + ceiling proof in §7 |

**Ledger headline (pre-Wave-1 baseline, µs/FE):** dt-gsk is slowest everywhere
(37–155); classics 3–48; `dt_subsystems` = 47–55% of dt-gsk at D30/D100; "other"
(numpy alloc/copy internals — the Wave-1/2 surfaces) = 27–42% for the classics.
Anomaly noted: `egsk|cec2013|D50` ss = −0.8 µs/FE (early-termination differencing
artifact).

**Execution law:** goldens are minted from PRE-fix HEAD and must stay green after
every wave. Every candidate is **microbenchmarked before coding** (T1 rule).
A fix that cannot state its bit-identity argument *by construction* is out of scope.

## 1. Certification backbone (Wave 0)

`test_family_golden_values.py`: 7 optimizers x 6 cells (sphere F1 D10, cec2017 F5
D10, cec2013 F1 D10, cec2020 F2 D10, cec2011 F1 native, cec2013lsgo F1 D1000),
seed 20240620, threefry, budget 3000, **hex-exact** `best_fitness` pins.
Mint: `python tests/regression/test_family_golden_values.py --mint`.
Re-mint only on a deliberate result-changing release, recorded in the CR register.
Acceptance for every campaign CR: goldens + `test_dt_gsk_byte_stable` +
`test_rng` + `test_dt_rng` green, fixtures untouched.

Certification gaps the CERT lens found (fix opportunistically): the CR-0010
scalar-reservoir path has no KAT pinning mixed scalar/batch interleaving; the
trial kernel `gsk_build_trial` has no numeric gate; the FP sentinel is
tolerance-based, never hex-pinned.

## 2. Wave 1 — shared RNG + the six classics

| ID | Fix | Surface | Class | Breadth |
|---|---|---|---|---|
| W1.1 | `_draw` direct-fill: generate full blocks straight into `out`, only the partial tail via a 4-double temp that becomes the reservoir | `threefry_rng.py:377-401` | removes 1 redundant alloc + 1 **full-size memcpy on every large draw** (~4.8 GB/run classic cec2020, ~70 GB/run dt-gsk LSGO) | all 7 algs, all suites |
| W1.2 | Persistent (3,NP,D) C-buffer + `np.copyto` per plane; pass contiguous prefix slices so `ascontiguousarray` passes through | `_kernels.py:208-210` + 4 call sites | kills 3 strided NP*D allocs/gen (copies retained — inherent to column-major reference order) | gsk/agsk/apgsk/fdb-agsk (+egsk boundary) |
| W1.3 | pop/popold single-buffer: delete the two byte-identical full copies/gen; end-of-gen in-place masked `copyto` | `gsk.py:150,203-204`; `agsk.py:282,331-332`; `apgsk.py:166,215-216`; `fdb_agsk.py:276,333-334`; egsk/atmals selection variants | 2 full NP*D copies + 2 allocs per gen | 6 classics |
| W1.4 | Reduction helper dead values: stop gathering `pop[survivors]` (dead at all call sites), drop the discarded arange, apgsk's never-read `k_vec` | `agsk.py:160-192` | ~0.8 MB dead gather per reducing gen | agsk/apgsk/fdb-agsk |
| W1.5 | Senior-donor 3 NP-draws -> 1 batched 3*NP draw (concatenation-consistency argument, same as W2.1) | classics donor helper | 2 dispatch round-trips/gen | classics |

Bit-identity arguments: W1.1/W1.5 by stream-position invariance (block index ->
fixed quadruple; `_draw(a)+_draw(b) == _draw(a+b)` split, reservoir tail
byte-identical). W1.2 by layout-only change (same doubles, same (i,j) mapping).
W1.3 by dead-copy proof (no writer between the copies; kernel and `_scan_best`
read-only; `trial` freshly allocated so no aliasing). W1.4 by dead-value proof.

## 3. Wave 2 — dt-gsk (`_dt_core.py`)

| ID | Fix | Surface |
|---|---|---|
| W2.1 | **Realize `_rng_3buf` (author-authorized):** replace 3 separate (NP,D) draws with one flat `random(3*n)` + three `reshape(D,NP).T` segment views. Full by-construction argument in the DTGSK lens finding #1 (segment k occupies exactly draw k's absolute stream positions; generator end-state and reservoir tail identical; NLPSR shrink safe because n is recomputed per gen) | `:992-1001, 1064-1077, 2566-2573` |
| W2.2 | Fuse trial assembly (`copyto` + 2 disjoint boolean scatters -> 1 numba pass) | `:3233-3236` |
| W2.3 | Delete dead `dim_updated_mask` O(NP*D) OR when the numba coverage kernel is active | `:3273-3278` |
| W2.4 | Gate `dim_coverage` kernel + DE coverage write on telemetry (coverage_i is telemetry-only in every shipped profile) | `:3275-3278, 3339` |
| W2.5 | Cache `_link_flat/_link_offsets` on refresh instead of rebuilding from Python lists every gen | `:3037-3059` |
| W2.6 | ISM-off tiers: skip `accepted_displacements` construction (no consumer below D50) | `:3405-3408` |

W2.3/W2.4/W2.6 are dead-code/telemetry gates — verify the "no consumer" claims
against source before applying (the lens cites consumers; re-check).

## 4. Wave 3 — suites

| ID | Fix | Surface |
|---|---|---|
| W3.1 | Hoist construction-time-constant dispatcher ceremony (arg-order sniff, fp_mode normalization) out of the per-call path, all 5 suites | each `functions.py` |
| W3.2 | cec2013 transform pipeline: reuse (NP,D) temporaries (5-9 fresh allocs per evaluate; GEMM out= where applicable) — **microbench first**, medium risk | `cec2013/*` |

## 5. Flagged, NOT in scope (result-changing)

- cec2017 serial-kernel twins (wired, dormant, R2: 93.20% rows bitwise, worst 13
  ULP). cec2020/cec2013 have no twin infrastructure at all.
- Row-major rand fill (removes the transpose entirely but remaps stream->cell).
- dt-gsk archive scan restructuring; ISM gating; archive shrink.
- Anything requiring the evidence rerun — batch into ONE campaign if ever taken.

## 6. Per-wave procedure

1. Microbench the candidate in isolation (T1 rule; whole-run A/B unreliable <1.3x).
2. Apply; state the by-construction argument in the commit/CR text.
3. `pytest tests/regression/test_family_golden_values.py tests/unit/test_rng.py
   tests/unit/test_dt_rng.py tests/regression -q` — green, fixtures untouched.
4. Full suite green. 5. Ledger spot re-measure. 6. CR register entry.

---

# 7. CAMPAIGN RESULT AND CEILING PROOF (2026-07-25)

## 7.1 Certification — the primary claim

**84 of 84 ledger cells reproduce their pre-campaign `best_fitness` bit-for-bit.**
7 algorithms × 12 cells (cec2017 D10/30/50/100, cec2013 D10/50, cec2020 D10/20,
cec2011 native ×3, cec2013lsgo D1000), hex-compared. **Zero breaks.**
Plus: 42-pin golden matrix, threefry + 13-substream KATs, dt byte-stable pins,
575-test suite — green after every one of CR-0013…CR-0017.

The frozen evidence release `rel-2026-07-20-67d9345f9` is untouched and still
reproduces. **No rerun was incurred; the full unfreeze was never spent.**

## 7.2 Measured speedup — and why the naive comparison was wrong

**Paired interleaved A/B, campaign tree vs baseline `428cf02e6`, alternating arms
in one time window (n=12):**

| cell | baseline µs/FE | campaign µs/FE | paired ratio |
|---|---|---|---|
| gsk cec2013lsgo D1000 | 64.4 | 44.9 | **1.718×** |
| dt-gsk cec2013lsgo D1000 | 101.3 | 75.9 | **1.440×** |
| agsk cec2013lsgo D1000 | 52.8 | 49.7 | **1.205×** |
| gsk cec2017 D100 | 8.0 | 7.5 | **1.076×** |
| **overall paired median** | | | **1.280×** |

⚠ **The sequential 84-cell re-measure said 0.79–0.90× — that reading is invalid.**
It was contaminated by machine drift, proven independently: over the same period
*fixed* workloads slowed by the same factor — the unchanged 575-test suite went
**77.0 s → 110.0 s (1.43×)** and the unchanged 42-pin golden test **3.6 s → 7.1 s**.
No edit to the optimizers can slow a test suite dominated by non-optimizer tests.
Uniformity across cells the campaign never touches was the tell.

**Methodological rule, now load-bearing for this repo: on this machine, only
paired/interleaved designs can resolve optimizer speedups. Sequential
before/after ledgers separated by hours measure the machine, not the code.**

## 7.3 What landed

| CR | Change | Isolated measurement |
|---|---|---|
| CR-0013 | W1.1 `_draw` direct-fill; W1.3 single population buffer (4 classics); W1.2 persistent rand-plane buffer; W1.4 dead reduction values | 56% of large-draw cost; 471 + 331 µs/gen of copies at D=1000 |
| CR-0014 | W2.1 fused `_rng_3buf` draw (authorized) | 2 dispatches + 2 allocs/gen |
| CR-0015 | W2.3 dead `logical_or`; W2.4 coverage gating; W2.6 displacement-gather gating | O(NP·D)/gen scans + O(K·D) gather |
| CR-0016 | W2.2 fused trial assembly (new numba kernel) | 71.5% of assembly surface on **real** captured densities (436→124 µs/gen) |
| CR-0017 | atmals dead snapshot; egsk single buffer + complement scatter + rand buffer | ~506 µs/gen at D=1000 |

Plus **Wave 0**: the golden-values matrix — certification is now one pytest run,
where before the campaign 6 of 7 algorithms had **no pinned end-to-end value at all**.

## 7.4 Ceiling proof — what remains, and why it is irreducible

**Rejected by measurement (static analysis proposed all of these; numbers killed them):**

| Candidate | Measured | Why it cannot pay |
|---|---|---|
| T1 wrapper ceremony | 0.03 s/run (~0.1%) | cProfile's 5–10.5% share was call-count instrumentation, not cost |
| W3.1 dispatcher hoisting | 1.7 µs/gen (cec2013 D50), ≈0 (cec2017 D100) | ceremony is already thin post-CR-0011 |
| W3.2 cec2013 transform reuse | whole `evaluate` is 0.44–2.81 µs/FE | full capture of the surface still under the bar; KAT-locked FP pipeline |
| W1.5 senior-donor batching | ~2 µs/gen | 2 dispatches only |
| W2.5 linkage-flatten cache | <0.5% surface | identity-caching risk for nothing |

**Structural floors (bit-identity forbids touching these):**

- **BSE archive distance scan** (`_archive_consider_batch_nb`, ~29% of dt-gsk):
  naive-order O(K·|A|·D), **order-dependent by construction** — each candidate
  sees the archive as mutated by earlier ones. Already numba, `fastmath=False`.
- **CR-0009 row-sum kernel** (~12% of dt-gsk): inherent FLOPs of the reference
  block extraction.
- **Threefry fill kernel**: already unrolled 4.19× (`61dc84bd8`).
- **Objective kernels**: 4–28% depending on suite/D, already JIT-compiled.
- **The column-major reference draw order**: forces one strided transpose per
  plane per generation. Removing it (row-major fill) remaps stream→cell and
  changes every masked decision — result-changing, flagged in §5.

**Conclusion.** The bit-identical surface is **exhausted**. Every remaining
candidate is either measured below the noise floor of this machine or protected by
an order-dependence/reference-fidelity constraint that bit-identity forbids
relaxing. Further speedup requires accepting result changes (serial-kernel twins
R2, row-major fill, ISM gating, archive resizing) and paying the full evidence
rerun — batched into ONE campaign if ever taken.

**Stopping here is the deliverable.**
