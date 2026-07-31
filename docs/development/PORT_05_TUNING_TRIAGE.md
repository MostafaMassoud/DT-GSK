# Porting project-05 tuning into 02 — Phase 1 audit and triage

Read-only audit, 2026-07-26. No code changed. Establishes what is actually
portable before anything is moved, because the headline claim ("all suites and
algorithms tuned in 05") turns out to be mostly already present here.

## Finding 1 — the suite kernels are NOT behind

Kernel inventories are **identical** between the projects on every suite:

| Suite | 02 kernels | 05 kernels |
|---|---|---|
| cec2011 | 13 | 13 |
| cec2013 | 22 | 22 |
| cec2017 | 25 | 25 |
| cec2020 | 19 | 19 |
| cec2013lsgo | 26 | 26 |

`cec2013lsgo/_numba.py` is byte-identical. The other four differ only in
**module docstrings** (cross-reference wording, warm-up prose) — no functional
drift. `optimizers/_kernels.py` is 214 lines in both.

**Triage: nothing to port.** 02's own acceleration campaign (CR-0009…CR-0018)
already closed this ground.

## Finding 2 — the serial-twin layer differs in style, not coverage (cec2017)

02 wraps kernels **lazily** through a module `__getattr__` + `_twin` helper
(6 defs). 05 wraps them **eagerly** via a `_serial_twin(dispatcher)` factory
applied to 25 kernels. Both re-jit `dispatcher.py_func` with `parallel=False`
while inheriting per-kernel `targetoptions`.

Coverage is equivalent; 02's lazy form arguably better, since it pays no compile
cost for kernels a run never touches.

**Triage: do not port.** Swapping an equivalent mechanism for a different one
risks regression for no measurable gain.

## Finding 3 — the real gap: cec2013 and cec2020 have NO serial layer

Confirmed absent in 02: neither `_kernel_mode.py` nor `_numba_serial.py` exists
for either suite. 05 has both for both.

This is the whole portable delta.

## Finding 4 — the fidelity class differs by suite, and it is decisive

02's own `cec2017/_numba_serial.py` carries a measured numerical contract
(94,240 rows, 19 kernels × dims {10,30,50,100} × K {1,3,8,50}):

* **cec2017: 93.20% bitwise identical, worst 13 ULP** (`katsuura_nb`, then egpr 9,
  esf6 7, schaffer_F7 6). Divergence tracks `fastmath` **and nothing else** — the
  one `fastmath=False` kernel is 100.00% bitwise. → **class (b)**, and
  independently reproduced here: F10 D30 differed by 1 ULP in 40 evaluations.
* **cec2013, cec2020, cec2013lsgo: 100.0000% bitwise, 0 ULP.** 05's
  `cec2013/_numba_serial.py` states the same, "bit-identical by construction".
  → **class (a)**.

**This is the key result of the audit.** The two suites 02 is missing twins for
are exactly the two whose twins are *bit-identical*. Porting them is therefore a
class (a) change that is safe on the default path — unlike cec2017's twins, which
must remain opt-in for a frozen project.

## Finding 5 — 02 cites a parity harness it does not contain

`cec2017/_numba_serial.py` attributes its contract to
`benchmarks/perf/cec2017_twin_parity.py`. **That directory does not exist in 02**,
and 05's `benchmarks/perf/` is empty. The numbers are quoted from a harness
neither project currently ships, so they cannot be re-derived on demand. Any
claim resting on them must either re-measure or be labelled as inherited.

## Plan that follows from this audit

1. Port `_kernel_mode.py` + `_numba_serial.py` for **cec2013** and **cec2020**
   only, following 02's existing lazy pattern rather than 05's eager one, keeping
   the suite-local thread-local flag rule ("a cec2017 scope can never route LSGO
   kernels").
2. Re-derive the parity contract instead of inheriting it: write the missing
   `benchmarks/perf/` harness and measure bitwise/ULP agreement for every suite
   that has twins, publishing the table.
3. Keep twins **opt-in and default-off everywhere**, including the class (a)
   suites — the frozen release was produced on the default path, and the cheapest
   way to keep that true is to never change what the default does.
4. Verify with the 42-pin golden matrix and the full gate sweep; measure any
   speed claim with a paired interleaved design, never sequential ledgers.

## Phase 2–4 result (2026-07-26): ported, verified, and it does NOT pay off

The two missing serial layers were built (`cec2013/` and `cec2020/`,
`_kernel_mode.py` + `_numba_serial.py`, following 02's lazy `__getattr__`
pattern) and wired into `make_problem(..., serial_kernels=True)`, default off.

**Fidelity — measured here, not inherited.** A replacement harness was written
(`benchmarks/perf/twin_parity.py`; the cited `cec2017_twin_parity.py` does not
exist in either project). Identical inputs to both kernels:

| Suite | Bitwise identical | Worst ULP | Class |
|---|---|---|---|
| cec2013 | 2,400/2,400 (100.0000%) | 0 | **(a) bit-identical** |
| cec2020 | 480/480 (100.0000%) | 0 | **(a) bit-identical** |
| cec2017 | 1,858/1,888 (98.4110%) | 5 (`egpr_nb`) | (b) float-reassociation |

The prediction from the fastmath rule held exactly, and cec2017 reproduced its
own documented divergent kernels (egpr, schaffer_F7, esf6, katsuura, happycat),
which validates the harness against a known result. End-to-end, problem-level:
**40/40 hex-identical for cec2013 and cec2020**.

*A harness bug worth recording:* the first version drew fresh randoms inside the
call helper, so the two kernels received **different inputs**. It reported ULP
distances near 9.2e18 — the entire float64 range — and pronounced both suites
class (b). Comparing two implementations requires giving them the same numbers;
an "impossibly large" disagreement is a harness defect until proven otherwise.

**Speed — the port does not help, and the first number was an artefact.** A naive
before/after showed "325×" for cec2013. That was JIT compilation, not evaluation.
Measured properly (warm, repeated, by batch size) on cec2013 F14 D=30:

| rows | default µs/eval | serial µs/eval | speedup |
|---|---|---|---|
| 1 | 75.1 | 67.8 | 1.11× |
| 2 | 46.1 | 47.8 | 0.97× |
| 8 | 51.5 | 57.3 | 0.90× |
| 25 | 61.1 | 59.5 | 1.03× |
| 100 | 70.9 | 72.6 | 0.98× |

At the family's population size (NP = 100) the twin is **0.98×** — no gain. The
launch-tax argument requires the kernel to be cheap relative to the ~60 µs
launch, which holds at D = 1000 with single-row local-search probes (the regime
project 05's guide targets) and does not hold for cec2013/cec2020 at D ≤ 50 with
full-population batches.

**Disposition.** The layers are kept: they are correct, bit-identical, default-off,
and cost nothing when unused; they will pay off for any future single-row consumer
(a local-search-heavy external baseline on these suites). But **no campaign should
enable them expecting a speedup**, and no claim of "50–170× faster" transfers from
project 05 to cec2013/cec2020 in this project's usage pattern.

## Addendum — the serial-kernel lever is dead in THIS project, at every batch size

The one regime where twins should have paid is single-row evaluation at
D = 1000: the LSGO externals (MOS's Solis-Wets and MTS-LS1-Reduced, SHADE-ILS's
MTS-LS1 and L-BFGS-B probes) evaluate one row at a time for half their budget,
and that is exactly what project 05's guide targets with its 50–170× claim.

Measured on cec2013lsgo D = 1000, warm, repeated:

| func | rows | default µs/eval | serial µs/eval | speedup |
|---|---|---|---|---|
| 1 | 1 | 61.8 | 60.4 | 1.02× |
| 4 | 1 | 129.8 | 140.5 | 0.92× |
| 8 | 1 | 147.9 | 154.7 | 0.96× |
| 1 | 100 | 629.3 | 576.8 | 1.09× |
| 8 | 100 | 1239.1 | 1158.5 | 1.07× |

**Single-row mean across F1/F4/F8: 0.95× — slower.** The launch tax the mechanism
exists to remove is not measurable here. The most likely reason is that 02's own
campaign already removed the cost the twins were meant to recover (CR-0009's
row-sum kernel gave 2.3–3× on this suite), so there is nothing left for them to
take.

Also relevant: `serial_kernels` is reachable only through
`make_problem(serial_kernels=True)` and is **not wired into the runner or the
CLI at all**. No campaign has ever used it, and on this evidence none should.
Wiring it would add a configuration surface with a measured negative return.

**Conclusion: the serial-kernel avenue is closed for this project on measurement,
not on opinion.** Project 05's 50–170× does not reproduce here at any batch size
or dimension tested.

## What this audit rules out

The premise that "all algorithms and all CEC suites in 05 are tuned and 02 is
behind" is **not supported**. On kernels the projects are equal; on optimizers 02
has its own completed campaign; the only genuine gap is two missing serial layers
whose expected benefit is confined to the single-row evaluation path. Expect a
narrow, well-scoped win — not a broad speedup.
