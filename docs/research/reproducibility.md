# Reproducibility

> **What this page is.** The rules and procedure for making a run repeatable —
> same config, same seeds, same artifacts — and an honest statement of what is
> and is not bit-exact against the upstream source.
>
> **Who it is for.** Anyone who needs a run to come out the same way twice, or
> who is preparing evidence for a paper or release.
>
> **What you will get.** How to record the environment, how seeds work, the
> settings that pin determinism, a step-by-step experiment procedure, and the
> precise bit-exact caveats.
>
> **Prerequisites.** Workflow context is in the
> [Researcher Handbook](researcher_handbook.md); seed formulas are in
> [Seed Policy](../reference/seed_policy.md). Terms are defined in
> [the glossary](../reference/glossary.md).

This project treats reproducibility as a first-class project deliverable.

## Environment

Record exactly what software produced a result, so it can be recreated later.

Install the package in editable mode:

```powershell
python -m pip install -e ".[dev]"
```

Record the interpreter and package versions for published runs:

```powershell
python --version
python -m pip freeze
```

Each `gsk-run` execution writes an `environment.json` artifact below the run
directory with config, package, platform, and budget metadata. Keep this file —
together with the campaign YAML it is the core provenance for the run.

The artifact includes an `fp_regime` block with a floating-point regime
sentinel (a SHA-256 fingerprint of fixed kernel-probe outputs). The runner
refuses to start any process whose numba JIT kernels are unavailable or whose
sentinel disagrees with the parent's, so every campaign is single-regime by
construction. When pairing runs **across** campaigns at run level (paired
Wilcoxon, seed-matched deltas), the operational rule is: **run the paired arms
sequentially on the same machine+build, and before trusting any cross-campaign
delta verify that both campaigns record matching FP sentinels *and* that the
should-be-identical guard cells differ by zero.** Different sentinels — or any
nonzero guard-cell diff — mean the runs are not bit-comparable even though each
campaign is internally deterministic. See
[Floating-Point Regime Verification](../reference/fp_regime.md) for the
canonical description of the sentinel and the guard-cell validity check.

## Reference data (single source of truth)

All paper data and statistics — the proposed `dt-gsk` included — are read from
the committed reference panel under
`benchmarks/cec_reference_results/<suite>/<optimizer>/`. Each optimizer
directory is a flat, self-contained run record: `<opt>_<suite>_D<dim>.csv`
summaries (plus a `<opt>_cec2011.csv` rollup for CEC2011), `per_run.csv`, the
provenance set (`environment.json`, `run_config.json`, `seed_schedule.csv`,
`verification.json`, `phase0_protocol.json`), and the `curves/` and `gen_logs/`
convergence assets. The full 7-optimizer panel is committed for **CEC2017**,
**CEC2011**, and **CEC2013** (the second comparison suite: 28 functions,
D = 10/30/50, 51 runs); `cec2020` (agsk only) and `cec2013lsgo` (`decc-g`,
`mos`) are partial context suites.

The analysis layer loads this tree **first** and treats a locally reproduced
run under `results/_run_all/` only as a fallback for cells the reference tree
does not carry (`analysis/result_loader.py::load_algorithm`,
`analysis/family_report.py`). The convergence-figure generators
(`papers/scripts/generate_full_convergence.py`,
`generate_cec2011_convergence.py`, `generate_cec2013_convergence.py`) likewise
read `curves/` and `gen_logs/` from the reference tree. One resolution caveat:
`per_run.csv` is complete for `dt-gsk` on every panel suite and dimension,
while some comparators carry only partial per-run coverage — their
per-dimension summary CSVs are the complete comparator source, so seed-matched
per-run analyses are guaranteed only for the proposed method (see
[Statistical Analysis — Data sources](statistical_analysis.md#data-sources)).

## Seeds

Seeds decide the random draws, so fixing them is what makes a run repeatable.

The default campaign policy is `unified`. It derives a stable seed from
`(base, dimension, function, run)` only — it is **optimizer- and
suite-independent**, so the same seed (and the same fair-start population) is
shared across optimizers for matching `(dimension, function, run)` cells. That
independence is exactly what makes the cross-optimizer starts fair. (See
[Fair start](../reference/glossary.md) for what "shared start" means.)

The two campaign-facing policies serve different goals:

| Seed policy | Use it to | Result |
|---|---|---|
| `unified` (default) | Compare optimizers fairly. | Matching cells share a fair-start population and post-init RNG state. |
| `reference` | Reproduce published reference tables. | Per-optimizer seeding that reproduces the published CEC tables. |

Two further diagnostic variants exist — `native` and `derived` — which route to
`derive_run_seed`; see [Seed Policy](../reference/seed_policy.md).

The unified seed for one cell is a closed-form function of the cell coordinates
(`get_cec_seed` in `src/gsk_family/runners/seed_policy.py`):

```text
seed = mod(base_seed + 1000003*Dim + 1000033*Function + 1000037*Run,
           2147483646) + 1
```

Worked example (matching [Seed Policy](../reference/seed_policy.md#unified-formula)):

```text
base_seed = 20240620, Dim = 30, Function = 7, Run = 12
20240620 + 1000003*30 + 1000033*7 + 1000037*12
  = 20240620 + 30000090 + 7000231 + 12000444
  = 69241385
mod 2147483646 = 69241385,  + 1  ->  seed = 69241386
```

The default `base_seed` is `20240620` (`DEFAULT_BASE_SEED`) and the modulus is
`2147483646` (`MAX_SAFE_SEED`). Because the optimizer id and suite are not inputs
to this formula, every optimizer in a matching `(Dim, Function, Run)` cell gets
the identical seed under the unified policy.

The seed helpers live in:

```text
src/gsk_family/runners/seed_policy.py
src/gsk_family/common/rng.py
```

See [Seed Policy](../reference/seed_policy.md) for the exact formulas and the
generator mapping, and
[Numerical Examples — Unified seed and fair start](numerical_examples.md#unified-seed-and-fair-start)
for a worked seed derivation.

### The threefry determinism story

A fixed seed only guarantees repeatability if the random *stream* derived from it
is itself deterministic and portable. Under the unified policy the family uses a
bundled counter-based **Threefry-4x64-20** generator
(`src/gsk_family/common/threefry_rng.py`, class `ThreefryGenerator`) selected by
the `threefry` label. It reproduces the source project's `rng(seed, 'threefry')`
double stream bit-for-bit, so the same seed yields the same draws across runs and
machines independent of NumPy's own `default_rng` versioning. `RandomContext`
(`src/gsk_family/common/rng.py`) wraps the generator and exposes `copy_state` /
`restore_state`, which is how the runner captures and replays the
post-initialization RNG state for a fair start.

`dt-gsk` always selects `threefry` regardless of the configured generator (it is
in `UNIFIED_ONLY_OPTIMIZERS`), and self-inits its `5*D` (`np_init_mult * D`,
`np_init_mult = 5`) population from that same `threefry(seed)` stream — keeping it
on identical seed/stream footing with the rest of the family while remaining a
documented fair-start exception.

Internally, `dt-gsk` does not draw every subsystem from one shared cursor.
`RNGStreams.from_seed` (`src/gsk_family/optimizers/_dt_rng.py`) fans the single
scheduled run seed out into **13 named, independent substreams** — `init`,
`core`, `ace`, `kexp`, `div`, `bse`, `arch`, `link`, `de`, `control`, `flow`,
`basin`, `trust` — each assigned a deterministic child seed **by position**. This
isolation means a subsystem that fires (or doesn't) in one generation cannot
shift the draws consumed by another, which is what keeps the trajectory
reproducible as the optimizer's high-dimensional controllers switch on and off.
The order is an append-only contract: the first nine names are prefix-locked
(`SUBSTREAM_NAMES` guards this with an assertion), and new substreams may only be
appended at the end so existing child-seed assignments never move.

## Deterministic Settings

Pin every source of variation explicitly rather than relying on a default that
could change.

| Setting | Recommended value | Why |
|---|---|---|
| `seed` | a fixed integer (default base `20240620`) | fixes every random draw |
| `seed_policy` | `unified` (fair) or `reference` (reproduce tables) | selects the seed schedule |
| `rand_generator` | `threefry` | portable, bit-stable family stream |
| `max_evaluations` | explicit value | makes reduced runs comparable |
| `overwrite` | `true` only when regenerating evidence | avoids silent stale results |

- Keep generated output outside `benchmarks/cec_reference_results/` so generated
  runs never overwrite committed reference tables. (Deliberately regenerating
  the reference panel is a separate, documented promotion step — see the
  root `runbook.md` single-source-of-truth and doubled-suite-trap notes.)
- Parallelism does not change the numbers: run seeds are derived from cell
  coordinates *before* dispatch and results are reordered to input order before
  writing, so process, thread, and `--serial` runs yield byte-identical numeric
  artifacts (see [Parallel determinism](numerical_examples.md#parallel-determinism)).
- Avoid the `thread` backend for timing-sensitive or kernel-heavy runs — it is
  numerically identical but can deadlock with `parallel=True` Numba kernels (see
  [Performance](performance.md#parallel-execution)).

## Experiment Procedure

Run the pipeline in confidence-building order: prove the code works, prove a
small run works, then commit to the full campaign, then validate and archive.

1. **Install dependencies.**

   ```powershell
   python -m pip install -e ".[dev]"
   ```

2. **Run `python -m pytest`** to confirm the suite passes before you generate
   evidence.

   ```powershell
   python -m pytest -q
   ```

3. **Run a smoke configuration** (a reduced budget that exercises the whole
   pipeline quickly).

   ```powershell
   gsk-run --config configs/smoke.yml --root .
   ```

4. **Run the intended campaign configuration** at the real budget and run count.

   ```powershell
   gsk-run --config configs/all_cec2017.yml --root .
   ```

5. **Validate generated summaries against imported reference tables** when
   applicable.

   ```powershell
   gsk-validate --compare results/_run_all/gsk/cec2017 benchmarks/cec_reference_results
   ```

6. **Archive** the YAML config, `environment.json`, `per_run.csv`, summary CSVs,
   convergence logs (`gen_logs/`), and `verification.json`.

To check that repeated runs land identically, run the same campaign twice (or
once normally and once with `--serial`) and byte-compare the deterministic
numeric artifacts:

```powershell
gsk-run --config configs/smoke.yml --root . --overwrite
# move/copy the run aside, then:
gsk-run --config configs/smoke.yml --root . --serial --overwrite
# compare per_run.csv / summary CSVs byte-for-byte
```

See [Numerical Examples](numerical_examples.md#parallel-determinism) for a worked
illustration of why parallel and serial runs produce identical artifacts.

## Bit-Exact Caveats

This is the honest scope of the port. Read it before claiming equivalence to the
upstream source.

Python and the reference source do not share identical floating-point library
paths or random generator implementations. The port preserves algorithm
structure, evaluation budgets, bounds, seed policy, and output schema. It does
not claim universal bit-exact replay of reference outputs.

What **is** locked bit-for-bit:

- **Within this project**, repeated runs of the same config are byte-identical,
  and process / thread / `--serial` runs agree (the determinism above).
- The **threefry double stream** matches the source project's
  `rng(seed, 'threefry')` generator bit-for-bit (see
  [The threefry determinism story](#the-threefry-determinism-story)).
- **`dt-gsk` parity with its source DT-GSK v2.1 project** is pinned by a golden
  regression, `tests/regression/test_dt_gsk_byte_stable.py`, which asserts exact
  `best_fitness` values on sphere and CEC2017 cells (validated byte-identical at
  `seed=12345`, `max_nfes=3000`).

What is **not** claimed: bit-exact reproduction of every upstream CEC reference
table across all suites, because the underlying floating-point math libraries
differ between the Python and reference toolchains. Treat a reduced-budget
`gsk-validate --compare` as a schema and consistency check, not a final
equivalence claim.
