# Stage 8 — Research Design, Experiments, Benchmarks, and Comparator Fairness

**Seat:** `s8_design_fairness` · **Lead role:** R3 · **Lead team:** T2-BENCH
**Review round:** 2026-07-22 · **Governing prompt:** `papers/PAPER_REVIEW_PROMPT.md` §§8 (L1740–1830), 5.4 (L1104–1148), 10 (L3160–3522), 15 (L3977)
**Package under review (verified in-repo, not from memory):**

| Item | Verified value | How verified |
|---|---|---|
| git HEAD | `45248eb31af7b01567c251f2a5da4f36e92d6030` | `git rev-parse HEAD` |
| Evidence release | `rel-2026-07-20-67d9345f9`, anchor `67d9345f9502a9a584e645fa8948f60a61d70e29`, 3,403 files / 712,437,624 bytes | `papers/governance/evidence_release_manifest.json` |
| Main PDF | 39 pp | `pypdf` page count of `papers/DT-GSK.pdf` |
| Panel | 7 algorithms × 3 suites = 21 (suite, optimizer) cells | `benchmarks/cec_reference_results/` |
| Per-run rows | CEC2017 5,916/alg; CEC2013 4,284/alg; CEC2011 550/alg | direct row count, all 21 `per_run.csv` |
| R-14 probe | `tests/regression/test_budget_crossing_semantics.py` → **14 passed in 4.23 s** | `python -m pytest -q` |

**Method.** Every finding below is anchored to a `file:line` in the current tree or to reproducible command output. I read the three comparator source publications from the local closed corpus (`reference_papers/`) rather than relying on the manuscript's characterisation of them, re-derived the panel's charged budgets from the released `per_run.csv`, re-ran the R-14 probe, and wrote two read-only instrumentation probes (paths given inline) to quantify the eGSK solver-substitution exposure and the terminal-batch overrun. No manuscript, code, or evidence file was modified.

---

## 0. Executive assessment

The design is, in most respects, unusually disciplined for this literature: one runner, one evaluator, one optimizer-independent seed schedule verified row-by-row (70,813 rows, 0 mismatches — **I re-derived the 70,813 total and it reconciles exactly**: 5,916×6 + 1,479 + 4,284×7 + 550×7), a single frozen DT-GSK configuration across three suites, an explicit development-suite disclosure, and a limitations section that names the mid-dimension deficit, the Holm-significant CEC2011 loss, the self-init asymmetry, and the authorship conflict of interest. Stage-8 gate **Gate H** is **not** failed on the central question: the design *can* answer "where does DT-GSK stand inside the GSK family under a common protocol", and no confirmed defect changes a reported number.

But the comparator-fairness surface is where this manuscript is most exposed, and three of its explicit fairness assertions do not survive checking:

1. **"All seven optimizers are therefore held to exactly the same MaxFES charge"** is false in the released data — 1,845 comparator runs stop below MaxFES under a stopping rule two of seven optimizers implement and five do not (§2.1).
2. **"the six comparators run their published reference constants"** is false for three of them — AGSK, APGSK and FDB-AGSK publish dimension-scaled initial populations (20·D, 200·D, 40·D) and were all run at a flat `NP_init = 100` (§2.2).
3. **"one code base, one protocol and one harness"** understates the actual production: the CEC2017 panel was produced at **seven different producer commits** across ten days, and the project's own RT-001 record documents that re-running the six comparators at the current commit yields **3,772 scientific-column differences** (§2.4).

None of these is fatal; all three are correctable by text (plus, ideally, one cheap sensitivity run). But each is the kind of statement a specialist reviewer at *Algorithms* can falsify in minutes from the artifacts the paper itself ships, and a falsified fairness claim damages the paper far more than the underlying deviation does.

**Category score (Stage 8, research design & comparator fairness): 3 — adequate but vulnerable.** The design supports the claim; the fairness *statements* about it do not all hold.

---

## 1. Research-question audit

### 1.1 The stated questions

The paper poses one empirical question explicitly (rendered PDF, Introduction): *"within the seven-algorithm GSK-family panel, under a budget-fair, reference-locked protocol, where does DT-GSK stand, and how does that standing change across dimension tiers?"* — and three contributions C1–C3 (`papers/main.tex:127–153`; `papers/sections/introduction.tex`).

| Criterion (§8 research-question audit) | Verdict | Evidence |
|---|---|---|
| Explicit and falsifiable | **PASS** | Standing = Friedman mean rank in a fixed 7-panel; falsifiable by re-derivation from the release. |
| Endpoint addresses the question | **PASS** | Endpoint = per-function mean error (CEC2017/CEC2013), raw best objective (CEC2011); `performance.tex:41–70`. |
| Experimental unit vs observation unit clear | **PASS with one caveat** | Inferential unit is the **function** (29/28/22 paired per-function means); the run is the observation unit. Stated at `performance.tex:196–232`. Caveat: the `A_12` column is computed on the same 29 function-means but is an *unpaired* statistic — the paper flags this twice (`performance.tex:221–231`, `364–373`), correctly. |
| Appropriate control / comparison | **PARTIAL** | The comparison is the six-member family panel. There is no "same-scaffold-without-tier-gating" control, and per-component attribution is explicitly not claimed — consistent with §10.10. Acceptable for the claim as scoped. |
| Run/task count justified | **PASS by convention, not by analysis** | 51 runs (CEC2017/CEC2013) and 25 (CEC2011) are the suite conventions; no power analysis is offered and none is conventional here. `performance.tex:85`. |
| Enough variation for the claimed scope | **PASS** | 4 dimensions × 3 suites × 79 problems; the claim is bounded to exactly that. |
| Confirmatory vs exploratory separated | **PARTIAL — see F-06** | Primary (mean-based ranks, Holm within dimension) is pre-specified in `papers/governance/statistical_analysis_plan.md`; robustness battery and BH companion are labelled exploratory. **But** the configuration-selection search that produced the frozen profile is disclosed only qualitatively ("several full-panel candidate configurations"), so its multiplicity is unbounded. |
| Development vs evaluation benchmarks distinguished | **PASS — and creditably so** | `performance.tex:103–111` and `supplementary.tex:1148–1169` state plainly that CEC2017 is the *development* suite and is selection-exposed, and that the headline rank is therefore a development-suite result. This is the single most important honesty move in the paper and it is made without hedging. |
| Conclusion answers without expansion | **PASS** | `performance.tex:857–875` and `conclusions.tex` keep every comparative statement inside the panel and cite NFL. |

### 1.2 The structural design tension the reviewer will name

The headline result (best overall CEC2017 Friedman mean rank, 2.48) is a result **on the suite that was used to select the configuration**, and the tier boundaries of the frozen profile (D<20, 20–49, 50–99, ≥100) are themselves a design choice fitted against a dimension grid — {10, 30, 50, 100} — that is exactly the evaluation grid. The paper discloses the first half of this (selection exposure) but never names the second half (the *tier boundaries* are a selected hyper-structure aligned to the evaluation dimensions).

The mitigation the paper offers is real and I credit it: CEC2011 and CEC2013 were held out of selection, and the held-out evidence is *mixed* (best overall on CEC2013, second with a Holm-significant loss on CEC2011) rather than uniformly worse — which is what one would expect if the CEC2017 standing were purely selection artefact. That argument is stated at `supplementary.tex:1162–1169` and it is the right argument. It is under-used: it appears only in the supplement, while the main text carries only the bare exposure disclosure.

**Recommendation (text-only, no new evidence):** move one sentence of the S5 argument into `sec:exp:settings` — the held-out suites' mixed outcome is the paper's best defence against the optimistic-selection objection and it should not be buried in a reproducibility appendix.

---

## 2. Comparator-fairness audit

Panel roster verified against §10.4's expected seven: `gsk, agsk, apgsk, fdb-agsk, atmals-gsk, egsk, dt-gsk` — **all seven present in all three suites**, F2 excluded uniformly (`run_config.json: exclude_funcs: 2` in all 21 cells), function sets identical per suite. CEC2020 and CEC2013-LSGO appear **nowhere** in the manuscript (`grep -rn -i "cec2020|lsgo" papers/sections papers/main.tex papers/supplementary.tex` returns only related-work statements *about the comparators' own published evidence bases*, plus an explicit "no LSGO claim" limitation at `supplementary.tex:1213–1215`). The untracked `results/_run_all/*/cec2013lsgo/` trees are staging and are correctly outside the evidence boundary. **§10.4 scope check: PASS.**

### 2.1 F-01 (Major, P1, CONFIRMED) — budget equality is asserted but not true: an undisclosed asymmetric stopping rule

**Manuscript claim.** `papers/sections/performance.tex:169–170`, rendered verbatim in `papers/DT-GSK.pdf`:

> "All seven optimizers are therefore held to exactly the same MaxFES charge."

**What the released evidence shows.** Re-derived directly from the 21 `per_run.csv` files in `benchmarks/cec_reference_results/`:

| Suite | Optimizer | runs charged < MaxFES | of | termination label |
|---|---|---|---|---|
| CEC2017 | **agsk** | **404** | 5,916 | `target_error_reached` |
| CEC2017 | **apgsk** | **338** (D10: 325, D30: 13) | 5,916 | `target_error_reached` |
| CEC2013 | **agsk** | **558** | 4,284 | `target_error_reached` |
| CEC2013 | **apgsk** | **545** | 4,284 | `target_error_reached` |
| CEC2017/2013 | gsk, fdb-agsk, atmals-gsk, egsk, dt-gsk | **0** | — | always `max_evaluations` |
| CEC2011 | all seven | 0 | 550 each | no published optimum ⇒ `target_error = NaN` |

**Total: 1,845 of 41,412 CEC2017+CEC2013 panel runs are charged less than MaxFES, and every one of them belongs to AGSK or APGSK.** The extreme is AGSK CEC2017 D=10, where charged `nfes` runs as low as **44,497 of 100,000** — 44.5 % of the nominal budget.

**Root cause (code, not data).** Only two of the seven ports implement a target-error stop:
- `src/gsk_family/optimizers/agsk.py:348–355` — `if best_fitness - optimum < target_error: terminated_on_target = True; break`, then `error = 0.0` at `:356–358`.
- `src/gsk_family/optimizers/apgsk.py:234, 241, 244` — identical construction.
- `gsk.py`, `fdb_agsk.py`, `atmals_gsk.py`, `egsk.py`, `dt_gsk.py` have no such branch; their `while nfes < max_nfes` loops always exhaust the budget.

**Is it materially unfair? No — and I say so explicitly.** The stop threshold is `target_error = 1e-8` (`src/gsk_family/benchmark_adapter/factory.py:178, 267, 339, 371`), which is *identical* to the reporting floor the suite applies to every algorithm. A run that stops there is already recorded at error 0 and cannot improve below the floor; continuing would change nothing. I further verified the second-order channel: the convergence figures aggregate from `gen_logs/CheckpointErrors_*.csv` (`papers/scripts/_convergence_common.py:11–12, 75–76, 111`), **not** from the truncated `curves/` files, and I checked all 400 AGSK/APGSK checkpoint logs across CEC2017+CEC2013 — **0 ragged rows, 0 blank/NaN cells**. Every one of the 51 runs contributes at every checkpoint for every algorithm, so the "identical aggregation basis" caption claim (`performance.tex:669–673`) holds.

**Why it is still Major.** (a) The sentence is a *fairness* assertion and it is false as written; a reviewer who opens the shipped `per_run.csv` and sorts on `nfes` finds it in under a minute. (b) The asymmetry itself — two of seven optimizers carry a stopping rule the other five do not — is a §8 "identical stopping rules" item and appears **nowhere** in the manuscript: `grep -rn -i "target_error_reached|early stop|stopping rule" papers/sections/*.tex papers/main.tex papers/supplementary.tex` returns **zero hits**. (c) It brushes the governance guardrail on `MT-11`, whose `blocked_wording` is *"Any implication that comparators share this accounting guarantee"* (`papers/governance/claims_evidence_matrix.csv`). (d) The project's own audit already found it (`papers/governance/benchmark_protocol_audit.md:105, 189, 195, 203, 231, 234`; `benchmark_protocol_audit_part2.md:134–140`) and classified it `PROTOCOL_OBSERVATION / info` with "Note in cost-analysis captions" — the note was never propagated into the manuscript.

**Required correction (text-only; no rerun).** Replace the sentence with something true and stronger, e.g.: *"All seven optimizers are held to the same MaxFES cap. Five run to the cap on every cell; AGSK and APGSK additionally implement the CEC target-error stop inherited from their reference implementations and therefore terminate early on 1,845 of the 41,412 CEC2017/CEC2013 cells. Because that stop fires exactly at the 10⁻⁸ reporting floor, those runs are already recorded at error 0 and the early return cannot change any reported statistic; the per-checkpoint logs are complete for every run, so the convergence aggregation basis is unaffected."* Add one row to Table `tab:protocol` for the stopping rule.

**Post-revision verification.** Re-run the census (`per_run.csv` termination counts) and confirm the manuscript's stated figures match; confirm no caption still claims a uniform MaxFES *charge*.

### 2.2 F-02 (Major, P1, CONFIRMED) — "published reference constants" is false for three comparators; the population-size deviation is undisclosed

**Manuscript claims.** Two, both rendered in the PDF:
- `papers/sections/proposed_algorithm.tex:669` — "the six comparators run their published reference constants";
- `papers/sections/proposed_algorithm.tex:691–697` — panel table `tab:panel`, column *Configuration in this study*: `AGSK [mohamed2020agsk] published reference constants; in-repository re-run`, and identically for `APGSK [apgsk2021]` and `FDB-AGSK [fdbagsk2023]`;
- `papers/sections/performance.tex:100–101` — "comparator configurations follow their original publications".

**What the cited publications actually specify** (read from the local closed corpus; page indices are 0-based `pypdf` pages):

| Comparator | Cited source | Published initial population | Verbatim locus |
|---|---|---|---|
| GSK | `mohamed2020gaining` | NP = 100 (fixed) | corroborated by `jawad2024egsk` Table 3, p. 8 |
| **AGSK** | `mohamed2020agsk` | **NP = 20·D**, N_min = 12 | p. 3: *"The initial values of The initial population size (NP) were set to 20 * D."* |
| **APGSK** | `apgsk2021` | **NP = 200·D** (D = 10,15,20); 250 at D = 5; N_min = 12 | p. 4: *"The initial population size (NP) was chosen to be (200 ∗ D) for D = 10, 15 and 20"* |
| **FDB-AGSK** | `fdbagsk2023` | **popsize_init = 40·n**, popsize_min = 12 | p. 10, Eq. (62) discussion |
| ATMALS-GSK | `alfadli2025atmals` | NP = 100 (fixed) | p. 19: *"With a fixed population size of 100 …"* |
| eGSK | `jawad2024egsk` | NP = 100 | p. 8, Table 3 |

**What was actually run.** All six comparators ran with `optimizer_options: {}` (every `run_config.json`), and the runner's fallback is a flat 100 regardless of dimension:

```
src/gsk_family/runners/run_experiment.py:284-290
def _optimizer_population_size(optimizer, optimizer_options) -> int:
    if optimizer in {"agsk", "apgsk", "fdb-agsk"} and "np_init" in optimizer_options:
        return int(optimizer_options["np_init"])
    if "np" in optimizer_options:
        return int(optimizer_options["np"])
    return 100
```
with the same default inside each port (`agsk.py:209–210`, `apgsk.py:73–74`, `fdb_agsk.py:204–205`, `egsk.py:53`). The released `run_config.json` files confirm `NP_init = 100, min_pop_size = 12` for agsk/apgsk/fdb-agsk and `pop_size = 100` for gsk/atmals-gsk/egsk at **every** dimension. DT-GSK runs `NP_init = 5·D` (`src/gsk_family/optimizers/_dt_core.py:149–152`, `np_init_mult: int = 5`, `n_min: int = 12`).

**Resulting panel:**

| D | AGSK published → run | APGSK published → run | FDB-AGSK published → run | GSK/ATMALS/eGSK | **DT-GSK** |
|---|---|---|---|---|---|
| 10 | 200 → **100** | 2000 → **100** | 400 → **100** | 100 → 100 ✓ | **50** |
| 30 | 600 → **100** | (n/a) → **100** | 1200 → **100** | 100 → 100 ✓ | **150** |
| 50 | 1000 → **100** | (n/a) → **100** | 2000 → **100** | 100 → 100 ✓ | **250** |
| 100 | 2000 → **100** | (n/a) → **100** | 4000 → **100** | 100 → 100 ✓ | **500** |

**The fair counter-argument, stated in full.** The normalisation is *not* arbitrary and it is *not* unprecedented: `jawad2024egsk` Table 3 (p. 8) — a published, peer-reviewed GSK-family CEC2017 comparison at exactly D ∈ {10,30,50,100} — sets **AGSK NP = 100, N_min = 12; APGSK NP = 100, N_min = 12; FDB-AGSK NP = 100, N_min = 12**, i.e. precisely the constants used here. Further, AGSK and APGSK published their settings for CEC2020 at D ≤ 20; transposing APGSK's 200·D to D = 100 would give NP = 20,000 against MaxFES = 10⁶, i.e. 50 generations, which is not a sensible protocol. A transposition rule was *necessary*, and the one chosen has corpus precedent.

**Why it is nonetheless Major.** (a) The manuscript does not say any of that. It says the constants are the *cited papers'* constants, which for three of six they are not — a traceability failure of exactly the kind §5.5 calibrates as Major (an exhibit misdirecting the reader to a wrong referent). (b) The deviation is nowhere disclosed: `grep` across `papers/sections/*.tex`, `papers/supplementary.tex`, and `papers/governance/*.md` for `20*D | 200*D | 40*n | normalised to 100 | fixed at 100` returns only the *incidental* NP = 100 mentions in the budget-crossing audit; the comparability audit affirmatively records the opposite — *"Baselines run reference constants (`optimizer_options: {}`; pop_size 100 where applicable)"* and marks the row **PASS** (`papers/governance/comparability_audit.md:28`). The governance gate therefore passed on a false premise. (c) The paper's **own related-work section credits APGSK with "a much larger initial population"** as one of its four contributed mechanisms (`papers/sections/related_work.tex:60–64`) and then runs APGSK with the same population as plain GSK — the manuscript disables the mechanism it attributes. (d) Direction of effect is not neutral across the grid: at D ≥ 30 DT-GSK carries 1.5–5× the comparators' population while three comparators lose their published dimension scaling, precisely in the tiers carrying the first-place claims. (In fairness, at D = 10 the asymmetry runs the *other* way — DT-GSK's NP = 50 is half the comparators' 100 — and D = 10 is not a tier the paper wins comfortably. I note this because it argues against a self-serving reading of the choice.)

**Required correction (text-only; no rerun).** (i) Change the three `tab:panel` cells from "published reference constants" to something exact, e.g. *"reference constants; initial population normalised to NP = 100 (N_min = 12) across dimensions, following the CEC2017 panel settings of [jawad2024egsk, Table 3]"*, and add the same to `performance.tex:100–101`. (ii) Add a short paragraph in `sec:exp:settings` giving the published values (20·D / 200·D / 40·D), the transposition problem at D = 100, the precedent, and an explicit statement that the effect on the standings is unbounded by the present evidence. (iii) Correct `papers/governance/comparability_audit.md:28` and re-adjudicate that PASS. (iv) Register the sensitivity experiment (**MX-02** below) as the evidence that would close it properly.

### 2.3 F-03 (Major, P1, CONFIRMED) — the eGSK solver substitution is load-bearing, quantified here for the first time, and bounded only for runtime

**Manuscript claim.** The substitution is disclosed three times (`performance.tex:32–39`; `proposed_algorithm.tex:669–674`; `supplementary.tex:1766–1773`), always with the same bound: *"cross-implementation **runtime and environment** comparability is therefore limited, and no runtime-superiority claim is made anywhere in this paper."* The disclosure bounds **runtime**. It does not bound **performance**.

**What the code does.** `src/gsk_family/optimizers/egsk.py:149–212` replaces the published `fmincon(...,'sqp')` interior-point refinement with `scipy.optimize.minimize(method="SLSQP")`, budgeted at `ceil(2e-3 · MaxFES)` per invocation (`:170–171`) and correctly charged into `nfes` (`:211`). It is invoked inside the main loop in the late stage (`:313, 320–324`), so it can fire many times per run.

**Quantification (my probe — this number does not exist anywhere in the package).** Read-only instrumentation at `an out-of-tree read-only probe script (not committed)`, run on real CEC2017 cells with the campaign seed formula:

| D | F | polish invocations | evaluations through SLSQP | **share of MaxFES** |
|---|---|---|---|---|
| 10 | 1 | 0 | 0 | 0.0 % |
| 10 | 5 | 224 / 225 | 2,600 / 2,567 | 2.6 % |
| 10 | 12 | 189 / 202 | 6,100 / 4,888 | 4.9–6.1 % |
| 10 | **26** | 84 | **16,600** | **16.6 %** |
| 30 | 1 | 0 / 54 | 0 / 6,892 | 0–2.3 % |
| 30 | 5 | 569 / 567 | 18,148 / 18,300 | 6.0–6.1 % |
| 30 | 12 | 6 / 2 | 3,600 / 1,200 | 0.4–1.2 % |
| 30 | **26** | 529 / 419 | 22,176 / **33,100** | 7.4–**11.0 %** |

So on composition functions **up to one sixth of eGSK's entire evaluation budget passes through the substituted solver**, and the affected class (F21–F30) is one of the two classes the paper analyses by name. eGSK is not an incidental comparator: it is the *only* algorithm that beats DT-GSK anywhere (rank 2.29 vs 2.50 at CEC2017 D = 30; 2.52 vs 3.36 on CEC2011 with a Holm-significant loss), and DT-GSK and eGSK are never Nemenyi-separable on CEC2017. A solver substitution worth up to 16.6 % of eGSK's budget therefore sits directly underneath the paper's most consequential comparison — in **both** directions: if SLSQP is weaker than `fmincon`, DT-GSK's wins are inflated; if stronger, DT-GSK's losses are.

**Classification.** Under §8's scheme this comparison is **B — comparable with verified imported evidence**, *not* A. The manuscript's framing implies A-with-a-runtime-caveat.

**Required correction.** (i) Widen the disclosure from "runtime and environment comparability" to *performance* comparability, stating the measured budget share and that its sign is unknown. (ii) Classify the DT-GSK↔eGSK comparison explicitly as B in the text, and attach that qualification to the two cells where eGSK leads. (iii) Register **MX-01** (solver-sensitivity contrast) below.

### 2.4 F-04 (Major, P2, CONFIRMED) — the panel was produced at seven producer commits, and a documented re-run failed to reproduce the comparator half

**Manuscript claim.** `papers/supplementary.tex:1199–1201`: *"What the scope does buy is attribution: **one code base, one protocol and one harness**, so within-panel deltas reflect algorithmic differences up to the port and initialization asymmetries disclosed below."*

**What the release records.** Producer commits from each cell's `environment.json`:

| Suite | gsk | agsk | apgsk | fdb-agsk | atmals-gsk | egsk | dt-gsk |
|---|---|---|---|---|---|---|---|
| CEC2017 | `31c5a04c4` 07-08 | `f94817cc4` 07-08 | `20cfed0ac` 07-08 | `19f32fb83` 07-09 | `7483cac2e` 07-09 | `c35c26de7` 07-09 | **`251fc8cb8` 07-18** |
| CEC2013 | `c35c26de7` | `c35c26de7` | `c35c26de7` | `2d72f649` | `2d72f649` | `2d72f649` | **`251fc8cb8`** |
| CEC2011 | `c35c26de7` (all six) | | | | | | **`251fc8cb8`** |

Seven distinct commits on the primary suite, spanning ten days, with DT-GSK's cells produced nine days after the last comparator cell. Hardware/parallelism parity *is* clean — all 21 cells record `workers: 15`, the same platform string, `numba 0.64.0`, and an identical `suite` FP probe hash `9d0adb66…`, so the evaluator was byte-identical across the panel.

**The adverse result that is not disclosed.** `papers/governance/remediation_2026_07_18/ticket_status.csv`, ticket **RT-001** (`lifecycle_status: closed_verified`, `closed_utc: 2026-07-21`), `residual_work` field, verbatim:

> "Option 2 (re-time the six comparators) was executed 2026-07-21 via scripts/retime_comparators.py (CEC2017, 51 runs, ~22h) but **FAILED the determinism gate: 3,772 scientific-column diffs** — the 2026-07-08 comparator evidence (commit 31c5a04c4) is **not bit-reproducible under current code** (dc924dc48; version/FP drift amplified by chaotic search, worst for scipy/local-search **atmals-gsk ~31 % / egsk ~29 %**). Confirmed deterministic within-commit (fresh re-run == tonight 30/30), so NOT a bug."

This is a real, documented, adverse reproducibility result about **the comparator half of the panel**, and it is absent from the manuscript. The closest the paper comes is `performance.tex:155–158` — *"The comparator-specific update kernels are not covered by a numerical probe: their JIT state is recorded, but their numerical identity across producer commits rests on the shared-kernel probes and code history rather than on a direct hash."* That sentence anticipates the right risk and then understates it: the paper says the identity "rests on code history"; the project's own experiment shows that when the identity was actually tested it did **not** hold, for ~30 % of the cells of the two local-search comparators.

I note in mitigation, and it matters: (a) the determinism section (`proposed_algorithm.tex:718–728`) already restricts all three byte-stability levels to DT-GSK and states *"no byte-stability claim is made for the comparator implementations"* — the R-09 narrowing is correctly applied there; (b) RT-001's own verification confirms DT-GSK's **scientific** columns were byte-identical across the M038 fix (only `runtime_seconds` moved), so mixing DT-GSK's later commit into the panel did not perturb DT-GSK's numbers; (c) the failure is attributed to library/FP drift amplified by chaotic dynamics, which is a known property of stochastic search, not a defect. None of that removes the disclosure obligation: an executed experiment whose result weakens a comparability claim must be reported alongside the claim, not held in a governance CSV.

**Required correction (text-only).** Add to the limitations (`supplementary.tex` §"Limitations in Full", sixth item) roughly: *"The panel's cells were produced over ten days at seven producer commits of this repository; a subsequent re-execution of the six comparators under a later commit reproduced their scientific columns only partially (≈29–31 % of cells differed for the two local-search comparators), a version/floating-point drift amplified by chaotic search dynamics. Each algorithm's own cells were produced under a single commit and a single evaluator (identical suite probe hash across all 21 cells), so the within-panel comparison is internally consistent; but the comparator half of the release is not re-derivable from the current code, and only DT-GSK carries a byte-stability guarantee."* Also soften "one code base, one protocol and one harness" to "one repository, one evaluator, and one harness".

### 2.5 F-05 (Moderate, P2, CONFIRMED) — the pairing gate passes on a premise the manuscript disclaims

`papers/governance/seed_and_pairing_audit.md` §4 determines *"pairing is VALID for every comparator pair among the 7 panel optimizers, on all three primary suites"* on three bases, of which the third reads:

> "3. **Common random numbers at initialization.** `initial_population_policy = runner_supplied_X0`; … With identical seeds and the same `threefry` generator in all 21 cells, run r of **every** optimizer starts from the **same initial population** on the same instance."

That is false for DT-GSK, and the manuscript says so: `performance.tex:117–124` and `proposed_algorithm.tex:788–793` disclose the self-init exception, and the code is unambiguous (`src/gsk_family/optimizers/dt_gsk.py:14–18`: *"DT-GSK … draws its own initial population, so it does **not** consume the runner's fair-start `initial_population`"*). The released DT-GSK sidecar repeats the false version: `benchmarks/cec_reference_results/cec2017/dt-gsk/run_config.json` records `"initial_population_policy": "runner-generated shared X0 from get_cec_seed(...)"` — the string is hard-coded for every optimizer at `src/gsk_family/runners/run_experiment.py:972` and is not conditioned on the self-init exception.

**Does it invalidate any inference? No.** The inferential unit is the function, not the run: the primary Wilcoxon pairs 29 per-function *means* over 51 runs; the Friedman blocks are functions; the BCa intervals resample fixed per-function midranks (`performance.tex:196–246`). Nothing reported is a run-level *paired* statistic (the run-level `A_12` is unpaired by construction). Initialization differences are absorbed into the 51-run mean.

**Why it is still a ticket.** A governance gate that passes a fairness property on a stated basis the manuscript itself disclaims is not a passed gate, and the released metadata actively contradicts the paper. Fix: correct §4 basis 3 to "common seed / problem / run index, with DT-GSK's self-init exception recorded", re-affirm the pairing verdict on function-level grounds, and either condition the `run_config.json` string on the optimizer or add a `self_init: true` field (the latter touches the runner, not the byte-locked optimizer core — but note it would require a new release, so the honest minimum is an erratum row in the release README plus the audit correction).

### 2.6 F-06 (Moderate, P2, CONFIRMED) — the magnitude of the selection exposure is undisclosed and unauditable

`papers/supplementary.tex:1157–1161`:

> "Before the final configuration was promoted, **several full-panel candidate configurations** were compared against the family panel during development; this selection exposure is disclosed here as an author-attested development-history note (the intermediate candidates are not part of the immutable evidence release), rather than absorbed silently."

The disclosure is honest in kind but empty in degree. A reader cannot bound the optimistic-selection bias without knowing: how many candidates, over which cells (all 29×4? a subset?), against which selection statistic (overall Friedman rank? win/tie/loss?), and whether the selection was single-shot or iterative. "Several full-panel candidate configurations compared against the family panel" is, read literally, a model-selection search *scored on the same panel and the same statistic as the headline result* — the exact multiplicity the frozen analysis plan controls for within the confirmatory analysis but not across the selection stage.

**Fix (text-only; author attestation, no new evidence):** state the count, the selection cells, and the selection criterion, e.g. *"k candidate configurations were scored on CEC2017 overall Friedman mean rank across all 29 functions at all four dimensions; the promoted configuration was the rank-best. Because the selection statistic is the headline statistic, the CEC2017 standing should be read as an optimistically-selected estimate; CEC2011 and CEC2013 provide the unexposed comparison."* If the count cannot be attested, say so — an admitted unknown is auditable, a vague quantifier is not.

### 2.7 F-07 (Moderate, P2, CONFIRMED) — a post-recovery statement in the supplement no longer matches the shipped release

`papers/supplementary.tex:1754–1762` states the strict-source rule with one exception:

> "…for APGSK on CEC2017 at D = 10/30/50, where the per-run sidecar was overwritten by a later D = 100-only invocation, **the per-run source is** the final-checkpoint column of the corresponding per-generation logs…"

The shipped release contradicts the present tense. `benchmarks/cec_reference_results/cec2017/apgsk/per_run.csv` now contains **5,916 rows covering all four dimensions** (D10/30/50 rows carry real, non-zero `runtime_seconds`, so they are recovered records rather than reconstructions), and I verified **all 242 apgsk/cec2017 files match their SHA-256 in `evidence_release_manifest.json` (0 mismatches, 0 missing)** — i.e. the recovery was properly minted into `rel-2026-07-20-67d9345f9` rather than edited in place, so §10.3 is not breached.

The main text handles this correctly with the footnote at `performance.tex:134–139` (recovery disclosed, frozen basis conservatively retained). The supplement's reproducibility appendix does not, and a reviewer downloading the release will find a complete APGSK per-run file directly contradicting it. This is the §5.5 "stale existence claim after data recovery" pattern in its milder form — the supplement does not claim the data *does not exist*, but it does state a present-tense source that is no longer the shipped one.

**Fix:** past-tense the sentence and add the recovery: *"…at analysis freeze the per-run sidecar covered D = 100 only, so the frozen analysis read the final-checkpoint column of the per-generation logs for D = 10/30/50; those per-run records were subsequently recovered and are included in the accompanying release, and they reproduce the frozen summaries exactly."*

### 2.8 F-08 (Moderate, P2, CONFIRMED) — the governance early-stop census is 338 runs short of the shipped release

`papers/governance/benchmark_protocol_audit.md:134` reconciles *"(69,306 `max_evaluations` + 1,507 `target_error_reached` = 70,813)"*, and the anomaly rows enumerate A2-001 (cec2017/agsk, 404), A2-029 (cec2013/agsk, 558) and A2-032 (cec2013/apgsk, 545) — **1,507**. My census of the shipped release gives **1,845**; the missing 338 are the CEC2017/APGSK early stops (D10: 325, D30: 13) that live in the recovered per-run rows. The audit's arithmetic is consistent with the pre-recovery `experiment_matrix.csv` (which still holds only 1,479 apgsk/cec2017 rows, D100-only) but not with the release the paper ships. The audit is a governance artifact rather than reader-facing, so this is Moderate — but it is the evidentiary base for the budget claim in F-01, so it should be re-run against `rel-2026-07-20-67d9345f9` before F-01's replacement text is written.

Related and minor: `papers/governance/experiment_matrix.csv` (70,813 rows) still carries `evidence_release_id = PENDING-RELEASE-ID(phase2-evidence_release_manifest)` in every row and is bound to the superseded release.

### 2.9 F-09 (Major, P2, CONFIRMED) — `cover_letter.md` still carries the over-claim that R-09 removed from `cover_letter.tex`

R-09 narrowed the byte-stability claim. Verified applied in the built artifacts:
- `papers/cover_letter.tex:55` and the rendered `papers/cover_letter.pdf`: *"evaluated under a release-locked protocol, **with byte-stable determinism for DT-GSK in the declared supported environment**."* ✔
- `papers/cover_letter.md:22`: *"evaluated under **a byte-stable, release-locked protocol**."* ✘ — the pre-R-09 wording, which asserts byte-stability of the *protocol* (hence of the panel), exactly the claim F-04 shows is false for the comparators.

Both files also carry the reviewer-placeholder removal (R-09's other half) correctly. This is the §5.5 "orphan/superseded source file in the tree" pattern: the shipped PDF is right, but a superseded source carrying a withdrawn claim remains in the package, and a cover letter's `.md` is precisely the file an author pastes into a submission portal. **R-09 is therefore closed *incompletely*.** Fix: sync or quarantine `papers/cover_letter.md`.

### 2.10 F-10 (Moderate, P2, CONFIRMED) — the R-14 probe is sound but the manuscript overstates its reach

I re-ran the probe: **14 passed in 4.23 s**, and I independently reproduced its central measurement with my own instrumentation (`…\scratchpad\overrun_probe.py`):

```
gsk          charged= 1050 evaluated= 1100 uncounted=  50
agsk         charged= 1050 evaluated= 1058 uncounted=   8
apgsk        charged= 1050 evaluated= 1058 uncounted=   8
fdb-agsk     charged= 1050 evaluated= 1058 uncounted=   8
atmals-gsk   charged= 1050 evaluated= 1100 uncounted=  50
egsk         charged= 1050 evaluated= 1100 uncounted=  50
dt-gsk       charged= 1050 evaluated= 1050 uncounted=   0
```
matching the LaTeX evidence comment at `performance.tex:175–178` ("8-50 uncounted terminal rows (dt-gsk 0)") exactly. The R-05 disclosure is accurate and the R-14 evidence is real. **This remediation is correctly closed on its own terms.**

Two scope observations the manuscript should absorb:

(a) **The manuscript's verification verb is stronger than the experiment.** `performance.tex:172–174`: *"strictly truncating them was **verified** to leave the returned solution, its fitness, and the charged budget bit-identical **for all seven optimizers**"*. What was run is **one synthetic cell** — sphere, D = 10, NP = 100, MaxFES = 1,050, a single seed (`test_budget_crossing_semantics.py:40–45`) — not the campaign. Read as written, a reviewer will expect a campaign-wide check.

(b) **The stronger argument is structural and is not made.** Inertness is not stochastic here; it is guaranteed by construction. Every port scans the incumbent only over the counted prefix — `_scan_best(trial, children_fitness, n_count, …)` with `n_count = min(NP, max_nfes - nfes)` (`gsk.py:191–198`; `agsk.py:317–325`; `apgsk.py:201–209`; `fdb_agsk.py:319–327`; `atmals_gsk.py:331–339`; `egsk.py:294–298` via `_scan_best_with_index`) — and the post-selection population update that *does* see the full batch is never read again because the loop's `while nfes < max_nfes` guard fails immediately after. The uncounted rows are therefore provably unable to enter `best_fitness`, `best_x`, or the convergence trace, on *any* problem, seed, or dimension. One sentence citing that prefix-scan invariant converts the claim from "we tested one cell" to "this holds by construction, and here is a probe that exercises it".

(c) **The probe deliberately disables the asymmetry of F-01.** `test_budget_crossing_semantics.py:109` sets `target_error=float("nan")` with the comment *"NaN => never early-stop; consume the budget"*. That is the correct choice for isolating the crossing, but it means the R-14 evidence is silent on the one budget asymmetry that is actually present in the campaign. The two should be disclosed together.

**Fix:** scope the verb ("verified on a probe cell and guaranteed by the prefix-scan invariant of all seven ports"), cite the invariant, and add the F-01 sentence adjacent to it.

### 2.11 F-11 (Minor, P3, CONFIRMED) — governing-prompt staleness in my stage's area (recorded per the review brief)

Per the brief's instruction to record prompt staleness as a finding, and per §1.4 precedence (repo outranks the prompt's embedded snapshot):

| Prompt locus | Prompt says | Repo says | Verified by |
|---|---|---|---|
| §10.7, final bullet (L3299) | RT-001 **"IN PROGRESS"**; runtime table *"provisionally frozen"*; remedy = *"re-timing all six comparators on one idle machine (`scripts/retime_comparators.py`)"*; reviewer must *"not certify them as a settled single-environment comparison"* | RT-001 is `closed_verified`, `closed_utc: 2026-07-21`, resolved by **Decision 7 Option 3 (DT-GSK-only fallback)**; Option 2 (the comparator re-timing the prompt describes) was **executed and FAILED** the determinism gate (3,772 diffs). The shipped `tab:runtime` (`performance.tex:759–784`) tabulates **DT-GSK only** and states *"no cross-algorithm runtime comparison is made"* | `papers/governance/remediation_2026_07_18/ticket_status.csv` (RT-001 row); `papers/DT-GSK.pdf` Table 12 |
| §1.5 preamble (L120) | ledger at **73/80**, *"seven … tickets remain open"*, RT-001 named as *"the live runtime blocker"* | ledger has **80 rows, all `closed_verified` / `superseded_with_evidence`** | `ticket_status.csv` status census |
| §10.7 same bullet | *"the CURRENT release … pending regeneration when RT-001 lands"* | current release `rel-2026-07-20-67d9345f9` is final for this cycle; no regeneration pending | `evidence_release_manifest.json` |
| §1.5.0-B / supplement comment | — | `papers/supplementary.tex:1780` LaTeX comment still names *"the primary release rel-2026-07-16-78f075cb0"* (non-rendered, but a stale source comment) | direct read |

Consequence for my stage: the prompt instructs the reviewer to confirm an in-progress comparator re-timing. That remedy was abandoned after failing, and its failure is the substance of **F-04** — which the stale prompt would otherwise have caused a reviewer to overlook.

---

## 3. Comparator classification (§8 A/B/C/D)

| # | Comparison | Class | Justification |
|---|---|---|---|
| 1 | DT-GSK vs **GSK** | **A** | Published constants (NP = 100) match the run; identical evaluator, budget, seeds; no early-stop asymmetry; no solver substitution. Inferentially valid. |
| 2 | DT-GSK vs **ATMALS-GSK** | **A** | `alfadli2025atmals` p. 19 fixes NP = 100; run at 100. Runner injects a `protocol` branch (`run_experiment.py:318–322`) that selects the paper's own CEC2011/CEC2017 senior-donor variants (`atmals_gsk.py:131–134`) — this is fidelity to the source, applied uniformly, not per-suite tuning. Valid. |
| 3 | DT-GSK vs **AGSK** | **B** | Population normalised 20·D → 100 (F-02) **and** early-stop asymmetry (F-01, 962 runs across two suites). Endpoint-neutral for the stop; unbounded for the population. Comparable, but the deviation must be declared before the inference is quoted. |
| 4 | DT-GSK vs **APGSK** | **B** | Same two deviations (200·D → 100; 883 early stops) plus the disclosed D ≤ 50 per-run gap now recovered post-freeze (F-07). The paper's function-level fallback is the correct disposition. |
| 5 | DT-GSK vs **FDB-AGSK** | **B** | Population normalised 40·D → 100 (F-02). No stopping-rule or solver deviation. |
| 6 | DT-GSK vs **eGSK** | **B** | Solver substitution consuming up to **16.6 % of MaxFES** (F-03), unbounded in sign. This is the comparison carrying the paper's two adverse headline cells, so the class matters most here. |

No comparison is class C or D. **No comparison must be excluded from formal claims** — but four of six require a declared deviation the manuscript does not currently declare.

**Out of scope by directive:** external non-GSK baselines (L-SHADE-class, CMA-ES, differential-grouping) are ruled out of scope for this cycle by the governing prompt §1.5.4 and by my seat brief. I raise **no ticket** and record **no fairness gap** on that axis. It appears once in the missing-experiment register (MX-06) classified `optional_or_out_of_scope`, purely so the register is complete.

---

## 4. Verified-clean items (checks performed that found nothing)

Recording these so the panel can see what was tested and cleared, not only what failed.

| Check | Result |
|---|---|
| Seed schedules identical across optimizers | 6 of 7 CEC2017 schedules **byte-identical** (SHA-256 `77122f46c87d5737`, 5,916 rows); APGSK's sidecar holds its D100 subset (1,479) — the disclosed anomaly. |
| Seed-audit row total | **70,813 reconciles exactly** = 5,916×6 + 1,479 + 4,284×7 + 550×7. |
| Per-run uniqueness | 0 duplicate `(dimension, function, run)` keys in any of the 21 `per_run.csv`; runs/cell = 51 (CEC2017/2013) and 25 (CEC2011) with no exceptions. |
| Budget ceiling | `nfes` **never exceeds** MaxFES in any of 70,813 released rows. |
| Environment / parallelism parity | All 21 cells: `workers: 15`, same platform string, `numba 0.64.0`, `llvmlite 0.46.0`, identical `suite` FP probe hash `9d0adb66…`. Fair hardware and parallelism interpretation. |
| Evaluator identity | Identical suite probe hash across all seven optimizers per suite ⇒ run *r* of any two optimizers scores a byte-identical objective. |
| Convergence aggregation basis | Generator reads `gen_logs/CheckpointErrors_*.csv` (`_convergence_common.py:11–12, 75–76, 111`), not the truncated `curves/`. All 400 AGSK/APGSK checkpoint files: **0 ragged rows, 0 blank/NaN cells** ⇒ the "identical basis, all 51 runs, no interpolation" caption claim holds despite the early stops. |
| Comparator constants other than NP | AGSK `SENIOR_P = 0.05`, `INITIAL_KW = [0.85, 0.05, 0.05, 0.05]`, `c = 0.05` (`agsk.py:28–29, 271`) match `mohamed2020agsk`; APGSK negative pool `[-0.15,-0.05,-0.05,-0.15]` (`apgsk.py:39`) matches `apgsk2021`; GSK `p = 0.1, KF = 0.5, KR = 0.9, K = 10` match `mohamed2020gaining`. |
| eGSK polish budget accounting | `budget = min(ceil(2e-3·MaxFES), max_nfes - nfes)` with a hard sentinel at `budget` calls and every call charged (`egsk.py:170–171, 183–190, 211`) — the substituted solver cannot exceed its budget or evade the counter. |
| eGSK polish reachability | Fires inside the late-stage branch (`egsk.py:313–324`), **not** after budget exhaustion — the signature mechanism genuinely runs. |
| APGSK release integrity | All 242 `cec2017/apgsk` files match their manifest SHA-256 (0 mismatches, 0 missing) ⇒ the post-freeze recovery was minted into a new release, not edited in place. §10.3 not breached. |
| R-05 / R-14 disclosure accuracy | Overrun figures (8–50 rows; dt-gsk 0) reproduced independently; probe passes 14/14. |
| §10.4 suite scope | CEC2020 / CEC2013-LSGO appear in **no** manuscript claim; staging trees correctly outside the evidence boundary. |
| §10.5 same-family boundary | Every comparative statement I could find is panel-scoped; NFL cited (`performance.tex:871–875`); no field-wide claim. |

---

## 5. Missing experiments

Full register in `missing_experiment_register.csv` (Appendix A.5 schema, 15 columns, §12.11 vocabulary). Summary:

| ID | Question | Class | Priority |
|---|---|---|---|
| **MX-01** | How much of eGSK's standing depends on the SLSQP-for-`fmincon` substitution? | `recommended_for_q1` | P1 |
| **MX-02** | Do the three normalised-population comparators change the standings at their published NP schedules? | `recommended_for_q1` | P1 |
| **MX-03** | Does the stopping-rule asymmetry move any reported statistic? | `useful_for_q2` (cheap; largely settled analytically) | P2 |
| **MX-04** | How large is the optimistic-selection bias from configuration selection on CEC2017? | `essential_before_submission` (disclosure form) / `recommended_for_q1` (empirical form) | P1 |
| **MX-05** | Does DT-GSK's self-initialisation account for any of its advantage? | `useful_for_q2` | P2 |
| **MX-06** | External non-GSK calibration | `optional_or_out_of_scope` — **ruled out of scope by §1.5.4; no ticket raised** | — |
| **MX-07** | Are the comparator cells re-derivable under a pinned environment? | `useful_for_q2` | P2 |

**None of MX-01…MX-07 is required to make the paper's current claims true**, because every claim is already bounded to the panel, the suites, the budgets, and the disclosed deviations. What is required before submission is **disclosure** (F-01, F-02, F-03, F-04, F-06), which is text-only and compatible with the standing "no rerun / no new release" constraint. That distinction is deliberate: §15 forbids asking for experiments without a decision-relevant design, and it equally forbids treating a disclosure defect as an experimental one.

---

## 6. Gate H determination

**`Gate H — Study Design and Fairness`: PASS WITH REQUIRED CORRECTIONS (conditional).**

Gate H fails when (i) the central research question cannot be answered by the design, (ii) comparator unfairness changes conclusions, (iii) required controls are absent, or (iv) evaluation data were materially used for tuning without disclosure and mitigation.

- (i) **Not met** — the design answers the panel-scoped question.
- (ii) **Not met on the evidence available.** The two confirmed deviations that could bear on conclusions are the population normalisation (F-02) and the eGSK solver substitution (F-03). Neither is shown to change a conclusion; both are *unbounded*, which is a disclosure obligation rather than a demonstrated unfairness. The stopping-rule asymmetry (F-01) is analytically neutral. Note the direction of the population deviation is not uniformly self-serving (DT-GSK carries the *smaller* population at D = 10).
- (iii) **Not met** — the controls the design needs (common seeds, common evaluator, common budget cap, held-out suites) are present and verified.
- (iv) **Disclosed and mitigated**, but the mitigation is incomplete: the exposure is disclosed (`performance.tex:103–111`, `supplementary.tex:1148–1169`) and mitigated by two held-out suites, yet its *magnitude* is not stated (F-06).

The gate is therefore **conditional on F-01, F-02, F-03, F-04 and F-06 being corrected in text**. If any of the three false fairness assertions (F-01, F-02, F-04) ships as written, I would move Gate H to **FAIL** — not because the science is wrong, but because a fairness claim falsifiable from the paper's own released artifacts is a §10.13 hard-rejection risk ("unfair eGSK provenance or solver comparison"; "language polish that masks, rather than resolves, evidential weakness") and is exactly what a specialist reviewer at this venue will test first.

---

## 7. Tickets (§5.4 schema)

### Ticket S8-01

```text
ticket_id: S8-01
review_stage: Stage 8 — Research design, experiments, benchmarks, comparator fairness
reviewer_role: R3 (T2-BENCH)
severity: Major
priority: P1
confidence: Confirmed
issue_type: experimental-design
manuscript_location: papers/sections/performance.tex:169-170 (rendered DT-GSK.pdf, Experimental Setup, "Environment and determinism"); Table tab:protocol row "MaxFES" (performance.tex:86)
claim_id_or_artifact_id: PR-04 (run counts and budgets); MT-11 (blocked_wording: "Any implication that comparators share this accounting guarantee")
concise_issue: The manuscript asserts all seven optimizers are charged exactly the same MaxFES; 1,845 released comparator runs are charged less, under a target-error stopping rule only AGSK and APGSK implement, and the asymmetry is nowhere disclosed.
exact_evidence_or_observation: Census of the 21 released per_run.csv files: CEC2017 agsk 404/5916 and apgsk 338/5916 (D10 325, D30 13); CEC2013 agsk 558/4284 and apgsk 545/4284 rows carry termination=target_error_reached with nfes<MaxFES (AGSK CEC2017 D10 minimum nfes = 44,497 of 100,000). All other optimizers: 0. Code: agsk.py:348-355 and apgsk.py:234 break on best_fitness-optimum<target_error and force error=0.0; gsk.py/fdb_agsk.py/atmals_gsk.py/egsk.py/dt_gsk.py have no such branch. grep for "target_error_reached|early stop|stopping rule" over papers/sections/*.tex, papers/main.tex, papers/supplementary.tex returns zero hits.
root_cause: Two of seven ports are faithful to the CEC target-error stop of their reference implementations; the other five are not. The protocol table records only the MaxFES cap and the prose generalised "same cap" to "same charge".
scientific_or_editorial_justification: Stage 8 requires "identical boundary, missingness, failure, and stopping rules" and "complete disclosure of deviations". A fairness assertion that the released data falsifies is worse than the deviation it conceals.
impact_on_validity_or_acceptance: No reported statistic changes — the stop threshold (1e-8) equals the reporting floor, error is recorded as 0 either way, and the checkpoint logs are complete (400/400 AGSK+APGSK files, 0 ragged, 0 blank), so the convergence aggregation is unaffected. The risk is credibility: the claim is falsifiable in one sort of the shipped per_run.csv.
required_correction: Replace the sentence with an accurate one naming the two optimizers, the 1,845 affected runs, and the neutrality argument (threshold == reporting floor; complete checkpoint logs). Add a "Stopping rule" row to Table tab:protocol.
acceptable_alternatives: A footnote in sec:exp:settings plus a protocol-table row, provided the false sentence is removed.
additional_evidence_needed: None. Optionally MX-03 (recompute the four affected D10/D30 panels with the early-stopped runs excluded) as a one-line confirmation.
dependencies: S8-08 (regenerate the governance early-stop census against rel-2026-07-20-67d9345f9 before quoting a count).
expected_improvement: Converts a falsifiable claim into a verified, self-auditing disclosure; strengthens rather than weakens the fairness narrative.
post_revision_verification: Re-run the termination census over the release and confirm the manuscript's stated counts match exactly; confirm no caption or table still asserts a uniform MaxFES charge.
status: open
```

### Ticket S8-02

```text
ticket_id: S8-02
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Major
priority: P1
confidence: Confirmed
issue_type: method
manuscript_location: papers/sections/proposed_algorithm.tex:669 and Table tab:panel rows AGSK/APGSK/FDB-AGSK (proposed_algorithm.tex:692-696); papers/sections/performance.tex:100-101
claim_id_or_artifact_id: T-PANEL (tab:panel); papers/governance/comparability_audit.md:28 ("Transparent parameter-tuning effort", verdict PASS)
concise_issue: The panel table attributes "published reference constants" to AGSK, APGSK and FDB-AGSK while citing their originating papers; all three publish dimension-scaled initial populations (20*D, 200*D, 40*D) and all three were run at a flat NP_init=100 at every dimension. The deviation is undisclosed and its real provenance (jawad2024egsk Table 3) is uncited.
exact_evidence_or_observation: reference_papers/mohamed2020agsk.pdf p.3 "The initial population size (NP) were set to 20 * D"; reference_papers/apgsk2021.pdf p.4 "(200 * D) for D = 10, 15 and 20"; reference_papers/fdbagsk2023.pdf p.10 Eq.(62) "popsize_init = 40 * n, popsize_min = 12". Run configuration: every comparator run_config.json has optimizer_options {} with NP_init 100 / min_pop_size 12; runner fallback src/gsk_family/runners/run_experiment.py:284-290 returns 100; port defaults agsk.py:209-210, apgsk.py:73-74, fdb_agsk.py:204-205. DT-GSK runs NP_init=5*D (_dt_core.py:149-152). Precedent for NP=100: reference_papers/jawad2024egsk.pdf Table 3 p.8 sets AGSK/APGSK/FDB-AGSK at NP=100, NP_min=12 for CEC2017 at D=10/30/50/100. The manuscript's own related_work.tex:60-64 credits APGSK with "a much larger initial population".
root_cause: A necessary transposition (APGSK's 200*D is undefined and impractical at CEC2017 D=100) was implemented as a silent default rather than as a declared, cited protocol decision.
scientific_or_editorial_justification: Stage 8 requires "correct and current-enough method version", "authoritative implementation provenance" and "comparable parameter-tuning effort". Attributing a constant to a paper that specifies a different one is a traceability failure of the class §5.5 calibrates as Major.
impact_on_validity_or_acceptance: Direction unbounded by present evidence. At D>=30 DT-GSK carries 1.5-5x the comparators' population while three comparators lose their published dimension scaling, in the tiers holding the first-place claims; at D=10 the asymmetry inverts (DT-GSK NP=50 vs 100). A GSK-family reviewer will know AGSK's 20*D immediately.
required_correction: (a) Rewrite the three tab:panel cells and performance.tex:100-101 to state the normalisation and cite jawad2024egsk Table 3 as its source. (b) Add a short sec:exp:settings paragraph giving the published values, the transposition problem, the precedent, and an explicit statement that the effect on standings is unbounded. (c) Correct comparability_audit.md:28 and re-adjudicate its PASS.
acceptable_alternatives: If the authors prefer, run MX-02 on one dimension and report it — but disclosure alone is sufficient for submission.
additional_evidence_needed: None for the correction. MX-02 for a bound.
dependencies: none
expected_improvement: Removes a false provenance statement and converts an undisclosed deviation into a cited, defensible protocol decision.
post_revision_verification: Confirm no manuscript surface still attributes NP=100 to mohamed2020agsk/apgsk2021/fdbagsk2023; confirm the governance row is corrected and re-signed.
status: open
```

### Ticket S8-03

```text
ticket_id: S8-03
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Major
priority: P1
confidence: Confirmed
issue_type: method
manuscript_location: papers/sections/performance.tex:32-39; papers/sections/proposed_algorithm.tex:669-674; papers/supplementary.tex:1766-1773
claim_id_or_artifact_id: LM-04 (eGSK provenance / comparability)
concise_issue: The eGSK port substitutes SciPy-SLSQP for the published fmincon SQP polish. The manuscript bounds only runtime and environment comparability; the substituted solver consumes up to 16.6% of eGSK's total evaluation budget, so performance comparability is also affected and is nowhere bounded.
exact_evidence_or_observation: src/gsk_family/optimizers/egsk.py:149-212 (_egsk_ip_refine; SLSQP; budget ceil(2e-3*MaxFES) per call, charged at :211), invoked in the late-stage branch at :313,320-324. Read-only instrumentation on real CEC2017 cells (scratchpad/egsk_polish_share.py) measured polish evaluations as a share of MaxFES: D10 F1 0.0%; F5 2.6%; F12 4.9-6.1%; F26 16.6% (16,600 of 100,000). D30 F1 0-2.3%; F5 6.0-6.1%; F12 0.4-1.2%; F26 7.4-11.0% (33,100 of 300,000). eGSK is the only comparator that outranks DT-GSK anywhere (CEC2017 D30 2.29 vs 2.50; CEC2011 2.52 vs 3.36 with p_Holm=4.2e-2) and the two are never Nemenyi-separable on CEC2017.
root_cause: MATLAB fmincon is unavailable in the Python harness; the substitution is unavoidable and honestly disclosed, but the disclosure scope was set to runtime only.
scientific_or_editorial_justification: §10.13 names "unfair eGSK provenance or solver comparison" as a high-probability rejection risk. Stage 8 requires "fair hardware, language, solver, and parallelism interpretation" and "complete disclosure of deviations".
impact_on_validity_or_acceptance: The comparison is class B, not A. The sign of the bias is unknown and it lands on both of the paper's adverse headline cells and on its non-separability statement. A reviewer will ask "is eGSK weaker here than in its own paper because of your solver?" and the package currently has no answer.
required_correction: Widen the disclosure to performance comparability, state the measured budget share (up to ~17% on composition functions) and that its sign is unknown; classify DT-GSK vs eGSK as "comparable with verified imported evidence" and attach that qualification wherever an eGSK cell is quoted.
acceptable_alternatives: Run MX-01 and report the sensitivity instead of the caveat.
additional_evidence_needed: MX-01 (polish-disabled and/or alternative-solver eGSK contrast on one dimension) for a quantitative bound.
dependencies: none
expected_improvement: Converts an unquantified provenance caveat into a bounded, reviewer-answerable one and pre-empts the single most likely reviewer objection.
post_revision_verification: Confirm the disclosure names performance (not only runtime) and carries a number; confirm the class-B qualification appears at the eGSK cells.
status: open
```

### Ticket S8-04

```text
ticket_id: S8-04
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Major
priority: P2
confidence: Confirmed
issue_type: reproducibility
manuscript_location: papers/supplementary.tex:1199-1201 ("one code base, one protocol and one harness"); papers/sections/performance.tex:155-158 (comparator-kernel probe gap); supplementary.tex §"Limitations in Full", sixth item
claim_id_or_artifact_id: LM-03; comparability_audit.md (single-host row)
concise_issue: The CEC2017 panel was produced at seven different producer commits over ten days, and the project's own RT-001 record documents that re-running the six comparators under a later commit produced 3,772 scientific-column differences. Neither fact reaches the manuscript.
exact_evidence_or_observation: environment.json git_commit per cell, CEC2017: gsk 31c5a04c4 (07-08), agsk f94817cc4 (07-08), apgsk 20cfed0ac (07-08), fdb-agsk 19f32fb83 (07-09), atmals-gsk 7483cac2e (07-09), egsk c35c26de7 (07-09), dt-gsk 251fc8cb8 (07-18). papers/governance/remediation_2026_07_18/ticket_status.csv, RT-001.residual_work: "Option 2 ... FAILED the determinism gate: 3,772 scientific-column diffs -- the 2026-07-08 comparator evidence (commit 31c5a04c4) is not bit-reproducible under current code ... worst for scipy/local-search atmals-gsk ~31% / egsk ~29%". Mitigating: all 21 cells share workers=15, platform, numba 0.64.0 and an identical suite FP probe hash 9d0adb66...; RT-001 also verifies DT-GSK's scientific columns were byte-identical across the M038 fix (only runtime_seconds moved).
root_cause: The campaign was executed incrementally over ten days; the comparator half was never re-executed after subsequent library/code movement, and the failed re-execution was recorded in governance rather than in the paper.
scientific_or_editorial_justification: An executed experiment whose outcome weakens a comparability claim must be reported alongside that claim (loss-visibility parity, §10.7). "One code base, one protocol and one harness" overstates a panel built from seven commits.
impact_on_validity_or_acceptance: Does not invalidate any number — each algorithm's cells are internally consistent and the evaluator was byte-identical panel-wide — but the comparator half of the release is not re-derivable from the current code, which a reproducibility-minded reviewer will discover and which the paper currently under-states.
required_correction: Add a limitations sentence recording (a) production across seven producer commits over ten days, (b) the failed re-execution and its ~29-31% cell-difference magnitude for the two local-search comparators, (c) the mitigations (identical evaluator hash, within-algorithm single-commit production, DT-GSK scientific invariance). Soften "one code base" to "one repository, one evaluator, and one harness".
acceptable_alternatives: A one-line change-request footnote (the §10.7-sanctioned disclosure form) plus the softened phrasing.
additional_evidence_needed: None; MX-07 would upgrade the disclosure to a bound.
dependencies: F-11 (the governing prompt's stale RT-001 description would otherwise mask this)
expected_improvement: Aligns the reproducibility narrative with what the project actually measured; removes an overstatement that the release contradicts.
post_revision_verification: Confirm the limitation is present in the rendered supplement and that no surface still claims a single code base for the panel.
status: open
```

### Ticket S8-05

```text
ticket_id: S8-05
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/governance/seed_and_pairing_audit.md §4 basis 3 and its per-comparator PAIRED table; benchmarks/cec_reference_results/*/dt-gsk/run_config.json ("initial_population_policy")
claim_id_or_artifact_id: PR-06 (fair-start protocol and the documented self-init exception)
concise_issue: The governance pairing audit certifies pairing validity partly on "run r of every optimizer starts from the same initial population", which is false for DT-GSK; the released DT-GSK run_config.json repeats the same false policy string.
exact_evidence_or_observation: seed_and_pairing_audit.md §4 item 3 verbatim: "run r of every optimizer starts from the same initial population on the same instance." Contradicted by src/gsk_family/optimizers/dt_gsk.py:14-18 ("does not consume the runner's fair-start initial_population"), by papers/sections/performance.tex:117-124 and proposed_algorithm.tex:788-793. The policy string is hard-coded for all optimizers at src/gsk_family/runners/run_experiment.py:972.
root_cause: The audit was written against the runner's static metadata string rather than against the optimizer's behaviour; the string is not conditioned on the exception.
scientific_or_editorial_justification: Stage 8 requires "valid pairing when paired tests are used" and "compatible initialization and random-seed policy". A gate that passes on a premise the manuscript disclaims has not been evaluated.
impact_on_validity_or_acceptance: No reported inference is affected: the inferential unit is the function (29/28/22 paired per-function means), Friedman blocks are functions, BCa resamples fixed per-function midranks, and the run-level A12 is unpaired. Initialisation differences are absorbed by the 51-run mean. The defect is in the audit and the released metadata, not in the statistics.
required_correction: Correct §4 basis 3 to "common seed, problem instance and run index, with DT-GSK's documented self-init exception", re-state the pairing verdict on function-level grounds, and record an erratum for the DT-GSK run_config.json policy string (a code fix would require a new release, which the standing constraint forbids this cycle).
acceptable_alternatives: Erratum row in the release README naming the DT-GSK cells whose policy string is inaccurate.
additional_evidence_needed: none
dependencies: none
expected_improvement: The pairing gate rests on a true premise; the release metadata stops contradicting the manuscript.
post_revision_verification: Re-read §4 and confirm the basis matches dt_gsk.py and the manuscript; confirm the erratum exists.
status: open
```

### Ticket S8-06

```text
ticket_id: S8-06
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: experimental-design
manuscript_location: papers/supplementary.tex:1157-1161 (Configuration Selection and Development Protocol)
claim_id_or_artifact_id: R6-T03 (development-suite / selection-exposure disclosure); RS-01 (CEC2017 overall rank)
concise_issue: The selection exposure is disclosed qualitatively ("several full-panel candidate configurations") with no count, no selection cells, and no selection criterion, so the optimistic-selection bias on the headline result cannot be bounded by any reader.
exact_evidence_or_observation: supplementary.tex:1157-1161 verbatim: "Before the final configuration was promoted, several full-panel candidate configurations were compared against the family panel during development; this selection exposure is disclosed here as an author-attested development-history note (the intermediate candidates are not part of the immutable evidence release)". No count, cells, or criterion appears anywhere in papers/ or papers/governance/.
root_cause: The intermediate candidates were deliberately excluded from the immutable release, so the disclosure fell back to a qualitative attestation.
scientific_or_editorial_justification: Stage 8 requires that confirmatory and exploratory analyses be separated and that sample/task counts be justified. A model-selection search scored on the same panel and the same statistic as the headline result is a multiplicity the frozen plan does not control.
impact_on_validity_or_acceptance: The headline (2.48 overall CEC2017 Friedman rank) is a selected estimate of unknown optimism. The held-out CEC2011/CEC2013 results provide the right mitigation and are mixed rather than uniformly worse, which materially limits the concern — but that argument is only in the supplement and the exposure magnitude is still unstated.
required_correction: State the number of candidate configurations, the cells they were scored on, and the selection statistic; if the count cannot be attested, say so explicitly. Additionally, promote one sentence of the held-out-mixed-outcome argument (supplementary.tex:1162-1169) into sec:exp:settings.
acceptable_alternatives: An explicit "the exact number of candidates was not logged" attestation is acceptable and auditable; a vague quantifier is not.
additional_evidence_needed: MX-04 (held-out-only re-statement, or a nested-selection estimate) for an empirical bound.
dependencies: none
expected_improvement: Makes the selection exposure quantifiable; moves the paper's strongest defence of its headline into the main text.
post_revision_verification: Confirm S5 states a count (or an explicit non-availability) plus cells and criterion; confirm the main text carries the held-out argument.
status: open
```

### Ticket S8-07

```text
ticket_id: S8-07
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/supplementary.tex:1754-1762 (strict-source rule, APGSK exception)
claim_id_or_artifact_id: APGSK-GAP; PR-04
concise_issue: The supplement states in the present tense that the APGSK CEC2017 D10/30/50 per-run source "is" the per-generation logs because the sidecar was overwritten; the shipped release now contains a complete 5,916-row APGSK per_run.csv covering all four dimensions.
exact_evidence_or_observation: benchmarks/cec_reference_results/cec2017/apgsk/per_run.csv has 5,916 rows across D=10/30/50/100 with non-zero runtime_seconds in every dimension; all 242 apgsk/cec2017 files verified against evidence_release_manifest.json (0 checksum mismatches, 0 missing), so the recovery was minted into rel-2026-07-20-67d9345f9 rather than edited in place (§10.3 not breached). The main text handles this correctly at performance.tex:134-139; the supplement's reproducibility appendix does not.
root_cause: The post-freeze recovery was propagated to the main-text footnote but not to the supplement's strict-source paragraph.
scientific_or_editorial_justification: §10.7 recovery-versus-comparability disposition; §5.5 calibrates stale post-recovery statements as Major when they assert non-existence. Here the statement asserts a source rather than non-existence, hence Moderate.
impact_on_validity_or_acceptance: No number changes; the frozen function-level basis is correctly retained. A reviewer opening the release finds a complete APGSK per-run file contradicting the supplement.
required_correction: Past-tense the sentence and add the recovery: "...at analysis freeze the per-run sidecar covered D=100 only, so the frozen analysis read the final-checkpoint column of the per-generation logs for D=10/30/50; those per-run records were subsequently recovered, are included in the accompanying release, and reproduce the frozen summaries exactly."
acceptable_alternatives: A cross-reference to the main-text footnote, provided the present tense is removed.
additional_evidence_needed: none
dependencies: S8-08
expected_improvement: Supplement matches the shipped release; the recovery is disclosed consistently in both documents.
post_revision_verification: Re-read the rendered supplement paragraph against the release directory listing.
status: open
```

### Ticket S8-08

```text
ticket_id: S8-08
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: evidence
manuscript_location: papers/governance/benchmark_protocol_audit.md:134, 195, 203, 231, 234; papers/governance/experiment_matrix.csv (all rows)
claim_id_or_artifact_id: A2-001 / A2-029 / A2-032 anomaly rows; PR-04
concise_issue: The governance early-stop census totals 1,507 runs and reconciles against the pre-recovery experiment matrix; the shipped release contains 1,845, the extra 338 being CEC2017/APGSK early stops in the recovered per-run rows. The experiment matrix is also still bound to a placeholder release id.
exact_evidence_or_observation: benchmark_protocol_audit.md:134 "(69306 max_evaluations + 1507 target_error_reached = 70813) reconcile exactly"; anomaly rows enumerate 404 + 558 + 545 = 1507 and contain no cec2017/apgsk row. Release census: cec2017/apgsk 338 early stops (D10 325, D30 13), total 1,845. papers/governance/experiment_matrix.csv holds only 1,479 apgsk/cec2017 rows (D100-only) and carries evidence_release_id = "PENDING-RELEASE-ID(phase2-evidence_release_manifest)" in every one of its 70,813 rows.
root_cause: Both artifacts predate the APGSK post-freeze recovery and the current release mint.
scientific_or_editorial_justification: The audit is the evidentiary base for the budget-equality statement corrected in S8-01; a corrected manuscript sentence must not quote a stale count.
impact_on_validity_or_acceptance: Governance-internal, not reader-facing; no reported number depends on it. But it is a prerequisite for S8-01's fix.
required_correction: Re-run the termination census and the anomaly register against rel-2026-07-20-67d9345f9, add the cec2017/apgsk row, correct the 1,507 total, and resolve the placeholder release id in experiment_matrix.csv.
acceptable_alternatives: An addendum block in benchmark_protocol_audit.md recording the post-recovery delta, provided S8-01's manuscript text quotes the corrected figure.
additional_evidence_needed: none
dependencies: blocks S8-01 (count) and S8-07 (wording)
expected_improvement: The governance base matches the shipped release; the corrected manuscript sentence is citable.
post_revision_verification: Recompute the census; confirm 1,845 (or the then-current figure) appears in both the audit and the manuscript.
status: open
```

### Ticket S8-09

```text
ticket_id: S8-09
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Major
priority: P2
confidence: Confirmed
issue_type: production
manuscript_location: papers/cover_letter.md:22 (compare papers/cover_letter.tex:55 and the rendered papers/cover_letter.pdf)
claim_id_or_artifact_id: R-09 (cover-letter byte-stability narrowing)
concise_issue: R-09 narrowed the cover letter's byte-stability claim to DT-GSK in its declared environment. The narrowing was applied to cover_letter.tex and the shipped PDF but not to cover_letter.md, which still asserts "a byte-stable, release-locked protocol" for the whole panel.
exact_evidence_or_observation: cover_letter.tex:55 and cover_letter.pdf: "evaluated under a release-locked protocol, with byte-stable determinism for DT-GSK in the declared supported environment." cover_letter.md:22: "evaluated under a byte-stable, release-locked protocol." The withdrawn claim is precisely the one falsified for the comparators by RT-001 (see S8-04).
root_cause: The remediation edited the LaTeX source only; the Markdown source was left in the tree as a superseded parallel copy.
scientific_or_editorial_justification: §10.12 requires one canonical semantic source; §5.5 calibrates an orphan/superseded source file carrying a stale claim as Major, because it can be submitted by accident. A cover letter .md is a plausible paste source for a submission portal.
impact_on_validity_or_acceptance: The shipped PDF is correct, so no submitted artifact currently carries the over-claim; the risk is that the wrong file is used at submission.
required_correction: Sync cover_letter.md to the .tex wording, or delete/quarantine it and record the removal in the freeze manifest.
acceptable_alternatives: Quarantine under an explicitly non-shipped path with a header noting supersession.
additional_evidence_needed: none
dependencies: none — but note this means R-09 is closed incompletely
expected_improvement: Eliminates a withdrawn over-claim from the package and restores single-source integrity for the cover letter.
post_revision_verification: Diff cover_letter.md against cover_letter.tex for every scientific sentence; confirm the freeze manifest reflects the change.
status: open
```

### Ticket S8-10

```text
ticket_id: S8-10
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Moderate
priority: P2
confidence: Confirmed
issue_type: claim-scope
manuscript_location: papers/sections/performance.tex:170-174
claim_id_or_artifact_id: R-14 probe (tests/regression/test_budget_crossing_semantics.py); MT-11
concise_issue: The manuscript says strict truncation "was verified to leave the returned solution, its fitness, and the charged budget bit-identical for all seven optimizers". The verification is one synthetic cell, and the far stronger structural guarantee that actually holds is not stated.
exact_evidence_or_observation: The probe runs sphere, D=10, NP=100, MaxFES=1050, single seed 20240620 (test_budget_crossing_semantics.py:40-45), with target_error=NaN at :109 ("never early-stop; consume the budget") which deliberately disables the F-01 asymmetry. Probe re-run: 14 passed in 4.23s. Independent reproduction of its measurement (scratchpad/overrun_probe.py): uncounted terminal rows gsk 50, agsk 8, apgsk 8, fdb-agsk 8, atmals-gsk 50, egsk 50, dt-gsk 0 — matching the LaTeX evidence comment at performance.tex:175-178 exactly. The structural guarantee: every port updates the incumbent only over the counted prefix via _scan_best(..., n_count=min(NP, max_nfes-nfes)) (gsk.py:191-198; agsk.py:317-325; apgsk.py:201-209; fdb_agsk.py:319-327; atmals_gsk.py:331-339; egsk.py:294-298), and the post-selection population update that sees the full batch is never read again because the while-guard fails immediately after.
root_cause: The prose describes the empirical probe and omits the invariant that makes the property universal.
scientific_or_editorial_justification: §15 forbids inferring correctness from a check narrower than the claim. Here the underlying property is in fact universal, so the fix strengthens the paper.
impact_on_validity_or_acceptance: The claim is true; the stated warrant is narrower than the claim. A reviewer who opens the probe finds one sphere cell behind an "all seven optimizers" statement.
required_correction: Rescope the sentence to cite the prefix-scan invariant as the guarantee and the probe as its exercise, e.g. "...guaranteed by construction: every port scans the incumbent only over the counted prefix, so uncounted rows cannot enter the returned solution, its fitness, or the trace; a regression probe exercises this for all seven optimizers." Place the F-01 stopping-rule disclosure adjacent to it.
acceptable_alternatives: Extend the probe to a second (non-sphere, higher-D) cell, though the invariant argument is stronger than more cells.
additional_evidence_needed: none
dependencies: S8-01 (adjacent disclosure)
expected_improvement: Upgrades an empirical claim about one cell to a structural guarantee about the panel.
post_revision_verification: Confirm the revised sentence names the invariant and that the probe reference is scoped as an exercise, not a campaign-wide proof.
status: open
```

### Ticket S8-11

```text
ticket_id: S8-11
review_stage: Stage 8
reviewer_role: R3 (T2-BENCH)
severity: Minor
priority: P3
confidence: Confirmed
issue_type: compliance
manuscript_location: papers/PAPER_REVIEW_PROMPT.md §10.7 final bullet (L3299); §1.5 preamble (L120); papers/supplementary.tex:1780 (non-rendered LaTeX comment)
claim_id_or_artifact_id: governing-prompt snapshot (§1.4 precedence)
concise_issue: The governing prompt's embedded snapshot is stale in this stage's area: it describes RT-001 as an in-progress comparator re-timing and the ledger as 73/80, both of which the repo contradicts.
exact_evidence_or_observation: §10.7 L3299 instructs the reviewer to treat the runtime cells as "in-progress" pending "re-timing all six comparators on one idle machine (scripts/retime_comparators.py)". Repo: ticket_status.csv RT-001 is closed_verified 2026-07-21, resolved by Decision 7 Option 3 (DT-GSK-only fallback) after Option 2 -- the exact remedy the prompt describes -- was executed and FAILED the determinism gate. The shipped tab:runtime (performance.tex:759-784) is DT-GSK-only and states "no cross-algorithm runtime comparison is made". §1.5 L120 says 73/80 and names seven open tickets; the ledger has 80 rows, all closed_verified or superseded_with_evidence. supplementary.tex:1780 comment still names "the primary release rel-2026-07-16-78f075cb0".
root_cause: The prompt snapshot is dated 2026-07-20 and predates the 2026-07-21/22 remediation.
scientific_or_editorial_justification: §1.4 precedence: current project state outranks the prompt's embedded snapshot. Recording the staleness prevents the next round from re-certifying a withdrawn remedy.
impact_on_validity_or_acceptance: None on the manuscript. Material for review governance: a reviewer following §10.7 literally would look for an in-progress comparator re-timing and miss that its failure is the substance of S8-04.
required_correction: Update §10.7's RT-001 bullet to record the Option-3 resolution and the Option-2 failure; update the §1.5 ledger counts; fix the stale supplement comment.
acceptable_alternatives: A dated errata block at the head of §1.5.
additional_evidence_needed: none
dependencies: S8-04
expected_improvement: Future rounds inherit an accurate snapshot and are pointed at the real residual risk.
status: open
```

---

## 8. Summary table

| ID | Sev | Pri | Conf | One line |
|---|---|---|---|---|
| S8-01 | Major | P1 | Confirmed | "Same MaxFES charge for all seven" is false — 1,845 AGSK/APGSK runs stop early under an undisclosed asymmetric stopping rule (endpoint-neutral, but falsifiable from the shipped data). |
| S8-02 | Major | P1 | Confirmed | "Published reference constants" is false for AGSK/APGSK/FDB-AGSK — published NP is 20·D / 200·D / 40·D, all run at flat 100; deviation undisclosed, real provenance (`jawad2024egsk` Tab. 3) uncited. |
| S8-03 | Major | P1 | Confirmed | eGSK's substituted SLSQP polish consumes up to 16.6 % of MaxFES; disclosure bounds runtime only, not performance, under the paper's most consequential comparison. |
| S8-04 | Major | P2 | Confirmed | Panel produced at seven producer commits; RT-001 records a failed comparator re-run with 3,772 scientific-column diffs (~29–31 % for eGSK/ATMALS) — neither disclosed. |
| S8-05 | Moderate | P2 | Confirmed | Pairing audit certifies "same initial population for every optimizer", which DT-GSK's self-init disclaims; released DT-GSK `run_config.json` repeats it. No inference affected. |
| S8-06 | Moderate | P2 | Confirmed | Selection exposure disclosed as "several candidate configurations" — no count, cells, or criterion, so the optimistic-selection bias is unbounded. |
| S8-07 | Moderate | P2 | Confirmed | Supplement's strict-source rule still says APGSK D≤50 per-run data comes from gen-logs; the shipped release now carries the full 5,916-row per-run file. |
| S8-08 | Moderate | P2 | Confirmed | Governance early-stop census (1,507) is 338 short of the shipped release (1,845); `experiment_matrix.csv` still carries a placeholder release id. |
| S8-09 | Major | P2 | Confirmed | `cover_letter.md` retains the pre-R-09 "byte-stable protocol" over-claim that R-09 removed from the `.tex`/PDF — R-09 closed incompletely. |
| S8-10 | Moderate | P2 | Confirmed | R-14 probe passes (14/14) and its numbers reproduce, but the manuscript's "verified for all seven optimizers" rests on one sphere cell; the universal prefix-scan invariant is the stronger, unstated warrant. |
| S8-11 | Minor | P3 | Confirmed | Governing prompt §10.7/§1.5 stale: RT-001 described as in-progress, ledger as 73/80; repo shows RT-001 closed via a different remedy after the described one failed. |

Remediations verified **correctly closed** from this seat: **R-05** (budget-crossing semantics — disclosure accurate, figures reproduce), **R-14** (probe exists, passes, measures what it claims — see S8-10 for a scope-of-wording refinement only). Remediation verified **closed incompletely**: **R-09** (see S8-09).
