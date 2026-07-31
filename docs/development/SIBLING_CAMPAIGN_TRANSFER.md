# Sibling-Campaign Transfer — every tuning that can make the GSK family fast

**2026-07-17 · What was proven in `05-Human-Inspired-Family_Python_v0.1`, mapped onto
`02-GSK_Family_Python_v1.1` (7 algorithms × cec2017/cec2013/cec2011/cec2013lsgo/cec2020).**
Companion to `ACCELERATION_CAMPAIGN_PROMPT.md` (method + governance). Every number below is
**measured in the sibling campaign** unless marked *estimated*. Source of truth:
`05-Human-Inspired-Family_Python_v0.1/docs/development/OPTIMIZER_PERFORMANCE_AUDIT.md`.

---

## 0. The one fact that governs the whole transfer

The sibling project's **`gsk.py` is population-batch — the identical shape to this family**
(two `problem.evaluate` sites: init + one `(NP,D)` trial per generation, NP=100 fixed).
So it is not an analogy: **their gsk *is* our gsk**, and whatever it gained, we can expect.

It gained, in order:

| Lever | Measured on their population-batch gsk |
|---|---|
| Serial-kernel twins (cec2017) | **3.2× (F1 D10) → 10.8× (F28 D10)** |
| Serial-kernel twins (LSGO D=1000) | **1.5×** (kernel volume dominates at high D) |
| Unrolled Threefry fill | **3.9×** on RNG (96 → 376 M doubles/s); gsk "gains disproportionately" — **✅ already banked here at 4.19×** (§1.2) |
| `gsk.py` micro-set | **~8–15%** on the serial residual |

Result: *"The proposed method is now the fastest optimizer in the suite in the regime the
campaign actually runs"* — 4/4 race cells, +3% to +16% over the previous leader.

**Roughly two-thirds of that campaign does NOT transfer** — wave-splitting, rejection-aware
speculative batching, phase-merging, the local-read/global-read dichotomy — because it all
exists to drag *member-sequential* optimizers toward gsk's shape. **This family is already
at that target.** Do not port it; do not let its 10–19× headline numbers set expectations.

---

## 1. ✅ APPLIES — ranked by expected value here

### 1.1 Serial-kernel twins — **the biggest lever** ⭐
- **What:** re-jit each suite kernel's *same* `py_func` with `parallel=False`; route opted-in
  callers via a thread-local scope. Same math, no numba workqueue launch.
- **Why it pays even at NP=100:** one `evaluate` is **2–15 kernel launches** (F1–F10 ≈ 2 ≈
  135 µs; hybrids ≈ 4 ≈ 272 µs; compositions ≈ 6–15 ≈ 580–965 µs), and at `threads=1` the
  launch is paid **per call at every batch size** — 1-thread `parallel=True` is literally
  *serial + tax*. Single-row kernel call **60 µs → 0.4 µs**.
- **Expected here:** **~3–10× on cec2017**, **~1.5× on cec2013lsgo D=1000**, **0 on cec2011**.
- **Preconditions (all verified present):** suite kernels are `parallel=True` ✅ (cec2017,
  cec2013, cec2013lsgo, cec2020); campaign pins `NUMBA_NUM_THREADS=1` ✅
  (`run_campaign.py:146-153`).
- **Risk:** **R2** on cec2017/cec2013lsgo (fastmath tail). Sibling's exhaustive bar, 2.16 M
  rows: *95.68% bitwise; worst **11 ULP** (F29 D100); **relative ≤ 2.5e-15 everywhere***;
  documented contract **≤3e-15 relative under fastmath, bit-identical under strict fp**.
  → **R1 by construction on cec2013 and cec2020** (fastmath absent suite-wide, by audit
  ruling M-03/H1) and on cec2013lsgo's 4 group-reduction kernels (0 ULP measured there:
  4,080/4,080 rows).
- **⚠ Two traps to copy exactly:** `cache=False` on the re-jit is **load-bearing**
  (`cache=True` silently loads the *parallel* build's on-disk artifact — a silent-correctness
  trap, "verified twice"); and **per-suite scopes** so a cec2017 scope can never route LSGO
  kernels.
- **Cost:** ~2.3 s/worker one-time warmup, folded into the pool initializer.
- **Status here:** the cec2017 serial-twin **infrastructure has landed, opt-in and default-OFF**,
  and the R2 question was *measured* on cec2017 — **93.20% bitwise, worst 13 ULP** (close to the
  sibling's 95.68% / 11 ULP). That measurement is exactly why cec2017 twins are a **priced**
  choice (Option C — signed refreeze + full ×7 regeneration), not a free win. See §4.

### 1.2 Unrolled Threefry-4x64-20 fill kernel ⭐ — ✅ **LANDED**
- **What:** unroll the 20 rounds with literal rotation constants + compile-time key
  injection. Pure integer ops in identical order ⇒ **stream-identical by construction**.
- **Sibling measurement:** **96 → 376 M doubles/s (3.9×)**, suite-wide. Their note: *"gsk, the
  suite's heaviest RNG consumer (3·NP·D doubles/gen), **gains disproportionately**."*
- **Status here: DONE — this lever is spent.** `common/threefry_rng.py` is **already unrolled**:
  the fill kernel emits the rounds as literal `np.uint64` rotation constants (generated
  mechanically), and the old `r % 8` / `(r+1) % 4` / `s % 5` anti-patterns are gone. It landed
  as a **bit-identical R1 edit at 4.19×** on the RNG (measured here — on the optimistic side of
  the 3.9× sibling estimate), verified bitwise on **980,000 doubles** across seeds, counter
  offsets, and the carry/wraparound path. Threefry is the production stream
  (`run_campaign.py --rand-generator threefry`; dt-gsk forces it regardless of policy), so the
  win is realized family-wide. The measure-before-committing caveat (LLVM might already unroll a
  constant-trip `range(20)`) was settled by that measurement.

### 1.3 The `gsk.py` micro-set — 5 named R1 edits
Landed as one bit-identical batch, **~8–15% of the serial residual**, gated on a
**30-fingerprint battery** (best_fitness/best_x/convergence × 5 cells × 3 seeds × both
kernel paths) + a production replay. All five are shape-compatible with our six classics:
- **Copy elimination** — 2 full `(NP,D)` copies/gen → alias + one blended `np.where`.
  ✅ *Our gsk/agsk/apgsk/fdb_agsk/atmals/egsk each do exactly `pop = popold.copy(); popold = pop.copy()` per generation.*
- **Kernel-arg hoisting** — call the compiled trial-builder directly with loop-invariant
  vectors. ✅ *Our `_kernels.py:159-214` does **13 `ascontiguousarray` casts + 4 allocating
  `_as_f64_vector` calls per generation** (in `gsk_build_trial`). Lands once for six algorithms.*
- **Donor scratch-buffer reuse.** ✅ likely applicable (`common/donors.py`).
- **Flat 1-D draw** — `3×random(NP)` → one `random(3*NP)`.
  🚨 **PORT THE WARNING TOO:** *"1-D draws are stream-sequential; a 2-D `(3,NP)` draw would
  NOT be equivalent — column-major fill."* Our RNG fills column-major and returns
  non-contiguous transposed views (`reference_rng.py:59`) — this trap is **live**.
- **Constant-K scalar schedule pow.** ✅ *our gsk does a vector `power` over an all-equal
  `k_vec` where a scalar suffices.*

### 1.4 RNG scalar fast paths
- **Measured:** `integers(size ∈ {None,1})` **8.1 → 3.2 µs**; scalar `_draw(count==1)` combine.
- **Applies here:** ✅ **R1** — pays for **ATMALS-GSK**, whose `_local_search` makes
  **≥5·D scalar `float(rng.random())` calls/gen** in a nested Python loop
  (`atmals_gsk.py:95-107`); 500+/gen at D=100. Our scalar path goes
  `random(None) → float(self._draw(1)[0])` — a full Python→njit round trip per double.
- **Proof bar:** stream equivalence on 20k draws (bitwise + generator-state match) **and**
  frozen replays.

### 1.5 Persistent draw buffers (manual §6.4)
- **R1 by construction** for counter-based generators (block N always yields the same
  values ⇒ stream bytes unchanged). Serves ATMALS's singles from a bulk buffer.
- ⚠ The argument is **counter-based-specific**: it holds for threefry; MT19937/mcg16807 are
  sequential generators and need their own proof.

### 1.6 cec2011-style analytic quick wins
- **Measured:** scipy-import hoist ≈ **13% of F3**; memoization; constant hoists.
- **Applies here:** ✅ R1 — but **cec2011 is 1% of our campaign**. Do it only if free.

---

## 2. ❌ DOES NOT APPLY — do not spend a round

| Technique | Their result | Why it's dead here |
|---|---|---|
| **Wave-splitting** | sgo-social **10.4×** | Needs member-sequential + local-read. **1 dispatch/gen has no waves to split.** |
| **Rejection-aware speculative batching** ("single most valuable lever") | tlbo 2.84×, po 2.24× | Same. Also became *negative value* on their own serial path (sns's 9.84× speculative volume = "pure excess"). |
| **Phase-merging** | pro **2.80×** | Needs ≥2 independent same-iteration phases. Our junior/senior already build **one** trial matrix. |
| **`count_precomputed`** (kill redundant budget-accounting eval) | qsa 1.52× | Needs a double-eval. **GSK has none.** |
| **Per-member loop vectorization** | seeker-oa 3.76× | Our classics are already vectorized. |
| **Ragged-list → dense arrays** | hlo 1.65× | We use dense `(NP,D)` throughout. |
| **Telemetry dedup** | 82% of recomputes avoided | Needs multi-phase re-recording. Our classics record **1 point/gen**; DT-GSK's MEM-1 emits 2 scalars. |
| **Their gsk's #1 residual: dense per-gen diversity telemetry** (47% ceiling) | — | **Harness difference — does not transfer.** Their `TelemetryRecorder` snapshots diversity per generation; ours doesn't. |
| **Population size N** | — | Needs-decision there; **N=100 is already gsk's reference**. Research choice, not perf. |
| **Kernel fusion** | ~3–5% of launch slice | **Rejected twice**: not bit-identical, breaks F11–F30 reproducibility. Serial twins take the same prize without touching kernel arithmetic. |
| **gsk r3-collision draw blocking** | — | **Certified not-blockable**: unbounded redraw-until without a spec cap; **≤0.5 ms/run**. *Never re-propose.* |
| **cec2011 serial twins** | — | *"zero prange kernels — no launch tax."* Nothing to remove. |

---

## 3. 🔒 BLOCKED BY GOVERNANCE — the real difference between the two projects

**Block draws (R3)** — their single biggest wall win: **ema 3.83 s → 0.202 s (19×)**,
49.7% of the campaign → noise, 500/500 recording-replay cases bitwise.

**Unavailable here**, and their own text says exactly why it was available *there*:
> *"ema has no async structure (all phases snapshot-determined) and **no frozen results**."*

Every one of our 7 algorithms has archived cec2011+cec2013+cec2017 cells under a 3,409-file
manifest. **And the constraint travels with the *algorithm*, not the suite** — reordering
ATMALS's draws to speed up LSGO breaks ATMALS's archived cec2017 cells.

**What un-freezing actually cost them** (they did it, once, for gsk — the price is the
point):
1. **Explicit user authorization** — *the un-freeze is the gate, not the code*
2. 30-fingerprint battery, all byte-identical
3. Named production replay (`538.539710494278`)
4. **1.2 GB archive retired to a dated backup — moved, never deleted**
5. Allowlist/refusal-list surgery
6. **Full leg regeneration — the old results were thrown away and recomputed**
7. Full suite green + FP sentinel unchanged

They had **one** algorithm to regenerate. We have **seven × three suites**.

---

## 4. The recommendation — a priced choice

| Option | Gets you | Governance cost |
|---|---|---|
| **A. R1-only, all suites** | Threefry unroll **✅ banked (4.19×)** + micro-set (8–15%) + scalar fast paths | **None.** No ruling, no refreeze. |
| **B ⭐ RECOMMENDED. A + serial twins on greenfield only** (cec2013lsgo, cec2020 = **52% of the campaign**) | **+ ~1.5–10× on the two suites that have never been run** | **None** — nothing is frozen there, exactly as LSGO needed no ruling in the sibling ("no LSGO results exist to fork"). Archive untouched **by construction**. |
| **C. B + serial twins on cec2017** | **+ ~3–10× on the paper's primary suite** (32% of campaign) | **Signed refreeze + full regeneration of every archived dt-gsk/×7 cell.** R2 (≤3e-15). |
| **D. C + R3 block draws** | + up to 19× on ATMALS | Refreeze of **all** archived cells. Not recommended. |

**Option B is free, needs no ruling, and covers the majority of the projected campaign.**
It is also exactly what the sibling did first on LSGO, for the same reason.

Note the pleasing asymmetry: **cec2013 and cec2020 have no fastmath at all** (audit rulings
M-03 and H1) ⇒ serial twins there are **R1, bit-identical by construction** — no tolerance
argument needed even in principle.

---

## 5. Two warnings the sibling paid for — inherit them free

- **`cache=False` on every `py_func` re-jit.** `cache=True` silently loads the *parallel*
  build's cached artifact; your "serial" twin then runs at parallel speed with **no
  warning**, and `targetoptions` still *looks* right. They hit it twice.
- **Never widen a 2-D draw.** `random((3,NP)) ≠ 3× random(NP)` under column-major fill.
  Only flat-1-D (`random(3*NP)`) and leading-axis collapse are stream-equivalent. Our
  reference RNG fills column-major (`reference_rng.py:59`) — **live trap**.

## 6. Calibration — how much to trust the forward estimates

Their measured-vs-predicted record: hlo 1.53 predicted / **1.65 landed**; qsa 1.66 / 1.52;
po ~2.2–2.5 / 2.24; tlbo ~2.4–3 / 2.84; seeker-oa ~3.4–4.1 / 3.76 — good. **But two badly
overshot:** sns predicted ~3.7–4.6× and landed **1.52×**; bso predicted ~2–2.3× and landed
**~1×** (a correct fix with no payoff). **Treat forward estimates as ±2× on the pessimistic
tail — including the ones in this document.**

**The first landing here fits the record:** the Threefry unroll (§1.2) was estimated at 3.9×
(sibling) and **measured 4.19×** here — on the optimistic side, as expected for a
stream-identical, pure-integer-op change with no fastmath tolerance tail.

And the campaign **reversed its own conclusion once**: it declared *"the optimization
ceiling is the algorithm level, reached"* and *"realistic ceiling ~4×gsk"* — then found the
60 µs launch was not a floor at all and drove toa to 2.4× with **zero algorithm changes**.
**Measure; don't derive.** (This document's own v1.0 made precisely the derived-not-measured
error about serial twins — see the correction box in `ACCELERATION_CAMPAIGN_PROMPT.md` §3.1.)
