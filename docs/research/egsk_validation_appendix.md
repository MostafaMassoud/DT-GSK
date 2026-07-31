# EGSK Validation Appendix — Paired Port-vs-Reference Equivalence

> **What this page is.** The validation record for the Python EGSK optimizer
> (`src/gsk_family/optimizers/egsk.py`) against the imported MATLAB EGSK
> reference. It documents *why* a true paired per-run test is possible, the
> method, the reproducible command, and the measured agreement.
>
> **Who it is for.** Reviewers who need to know how far the EGSK port is
> verified before trusting either its runnable kernel or the published EGSK
> comparator numbers.
>
> **Related.** [Validation Report](validation_report.md) ·
> [EGSK algorithm](../algorithms/egsk.md) ·
> [Reproducibility](reproducibility.md) · [glossary](../reference/glossary.md).

## 1. Why EGSK is validated *statistically*, not byte-for-byte

The published EGSK reference always runs MATLAB `fmincon` (SQP) for its
interior-point refinement (`egsk_optimize.m:21`). `fmincon` has no
byte-identical Python equivalent, so the port substitutes
`scipy.optimize.minimize(method="SLSQP")`. Every other part of EGSK — the
dual-knowledge-factor schedule, the fixed 10/90 senior partition, the
gaining–sharing trial kernel, the bound handling, and the Threefry RNG/seed
layer — is a faithful port that draws the RNG in the reference's exact order.
Byte-identity is therefore **infeasible by construction**; equivalence is the
correct bar.

## 2. Why a *paired per-run* test is possible (and strong)

Most imported reference tables store only per-function summaries, which forces
the suite-level summary test in
[`scripts/wilcoxon_reference.py`](../../scripts/wilcoxon_reference.py). EGSK is
different: its reference ships **per-run checkpoint logs**

```
benchmarks/cec_reference_results/cec2017/egsk/gen_logs/CheckpointErrors_egsk_F<f>_D<d>.csv
```

with a `Run, Seed, E1000, …, E<budget>` schema — one row per run, including the
**seed** and the final-budget error. Those seeds are exactly this project's
unified Threefry schedule: for F5/D10 run 1 the reference seed is `36240853`,
and `get_cec_seed(20240620, dim=10, func=5, run=1) = 36240853`.

Because the seed is shared, the **entire GSK population trajectory is
byte-faithful** between the port and the reference; the *only* place they can
diverge is the interior-point polish (SLSQP vs `fmincon`). Running the Python
EGSK at each reference seed and pairing the final errors is thus a genuine
**paired** comparison that isolates exactly the one intended deviation — far
tighter than a mean-vs-mean check.

## 3. Method

For each `(function, dimension)` cell, `scripts/validate_egsk_vs_reference.py`:

1. reads the reference `CheckpointErrors` CSV → `(run, seed, final_error)` rows;
2. runs the Python EGSK at the **same seed** and `10000·D` budget → final error;
3. pairs the two final-error vectors and reports:
   - Python vs reference **mean** and **median** error,
   - **max |Δ|** — the largest absolute paired difference,
   - **exact** — runs matching to `|Δ| ≤ 1e-12`,
   - **paired Wilcoxon** two-sided *p* (small *p* ⇒ a systematic SLSQP-vs-`fmincon`
     shift; large *p* ⇒ statistical equivalence).

## 4. Reproduce

Bounded representative validation (10 functions spanning every CEC2017 category
× D=10/30/50 × 15 paired runs):

```bash
python scripts/validate_egsk_vs_reference.py \
    --dims 10,30,50 --funcs 1,3,5,7,9,11,15,21,27,30 --runs 15 \
    --out egsk_validation.json
```

Full appendix sweep (all CEC2017 scored functions, all dims, all 51 reference
runs — compute-heavy):

```bash
python scripts/validate_egsk_vs_reference.py \
    --dims 10,30,50,100 \
    --funcs 1,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 \
    --runs 51 --out egsk_validation_cec2017_full.json
```

(CEC2011 uses native per-function dimensions and a 150000-NFE budget; point the
same script at `--suite cec2011` once its per-run checkpoint logs are present.)

## 5. Results — bounded representative validation

CEC2017, D=10 and D=30, ten functions spanning every category (unimodal 1/3;
simple multimodal 5/7/9; multimodal 11; hybrid 15/21; composition 27/30), 15
paired runs per cell (300 paired runs), error vs optimum. Produced by the
bounded command in §4 (cell-parallel, one single-threaded worker per cell).
`max |Δ|` is the largest absolute paired final-error difference; `exact` counts
runs matching to `|Δ| ≤ 1e-12`; `Wilcoxon p` is the two-sided paired signed-rank
p-value.

> **Provenance of this table.** The `egsk/gen_logs/CheckpointErrors_*` files now
> committed under `benchmarks/cec_reference_results/cec2017/egsk/` are the
> promoted **Python (`scipy`-SLSQP) port** run that serves as EGSK's comparator
> of record (§7) — a *generated* run (`environment.json` `optimizer: egsk`,
> `verification.json` verdict `CONSISTENT`) whose 51-run means equal the committed
> summary CSVs (F5/D10 = `4.816`, the SLSQP value, not the `fmincon` `4.994`). The
> **seeds** in those logs are the genuine unified Threefry schedule (F5/D10 run 1
> = `36240853`), which is what makes a paired test possible at all. The figures in
> the table below are the **recorded** output of the paired validation whose `Ref`
> column is the original MATLAB `fmincon` per-run reference; that `fmincon`
> reference is external to the committed evidence tree. Treat this table as an
> archived measurement — re-running the §4 command against *today's* committed
> tree pairs the port against its own promoted SLSQP logs, not against `fmincon`.

| F | D | n | Py mean | Ref mean | Py median | Ref median | max \|Δ\| | exact | Wilcoxon p |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 10 | 15 | 0 | 0 | 0 | 0 | 0 | 15/15 | 1.000 |
| 3 | 10 | 15 | 0 | 0 | 0 | 0 | 0 | 15/15 | 1.000 |
| 5 | 10 | 15 | 4.643 | 4.842 | 3.98 | 4.975 | 1.99 | 5/15 | 0.330 |
| 7 | 10 | 15 | 14.86 | 15.25 | 14.82 | 15.5 | 4.814 | 0/15 | 0.005 |
| 9 | 10 | 15 | 0 | 0 | 0 | 0 | 0 | 15/15 | 1.000 |
| 11 | 10 | 15 | 0 | 9.09e-13 | 0 | 2.27e-13 | 5.68e-12 | 12/15 | 1.000 |
| 15 | 10 | 15 | 0.3074 | 0.3082 | 0.4797 | 0.4918 | 0.01205 | 0/15 | 0.847 |
| 21 | 10 | 15 | 163.7 | 163.5 | 204.7 | 204.7 | 3.182 | 3/15 | 0.064 |
| 27 | 10 | 15 | 389.5 | 389.5 | 389.5 | 389.5 | 5.68e-14 | 15/15 | 1.000 |
| 30 | 10 | 15 | 446.2 | 444.0 | 442.7 | 442.7 | 48.14 | 0/15 | 0.679 |
| 1 | 30 | 15 | 0 | 6.35e-08 | 0 | 7.11e-14 | 9.44e-07 | 11/15 | 0.001 |
| 3 | 30 | 15 | 0 | 3.72e-10 | 0 | 3.87e-11 | 3.44e-09 | 2/15 | 1.000 |
| 5 | 30 | 15 | 19.97 | 19.77 | 19.90 | 19.90 | 1.99 | 1/15 | 0.890 |
| 7 | 30 | 15 | 50.06 | 50.30 | 46.76 | 47.38 | 4.906 | 0/15 | 0.064 |
| 9 | 30 | 15 | 0 | 1.21e-13 | 0 | 1.14e-13 | 2.27e-13 | 15/15 | 1.000 |
| 11 | 30 | 15 | 8.909 | 8.909 | 4.975 | 4.975 | 5.70e-07 | 0/15 | 0.004 |
| 15 | 30 | 15 | 5.369 | 5.696 | 5.20 | 5.232 | 4.061 | 0/15 | 0.000 |
| 21 | 30 | 15 | 219.3 | 219.3 | 218.2 | 218.2 | 1.02e-07 | 0/15 | 0.001 |
| 27 | 30 | 15 | 495.2 | 495.2 | 493.7 | 493.7 | 9.68e-04 | 3/15 | 0.121 |
| 30 | 30 | 15 | 2141 | 2140 | 2118 | 2116 | 2.114 | 0/15 | 0.000 |

**Aggregate:** 14/20 cells show no detectable difference (paired p ≥ 0.05); 5/20
match exactly on every run.

## 6. Interpretation (honest)

The port tracks the `fmincon` reference closely across all 20 cells, but the two
interior-point solvers are not identical, so a paired test — which is sensitive
to tiny *consistent* offsets — flags six cells. Reading them by magnitude and
direction, none is a behavioural regression:

- **Negligible-magnitude flags (equivalent in practice).** On F1/D30, F11/D30,
  and F21/D30 the means are equal to ~4 significant figures and the largest
  paired difference is `≤ 1e-6` — SLSQP simply lands on a marginally different
  stationary point with the *same* objective to ~7 digits. F1/D30 in particular
  is flagged only because the port reaches exact `0` while `fmincon` leaves a
  `~1e-8` residual (i.e. the port is **better**).
- **Small flags in the port's favour.** On the genuinely polish-sensitive cells
  F7/D10 (14.86 vs 15.25) and F15/D30 (5.369 vs 5.696) the port's mean is
  **lower (better)** than the reference — the SLSQP endgame is at least as good
  as `fmincon` here.
- **One tiny flag against the port.** Only F30/D30 has the port marginally worse
  (2141 vs 2140, a `~0.05%` gap; median 2118 vs 2116).

The unflagged cells are equivalent (large p) or exact (`0` vs `0` to machine
precision, e.g. F27/D10, F9/D10, F9/D30). **The port is never materially worse
than the reference; the residual differences are the expected SLSQP-vs-`fmincon`
endgame, not a divergence in the GSK search** (which is byte-faithful at the
shared seed). This statistical faithfulness is why the reproducible SLSQP port
can stand as EGSK's comparator of record in the published panel (§7); the
port-vs-`fmincon` residual moves only a handful of cells by these sub-percent,
mostly-favourable amounts.

## 7. Comparator-data decision (for the published panel)

The published statistical panel uses the committed **Python (`scipy`-SLSQP) port**
run as EGSK's **comparator of record**: the `egsk` summary CSVs under
`benchmarks/cec_reference_results/<suite>/egsk/` (e.g. CEC2017 F5 D10 mean 4.816,
the SLSQP value, not the `fmincon` 4.994). The validation above establishes that
the port is statistically faithful to the published `fmincon` algorithm, so the
reproducible port stands as the comparator of record; the panel reads these
committed CSVs rather than a fresh live run so the numbers are fixed. (This
supersedes an earlier decision, 2026-07-03, that had kept the `fmincon` reference
CSVs as the comparator of record.) The current state is recorded in
[`PROJECT_RULES.md`](../../PROJECT_RULES.md) §6, `BENCHMARK_RULES.md`, and
[`docs/LICENSES.md`](../LICENSES.md).
