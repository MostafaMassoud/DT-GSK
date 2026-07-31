# DECC-G port — fidelity and validation record

**Status: implemented, paper-faithful, NOT oracle-validated.** Read this before any
DECC-G number goes into the manuscript.

## What it is

`src/gsk_family/optimizers/external/decc_g.py`, registered as `decc-g`. Written
here against Yang, Tang & Yao (2008), *Large scale evolutionary optimization using
cooperative coevolution*, Inf. Sci. 178(15) 2985–2999, doi
`10.1016/j.ins.2008.02.017` (`reference_papers/yang2008large.pdf`).

**It is not a vendored oracle.** MOS and SHADE-ILS were vendored byte-faithfully
from project 05, where they carry line-mapped parity verdicts against author code
(SHADE-ILS is user-signed FROZEN, 14/15 within 2× of its published table). DECC-G
has no such backing: it rests on this implementer's reading of the paper. The
supplement must say so if DECC-G appears in the panel.

## Defects found and fixed during bring-up

Five, in order of discovery. The first was in the third-party reference code; the
rest were mine.

1. **Weighting outside the loop** (third-party code). The consulted implementation
   (github `decc`, Moésio Filho, MIT) applies adaptive weighting *once* after the
   main loop terminates. Paper Section 3, step 5 applies it at the end of **every
   cycle**. Weighting is what distinguishes DECC-G from plain DECC, so this is not
   cosmetic. That code was therefore consulted, not used.
2. **Context-vector fitness mismatch.** SaNSDE was seeded with each individual's
   full-vector fitness while its trials were evaluated through the context vector —
   incommensurable quantities, making the greedy test meaningless and corrupting the
   fitness array. Symptom: the best value was *bit-identical* at 5k, 12k and 30k
   budgets. Fixed by re-evaluating the sub-population baseline in context.
3. **Initial-population budget overspend.** `BudgetEvaluator` deliberately does not
   auto-truncate; the initial evaluation ignored `remaining()`, so a cap below `np`
   overspent (cap 50 consumed 100). Fixed; verified exact at caps 1/37/50/99/100/5k/30k.
4. **Wrong mutation structure.** Used two *different* strategies (rand/1 and
   current-to-best/1) selected by an adapting probability — that is SaDE's design.
   Paper Eq. (7) gives NSDE: **one** structure, DE/rand/1 with base `x_r1` and
   differential `x_r2 - x_r3`, and **two ways of drawing the scaling factor**,
   `N(0.5, 0.5)` or `Cauchy(0, 1)`, with SaNSDE adapting that balance. Corrected.
5. **Cycle count not pinned.** A fixed per-subcomponent allowance of 500 FEs yielded
   ~476 cycles at a 3×10⁶ budget. Paper Section 5.1 pins **50 cycles** (it is the
   `N` in Theorem 1's regrouping-probability analysis). The allowance is now
   *derived* from the cycle count and the budget.

## Validation attempt, and why it is inconclusive

Full-budget (3×10⁶ FEs), one seed, against the `decc-g` column in project 05:

| F | pre-fix (476 cycles) | post-fix (50 cycles) | published | post/pub |
|---|---|---|---|---|
| 1 | 7.03e-02 | 1.64e-02 | 3.22e-06 | 5106× worse |
| 2 | 2.47e+03 | 1.79e-01 | 1.31e+03 | **7300× better** |
| 4 | 1.53e+10 | 7.46e+11 | 2.16e+11 | 3.45× worse |
| 8 | 2.93e+14 | 9.89e+16 | 6.94e+15 | 14× worse |

The paper-faithful setting is dramatically better on the separable/multimodal cells
(F1, F2) and worse on the grouped-nonseparable ones (F4, F8) — the trade Theorem 1
predicts, since fewer cycles means fewer chances to co-locate interacting variables.

**The published column cannot adjudicate this.** `papers/governance/data_ledger.csv`
records it as `unverified (summary-only import or local; no environment.json)` and
annotates it "context-suite … do not promote to formal panel without complete
comparable evidence". Yang 2008 also *predates* CEC2013LSGO (2013) by five years and
benchmarked on the CEC2005 special-session suite, so that row is a later third-party
re-run under unknown settings, not the paper's own result. Exact reproduction was
never an available target.

## Standing decision

Keep the **paper-faithful** configuration (50 cycles, NSDE mutation, derived
allowance): when an implementation and an unverified third-party table disagree,
follow the paper. Record the disagreement rather than tuning toward the table —
tuning a comparator to match a number is how a baseline gets quietly strengthened
or weakened to suit a result.

## What remains before publication use

* Full 15 × 25 campaign (~10 CPU-hours; ~100 s/run) and a function-by-function
  comparison against the published column, reporting losses as well as wins.
* A regression pin so future edits cannot silently change its trajectories.
* An explicit supplement sentence that DECC-G is first-party code without an
  author-code oracle, unlike MOS and SHADE-ILS.
