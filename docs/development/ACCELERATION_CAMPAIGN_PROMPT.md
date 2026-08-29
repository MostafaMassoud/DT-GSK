# GSK-Family Acceleration Campaign — Execution Prompt

> **Internal quality-assurance instrument.** This is a work-sequencing and
> execution prompt the authors used on their own project. It is **not** the
> journal's peer review and did not substitute for it, and it governs tooling
> and campaign ordering rather than scientific judgement. It may be executed by
> a human team or with AI assistance; the authors used the latter, disclosed in
> the manuscript's *Use of Generative Artificial Intelligence* statement, which
> is the authoritative account. See the README section "Internal
> Quality-Assurance Instruments".


**Version 1.2 · 2026-07-17 · grounded on commit `056fb3ff0` · repo `02-GSK_Family_Python_v1.1`**

> **SUPERSEDED STATUS BOX (2026-08-01).** The box below describes the world of
> 2026-07-20 and is kept as a dated record. It is **not** current: the remediation
> ledger it cites closed, the manuscript has since advanced through freeze passes
> 27-31 and tag `v2.6`, and the evidence base now spans four releases rather than
> the two named below. For the current state read the freeze manifest's `phase`
> field and the newest entry in `papers/governance/decision_log.md`.
>
> **CURRENT STATUS (2026-07-20) — read before acting; this campaign is not the active
> workstream.** The project is in **final pre-submission remediation of a BUILT manuscript**,
> not an open acceleration push. The 80-ticket remediation ledger
> (`papers/governance/remediation_2026_07_18/ticket_status.csv`) stands at **80/80 terminal**
> (70 `closed_verified` + 10 `superseded_with_evidence`; no ticket is open),
> every build / cross-format-parity / provenance / citation gate green (2026-07-20). The
> evidence base was just re-minted as `rel-2026-07-20-67d9345f9` / `abl-rel-2026-07-20`, so
> §5's byte-reproducibility constraint is at its **most** binding now, not least. Two live
> items bear directly on this campaign:
> - **RT-001 is CLOSED — do not re-run it.** The six-comparator re-timing was executed and
>   *failed* its determinism gate (3,772 differing rows), so it was not adopted; `tab:runtime`
>   was narrowed to DT-GSK-only, single-session instead. It is recorded here only as campaign
>   history. It originally existed because the
>   **M038 backend fix** bound DT-GSK's compiled interaction-graph (numba) kernels — bit-for-bit
>   identical to the NumPy path, yet **−39.8 %** DT-GSK wall-clock at D100 (69.04 → 41.59 s).
>   That is the D≥100 **KERNEL-BOUND** term the §3 triage flagged for DT-GSK, already reclaimed
>   as a correctness/backend fix (not via this campaign), every scientific column byte-identical.
> - The **terminal freeze is pending**: ticket **C-008** (mint a fresh
>   `main_manuscript_freeze_manifest.json`) → **C-001** (single authoritative commit). Do not let
>   any acceleration edit enlarge the pending refreeze (§5.5 item 4) while it is open. The v1.2
>   lever ranking below still stands, but serial twins remain **governance-gated** here (frozen
>   DT-GSK core §5.4 + archived evidence §5); the near-term R1 surface is the Threefry unroll, the
>   `_kernels.py`/adapter ceremony, and ATMALS scalar fast paths.
>
> **v1.2 — MAJOR CORRECTION.** v1.0–v1.1 claimed serial-kernel twins were "mostly
> inapplicable" here because the family is population-batch. **That was WRONG, and it was
> this document's central claim.** The sibling campaign's own `gsk.py` is population-batch
> with the identical shape and measured **3.2×–10.8×** from serial twins, becoming the
> fastest optimizer in its suite. **Batch shape does not gate the technique**;
> `parallel=True` kernels + low thread count do, and this repo has both. See the correction
> box in §3.1 and the re-based expectations in §11. Full ported inventory of the sibling's
> proven techniques: **`docs/development/SIBLING_CAMPAIGN_TRANSFER.md`**.
>
> **v1.1 — owner ruling landed:** §5.5 ruling 1 is **answered — cec2013lsgo and cec2020 are
> IN SCOPE** (2026-07-17). §4's projection stands; cec2020 D=20 (~29% of the campaign) is
> the block to measure first. Rulings 2 (R2/R3 dual path) and 3 (refreeze appetite) remain
> open; **the default stands: R1-only, no dual paths.**

---

## 0. What this document is, and how to use it

This is an **execution prompt** for an engineering agent (or engineer) tasked with
accelerating the GSK-family benchmarking codebase across all five CEC suites.

It has two parts, and **they are not equal in authority**:

| Part | Authority | Contents |
|---|---|---|
| **Parts 1–10** (this document) | **Binding.** Project-specific. Where it contradicts Appendix A, this wins. | Scope, verified triage, projection, governance overlay, phase plan, gates, live traps |
| **Appendix A** | **Normative reference.** Codebase-agnostic method. | The Stochastic-Computing Acceleration Manual v2, verbatim |

**Read Appendix A first, once, end to end.** Then return here. Appendix A teaches the
method; Parts 1–10 tell you what is already known about *this* repository, what is
forbidden in it, and in what order to work. Appendix A was written from a **different
project** (the sibling 24-algorithm study at
`D:/AI/PhD-Projects/00-GSK-Family/05-Human-Inspired-Family_Python_v0.1`, whose evidence
record `docs/development/OPTIMIZER_PERFORMANCE_AUDIT.md` **does not exist in this repo**).
Its worked examples are from that codebase. **Its patterns transfer; its diagnoses do not.**
Section 3 below explains exactly where this repo's profile differs — and it differs on the
manual's single biggest lever.

**The prime directive of this campaign is not speed. It is that
`benchmarks/cec_reference_results/` remains byte-reproducible.** A paper depends on it.
Read §5 before you touch anything; §5 is the reason most of Appendix A's toolkit is
unavailable to you here.

---

## 1. Mission

Reduce campaign wall-clock for the GSK-family benchmarking codebase across
**7 algorithms × 5 CEC suites**, with:

- **zero regressions**, every change gated on a proof, most bitwise;
- **zero change to archived evidence reproducibility** (§5 — this is a hard constraint,
  not a goal);
- a **written attribution ledger and ceiling proof** as the permanent deliverable, so a
  future maintainer does not repeat this work (Appendix A §13, §4).

**Stopping is a deliverable.** If the ledger shows only ceiling lines, write the proof and
stop. A campaign that lands 4 proven changes and one honest "the rest is the published
algorithm's mandated cost" is a success. A campaign that lands 40 changes and breaks one
frozen hash is a failure that costs the paper.

---

## 2. Scope grid

### 2.1 The seven algorithms

| Algorithm | File | LOC | Archived evidence? |
|---|---|---|---|
| GSK | `src/gsk_family/optimizers/gsk.py` | 234 | cec2011, cec2013, cec2017 |
| AGSK | `src/gsk_family/optimizers/agsk.py` | 388 | cec2011, cec2013, cec2017 |
| APGSK | `src/gsk_family/optimizers/apgsk.py` | 275 | cec2011, cec2013, cec2017 |
| FDB-AGSK | `src/gsk_family/optimizers/fdb_agsk.py` | 378 (+71 `fdb_scores.py`) | cec2011, cec2013, cec2017 |
| ATMALS-GSK | `src/gsk_family/optimizers/atmals_gsk.py` | 400 (+201 `atmals_helpers.py`) | cec2011, cec2013, cec2017 |
| EGSK | `src/gsk_family/optimizers/egsk.py` | 365 | cec2011, cec2013, cec2017 |
| **DT-GSK** | `dt_gsk.py` (328, adapter) + **`_dt_core.py` (5,162, FROZEN)** | ~8,600 total | cec2011, cec2013, cec2017 |

Shared: `_kernels.py` (214) — the sequential `gsk_build_trial` kernel used by all six
classics. DT-GSK subsystems: `_numba_accel.py` (1,433), `interaction_graph.py` (968),
`budget.py` (328), `budget_policy.py` (296), `_dt_rng.py` (261), `_dt_profiles.py` (293).

### 2.2 The five suites (all six registered names verified from `SUITE_PROTOCOLS`)

| Suite | Funcs | Dims | Budget rule | Kernel decorator policy | Archived GSK-family cells |
|---|---|---|---|---|---|
| **cec2017** | 29 (F2 excluded from defaults) | 10, 30, 50, 100 | `10_000·D` | `parallel=True, fastmath=True` **except** `_cf_cal_nb` (composition weights), `bent_cigar_strict_nb`, `_shift_only_strict_nb`, `_shift_rotate_strict_nb` | **all 7** |
| **cec2013** | 28 | 10, 30, 50 (suite validates {2,5,10…100}) | `10_000·D` | `parallel=True`, **fastmath absent suite-wide** (audit M-03) | **all 7** |
| **cec2011** | 22 | native per-function (1 … 240) | **flat 150,000** | **scalar per-row Python dispatcher** ("NOT vectorizable"); numba assists hot spots only, **no `parallel=True` anywhere**; mixed fastmath | **all 7** |
| **cec2013lsgo** | 15 | native: 1000 (F13/F14 = 905) | **flat 3,000,000** | fused single-pass `parallel=True, fastmath=True` **except** 4 group-reduction kernels | **NONE** — only imported `decc-g`, `mos` |
| **cec2020** | 10 | 5, 10, 15, 20 | **per-dim**: {5: 50k, 10: 1M, 15: 3M, **20: 10M**} | `parallel=True`, **fastmath absent suite-wide** (audit H1) | **NONE** — only imported `agsk` |

`sphere` is the sixth registered suite (smoke test, pure NumPy) — out of scope except as a
harness fixture.

**Verified constructibility:** cec2013lsgo and cec2020 are fully constructible end to end
(vendored SHA-256-verified `data.pkl` blobs; live construction + evaluation confirmed).
**Four cec2020 cells are hard-unavailable and raise at construction**: (F1,D5), (F1,D15),
(F8,D5), (F8,D15) — the reference distribution ships no shuffle data for them.

### 2.3 The scope finding you must surface before starting

**No GSK-family algorithm has ever been run on cec2013lsgo or cec2020 in this repo.**
Those directories contain *imported third-party reference tables* (`decc-g`, `mos` for
LSGO; `agsk` for cec2020 — a source-faithful import, D05 zero-padded), not runs we
generated. Yet by §4's projection they are **52% of the projected campaign**.

So the mission as scoped is **not** "speed up existing runs." It is:
- **cec2011 / cec2013 / cec2017** → accelerate *re-runs* of a campaign that already has
  frozen results (maximum governance constraint, §5);
- **cec2013lsgo / cec2020** → make a campaign that has **never been run** feasible at all
  (no archived GSK-family results to protect — but see §5.3, the constraint travels with
  the *algorithm*, not the suite).

State this explicitly in your P0 report. If the owner's intent was only the first,
the projection changes completely and cec2020/D20 drops out of the ranking.

---

## 3. The pre-computed triage — **verify it, do not rediscover it**

A five-agent reconnaissance sweep (2026-07-17) already produced the Appendix A §2 triage
with file:line evidence. **Your job is to confirm or refute it by measurement (Appendix A
§3), not to redo the reading.** If measurement contradicts the table below, the
measurement wins and you must say so loudly — a wrong triage is how Appendix A §11 T3
burned a whole round in the source campaign.

| Algorithm | Triage class | Evidence |
|---|---|---|
| GSK, AGSK, APGSK, FDB-AGSK | **PYTHON-FLOOR-BOUND** | 1 batch eval/gen; trial math compiled; residual = 2 full `(NP,D)` copies + `stable_argsort` + wrapper conversions + validation |
| **ATMALS-GSK** | **RNG-CALL-BOUND** | `_local_search` draws scalar `float(rng.random())` in a **nested Python loop**: `nls(=5) × D` gate draws + one per hit ⇒ **≥ 5·D single-double RNG dispatches/gen** (D=100 → 500+/gen). `atmals_gsk.py:71-108` (esp. 90, 95-107) |
| **EGSK** | **DISPATCH-BOUND** | scipy-SLSQP endgame `_egsk_ip_refine` makes **single-row `(1,D)`** `problem.evaluate` calls (`evaluate(z.reshape(1,dim))`, `egsk.py:186`), budget `min(ceil(2e-3·max_nfes), remaining)` per triggered generation (`:59,170-171`), **no cooldown**. Trigger = `gen ≥ 0.75·g_max` **AND** `(no optimum or best > optimum+target)` **AND** `std([a2,b2,c2])·1e-2 ≤ 1.0` (`:313, 320-321`) — the latter two usually hold late on hard functions, so it approximates "every late generation", **but instrument the real condition, not the shorthand**. Measured share of budget in 1-row dispatches: **16.6% (D10) / 21.4% (D30) / 22.7% (D50) / 23.8% (D100)**; closed form `0.25·ip_fe/(NP+ip_fe)`, strictly **< 25%**. Wall share is *higher* (1-row evals cost more each) + SLSQP's own FD gradients. Side effect: EGSK terminates ~21–24% short of `g_max` generations |
| **DT-GSK** | **PYTHON-FLOOR-BOUND** (low/mid D) → **KERNEL-BOUND** (D≥100) | ~30 sequential Python subsystem blocks/gen is the floor; already heavily de-overheaded (pre-alloc B03/B04/B14, hoists S5/S7, fused bincounts H1, argpartition H6b, argsort skip B06, telemetry gate MEM-1). At D≥100: `NP=5·D=500`, parallel `(NP,D)` kernels + 3 reference-RNG fills dominate |
| *(any)* | **TELEMETRY-BOUND** | **applies to no default configuration.** All six classics record exactly 1 convergence point/gen. DT-GSK's MEM-1 fast path emits 2 scalars/gen and `continue`s past the ~150-field log. The JSONL diagnostics path is **opt-in** (`dt_diagnostics`) |

### 3.1 ⚠ Serial-kernel twins — **AVENUE CLOSED by measurement (2026-08-01)**

> **FINAL CORRECTION (2026-08-01).** This section has now been wrong in both
> directions. v1.0 said serial twins were inapplicable; the v1.2 correction below
> reversed that to "the biggest lever". A later direct measurement recorded in
> `PORT_05_TUNING_TRIAGE.md` (Addendum) came back at **0.95x — no gain** — and
> closed the avenue. The v1.2 correction and its reasoning are kept below as the
> record of how the estimate was formed, not because it held.

#### Superseded heading, retained: *Serial-kernel twins ARE the biggest lever here*

> **CORRECTION (v1.2, 2026-07-17).** v1.0–v1.1 of this section claimed serial twins were
> "mostly inapplicable because the family is population-batch." **That was wrong, and it was
> the document's most load-bearing claim.** The sibling campaign's own `gsk.py` is
> **population-batch with exactly the same shape as this family** (2 evaluate sites: init +
> one `(NP,D)` trial per generation, NP=100 fixed) — and it measured
> **batch→serial gsk: 3.2× (F1 D10) to 10.8× (F28 D10)**, which made it *the fastest
> optimizer in its suite*. Source: `05-Human-Inspired-Family_Python_v0.1/docs/development/
> OPTIMIZER_PERFORMANCE_AUDIT.md`, §"GSK REFREEZE (2026-07-17)".
>
> **The error, named so it is not repeated:** I reasoned that a 60 µs launch amortizes to
> 0.6 µs/eval across NP=100 rows. It does not. **One `problem.evaluate` is 2–15 kernel
> launches, not one** ("2 launches for F1–F10 ≈ 135 µs, 4 for hybrids ≈ 272 µs, 6–15 for
> compositions ≈ 580–965 µs"), and at `threads=1` a `parallel=True` kernel pays the numba
> **workqueue launch on every call regardless of batch size** — 1-thread parallel is
> literally *serial + launch tax*. Appendix A §5.2 states this outright ("**No batch-size
> threshold when production runs 1 thread/worker: serial beats parallel at every batch size
> there**"); v1.0 quoted that line and then contradicted it with assumed arithmetic instead
> of the sibling's measured data. **Measure, don't derive — Appendix A's first rule.**
>
> Round 2 of that campaign closed the question explicitly: "**at threads=1 the parallel
> launch is pure overhead at every batch size**, so the 'indifferent' 11 also gain."
>
> **Batch shape does NOT gate this technique. `parallel=True` kernels + low thread count
> gate it.** This repo has both (§2.2; `run_campaign.py` pins `NUMBA_NUM_THREADS=1`).
> **Serial twins are P3, not a footnote.**

**Appendix A §5.2 (serial-kernel twins) was worth 17–36× per dispatch in the source
campaign. Its headline victims were member-sequential — but its own population-batch gsk
still gained 3.2–10.8×.**

**The shape facts still hold** (verified adversarially, §3.4): the six classic optimizers
are strictly population-batch — one `problem.evaluate(pop)` per generation, batch = current
`NP` (GSK/ATMALS/EGSK: fixed 100; AGSK/APGSK/FDB-AGSK: 100→12; DT-GSK: 5·D → n_min = 12
default, **25 at D≥50**); EGSK adds a single-row SLSQP endgame and DT-GSK a 2-row polish
loop. **What changed is the conclusion drawn from them: shape governs how many dispatches
you make, NOT whether the launch tax is worth killing.** Both classes gain.

**Open with the serial-twin port** (§7 P3). Expected here, by direct analogy to the
sibling's population-batch gsk: **~3–10× on cec2017**, less at high D where kernel volume
dominates (their gsk got only **1.5×** on LSGO D=1000). The extra dispatch surface below
gains *on top* of that, and is where the sibling's 17–36×-per-dispatch figures live:

1. **EGSK's SLSQP endgame** — the family's **largest** member-sequential path
   (§3, DISPATCH-BOUND). This is where §5.2/§5.4 earn their keep, if anywhere.
2. **DT-GSK's final polish** — a serial Python `while` loop dispatching **2-row batches**
   via `eval_batch_strict` at **`_dt_core.py:1960`** (called from `:4621`; `cand =
   np.empty((2, …))` at `:1948`), D≥50 only, budget `floor(0.02·max_nfes)` ⇒ up to
   **~5,000 dispatches at D=50**. This is a **second near-serial path** — the family's
   member-sequential surface is *not* EGSK alone. **The polish call site is inside the
   frozen core (§5.4) — you may not touch it.**
3. **DT-GSK's conditional extra batches** — BSE cauchy (~0.10·NP rows), BSE restart
   (~0.30·NP), coordinate-LS (≤2·elites rows), deep-stall (NP rows). Small batches, not
   single rows. Frozen core.
4. **cec2011 as a whole** — the dispatcher is a **per-row Python loop** over M rows
   (`cec2011/functions.py:536-545`) with no `parallel=True` kernels at all. There is no
   launch tax to remove; the cost is Python per row. Note it is **1% of the campaign** —
   do not spend a round here regardless of how bad it looks.
5. **DT-GSK's dormant single-row LS paths** — `subspace_nm` / `nelder_mead` evaluate
   `(1,D)` per objective call **but are dormant under the pub profile**
   (`local_search_method` defaults to `"coordinate"` at every tier). **Do not optimize a
   dormant path.**

**Where the twins might still pay, and you must measure rather than assume:** the suite
kernels *are* `parallel=True`, and production runs **1 numba thread per worker** (§4.2).
A 1-thread `parallel=True` kernel is "serial + launch overhead" (Appendix A §5.2). At
`NP=100`, a 60 µs launch amortizes to 0.6 µs/eval — but cec2020 D20 runs **10M evals =
~100,000 generations/run**, so that is ~6 s/run of pure tax, ×10 funcs ×25 runs ×7
algorithms. Whether that is 1% or 15% of the cell **is an empirical question**. Answer it
with Appendix A §3.2 at `K = NP` (not K=1) before deciding.

### 3.2 The three concrete §7-class targets already located

Verified, with evidence. Each is a candidate; each still needs its own G1 gate.

> **Verification provenance.** §3.1's headline, EGSK's trigger/budget, ATMALS's draw
> counts, the `_rng_3buf` bypass, the dormant-LS claim, and the Threefry-unroll question
> were each put to an **adversarial verifier instructed to refute them** (2026-07-17).
> Results: ATMALS, `_rng_3buf`, and dormant-LS **confirmed**; EGSK's trigger and the
> "population-batch everywhere" headline came back **partly wrong** and are corrected above;
> the Threefry-unroll hedge came back **refuted** (it is *not* unrolled — the lever is
> live). Two claims in five needed correction. **Apply the same standard to your own P0
> findings: they will not be better than these were.**

1. **`_kernels.py` wrapper ceremony (all six classics, every generation)** —
   `gsk_build_trial` normalizes every input per call: **8 `ascontiguousarray` casts** plus
   **4 `_as_f64_vector` calls that `np.full`-allocate NP-length vectors** when `kf`/`kr`/
   `junior_prob` are scalars. This is Appendix A §5.3 (dispatch pre-resolution) + §7 item 2,
   and it lands **once for six algorithms**. `_kernels.py:159-214`.
2. **Adapter + dispatcher duplicate ceremony (every suite, every call)** — `as_population`
   does contiguity coercion **and a full `np.all(np.isfinite)` scan**, and the suite
   dispatcher **does it again**; plus argument-order sniffing and (cec2017) per-call
   `fp_mode` string normalization. Appendix A §5.3 exactly.
   `benchmark_adapter/problem.py:48-63`, `factory.py:103-110`.
3. **DT-GSK's `_rng_3buf` fast path is dead code in every production run** —
   `_build_phase4_masks` only uses the pre-allocated single-fill buffer when
   `not rng_core.uses_reference_matrix_order`; **`ReferenceRNG` sets it `True` as a CLASS
   attribute** (`_dt_rng.py:85`), so the fast path is unreachable under **every** generator
   (threefry, twister, mcg16807 alike — it is *not* a threefry-specific effect). Production
   always takes the else branch: **three separate `(NP,D)` column-major draws per
   generation, each a freshly allocated non-contiguous transposed view**
   (`reference_rng.py:59`: `flat.reshape(…, cols, rows).swapaxes(-1,-2)`), then consumed by
   numba mask kernels. At D=100, NP=500 → 3 × 50,000-element non-contiguous fills/gen. The
   `(3·NP_init, D)` buffer allocated at `_dt_core.py:2573` **is never filled in any run.**
   Guard repeats at `:993-1001` and `:1064-1077`. **The blocker is the guard, not the
   buffer** — and the reference matrix order it protects is load-bearing (T2′), not
   incidental.
   **⚠ This is inside the FROZEN core (§5.4). It is a documented ceiling line for this
   campaign, not a target.** Record it in the ledger as `ceiling (frozen-core)` with a
   note that it is the single largest known unrealized DT-GSK saving, so a future
   refreeze-authorized campaign knows where to look. **Do not edit it. Do not "just try
   it" on a branch to see.**

### 3.3 The RNG picture

All three reference generators (`ThreefryGenerator`, `TwisterGenerator`,
`Mcg16807Generator`) are Python classes over **njit fill kernels**, subclassing
`DoublesStreamGenerator`. **A scalar `rng.random()` costs a full Python → wrapper → njit
round trip for one double.** That is precisely why ATMALS is RNG-CALL-BOUND.

- Production campaign generator: **threefry** (`run_campaign.py` passes
  `--rand-generator threefry`). GSK's own default is `twister` — **Appendix A §3.1 rule 2
  applies: profile with the production stream or your RNG numbers are meaningless.**
- **[STALE 2026-07-25 — CORRECTED] The Threefry fill kernel IS NOW UNROLLED; this
  lever is CLOSED, not available.** Delivered by `61dc84bd8` ("unroll the
  Threefry-4x64-20 fill kernel - 4.19x, bit-identical (R1)"). The current source has
  20 explicit `# --- round N ---` blocks with literal rotation constants and literal
  key injection; none of the anti-patterns quoted below remain. Do not re-attempt.
  Any RNG share measured now is the cost of the ALREADY-optimised kernel.
  Original (now historical) finding follows:
- ~~**The Threefry fill kernel is NOT unrolled — §6.1's lever is AVAILABLE.**~~ Adversarially
  verified against `threefry_rng.py:113-130`: the rounds loop exhibits **all three** of
  Appendix A §6.1's trigger anti-patterns —
  ```python
  for r in range(20):
      j = r % 8                       # modulo
      r1 = rot_x1[j]                  # rotation-table lookup
      r3 = rot_x3[j]                  # rotation-table lookup
      ...
      if (r + 1) % 4 == 0:            # branchy key injection
          s = (r + 1) // 4
          x0 = x0 + (parity if (s % 5) == 4 else np.uint64(0))
  ```
  Three distinct modulos (`r % 8`, `(r+1) % 4`, `s % 5`), table lookups, ternary key
  injection, **no literal constants**. Appendix A §6.1 measured **3.9×** (96 → 376M
  doubles/s) for exactly this shape, suite-wide, and it is **R1 bit-identical by
  construction** (pure integer ops in identical order) — so it survives the §5 governance
  overlay intact. **Fair caveat before you commit the round:** the kernel is
  `njit(cache=True, fastmath=False)`-compiled (`:138-139`) and LLVM may already unroll a
  constant-trip-count `range(20)` loop, so the *measured* win may fall well short of what
  the source shape suggests. **Measure first** (Appendix A §3.2), then decide. Generate the
  unrolled code mechanically, never by hand-transcription.
- **Column-major fills are real here** (Appendix A trap T2): 2-D draws fill column-major
  and return a transposed `reshape/swapaxes` **view (non-contiguous)**. The ✅/❌ table in
  Appendix A §6.3 is **live** — this is not a hypothetical trap.
- **Existing RNG KATs** to protect you: `tests/unit/test_rng.py` (threefry known-answer
  draws vs external reference + top-of-range seeds), `tests/unit/test_dt_rng.py`
  (13-substream KAT vs `fixtures/dt_rng_kat.json` generated from the source project).

---

## 4. Campaign projection — the ranking that sets your work order

Appendix A §4 demands a projection **before** optimizing. It is done. Assumptions stated
so you can redo it: 51 runs for cec2017/cec2013 (campaign standard), 25 for cec2011
(campaign standard), **25 assumed for cec2013lsgo/cec2020 (never run — confirm with the
owner)**, all four cec2020 unavailable cells excluded.

| Suite | evals/algorithm | family × 7 | **share** |
|---|---:|---:|---:|
| **cec2020** | 3.36e9 | **23.5e9** | **38.8 %** |
| **cec2017** | 2.81e9 | **19.7e9** | **32.4 %** |
| cec2013 | 1.29e9 | 9.0e9 | 14.8 % |
| cec2013lsgo | 1.12e9 | 7.9e9 | 13.0 % |
| cec2011 | 0.08e9 | 0.6e9 | **1.0 %** |
| **TOTAL** | | **60.6e9** | |

At 51 runs instead of 25, cec2020 → 48.0e9 and cec2013lsgo → 16.1e9, pushing the two
greenfield suites to **~64%** of the campaign.

**What this ranking means for you:**

- **cec2020 D=20 alone is 74.4% of the cec2020 suite ⇒ ~29% of the entire campaign.**
  One dim of one suite. Its 10M-eval budget with `NP=100` is ~100,000 generations/run —
  the **per-generation Python floor is multiplied by 100,000**, which is exactly why
  §7-class micro-work (normally worth 0.1–0.8 s/run) can matter here and nowhere else.
  This is your highest-value block. **Start your measurement here.**
- **cec2011 is 1% of the campaign.** It is the most *pathological*-looking suite
  (per-row Python, no parallel kernels, 22 bespoke problems, ODE integrators). Appendix A
  §4's whole point is that this is a trap: it will absorb unlimited effort for ≤1% of
  wall. **Do not enter it** unless the ledger proves otherwise.
- **cec2013lsgo D=1000** is only 13% despite 3M evals/run, because it is 15 functions.
  Its kernels are *already* fused single-pass (no `M×1000` temporaries) — likely
  KERNEL-BOUND and near ceiling. Check §5.3 of Appendix A (pre-resolution) and stop.
- **cec2017 (32%) is the paper's primary suite** — and therefore the one where §5's
  governance constraint bites hardest. Maximum value, minimum freedom.

**Before you use this table: convert it to hours.** Eval counts are not wall-clock;
cec2011 F5/F6 (Tersoff) and F3/F4 (ODE) may be 10³× more expensive *per eval* than a
cec2017 sphere. Run the Appendix A §4 projection properly: short-budget timing × (full
budget / short budget) × runs × cases ÷ workers, **per (algorithm, suite, dim) block**.
The eval-share table above is a *starting hypothesis*, not the answer. Report the
hours-ranked table in P0 and work strictly down it.

---

## 5. ⚠ The governance overlay — **read this before touching a file**

This is where this repo departs most sharply from the source campaign. Appendix A's risk
ladder (R1–R4) assumes you can negotiate tolerance and draw-order rulings. **Here, three
of the four rungs are effectively closed.**

### 5.1 The archived-evidence surface

`benchmarks/cec_reference_results/` is the **single source of evidence for a paper under
submission**. It is bound by four manifests:

| Manifest | Release id | Binds | Format |
|---|---|---|---|
| `papers/governance/evidence_release_manifest.json` | `rel-2026-07-20-67d9345f9` | **3,403 files**, 712,437,624 bytes — cec2011/cec2013/cec2017 × 7 algorithms (context_suites now empty — no cec2013lsgo/cec2020 CSVs) | LF, 1-space indent |
| `benchmarks/cec_reference_results/_ablation/manifest.json` | `abl-rel-2026-07-20` | 1,297 files (amendment A1, 2026-07-17) | **LF, 1-space indent** |
| ~~`benchmarks/cec_reference_results/_oracle/manifest.json`~~ (**REMOVED** 2026-07-18, commit `0d2f291fd`) | `orc-rel-2026-07-14` | tree deleted with the oracle study's removal from the paper; **no longer a verification target** (absent from `BENCHMARK_EVIDENCE_INDEX.md`) | n/a |
| `benchmarks/cec_reference_results/_paper_tables/manifest.json` | `rel-2026-07-20-67d9345f9` | 17 files | CRLF, 1-space |

Plus the paper freeze manifests in `papers/governance/` — **CRLF + 2-space indent**,
edited **byte-surgically, never rewritten wholesale**.

**Every hash binds mint-time working-tree bytes.**

### 5.2 The risk ladder, mapped to this repo

| Class | Appendix A says | **Verdict here** |
|---|---|---|
| **R1 bit-identical** | Gate G1 | ✅ **AVAILABLE.** This is your campaign. Nearly everything you land must be R1. |
| **R2 tolerance** (fastmath compile variance) | Gate G2 + standing human ruling | ❌ **CLOSED by default.** Every one of the 7 algorithms has archived cec2011+cec2013+cec2017 results. Appendix A G2 item 4 is explicit: *"Consumers with archived results excluded by construction — never argue tolerance for frozen data."* An opt-in fast path with a config allowlist could open R2 **for new suites only** — but see §5.3, the trap. |
| **R3 trajectory-changing** (block draws) | Gate G3 + standing "P29 precedent" ruling | ❌ **CLOSED.** No such precedent exists in this repo. Appendix A G3 item 7: *"No archived results exist for the algorithm, or a refreeze is signed."* All 7 algorithms have archived results. **The one juicy R3 target — ATMALS's `5·D` scalar LS draws — is exactly the change that would invalidate ATMALS's archived cec2011/cec2013/cec2017 cells.** |
| **R4 protocol-visible** (telemetry) | Gate G4 + explicit sign-off | ⚪ **MOOT.** Telemetry is already thin by default (1 point/gen; DT-GSK MEM-1 emits 2 scalars). Nothing to thin. Do not manufacture work here. |

### 5.3 The trap that will bite you: *the constraint travels with the algorithm, not the suite*

It is tempting to reason: "cec2013lsgo and cec2020 have no GSK-family archived results, so
I can use R3 block draws there." **That is wrong and it is the single most likely way this
campaign destroys the paper.**

`atmals_gsk.py` is **one file**. If you reorder its draws to run LSGO faster, ATMALS's
archived **cec2017** results stop reproducing. The suite you are *running* is irrelevant;
the constraint attaches to the **algorithm source**.

The only structurally sound way to open R2/R3 for the greenfield suites is Appendix A
§5.2's discipline, applied to *algorithms* rather than kernels: an **opt-in, default-off,
config-allowlisted path**, with a **loader guard that refuses the fast path for any
(algorithm, suite) cell that has archived results**, so the frozen cells keep the legacy
path **by construction** and no tolerance/draw-order argument is ever needed for them.
That is a substantial piece of engineering with its own correctness burden, and it splits
each algorithm into two behavioral paths — a real maintenance and publication-defense
cost.

**Do not build it on your own authority.** Propose it, price it, and get the owner's
explicit ruling (§5.5).

### 5.4 The frozen core — absolutely untouchable

Under a **byte-identity lock**, "vendored and must not be edited for behavior":

```
src/gsk_family/optimizers/_dt_core.py            (5,162 LOC)
src/gsk_family/optimizers/_dt_rng.py             (261)
src/gsk_family/optimizers/_dt_profiles.py        (293)   "data, not logic; never hand-edit a value"
src/gsk_family/optimizers/_dt_subsystems/        (all: _numba_accel, interaction_graph,
                                                  budget, budget_policy, basin_memory,
                                                  bound_constraint, gained_shared_junior,
                                                  gained_shared_senior, _dt_provenance)
```

`dt_gsk.py` (the adapter) is **not** frozen. Per-file SHA-256 of every frozen file is
recorded in `papers/governance/audit_evidence/evaluator_hash_inventory.csv`
(e.g. `_dt_core.py` = 253,027 bytes, `1ef815ce…`).

**Consequence:** DT-GSK — the paper's own algorithm, ~8,600 LOC, and the *most* compute at
D≥50 — is **almost entirely off-limits**. Its residual per-generation Python (linkage
flatten rebuild, deque means at ~6 sites/gen, ARGP ring-buffer loops, `_rng_3buf` bypass)
is a **ceiling line for this campaign by governance, not by physics.** Say so in the
ledger, precisely, with the note that a future refreeze-authorized campaign could reclaim
it. Do not blur "we may not" into "we cannot."

### 5.5 Owner rulings you must obtain **before** the corresponding work

Ask once, in one batch, at the end of P0 — do not trickle these out, and do not proceed on
any of them by assuming:

1. ~~**Scope**: is cec2013lsgo/cec2020 GSK-family execution actually intended?~~
   ✅ **RULED 2026-07-17 — IN SCOPE.** The owner confirmed **cec2013lsgo and cec2020 are
   both in scope** for GSK-family execution. Consequences, binding:
   - §4's projection **stands as written**: 60.6e9 evals, **cec2020 38.8% + cec2017 32.4%**,
     **cec2020 D=20 alone ≈ 29% of the entire campaign**. Work the hours-ranked table.
   - This is a **greenfield campaign for 52% of the work** — no GSK-family results exist for
     either suite. Two things follow that do *not* apply to the paper suites: (i) there is
     no archived baseline to replay against, so **the §6.2 fingerprint battery is the only
     safety net there** — build it first; (ii) the **§5.3 trap is now live and dangerous** —
     these suites are greenfield, but **the algorithms are not**, and R2/R3 on a shared
     algorithm file breaks its archived cec2011/cec2013/cec2017 cells. Re-read §5.3.
   - **Run count is still unconfirmed.** §4 assumes 25; at 51 the two greenfield suites rise
     to ~64% of the campaign (cec2020 → 48.0e9, cec2013lsgo → 16.1e9). Confirm before
     costing, and state which you used in the P0 report.
   - **Feasibility is now a first-class P0 question, not an afterthought**: nobody has ever
     run these cells, so the per-eval cost of cec2013lsgo D=1000 and the wall-clock of a
     single cec2020 D=20 run (10M evals) are **unmeasured**. Measure one cell of each
     *before* projecting the block, and report if either is infeasible on this machine
     regardless of acceleration.
2. **R2/R3 for greenfield suites**: build the opt-in allowlisted dual path (§5.3), or stay
   strictly R1 everywhere?
3. **Refreeze appetite**: is any deliberate, signed refreeze of archived cells on the
   table (Appendix A §9.3), or is byte-reproducibility of `rel-2026-07-20-67d9345f9`
   absolute for this paper cycle?
4. **The already-pending refreeze**: `papers/governance/_pending_refreeze.json`
   (regenerated 2026-07-20 under `rel-2026-07-20-67d9345f9`) records that
   `main_manuscript_freeze_manifest.json` still binds pre-rerun bytes for **11 of 12 files**
   (`main.tex`, `conclusions.tex`, `introduction.tex`, `performance.tex`,
   `proposed_algorithm.tex`, `related_work.tex`, `DT-GSK.pdf`, `DT-GSK.docx`,
   `claims_evidence_matrix.csv`, `citation_usage_map.csv`, `artifact_binding.csv`) —
   remediation ticket **C-008** (terminal, still open). It is a **human byte-surgical step**
   (*"CRLF + 2-space indent; edit hashes in place, never rewrite the file"*).
   **Do not perform it as part of this campaign** and do not let your changes enlarge it.

**Default if no ruling arrives: R1-only, all suites, no dual paths.** That default is a
legitimate, publishable campaign. Take it and proceed rather than blocking.

---

## 6. What this repo already has, and what it is missing

### 6.1 Already in place (do not rebuild — Appendix A §10 assets that exist)

| Appendix A asset | This repo's version | Notes |
|---|---|---|
| **§10.5 integrity sentinel** | ✅ **`runners/fp_regime.py:265-297`** — hard-verified **at every worker spawn**; `run_experiment.py:1149-1186` passes it via `initargs` at every pool build; recorded in `environment.json`. Motivating witness in its docstring: CEC2017 F20 D10 seed 54241459 → `3.1217325598e-01` in fallback vs `0.0` fully-JIT | **This is the manual's §10.5 design already realized.** Its existence is exactly why Appendix A's *"make every fast path opt-in so the sentinel is invariant by construction"* is not optional advice here — it is enforced by a process that **fails the pool** |
| **§10.2 parity sweep (partial)** | ✅ `tests/regression/test_dt_graph_backend_parity.py` — numba-vs-NumPy bit-identity for 6 interaction-graph kernels at D≥50, **and** asserts the kernels are actually *bound* (guards the historical silent-fallback bug) | Model your sweeps on this |
| **§10.1 fingerprint battery (DT-GSK only)** | ✅ `tests/regression/test_dt_gsk_byte_stable.py` — 4 golden cells, seed 12345, `max_nfes=3000` | D≤30 only (below the D≥50 tier) |
| FP-regime bit sentinel test | ✅ `tests/regression/test_fp_regime.py` — exact IEEE-754 bit pattern (struct-packed hex) | |
| RNG / config KATs | ✅ `tests/unit/test_rng.py`, `test_dt_rng.py` (13 substreams), `test_dt_profiles.py` | Generated from the source project |
| Replay ladder | ✅ `tests/regression/test_validation_ladder.py` — exact Python replay of runner artifacts | |
| Thread/BLAS pinning | ✅ **only in the wrappers**: `scripts/run_campaign.py:179-186` (`pinned_env`) and `papers/scripts/finalize_evidence.py:159-166` (`base_env`) set `OMP/MKL/OPENBLAS/VECLIB/NUMEXPR/NUMBA_NUM_THREADS=1` | ⚠ see §9 T3′ |
| Output-safety guard | ✅ `runners/verification.py` — `ensure_output_root_allowed` **refuses to write generated output into the reference tree** | |

Full suite: **618 tests, ~2 min**, `python -m pytest` (testpaths=`tests`, pythonpath=`src`,`.`).

### 6.2 The gap you must close first — **six of seven algorithms have no golden trajectory**

**Golden-trajectory KATs exist only for DT-GSK.** GSK, AGSK, APGSK, FDB-AGSK, ATMALS-GSK
and EGSK have only contract/determinism smoke tests (same-seed-twice, fair-start
equivalence) and exact values on **tiny hand-computable quadratics (46.0 / 90.0)**.
EGSK's test is a MATLAB smoke-oracle *threshold* (`sphere F1 D10 < 1e-2`) — **not** a
golden trajectory.

**Appendix A G1 step 1 is therefore not optional and not cheap here: you must build the
fingerprint battery for six algorithms before you edit any of them.** Follow §10.1:
≥3 cells across function classes × ≥2 seeds × every kernel path, recording `repr(best)`,
`sha256(solution bytes)`, `sha256(full trace arrays)`, `nfes`. Capture **through the
production runner entry point** (§9 T4′), on the **threefry** stream, **before** the first
edit. Commit the captured JSON.

There is a strong argument for promoting that battery into `tests/regression/` permanently
— it is the asset the repo most conspicuously lacks, and it outlives this campaign.

### 6.3 Absent (do not go looking)

- **`docs/development/OPTIMIZER_PERFORMANCE_AUDIT.md` does not exist in this repo.** It is
  the sibling project's record (`05-Human-Inspired-Family_Python_v0.1`). **You will create
  this repo's equivalent — that is deliverable D5 (§10).**
- No `CLAUDE.md` anywhere in the tree or above it.
- The DT-GSK tuning registry — referenced in older notes under its former name
  `ism_gsk_tuning_registry.md` (pre the 2026-07-14 ISM-GSK→DT-GSK rename) — **does not exist**
  in this repo under either that name or a renamed `dt_gsk_*` path; do not hunt for it.
- Nothing under `results/` for cec2013lsgo or cec2020.

---

## 7. Phase plan

Work strictly in order. Each phase has an exit artifact. **Do not skip P0 — the entire
value of Appendix A is that P0 stops you from optimizing the wrong term.**

### P0 — Parity, census, ledger, projection *(no edits)*

1. Establish production parity (Appendix A §3.1). **All four rules, all live here:**
   - **threads**: `numba.set_num_threads(1)` *before anything compiles* — production is
     `run_campaign.py --workers 15` with `NUMBA_NUM_THREADS=1`. Note `run_experiment.py`'s
     own default is `workers=2` with an **auto CEC2017 F21+ cap of 8**, and each worker's
     initializer caps numba threads to `cores // workers`. **Profile the campaign regime
     (15/1), not the CLI default.**
   - **stream**: `threefry` (campaign) — **not** GSK's `twister` default.
   - **warmup**: the runner JIT-warms the first cell per worker; your probes must too.
   - **load discipline**: interleaved A/B/A/B, report `min`, ratios vs a same-session
     reference.
2. Dispatch census (Appendix A §3.3) per (algorithm, suite): calls + batch-size histogram.
   **Expected result: K=NP-dominant everywhere except EGSK's endgame.** If you see
   K=1 dominance anywhere else, §3.1 above is wrong — report it.
3. Layer isolation (§3.2) at K=1 **and** K=NP for each suite's `evaluate`.
4. Attribution ledger (§4): 100% of a run's wall to named owners, each stamped **ceiling**
   or **target**. Stamp frozen-core lines `ceiling (frozen-core)` — a distinct third label;
   do not silently merge them into physics-ceiling.
5. **Hours-ranked campaign projection** (§4) per block. Convert §4's eval-share table into
   wall-hours. cec2011's per-eval cost is the biggest unknown — measure it.
6. **Exit artifact**: a P0 report containing the ledger, the hours-ranked table, the
   confirmed-or-refuted §3 triage, the §2.3 scope finding, and the **§5.5 ruling requests**.

### P1 — Build the fingerprint battery *(no optimization edits)*

Six algorithms × the §6.2 recipe, through the production entry point, on threefry.
Commit the baseline JSON. **Exit**: batteries regenerate byte-identically twice in a row
(this also proves determinism, G1 step 4).

### P2 — Wire the gates

G1–G4 checklists (§8) as runnable scripts before landing anything. Frozen-replay gate
(§10.4) covering every archived (algorithm, suite) cell.

### P3 — The highest-projected block *(from P0's hours ranking, not from §4's guess)*

Almost certainly cec2020 D=20 (≈29% of campaign) or cec2017. Enter Appendix A Part II at
the section your ledger points to — **most likely §7 (micro-set) and §5.3
(pre-resolution)**, given the triage.

### P4 — The shared, land-once wins

`_kernels.py` wrapper (§3.2 item 1) and adapter/dispatcher double-ceremony (§3.2 item 2).
These benefit **six algorithms × five suites** from one change each. All R1. Highest
value-per-risk in the campaign.

### P5 — ATMALS-GSK, within R1

Its `5·D` scalar-draw loop is the family's hottest scalar site — **and the block-draw fix
is R3, which is closed (§5.2).** So: what is reachable at R1?
- Appendix A **§6.2 scalar fast paths** (bit-identical, 1.3–2×) — *if* the scalar path
  isn't already fast-pathed. **Verify first.**
- Appendix A **§6.4 persistent draw buffers** — R1 *by construction* for counter-based
  generators (block N yields the same values ⇒ stream bytes unchanged). **This is the one
  structural RNG lever that survives the governance overlay.** It is the most interesting
  technical question of this campaign: can you refill in bulk chunks and serve ATMALS's
  singles from the buffer, bitwise-identically, for the **threefry** counter-based stream?
  (For MT19937/mcg16807 the same argument needs its own proof — they are sequential
  generators, not counter-based.)
- Appendix A **§6.1 unroll** — **check whether it is already unrolled** (§3.3) before
  planning.
- If none survive: **stamp it ceiling and say why.** "R3 would give 19× and is
  governance-closed" is a legitimate, valuable ledger line — it tells the owner the exact
  price of the freeze.

### P6 — EGSK's dispatch surface

The family's only genuine §5.2/§5.4 target. Note the endgame calls `problem.evaluate` with
`(1,D)`; Appendix A §5.4's K=1 wrapper fast path applies to the **adapter**, which is
shared — so it must be R1 with **identical error strings, state transitions, and return
values**, and it is covered by the frozen-replay gate for all seven algorithms.

### P7 — cec2013lsgo / cec2020 kernels *(only if P0's hours say so)*

LSGO kernels are already fused single-pass; expect KERNEL-BOUND / near-ceiling. cec2020 is
`parallel=True, fastmath=False` **suite-wide by audit ruling H1** (composition F8–F10 blend
basic-kernel outputs; FMA/reordering would break bit-for-bit reproducibility). **Adding
fastmath there is not a tuning decision — it would overturn a recorded audit ruling. Do not.**

### P8 — Re-ledger, ceiling proofs, stop

Appendix A §13 per algorithm: residual wall decomposed into (a) mandated RNG volume
(a formula), (b) mandated dispatch structure, (c) mandated kernel math, **(d) governance-
frozen (this repo's fourth category — name the manifest/lock and what it would take to
reclaim)**. Then stop.

---

## 8. Gates — Appendix A §9, with this repo's actual commands

Run mechanically. **Revert rule: any gate failure reverts the *item*, not the batch.**

**G1 (bit-identical)** — every change in this campaign, by default:
```
# 1. BEFORE any edit — capture (§6.2 battery), through the production runner, threefry
# 2. edit
# 3. regenerate → dict-equality, no tolerance
# 4. determinism: same seed twice ⇒ identical repr
python -m pytest tests/unit tests/smoke tests/regression -q     # 618 tests, ~2 min
# 5. if shared code touched (_kernels.py, benchmark_adapter/*, common/rng*) → ALSO G4
```

**G2 (tolerance)** — **presumed unavailable (§5.2).** Do not open it without a §5.5 ruling.
If ruled available for greenfield suites only: exhaustive sweep, all functions × dims ×
K ∈ {1,3,8,50} × ≥300 seeded batches, ≥10⁵ rows, ULP via Appendix A §10.2's
sign-corrected int64 distance; calibrate the documented bound **on the exhaustive sweep**
(trap T5); archived cells excluded **by construction**.

**G3 (trajectory-changing)** — **unavailable (§5.2/§5.3).** No standing ruling exists.

**G4 (shared-code / protocol)** — mandatory whenever you touch `_kernels.py`,
`benchmark_adapter/*`, `common/rng.py`, `common/reference_rng.py`,
`common/threefry_rng.py`, or anything the runner imports:
```
# 1. frozen replays: EVERY archived (algorithm, suite) cell reproduces byte-identically
#    THROUGH THE PRODUCTION RUNNER (never a direct algorithm call — trap T4′)
# 2. FP-regime integrity sentinel unchanged (runners/fp_regime.py) — it fails the pool if not
python -m pytest -q                                            # full suite green
# 3. verify manifest hashes still resolve:
#      papers/governance/evidence_release_manifest.json         (3,403 files)
#      benchmarks/cec_reference_results/_ablation/manifest.json (1,297)
#    EOL-TOLERANTLY (§9 T10′) — raw, CRLF→LF, LF→CRLF
# 4. commit the verified state promptly (trap T8)
```

**G5 — this repo's extra gate. THE MANIFESTS.** Not in Appendix A because the source
campaign had no equivalent. Before **and** after any landed batch:
- recompute the 3,403-file release manifest and the 1,297-file ablation manifest
  **EOL-tolerantly**;
- confirm `papers/governance/_pending_refreeze.json` still lists **exactly 11** changed
  files — **if your work enlarges that list, you have broken the paper's freeze and must
  revert**;
- never rewrite a manifest wholesale. **Freeze manifests: CRLF + 2-space, byte-surgical
  edits in place. Ablation manifest: LF + 1-space.** `sed -i` and
  `Path.read_text()/write_text()` **normalize line endings and silently break every hash
  in the file.** Read bytes, write bytes.

---

## 9. Traps — Appendix A §11, re-scored for **this** repo

Appendix A's traps are all real. These are the ones that are **live here specifically**,
with this repo's evidence:

- **T1′ Cache-artifact poisoning** — LIVE if you attempt serial twins (§3.1). Every suite
  kernel is `cache=True`. `cache=False` on all `py_func` re-jits, warmup per worker.
- **T2′ Column-major fills** — **LIVE, confirmed**: 2-D draws fill column-major and return
  non-contiguous transposed views (`reference_rng.py:39-59`). Any draw consolidation must
  obey Appendix A §6.3's ✅/❌ table. This is also *why* DT-GSK's `_rng_3buf` fast path is
  bypassed in production (§3.2 item 3) — the reference matrix order is load-bearing, not
  incidental.
- **T3′ Off-parity profiling** — **LIVE and sharpened**: `run_experiment.py` **sets no env
  vars itself**; BLAS/OMP pinning exists **only** in `run_campaign.py` and
  `finalize_evidence.py`. **A bare `python run.py …` runs UNPINNED.** If you profile that
  way, your numbers are from a different machine than production. Put the parity preamble
  in every probe script.
- **T4′ False replay mismatches** — **LIVE and pre-loaded**: GSK's default generator is
  `twister`, the campaign uses `threefry`; `run_experiment.py` defaults `workers=2`, the
  campaign uses 15. A direct algorithm call resolves **different defaults** and will
  "fail" a replay that is actually fine. **Replays go through the production entry point,
  always.**
- **T5′ Sampled-tolerance falsification** — dormant (G2 closed). Reactivates the moment a
  §5.5 ruling opens R2.
- **T6′ Hidden re-association** — **LIVE, high probability**: the §3.2 §7-class targets are
  exactly where this bites (`d_junior = ceil(dim*power(schedule_base, k_vec))`, the
  `_as_f64_vector` scalar broadcasts, hoisting `(ub-lb)`). Appendix A §7 item 2's rule is
  absolute: **never re-associate**. Keep `((1-2r)*(ub-lb))/t`; keep `floor((1.0+r)+0.5)`.
  Diff the float expression trees, not the algebra.
- **T7′ Tie-set divergence** — **LIVE**: all six classics call `stable_argsort` every
  generation, and it is an obvious argpartition "optimization" target. **First-occurrence
  semantics are part of the behavioral contract.** DT-GSK already uses argpartition for DE
  donors (H6b) *inside the frozen core* — that is precedent for the core, **not** licence
  for the classics.
- **T8′ Shared-tree races** — **LIVE**: this session has already hit `index.lock` from
  concurrent git operations. Capture baselines and re-checks in the same tree state; verify
  `HEAD == verified tree`.
- **T9′ Trusting run-config cosmetics** — LIVE: per-run `run_config.json` records *runner*
  values; do not read them as algorithm parameters.
- **T10′ (NEW — not in Appendix A) EOL / hash-basis.** `core.autocrlf = true`, **no
  `.gitattributes` anywhere** in this repo or at the git root `D:/AI/PhD-Projects`. Hash
  basis is **checkout-EOL-dependent** (the now-removed `_oracle` tree was the mixed-CRLF/LF case). All manifest
  verification must be EOL-tolerant (raw / CRLF→LF / LF→CRLF). A `-text` pin plus one-time
  re-mint is planned **post-submission** — **not your job, and do not pre-empt it**: adding
  `.gitattributes` mid-campaign would re-write working-tree bytes and break 3,403 hashes at
  once.
- **T11′ (NEW) Optimizing a dormant path.** DT-GSK's `subspace_nm`/`nelder_mead` single-row
  LS paths look like prime §5.4 targets and are **never executed under the pub profile**
  (`local_search_method` defaults to `"coordinate"` at every tier). Verify a path is live
  in the **production profile** before you cost it. The same applies to
  `atmals_prob_update`'s O(history) vstack — **it exists but the optimizer never calls it**.

---

## 10. Deliverables

| # | Deliverable | Where |
|---|---|---|
| **D1** | **P0 report** — ledger (ceiling / target / **ceiling(frozen-core)**), hours-ranked projection, triage confirmed-or-refuted, §2.3 scope finding, **§5.5 ruling requests** | `docs/development/` |
| **D2** | **Fingerprint batteries** for the six un-KAT'd algorithms, captured pre-edit; ideally promoted to `tests/regression/` | `tests/` + committed JSON |
| **D3** | **Landed changes**, each with its proof attached, each R1 unless a §5.5 ruling says otherwise | source + gate evidence |
| **D4** | **Ceiling proofs** (Appendix A §13) per algorithm, with this repo's 4th category: *governance-frozen* — naming the manifest/lock and the cost to reclaim | `docs/development/` |
| **D5** | **`docs/development/OPTIMIZER_PERFORMANCE_AUDIT.md`** — this repo's permanent audit register (the sibling project's equivalent is the model). **The register is the publication defense.** | `docs/development/` |

**Do not `git push`.** The owner pushes. Commit verified states promptly with real
messages (T8′).

---

## 11. The honest prior

The source campaign cut weeks → 1–2 days. **A large win IS available here** — the sibling's
own population-batch gsk is the proof. But the mix is different: its kernel/RNG-layer wins
transfer wholesale, while its dispatch-collapsing wins (two-thirds of that campaign) target
member-sequential shapes this family doesn't have, and its biggest RNG win is
governance-closed here.

Measured in the sibling campaign (**not** estimates), mapped:

| Technique | Its measured win | **Available here?** |
|---|---|---|
| **§5.2 serial twins — cec2017** | **gsk (population-batch) 3.2×→10.8×**; member-sequential 17–36×/dispatch | ✅ **YES — the biggest lever. P3.** Our cec2017 kernels are `parallel=True` + campaign pins `threads=1`. ⚠ **R2 (≤3e-15 rel under fastmath)** ⇒ governance-gated (§5.2) |
| **§5.2 serial twins — LSGO D=1000** | gsk **1.5×** (kernel volume dominates at high D) | ✅ available; **greenfield, no archive to protect** — 0 ULP measured there (their group kernels are `fastmath=False`, as ours are) |
| §5.2 serial twins — cec2011 | **none** — "zero prange kernels, no launch tax" | ❌ **N/A by construction.** Matches our recon exactly. And it's 1% of our campaign |
| **§6.1 Threefry unroll** | **96→376 M doubles/s (3.9×)**, suite-wide, **stream-identical** | ✅ **YES, R1.** Verified NOT banked here (`threefry_rng.py:113-130`). Their note: "**gsk, the heaviest RNG consumer (3·NP·D doubles/gen), gains disproportionately**" |
| **§7 gsk.py micro-set** | **~8–15%** on the serial residual, 5 named R1 edits | ✅ **YES, R1** — copy elimination, kernel-arg hoisting, donor scratch reuse, flat 1-D draw, scalar pow. Directly shape-compatible |
| §5.3 dispatch pre-resolve | ~3 µs of a ~15 µs **single-row** round-trip | ⚠ **marginal** — only EGSK's endgame is single-row here |
| §6.2 RNG scalar fast paths | 8.1→3.2 µs on `integers(size=1)` | ✅ **R1** — pays for **ATMALS** (`≥5·D` scalar draws/gen) |
| §6.3 block draws | **19×** on their worst algorithm | ❌ **R3, governance-closed** — and it is exactly ATMALS's hot site. Their enabler was explicit: *"ema has no async structure and **no frozen results**"* |
| §7 telemetry dedup | 82% of snapshot recomputes avoided | ⚪ **moot** — our classics record 1 point/gen; their gsk's 47%-ceiling telemetry lead does **not** transfer (different harness) |
| §6.3 gsk r3-collision blocking | — | ❌ **certified dead**: "class iii **not-blockable** (unbounded redraw-until), ≤0.5 ms/run — leave as-is". **Do not re-propose** |
| Kernel fusion | ~3–5% of the launch slice | ❌ **rejected twice** — not bit-identical, breaks F11–F30 reproducibility. Serial twins get the same prize without touching kernel arithmetic |

**Realistic shape of the win: serial twins on cec2017 (~3–10×) + Threefry unroll (up to
3.9× on RNG) + the micro-set (~8–15%), concentrated at cec2020 D=20** where a 10M-eval
budget at NP=100 multiplies every per-generation saving by ~100,000 generations.

**But the governance ceiling is real and it is the difference between the two projects.**
The sibling could land serial twins on gsk only via an **explicit user-authorized un-freeze**
that cost: a 30-fingerprint battery, a named production replay, a **1.2 GB archive retired
to a dated backup**, allowlist surgery, and **a full regeneration of gsk's leg — the old
results were thrown away and recomputed**. Here, *all seven* algorithms × three suites are
archived under a 3,403-file manifest. **The serial-twin win on cec2017 is R2 (≤3e-15
relative under fastmath), so it is not free: it requires the same ruling (§5.5 #3), or it
must be scoped to the greenfield suites by construction.** LSGO/cec2020 need no ruling —
nothing is frozen there, exactly as LSGO needed none in the sibling ("no LSGO results exist
to fork").

**So the honest priced choice for the owner:**
- **R1-only, all suites** → Threefry unroll + micro-set + scalar fast paths. Real, safe, modest.
- **R1 everywhere + serial twins on greenfield only** (cec2013lsgo/cec2020, 52% of the
  campaign) → **no refreeze needed, no ruling needed** — the archive is untouched by
  construction. **This is the recommended default.**
- **+ serial twins on cec2017** → the 3–10× on the paper's primary suite, but it costs a
  signed refreeze and a full regeneration of every archived cell. The sibling paid exactly
  that price and judged it worth it — but they had one algorithm to re-run, not seven.

---
---

# APPENDIX A — The Stochastic-Computing Acceleration Manual (v2)

> **Normative reference, reproduced verbatim.** Its worked examples come from the sibling
> 24-algorithm campaign, **not** this repo. Where it conflicts with Parts 1–10 above,
> Parts 1–10 win. Its evidence record `docs/development/OPTIMIZER_PERFORMANCE_AUDIT.md`
> lives in `05-Human-Inspired-Family_Python_v0.1`, not here.

# The Stochastic-Computing Acceleration Manual
### (GSK-Family Tuning Playbook, v2 — codebase-agnostic edition)

**Purpose.** A complete, self-contained acceleration manual for any
scientific-Python codebase of the GSK-family shape: NumPy/Numba compute
cores, stochastic algorithms with reproducibility constraints, and
campaign-scale workloads (thousands of runs × millions of evaluations).
An engineer who has never seen the originating repository should be able to
follow this document alone and reproduce order-of-magnitude campaign
accelerations with a zero-regression safety record.

**Provenance.** Every pattern here was developed, proven, and landed in a
real four-round campaign (a 24-algorithm metaheuristics benchmarking study,
2026-07-14 → 2026-07-17) that cut total campaign wall-clock from **weeks to
~1–2 days** with **every change gated on a proof** — most bitwise, the rest
distributionally validated. The concrete instances and measured numbers from
that campaign appear throughout as *worked examples*; the patterns are
primary. Full evidence record: `docs/development/OPTIMIZER_PERFORMANCE_AUDIT.md`.

**How to use this manual.** Read Part I once. Then triage your codebase with
§2, enter Part II at the section the triage points to, and never land
anything without the matching gate checklist from Part III.

---

# PART I — METHOD

## 1. The cost model

> **wall ≈ Python/RNG floor + (number of dispatches) × (fixed cost per dispatch)**

Every hot loop in this class of codebase decomposes into these three terms.
The entire manual is techniques for shrinking each term — but the order is
fixed: **measure which term dominates before touching anything.** Optimizing
the wrong term produced zero-value work every time it was attempted.

A *dispatch* is any crossing from interpreted Python into compiled/vectorized
work: a JIT kernel call, a BLAS call, a vectorized NumPy op on a tiny array.
Each carries a fixed cost (argument boxing, runtime entry, thread-pool
launch) that is invisible for large batches and dominant for small ones.

## 2. Triage decision tree

Profile first (§3), then follow the tree. Expected-gain ranges are from the
worked campaign; your mileage scales with how badly the symptom presents.

```
START: cProfile one production-shaped run (§3.1). Where does cumulative time sit?
│
├─ Mostly inside compiled kernels / problem.evaluate?
│   ├─ Is evaluate(1 row) ≈ evaluate(100 rows) in wall time?     → DISPATCH-BOUND
│   │     → §5 (serial twins, launch-tax elimination)             gain 2–25×
│   │     risk: bit-identical-or-tolerance  |  gates: G1+G2+G4
│   └─ Per-row math genuinely dominates at all batch sizes?      → KERNEL-BOUND
│         → you are near ceiling; only §5.3 pre-resolution +      gain 5–15%
│           §7 micro-set apply. Consider it proven-floor (§13).
│
├─ Mostly inside RNG calls (generator._draw, random(), integers())?
│   ├─ Millions of SCALAR draws (size None/1) per run?           → RNG-CALL-BOUND
│   │     → §6.3 P29 block draws (if in data-dependent loops)     gain 5–20×
│   │     → §6.2 scalar fast paths (if unavoidable singles)       gain 1.3–2×
│   └─ Bulk draws but the fill kernel itself is slow?            → RNG-FILL-BOUND
│         → §6.1 unroll the generator                             gain 2–4×
│
├─ Mostly in the algorithm's own Python (loops, allocation, copies)?
│                                                                 → PYTHON-FLOOR-BOUND
│     → §7 micro-set sweep (hoists, aliases, draw consolidation)  gain 1.1–2×/file
│     → §5.2 if the loop also emits tiny dispatches (usually both)
│
├─ Mostly in telemetry/recording?                                 → TELEMETRY-BOUND
│     → §8 compute-thinning + snapshot caching                    gain 5–15%
│     risk: PROTOCOL-VISIBLE — requires human sign-off (§9.3)
│
└─ Nothing dominates / all small?                                 → NEAR CEILING
      → write the ceiling proof (§13) and STOP. Stopping is a
        deliverable, not a failure.
```

**Risk classes referenced everywhere below:**
- **R1 BIT-IDENTICAL** — outputs provably byte-equal. Gate checklist G1.
- **R2 TOLERANCE** — outputs equal within a measured, documented FP bound
  (compile-variance class). Gate checklist G2. Requires a standing
  human ruling on the acceptable bound.
- **R3 TRAJECTORY-CHANGING** — same distributions/consumed-counts, different
  draw order ⇒ legitimately different runs. Gate checklist G3. Requires a
  standing human ruling (the "P29 precedent" in the worked campaign).
- **R4 PROTOCOL-VISIBLE** — changes recorded artifacts (telemetry density,
  archived formats). Gate checklist G4 + explicit human sign-off per change.

## 3. Production-parity profiling

### 3.1 The parity rules
Measure under the *exact* production regime or your numbers will lie:

1. **Thread count:** set it before any kernel compiles or runs
   (`numba.set_num_threads(1)` if production pins one thread per worker).
   *Worked example:* the campaign's worst offender measured "96× slower than
   baseline" at default 16 threads but ~7× at production 1 thread — the
   per-launch cost changes >2× with thread count, and interleaved
   thread-wake penalties change it far more. A whole round of prioritization
   would have been wrong.
2. **RNG stream:** use the production generator. Ad-hoc calls often fall to
   a different default (twister vs threefry here) and mis-measure RNG-heavy
   code paths completely.
3. **Warmup:** run each subject once before timing (JIT compilation).
4. **Load discipline:** measure `min` over interleaved A/B/A/B repetitions so
   machine-load drift hits every variant equally; report load conditions;
   treat *ratios against a same-session reference* as the durable quantity,
   never absolutes.

### 3.2 Layer isolation skeleton

```python
import time, numba
numba.set_num_threads(PROD_THREADS)          # BEFORE anything compiles

def timeit(fn, *a, reps=2000):
    fn(*a)                                    # warm
    t0 = time.perf_counter()
    for _ in range(reps): fn(*a)
    return (time.perf_counter() - t0) / reps

full   = timeit(problem.evaluate, one_row)        # public API
kernel = timeit(inner_kernel, *prepared_args)     # innermost JIT directly
# wrapper cost = full - kernel; repeat at K=1 and K=100 to expose fixed costs
```

### 3.3 Dispatch census skeleton
Count every evaluate call and its batch size per algorithm — the histogram
identifies dispatch-tax victims instantly (K=1-dominant ⇒ victim):

```python
CTR = {"calls": 0, "hist": collections.Counter()}
orig = problem.evaluate
def counting(x):
    a = np.atleast_2d(np.asarray(x)); CTR["calls"] += 1; CTR["hist"][a.shape[0]] += 1
    return orig(x)
object.__setattr__(problem, "evaluate", counting)   # frozen dataclass override
run_algorithm(problem, options)
```

*Worked example:* the census showed three algorithms issuing 95–99% single-row
dispatches (4,400–6,300 per 6,000 evaluations) — the launch-tax victims — and
one issuing 10× more *rows* than counted evaluations (a speculative design:
math-bound, not tax-bound). Two different problems, two different fixes.

## 4. Attribution ledger + wall-clock projection

**Ledger:** attribute 100% of a run's wall to named owners (kernel math, RNG,
algorithm Python, harness wrapper, telemetry, dispatch overhead) and stamp
every line **ceiling** (mandated by the published algorithm/protocol —
untouchable) or **target** (implementation-borne — must die). Only targets
get effort. The ledger is also your stopping criterion (§13).

**Projection:** before optimizing, project the full campaign per work block:
`short-budget timing × (full budget / short budget) × runs × cases ÷ workers`.
Rank blocks by projected hours; work strictly down the ranking.
*Worked example:* projection revealed one algorithm was **49.7% of the entire
remaining campaign** and one benchmark suite was **75–85% of all remaining
wall** — neither was the loudest-looking problem in casual profiling.

---

# PART II — STRATEGIES

Every strategy: **Trigger → Recipe (skeleton) → Proof → Risk class → Worked
example.**

## 5. Dispatch-bound codebases

### 5.1 Know the launch tax
`@njit(parallel=True)` kernels enter the threading runtime on every call:
~60 µs/launch at 1 thread (workqueue), ~110 µs at 16, and worse when calls
interleave with Python (sleeping worker threads must wake). One logical
"evaluation" may be several launches (shift kernel + base kernel +
composition weights…). The tax is per-*call*, not per-row.

**Detection test:** time `evaluate` at K=1 and K=100. If they are within ~2×
of each other, you are paying fixed dispatch cost, not math.

### 5.2 Serial-kernel twins (the biggest lever; R1-or-R2)
Give every parallel kernel a `parallel=False` twin compiled from the *same*
source object, and route opted-in callers to the twins through a thread-local
scope. Same math, no launch.

```python
# _numba_serial.py — twin factory
def _serial_twin(dispatcher):
    opts = dict(dispatcher.targetoptions)        # inherits per-kernel fastmath policy
    opts.pop("parallel", None); opts.pop("nopython", None); opts.pop("cache", None)
    return njit(cache=False, **opts)(dispatcher.py_func)
    #          ^^^^^^^^^^^ LOAD-BEARING. cache=True silently LOADS THE
    #          PARALLEL BUILD'S on-disk artifact for the same py_func —
    #          your "serial" twin runs at parallel speed with no warning.
    #          Verified twice. Pay the ~0.25 s/kernel compile once per
    #          worker in an explicit warmup() instead.

# _kernel_mode.py — thread-local routing (per compute-backend package)
_STATE = threading.local()
def serial_kernels_active(): return getattr(_STATE, "serial", False)
class serial_kernel_scope:                       # __slots__ class ≈ 0.1 µs/entry
    __slots__ = ("_prev",)
    def __enter__(self): self._prev = getattr(_STATE, "serial", False); _STATE.serial = True
    def __exit__(self, *exc): _STATE.serial = self._prev

# each kernel call site
kernel = _ns.rastrigin_nb if serial_kernels_active() else _rastrigin_nb
return kernel(np.ascontiguousarray(x, dtype=np.float64))
```

Design rules proven necessary:
- **Opt-in only, default off.** Callers with archived/frozen results and any
  integrity sentinel keep the legacy path *by construction* — no tolerance
  argument needed for them.
- **Per-backend scopes** (one thread-local per compute package) so a scope
  can never route a different backend's kernels.
- **No batch-size threshold** when production runs 1 thread/worker: serial
  beats parallel at *every* batch size there (1-thread parallel = serial +
  launch overhead). One kernel set per opted-in run ⇒ clean provenance.
- **Config allowlist + loader guard:** opting in is a per-algorithm config
  entry; the loader *refuses* algorithms whose archived results were
  generated on the legacy path (removing one from the guard is a deliberate,
  signed "refreeze" — §9.3). Make the guard *scope-aware*: it protects the
  dataset it was written for, not unrelated datasets with no archives.
- **Fail closed:** if the twins' JIT is unavailable, constructing an
  opted-in problem raises — never silently fall back to a different FP path.
- **Record provenance everywhere:** console banner, per-run config JSON,
  problem metadata.

**Proof:** exhaustive twin-vs-original parity sweep over ALL functions ×
dims × batch sizes (§10.2). Non-fastmath kernels: bitwise **by construction**
(same instruction order). Fastmath kernels: compile-variance tolerance,
calibrated on the exhaustive sweep (§11, trap T5).

*Worked example:* single-row kernel call 60→0.4 µs (~160×); end-to-end
per-dispatch 17–36×; the three member-sequential victims went from 58–85× the
reference to 2.4–3.8×; on a D=1000 suite the same port was worth an estimated
45–110 wall-hours, with 4,080/4,080 parity rows bitwise (hot kernels were
non-fastmath).

### 5.3 Dispatch pre-resolution (R1)
**Trigger:** the public evaluate wrapper re-does per-call ceremony on values
frozen at construction — argument sniffing, mode parsing, duplicate
contiguity coercion, duplicate finiteness scans, dimension re-validation.
**Recipe:** bind the final callable once at closure-build time; keep exactly
one validation layer and *write the redundancy proof in a comment* ("upstream
`as_population` already returns validated contiguous finite float64 of the
right width"). ~3 µs of a ~15 µs single-row round-trip in the worked example.

### 5.4 The K=1 fast path in shared wrappers (R1)
**Trigger:** member-sequential algorithms make ~one single-row wrapper call
per evaluation; array machinery (`np.all(np.isfinite(v))`, argmin) on a
1-element vector is ~2 µs of pure overhead.
**Recipe:** a `shape[0]==1` branch using scalar ops — with **identical error
strings, state transitions, and return values** (byte-equality of behavior,
not just numbers). Lands once, benefits every caller.

## 6. RNG-bound codebases

### 6.1 Unroll counter-based fill kernels (R1)
**Trigger:** the generator's fill kernel loops rounds with table lookups
(`rot[r % 8]`), modulo, and branchy key-injection per round.
**Recipe:** fully unroll with literal constants; *generate the unrolled code
mechanically* (a 20-round transcription by hand invites typos; a bitwise
verifier catches them, but generation avoids them). Pure integer ops in
identical order ⇒ bit-identical by construction — still verify on 100k+
values across seeds, counter offsets, and the carry/wraparound path.
*Worked example:* Threefry-4x64-20 fill 96 → 376M doubles/s (**3.9×**),
suite-wide; the heaviest RNG consumer (the reference algorithm itself,
3·N·D doubles/gen) gained disproportionately — this single change flipped the
final "fastest algorithm" ranking.

### 6.2 Bit-identical scalar fast paths (R1)
**Trigger:** hot single-value draws routed through vectorized machinery
(per-call `asarray/floor/astype/clip` + dtype-info construction for ONE value).
**Recipe + the two proofs that make it R1 (write both in comments):**

```python
if size is None or size == 1:
    u = float(self._draw(1)[0])
    v = lo + int(u * span)      # int() == floor ONLY because u*span >= 0
    if v > hi - 1: v = hi - 1   # u<1 can still ROUND u*span up to span at
    ...                         # the float boundary — clamp is reachable
```

**Gate:** stream equivalence (singles sequence == block draw, bitwise, plus
generator state match) **and** frozen replays (§10.4) — shared RNG code is
upstream of everything.

### 6.3 The block-draw doctrine (R3 — the approved trajectory-changing class)
**Trigger:** scalar draws inside *data-dependent* loops — draw-until-done
allocation loops, per-member redraws — thousands per generation.
**Recipe:** pre-draw fixed-shape blocks sized by the loop's hard cap;
consume them by index inside the **unchanged** recurrence; unread tails are
deliberate speculative draws (the schedule stays data-independent).

```python
# per phase: one index block (rows, CAP+1) + one fraction block (rows, CAP)
dims  = rng.integers(0, dim, size=rows * (CAP + 1)).reshape(rows, CAP + 1)
fracs = rng.random(rows * CAP).reshape(rows, CAP)
# the recurrence body is IDENTICAL — only where values come from changed:
while budget > tol and steps < CAP:
    amount = float(fracs_row[steps]) * budget
    delta[int(dims_row[steps])] += sign * amount
    budget -= amount; steps += 1
```

**What must stay exact:** per-element distributions; per-operation *consumed*
draw counts; the recurrence's floating-point association (**never**
reformulate `budget -= f*budget` via cumprod — it reassociates and can change
step counts). Only draw ORDER moves.

**THE COLUMN-MAJOR TRAP (memorize):** reference-faithful RNGs fill matrices
column-major (MATLAB semantics). Therefore:
- ✅ `random(3n)` == three consecutive `random(n)` (1-D fills are stream slices)
- ✅ `random((k, N, D))` == k successive `random((N, D))` (leading-axis collapse)
- ❌ `random((3, N))` ≠ three `random(N)`  — interleaves the stream
- ❌ widening 2-D shapes (`(5N, D)`, `(N, 5D)`) — interleaves the stream

**Proof (all four required, §10.3):** recording-RNG replay (block path ==
scalar path bitwise given the same values); KS-grade distribution tests;
algorithm-invariant checks; full-budget quality sanity vs sibling algorithms.
*Worked example:* the campaign's worst algorithm made ~395k scalar RNG
round-trips per run (80% of its wall). Block draws: 19× — from 49.7% of the
campaign to noise — with 500/500 recording-replay cases bitwise and KS
p-values 0.29–0.90 on every distributional check.

### 6.4 Persistent draw buffers (R1)
Refill scalar-draw streams in bulk chunks from the counter-based generator
(block N always yields the same values ⇒ stream bytes unchanged); singles are
then buffer reads instead of kernel dispatches.

## 7. Python-floor-bound: the micro-set catalogue (all R1)

Run this rubric over every algorithm file. Each item: the pattern, the
one-line proof requirement.

| # | Pattern | Recipe | Proof point |
|---|---|---|---|
| 1 | Full-array copies per generation | alias + one blended `np.where(mask[:,None], new, old)` | prove the aliased array is never mutated before its last read; fresh output array keeps id-keyed caches honest |
| 2 | Loop-invariant recomputation | hoist `(ub-lb)`, `np.full` constants, partition bounds, `np.finfo` tiny, scalar powers of constants | **never re-associate**: keep `((1-2r)*(ub-lb))/t`, never pre-divide; keep `floor((1.0+r)+0.5)`, never `1.5+r` — both change rounding |
| 3 | Scratch buffers rebuilt per generation | hoist + `.fill()` reset | every element rewritten each use; no consumer retains a reference |
| 4 | Consecutive same-size draws | one flat draw + slices (§6.3 rules!) | 1-D only, or leading-axis; never 2-D widening |
| 5 | Fancy gathers on contiguous ranges | `arr[start:stop]` views instead of `arr[np.arange(start,stop)]` copies; drop `.copy()` after advanced indexing (already fresh) | nothing mutates the source during the view's lifetime |
| 6 | Per-element Python unboxing loops | `.tolist()` first, or vectorize the scan | control flow identical |
| 7 | Per-call helper ceremony | specialize generic helpers at hot sites (e.g. 1-exclusion index draw: `d=rng.integers(0,n-1); d += d>=i`) | identical reduced-range draw + shift mapping, probe 10k draws |
| 8 | Dict/list rebuilds per generation | hoist + reset in place | trivial; watch signature churn (skip if it costs more review than it saves) |

**Measured anti-patterns (do not do):** `count_nonzero`→`any` (slower);
argpartition for top-k with ties (tie-order divergence ⇒ R3, not R1);
norm→loop without checking accumulation order; buffer-threading through 3+
signatures for <1 ms/run (skip and record the judgment).

*Worked example:* a five-agent sweep with this rubric landed ~60 items across
18 algorithm files — every one gated byte-identical, zero reverts — worth
0.1–0.8 s/run per file on top of the structural wins.

## 8. Telemetry-bound (R4 — protocol-visible)

- **Snapshot caching (R1):** multi-phase algorithms record the same
  population several times per iteration — cache the O(N·D) snapshot keyed by
  a collision-safe population fingerprint (id + shape + corners + sum).
- **Compute-thinning (R4):** compute expensive per-generation statistics only
  on a log-spaced evaluation grid via a default-off config knob; keep
  counters and cheap stats dense; keep protocol checkpoints exact (they
  compute their own snapshots). **Requires explicit sign-off** because
  archived series density changes. Verify: default-off byte-identity; on-grid
  values byte-equal to a dense run; trajectory identical.
- **Storage-thinning (R1 for storage):** subsample the on-disk log,
  compute summaries from the full in-memory series.

---

# PART III — SAFETY

## 9. Risk classes and gate checklists (run these mechanically)

### G1 — BIT-IDENTICAL claims
1. □ **Capture BEFORE any edit:** fingerprint battery (§10.1) on every
   touched algorithm: ≥3 cells across function classes × ≥2 seeds × every
   kernel path, recording `repr(best)`, sha256(solution bytes),
   sha256(full trace arrays), evaluation count.
2. □ Apply the change.
3. □ Regenerate the battery: **every fingerprint byte-equal.** Any mismatch
   ⇒ bisect items, revert the offender, record it with evidence.
4. □ Determinism: same seed twice ⇒ identical `repr`.
5. □ Unit + smoke tests for the touched files green.
6. □ If shared code was touched → also G4.

### G2 — TOLERANCE claims (compile-variance class)
1. □ A standing human ruling exists for the bound (get one; don't assume).
2. □ **Exhaustive** parity sweep — all functions × dims × batch sizes,
   ≥10⁵ rows total; calibrate the documented bound on this sweep (trap T5).
3. □ Non-fastmath subset verified strictly bitwise.
4. □ Consumers with archived results excluded by construction (opt-in gating)
   — never argue tolerance for frozen data.
5. □ Provenance label distinguishes the new path in every artifact.

### G3 — TRAJECTORY-CHANGING (block-draw / draw-order) claims
1. □ A standing human ruling covers the class; the change is draw-ORDER only.
2. □ Recording-replay proof: new path == old path **bitwise** when fed the
   identical values (≥100 randomized cases).
3. □ KS tests (α=0.01, ≥2k samples) on step counts + per-dimension marginals.
4. □ Algorithm invariants hold through the *production* path (e.g.,
   conservation identities to ~1e-16 relative).
5. □ Full-budget quality sanity vs sibling algorithms (nothing catastrophic).
6. □ Consumed-count and distribution documentation updated in the module
   docstring + notes metadata (trajectories differ — say so).
7. □ No archived results exist for the algorithm, or a refreeze is signed.

### G4 — SHARED-CODE / PROTOCOL changes
1. □ Frozen replays (§10.4): every archived algorithm reproduces its recorded
   fingerprint **byte-identically** through the *production* execution path.
2. □ Integrity sentinel (§10.5) unchanged.
3. □ Full test suite (unit + smoke + regression) green.
4. □ For R4 specifically: explicit human sign-off recorded with date and
   scope before landing.
5. □ Commit the verified state promptly (trap T8).

**Revert rule (all classes):** any gate failure reverts the *item*, not the
batch; bisect to the offender; a frozen-replay failure reverts *everything*
touching that algorithm, no exceptions.

## 10. Verification harness skeletons

### 10.1 Fingerprint battery

```python
def fingerprint(alg, cells, seeds, budget, **path_flags):
    out = {}
    for f, d in cells:
        for s in seeds:
            r = run(alg, make_problem(SUITE, f, d, budget=budget, **path_flags),
                    {"seed": s, "rand_generator": PROD_STREAM})
            out[f"{f}_{d}_{s}"] = dict(
                bf=repr(float(r.best_fitness)),
                bx=sha256(np.asarray(r.best_x).tobytes()).hexdigest(),
                conv=sha256(np.asarray(r.convergence).tobytes()).hexdigest(),
                nfes=int(r.nfes))
    return out
# capture → json to disk → edit → regenerate → dict-equality, no tolerance
```

### 10.2 Exhaustive parity sweep (for G2)
All functions × dims × K ∈ {1, 3, 8, 50} × ≥300 seeded batches; per cell:
fraction bitwise + max ULP via sign-corrected int64 bit-pattern distance:

```python
ia = a.view(np.int64).copy(); ia[ia < 0] = np.int64(-(2**63) + 1) - ia[ia < 0]
ib = b.view(np.int64).copy(); ib[ib < 0] = np.int64(-(2**63) + 1) - ib[ib < 0]
max_ulp = int(np.max(np.abs(ia - ib)))
```

### 10.3 Recording-RNG equivalence proof (for G3)

```python
class RecordingRng:                       # wraps the real generator
    def integers(self, lo, hi, size=1):
        v = self._rng.integers(lo, hi, size=size); self.ints.append(int(v[0])); return v
    def random(self, size=1):
        v = self._rng.random(size); self.fracs.append(float(v[0])); return v
# 1) run the SCALAR path with the recorder → expected output + value log
# 2) pack the log into the block layout (pad tails arbitrarily — unread)
# 3) run the BLOCK path on the packed log → np.array_equal REQUIRED
```

### 10.4 Frozen-replay gate
Record, once, the production-path fingerprints of every algorithm with
archived results (a short fixed cell, fixed seed, through the *runner's* own
entry point — **not** a direct algorithm call, which resolves different
defaults and produces false mismatches; this mistake cost a real debugging
session — trap T4). Re-run after every shared-code change; byte-equality or
revert.

### 10.5 Integrity sentinel
A hash over (a) compiled-kernel availability flags and (b) output bytes of
fixed probe inputs through *default-constructed* problems, enforced at
worker spawn. Any default-path FP change breaks loudly and fails the pool.
**Design consequence:** make every fast path opt-in so the sentinel is
invariant *by construction* — you never have to argue about it.

### 10.6 Adversarial verification (highest-assurance changes)
Independent reviewers/agents instructed to **refute** the safety claim:
thread-leak attacks on the scope, cache-poisoning checks (list compiled-
artifact dirs before/after), replays against pre-change checkouts, exhaustive
sweeps sized to falsify sampled claims. In the worked campaign this layer
*did* falsify a sampled tolerance claim (§11 T5) — that is it paying rent.

## 11. THE TRAPS (paid for once; never pay again)

**T1 — Cache-artifact poisoning.**
*Symptom:* a `parallel=False` re-jit shows zero speedup; "compile" takes 0.2 s.
*Wrong conclusion:* "serial kernels don't help here."
*Detection:* time the twin — if 1-row ≈ the parallel build, you loaded its
cached artifact; also `twin.targetoptions` looks right, which deepens the trap.
*Handling:* `cache=False` on all `py_func` re-jits; explicit warmup per worker.

**T2 — Column-major matrix fills.**
*Symptom:* a consolidated 2-D draw passes shape checks but the fingerprint
battery diverges.
*Wrong conclusion:* "the consolidation math is wrong somewhere else."
*Detection:* compare `random((k, n))` element order against k×`random(n)`.
*Handling:* the ✅/❌ table in §6.3. Leading-axis collapse and flat-1-D only.

**T3 — Off-parity profiling.**
*Symptom:* huge slowdowns that shrink dramatically in production.
*Wrong conclusion:* mis-ranked optimization targets (a full round of effort).
*Detection:* re-measure the headline number at production thread count/stream.
*Handling:* §3.1 parity rules; put the parity preamble in every probe script.

**T4 — False replay mismatches.**
*Symptom:* a frozen replay "fails" after a provably inert change.
*Wrong conclusion:* "the bit-identical claim was wrong" — panic revert.
*Detection:* did you call the algorithm directly instead of through the
production runner? Different default generator/init ⇒ different result.
*Handling:* replays go through the production entry point, always (§10.4).

**T5 — Sampled-tolerance falsification.**
*Symptom:* the exhaustive sweep finds ULP outliers far beyond the sampled bound
(here: "≤2 ULP" from 6k rows became **11 ULP** at 2.16M rows).
*Wrong conclusion:* shipping a documented contract that reviewers can falsify.
*Detection/Handling:* calibrate documented bounds on the exhaustive sweep;
restate docs everywhere the old bound appeared; keep relative-error framing
(11 ULP ≈ 2.5e-15 relative) alongside ULP counts.

**T6 — Hidden re-association.**
*Symptom:* an "algebraically identical" refactor fails the battery.
*Wrong conclusion:* "the battery is flaky."
*Detection:* diff the float expression trees: `1.0+r+0.5` vs `1.5+r`,
`x/t` hoisted as `x*(1/t)`, `a-=f*a` vs `a*=(1-f)`, cumprod forms.
*Handling:* preserve the exact association and operation order; write "do not
refold" comments at the load-bearing spots.

**T7 — Tie-set divergence.**
*Symptom:* argpartition/argsort-based "equivalent" selection changes results
on ties. *Handling:* first-occurrence semantics (`argmin`, stable sorts) are
part of the behavioral contract; treat any change as R3, not R1.

**T8 — Shared-tree races.**
*Symptom:* background auto-commit jobs snapshot mid-edit states; concurrent
agents confound each other's before/after baselines.
*Handling:* capture baselines and run final re-checks in the same tree state;
commit verified states promptly with real messages; move archives aside
(dated backup dirs), never delete; verify `HEAD == verified tree` after any
auto-commit interference.

**T9 — Trusting run-config cosmetics.**
*Symptom:* archived config fields that record *runner* values (e.g. a
fair-start payload size) get read as *algorithm* parameters by reviewers.
*Handling:* audit recorded-artifact field names before publication.

## 12. Governance (the lines that are never crossed)

- Published operators, equations, phase ordering, selection semantics, and
  search dynamics: exactly per the source specification. Performance work
  never changes *what* is computed for accepted results — only how fast.
- Asynchronous member-sequential structures stay asynchronous. (The
  async→phase-synchronous "vectorization" was attempted twice by independent
  implementers in the worked campaign and reverted both times by ruling —
  it changes search dynamics.)
- Draw distributions and per-operation consumed counts are sacred; draw
  order is movable only under a standing R3 ruling.
- Archived result sets are byte-reproducible or deliberately, sign-off
  refrozen — nothing in between.
- Every landing carries its proof, and the proof is preserved in the audit
  register: the register *is* the publication defense.

---

# PART IV — EVIDENCE APPENDIX (the worked campaign)

## 13. Ceiling proofs — the stopping criterion

Optimization *stops* when the attribution ledger shows only ceiling lines,
and that endpoint is **proven, not assumed**, with a short written argument
per algorithm: its residual wall decomposed into (a) mandated RNG volume
(a formula: draws per generation × generations), (b) mandated dispatch
structure (e.g. ~3N single-row evaluations per iteration for asynchronous
member-sequential designs — irreducible without changing the published
algorithm), (c) mandated kernel math. *Worked example:* the slowest compliant
algorithms plateau at ~2–4× the reference precisely because of (b) — the
written proof of that floor is what lets future maintainers not waste a fifth
round discovering it.

## 14. The measured ledger (what each strategy bought)

Campaign trajectory: **weeks → ~57 h → ~1–2 days** for 24 algorithms × 3
benchmark suites, zero regressions, every change proof-gated.

| Strategy | § | Measured effect (worked campaign) |
|---|---|---|
| Serial-kernel twins, suite 1 | 5.2 | dispatch 17–36×; worst algorithms 58–96× ref → 2.4–3.8× |
| Serial-kernel twins, D=1000 suite | 5.2 | 5.3×/4.4×/1.7× end-to-end; ~45–110 h recovered |
| Block-draw doctrine (worst algorithm) | 6.3 | 3.83 → 0.202 s (19×); 49.7% of campaign → noise |
| Generator unroll (Threefry) | 6.1 | 96→376M doubles/s; flipped the fastest-algorithm ranking |
| RNG scalar fast paths | 6.2 | ~30% on scalar-draw-heavy algorithms |
| Reference-algorithm micro-set + refreeze | 7, 9.3 | rank 12 → rank 1 of 24 (4/4 race cells) |
| K=1 wrapper fast path | 5.4 | ~2 µs/evaluation × every member-sequential algorithm, landed once |
| All-file micro-set sweep (~60 items) | 7 | 0.1–0.8 s/run per file; zero reverts across 18 files |
| Dispatch pre-resolution | 5.3 | ~3 µs of a ~15 µs round-trip |
| Telemetry thinning (D=1000, signed) | 8 | few core-hours; protocol-gated |

## 15. Replay checklist for a new codebase

1. □ Production parity established (§3.1) — threads, stream, warmup, load discipline.
2. □ Dispatch census + attribution ledger + campaign projection (§3.3, §4).
3. □ Triage via §2; enter Part II at the indicated section, in projected-hours order.
4. □ Wire §10 harnesses and the §9 gates BEFORE landing anything.
5. □ Dispatch-bound → serial twins (mind T1), pre-resolution, K=1 paths.
6. □ RNG-bound → unroll, scalar fast paths, block draws (mind T2, T6).
7. □ Python-floor → run the §7 rubric over every algorithm file.
8. □ Telemetry → quantify, then sign-off before thinning.
9. □ Re-ledger; stamp remaining lines ceiling; write the §13 proofs; STOP.
10. □ Preserve the ledger + proofs as the permanent audit register.
