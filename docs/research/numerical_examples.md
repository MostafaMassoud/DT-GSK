# Numerical Examples

> **What this is:** small, hand-checkable walkthroughs of the mechanics shared
> across the GSK family. **For:** anyone who wants to verify the implementation
> by arithmetic. **Each optimizer's *distinctive* operator** has its own worked
> example in its guide (indexed at the [bottom](#per-optimizer-distinctive-examples));
> this page covers the steps every optimizer shares. All examples use tiny
> values so each line can be checked by hand, and cite the code that implements
> them.

## Population initialization

Each coordinate is a uniform draw scaled into the box `[lb, ub]`
(`common/population.py`, `gsk_init_population`):

```text
dimension = 2,  population size = 3,  lb = [-5, -5],  ub = [5, 5]
uniform draws U =
  [0.10, 0.70]
  [0.40, 0.50]
  [0.90, 0.20]

X = lb + U * (ub - lb)            # ub - lb = [10, 10]
  = [-4,  2]
    [-1,  0]
    [ 4, -3]
```

For the sphere function `f(x) = sum(x^2)`:

```text
f([-4, 2]) = 16 + 4  = 20
f([-1, 0]) =  1 + 0  =  1      <- best
f([ 4,-3]) = 16 + 9  = 25
```

## Unified seed and fair start

The `unified` policy derives one run seed from the run coordinates and gives
every optimizer in the same cell the *same* starting population
(`runners/seed_policy.py`, `get_cec_seed`):

```text
inputs:  base seed, dimension, function id, run id
         -> hashed run seed
         -> fair-start population (shared by all optimizers in the cell)
         -> captured post-initialization RNG state (each optimizer restores it)
```

The hash is a closed form, so the integer is hand-checkable:

```text
seed = mod(base_seed + 1000003*Dim + 1000033*Function + 1000037*Run,
           2147483646) + 1

base_seed = 20240620, Dim = 30, Function = 7, Run = 12
  20240620 + 1000003*30 + 1000033*7 + 1000037*12
  = 20240620 + 30000090 + 7000231 + 12000444
  = 69241385
mod 2147483646 = 69241385,  + 1  ->  seed = 69241386
```

This makes cross-optimizer comparisons fair: the optimizer id and suite are *not*
inputs, so every optimizer in the same `(Dim, Function, Run)` cell gets the
identical seed, and differences come from the algorithms rather than luckier
initial points. The [Seed Policy](../reference/seed_policy.md#unified-formula)
page works the same derivation; the
[reference policy](../reference/seed_policy.md#reference-policy) reproduces
published tables bit-for-bit. `dt-gsk` always uses this unified seed but
self-inits a `5*D` population from the same `threefry(seed)` stream (a documented
fair-start exception — see
[Seed Policy — DT-GSK Unified-Only Seeding](../reference/seed_policy.md)).

## Boundary handling (midpoint repair)

A gained coordinate that leaves the box is pulled to the midpoint between the
**parent** value and the breached bound — never reflected past the parent. The
same repair applies identically to the junior and senior gained coordinates
(`_kernels.py:132-135` and `140-143`; `common/bounds.py`):

```text
parent = [4, 1],  gained = [7, 1],  ub = [5, 5]
dim 0: 7 > 5  ->  (parent_0 + ub_0)/2 = (4 + 5)/2 = 4.5
dim 1: 1 in bounds -> unchanged
repaired = [4.5, 1]
```

## Fitness comparison (greedy selection)

Replacement is strictly greedy — a child must *beat* its parent
(`gsk.py:201-204`):

```text
parent fitness = 12,  child fitness = 8   ->  child replaces parent
parent fitness = 12,  child fitness = 14  ->  parent stays
```

## Best-so-far tracking

The convergence trace records the best objective seen at each checkpoint. It is
monotone non-increasing — it can repeat but never worsen:

```text
nfes:         20, 40, 60, 80
best fitness: 12,  8,  8,  5
```

## Summary statistics

CEC-style summaries report best/median/mean/worst and the **sample** standard
deviation (`np.std(..., ddof=1)`, divisor `n-1`) — see `stats.py:22-43`
(`sample_sd`, `summarize`). For three runs:

```text
errors = [1.0e-3, 5.0e-4, 2.0e-3]

best   = min    = 5.0000000e-4
median =          1.0000000e-3
mean   = sum/3  = 1.1666667e-3
worst  = max    = 2.0000000e-3
sd     = sqrt( ((1e-3-mean)^2 + (5e-4-mean)^2 + (2e-3-mean)^2) / (3-1) )
       = sqrt( 1.1666667e-6 / 2 ) = 7.6376262e-4      # sample SD (ddof=1)
```

Using the population divisor `n` instead would give `6.236e-4`; the project uses
the sample divisor `n-1`, matching the reference summaries.

## LPSR population schedule (adaptive variants)

AGSK and its descendants shrink the population as the budget burns
(`agsk.py:148-157`): with `max = np_init`, `min = min_pop_size`, and budget ratio
`t = nfes / max_nfes`,

```text
NP_target(t) = round( (min - max) * t^(1 - t) + max )      # round half away from zero
```

For `np_init = 100`, `min_pop_size = 12`, `max_nfes = 10000`:

| nfes | t | t^(1-t) | NP_target |
|---:|---:|---:|---:|
| 0 | 0.00 | 0.000 | 100 |
| 1000 | 0.10 | 0.126 | 89 |
| 2500 | 0.25 | 0.354 | 69 |
| 5000 | 0.50 | 0.707 | 38 |
| 7500 | 0.75 | 0.931 | 18 |
| 9000 | 0.90 | 0.990 | 13 |
| 10000 | 1.00 | 1.000 | 12 |

The curve is steepest mid-run (the exponent is `1 - t`, not `1`) and bottoms out
at `min_pop_size`. See [AGSK](../algorithms/agsk.md) for the full reduction step.

## Parallel determinism

The process backend may finish tasks out of order, but the runner restores
input order before writing, so artifacts are byte-identical to a serial run
(`runners/parallel.py`):

```text
serial task order:   run 1, run 2, run 3
parallel completion: run 2 may finish first
writer order:        run 1, run 2, run 3     # restored before any CSV is written
```

The run seed is a function of the run coordinates only, so it never depends on
the backend or the worker count.

## Pairwise win-tie-loss (Wilcoxon framing)

The statistical suite pairs the proposed algorithm against a comparator **by
function**, using each function's mean error, with the convention that a
*positive* difference `ref_mean - new_mean` means the proposed algorithm is
better (lower error). Sign each function, then tally
(`analysis/statistical_tests.py`, `wilcoxon_signed_rank`):

```text
function:    F1     F3     F4     F5
new  (mean): 1.0e0  2.0e1  5.0e0  3.0e0     # proposed
ref  (mean): 4.0e0  1.0e1  5.0e0  9.0e0     # comparator
diff=ref-new:+3.0e0 -1.0e1  0      +6.0e0
sign:          +      -      =       +       # +=win, -=loss, ==tie
```

This cell gives win/tie/loss = 2/1/1 for the proposed algorithm. Differences
inside a scale-aware tie band (absolute floor plus a relative `1e-10 * max|.|`
term) are counted as ties, so sub-noise gaps on large-magnitude functions do not
masquerade as wins. The signed-rank `R+`/`R-`, two-sided p-value, and the
standardized effect size `r = Z / sqrt(n)` are computed over these paired
differences. See [Statistical Analysis](statistical_analysis.md) for the full
panel (Friedman ranks, Nemenyi CD, Holm correction, A12/Cliff's delta).

## Friedman average rank (by hand)

Friedman ranks the algorithms *within each function* (rank 1 = best/lowest
error), then averages each algorithm's ranks across functions; a lower average
rank is better (`analysis/statistical_tests.py`, `friedman_rank_test`). For three
algorithms on three functions:

```text
            F1     F3     F4        per-function ranks (1=best)
alg A:    1.0e0  5.0e0  2.0e0   ->   1, 2, 1
alg B:    3.0e0  4.0e0  8.0e0   ->   2, 1, 3
alg C:    9.0e0  6.0e0  4.0e0   ->   3, 3, 2

mean rank A = (1+2+1)/3 = 1.333    <- best
mean rank B = (2+1+3)/3 = 2.000
mean rank C = (3+3+2)/3 = 2.667
```

The Friedman chi-squared statistic tests whether these mean ranks differ more
than chance; the Nemenyi critical difference then says which gaps are
significant. For CEC2017 the panel ranks all seven GSK-family algorithms over the
scored functions (F2 excluded).

## Per-optimizer distinctive examples

Each guide carries a hand-checkable example of the operator that sets that
optimizer apart:

| Optimizer | Distinctive operator | Worked example |
|---|---|---|
| GSK | junior/senior gaining-sharing + dimension schedule | [gsk.md](../algorithms/gsk.md#worked-example) |
| AGSK | adaptive `(kf, kr)` pools + LPSR | [agsk.md](../algorithms/agsk.md#worked-example) |
| APGSK | negative-`KF` gate + stochastic junior schedule | [apgsk.md](../algorithms/apgsk.md#worked-example) |
| FDB-AGSK | fitness-distance-balance donor selection | [fdb-agsk.md](../algorithms/fdb-agsk.md#worked-example) |
| ATMALS-GSK | memory-roulette pools + local search | [atmals-gsk.md](../algorithms/atmals-gsk.md#worked-example) |
| DT-GSK | NLPSR nonlinear population reduction (`5·D` → tier floor) | [dt-gsk.md](../algorithms/dt-gsk.md#worked-example) |
