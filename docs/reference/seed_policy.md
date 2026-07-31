# Seed Policy

> **What this page is.** The exact deterministic seed formulas, the four seed
> policies, and how a fair start is shared across optimizers.
> **Who it is for.** Anyone reproducing results or auditing determinism.
> **Prerequisites.** [Reproducibility](../research/reproducibility.md) for the
> surrounding procedure; a worked derivation is in
> [Numerical Examples](../research/numerical_examples.md).

The runner supports four deterministic seed policies:

- `unified`: optimizer-independent seeds for fair cross-optimizer comparisons.
- `reference`: optimizer-family reference formulas.
- `native`: derived diagnostic seed.
- `derived`: same derived diagnostic seed path as `native`.

## Unified Formula

```text
seed = mod(base_seed + 1000003*Dim + 1000033*Function + 1000037*Run, 2147483646) + 1
```

Example:

```text
base_seed = 20240620, D = 30, F = 7, run = 12
seed = 69241386
```

In unified mode the runner also creates a fair-start initial population and
passes the captured post-initialization RNG state into each optimizer. The single
function that implements this formula is
`gsk_family.runners.seed_policy.get_cec_seed(base_seed, dim, func, run)`.

This means two optimizers in the same `(dimension, function, run)` cell receive
the same seed and the same initial population. Optimizers that are not ported
yet still receive the same seed schedule in their output directory when the
runner skips them.

This shared-seed footing is also what makes the downstream statistical
comparison fair: the `gsk-stats` family report (see
[research/statistical_analysis.md](../research/statistical_analysis.md)) ranks
the proposed optimizer against comparators that were all started from the same
unified seed schedule, so rank differences reflect the algorithms rather than
divergent initial conditions.

## Reference Policy

Baseline GSK-family linear variants use:

```text
seed = base_seed + 9973*Function + (Run - 1)
```

Adaptive/product-family variants use:

```text
seed = Dim * Function * Run
```

## DT-GSK Unified-Only Seeding

`dt-gsk` is in `seed_policy.UNIFIED_ONLY_OPTIMIZERS`: under **every** seed
policy it always uses the unified shared seed (`get_cec_seed`, the
[unified formula](#unified-formula) above) together with the `threefry`
generator — its default, with `twister` honored only when explicitly requested
(`effective_rand_generator`). This puts it on exactly the same shared seed and
generator footing as the rest of the GSK family under the unified policy,
regardless of the policy configured for the campaign.

DT-GSK also self-inits its own `5*D` initial population (`np_init_mult = 5` in
`DTGSKConfig`) from that same unified `threefry(seed)` stream (its `init`
substream equals `threefry(seed)`). It intentionally ignores the runner's
fair-start population — a documented fair-start exception intrinsic to the
algorithm — yet because it draws from the identical shared seed/stream it remains
directly comparable to the rest of the family.

### DT-GSK substream layer

The one scheduled run seed is not consumed as a single stream. DT-GSK derives a
fixed set of **13 named, independent substreams**
(`optimizers/_dt_rng.py`, `RNGStreams.from_seed`) so toggling any subsystem
cannot perturb another subsystem's draws. In declaration order
(`SUBSTREAM_NAMES`, load-bearing because each child seed is assigned by
position):

```text
init, core, ace, kexp, div, bse, arch, link, de, control, flow, basin, trust
```

The child seed for substream index `i` (`_child_seed`) is:

```text
i == 0 (init):  child = run_seed                                   (verbatim)
i  > 0:         child = (run_seed + 1_000_003 * (i + 1)) mod 2_147_483_646 + 1
```

so **stream 0 (`init`) is the run seed verbatim** — which is exactly why the
initial-population draw equals `threefry(run_seed)` and stays comparable to the
family fair start. The first nine names are prefix-locked; new substreams may
only be appended at the end (append-only contract).

Worked derivation for the `agsk`/`gsk`/`dt-gsk` shared cell F1, D10, run 1
(`run_seed = 32240721`, from the [unified formula](#unified-formula)):

```text
init  (i=0): 32240721                                        (verbatim)
core  (i=1): (32240721 + 1_000_003 * 2) mod 2_147_483_646 + 1 = 34240728
ace   (i=2): (32240721 + 1_000_003 * 3) mod 2_147_483_646 + 1 = 35240731
```

Every substream draws from a `threefry` generator seeded with its child seed,
reproducing the source DT-GSK trajectory bit-for-bit.

## RNG Labels

The Python runtime records the requested generator label and resolves each to a
generator that matches the MATLAB family it names:

- `threefry` -> a bundled counter-based Threefry-4x64-20 generator reproducing
  `rng(seed, 'threefry')` bit-for-bit (the default).
- `twister` -> MT19937 seeded with the reference `init_genrand(seed)` recurrence
  and emitting doubles via `genrand_res53` (two 32-bit words per double), matching
  `rng(seed, 'twister')`.
- `seed` -> the legacy v4 multiplicative congruential generator mcg16807
  (Park-Miller, `x <- 16807 * x mod (2^31 - 1)`, seeded
  `x0 = (seed << 16) mod (2^31 - 2^15)`), matching
  `RandStream('mcg16807', 'Seed', seed)`.

These three are the only supported generators; any other label is rejected. The
v5 `state` generator (swb2712) is intentionally not bundled -- it combines a
subtract-with-borrow generator (lags 27/12) with a second 53-bit generator whose
state is not recoverable from MATLAB's floating-point introspection, so it cannot
be reproduced bit-for-bit. All three generators fill matrices column-major to
match `rand(m, n)` and share the `floor(imax*rand)+1` / `sort(rand(n))` rules for
`randi` / `randperm`.

The MATLAB threefry seeding was reverse-engineered from the `RandStream` state:
key `(0, 0, 0, 0)` and a counter derived from the integer seed `S` as
`counter[j] = bitshift(S + 2*j + 1, 32) + (S + 2*j)` for `j = 0..3`. Each 4-output
block yields four doubles via `(word >> 11) * 2^-53`, the low counter word advances
by one per block, and matrix draws fill column-major to match `rand(m, n)`. This
makes the `rand` stream identical to MATLAB, so the `rand`-only optimizers (GSK,
AGSK, APGSK) reproduce the imported reference convergence to machine precision.

The effective generator is written to `summary/environment.json` so result
folders remain self-describing.

## MATLAB Seed-Compatibility Exception

This is the only active documentation section that intentionally keeps the
MATLAB term. The Python runner imitates the original seed labels and seed
formulas so experiments configured with the same base seed, dimension, function,
and run index can use the same intended seed schedule in Python. This supports
fair comparison, reproducible reruns, and traceable validation against imported
reference summaries.

The exception is seed-policy specific. It does not mean the project requires
MATLAB at runtime, writes output into external reference folders, or promises
byte-identical random streams for every generator implementation. The contract
is:

- preserve the documented seed formulas;
- preserve accepted generator labels for readable metadata;
- map those labels to deterministic NumPy generators;
- record both requested and effective generator metadata in results;
- use fair-start initial populations when the unified policy is selected;
- compare results under the same configured seed schedule whenever validation
  evidence is available.

When exact stream identity is required, document the generator, seed, suite,
dimension, function, run index, Python dependency versions, and output metadata
beside the experiment results.

## Stream Reproduction Status

With `rand_generator: threefry` the full random stream is now byte-identical to
the MATLAB reference: `rand` (column-major), `randi` (`floor(imax*rand)+1`), and
`randperm` (the `sort(rand(1,n))` method) all match reference draws bit-for-bit
(see the RNG Labels section). Validated against the imported `cec2017` `gen_logs`
checkpoints:

- **Bit-parity (machine precision):** GSK, AGSK, APGSK, ATMALS-GSK reproduce the
  reference convergence to ~1e-13 relative across functions and dimensions.
- **Residual difference (benchmark arithmetic):** the remaining gap is the
  irreducible floating-point difference between the numba benchmark kernels and
  the reference MEX (relative ~1e-14), which can flip a selection tie in the deep
  tail of an already-solved function.
- **Documented exception:** FDB-AGSK is more sensitive to the
  benchmark-arithmetic residual than the others: its donor selection ranks
  fitness-distance-balance scores (built from floating-point distances), so a
  ~1e-14 score difference can pick a different donor and amplify over
  generations. This is the same floating-point sensitivity, not an RNG
  difference -- `randi` and `randperm` are stream-exact.

## CLI Examples

YAML config:

```yaml
seed: 20240620
seed_policy: unified
rand_generator: threefry
```

Direct command:

```powershell
gsk-run --optimizer gsk --suite sphere --dimension 4 --function 1 --runs 2 --seed 20240620 --seed-policy unified --rand-generator threefry --max-evaluations 80 --overwrite
```
