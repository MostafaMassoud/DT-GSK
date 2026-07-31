# Evidence card — fdbagsk2023

Group: family-panel (Appendix B.1 — Foundation and GSK family)
Prepared: 2026-07-10, Phase 1 tasks 4–5. Read: method Sect. 3 (pp. 3127–3132), settings Sect. 4 (p. 3133), benchmark results Sect. 5.1 (pp. 3133–3141), conclusions Sect. 6 (pp. 3155–3156); ORPF model skimmed (Sect. 2).

## 1. Verified bibliographic identity

- Title: "Improved adaptive gaining-sharing knowledge algorithm with FDB-based guiding mechanism for optimization of optimal reactive power flow problem"
- Authors: Hüseyin Bakır, Serhat Duman, Ugur Guvenc, Hamdi Tolga Kahraman
- Venue: Electrical Engineering (2023) 105:3121–3160; DOI 10.1007/s00202-023-01803-9 (printed on p. 3121).
- Identity status in `reference_inventory.csv`: **verified / readable / admissible**.
- Local file: `reference_papers/fdbagsk2023.pdf`, 41 PDF pages.
- **Locator convention: printed journal pages 3121–3160 (PDF page N = printed page 3120+N) plus section/equation/table numbers.**

## 2. Research question and context

Can the AGSK algorithm's premature convergence and weak exploration be fixed by redesigning its guide selection with the **fitness–distance balance (FDB)** method, and is the resulting FDBAGSK effective both on CEC benchmarks and on the AC/DC optimal reactive power flow (ORPF) problem with distributed generation and HVDC systems? (Sects. 1 and 3, pp. 3122–3127.)

## 3. Method

- **FDB selection** (Sect. 3.1, pp. 3127–3128, Eqs. 52–56): score S_x[i] = w·normFV[i] + (1−w)·normD[i] with **w = 0.5**; normD from Euclidean distance to x_best; guides chosen by highest score (x_FDB, greedy) or FDB-roulette (x_RFDB). FDB is Kahraman et al.'s selection method (their ref. [37]).
- **AGSK recap** (Sect. 3.2, pp. 3128–3131): junior/senior stages (Algorithms 2–3, p. 3129); dimension split Eq. (57); K takes random value in [0,1] for half the population and integer in [1,20] for the other half (p. 3128); senior partition p = 0.1 (p. 3129); adaptive (kf, kr) pool kf = [0.1 1 0.5 1], kr = [0.2 0.1 0.9 0.9] with Kw_P updated after FEs > 0.1·maxFEs (Algorithm 4, Eqs. 59–61, p. 3130); **linear** population reduction Eq. (62) with popsize_init = 40×n and popsize_min = 12 (pp. 3130–3131). (Note: this paper's AGSK description has minor deviations from mohamed2020agsk — e.g., popsize_init = 40×n and a linear-reduction formula; cite mohamed2020agsk for canonical AGSK.)
- **FDBAGSK variants** (Sect. 3.3, Table 1, p. 3131, Eqs. 63–72): five cases replacing guide vectors with FDB-selected ones — **Case-1: senior phase, x_FDB replaces x_m**; Case-2: senior, x_FDB replaces x_pworst; Case-3/4/5: junior-phase replacements using x_RFDB and/or x_FDB. Pseudo-code Algorithm 5 (pp. 3131–3132).

## 4. Experimental scope

- **Benchmarks: 39 functions = 29 (CEC 2017) + 10 (CEC 2020)** (Table 2, p. 3134); problem types unimodal/multimodal/hybrid/composition; **D = 30, 50, 100**; **51 independent runs**; **maxFEs = 1000×Dimension** (Sect. 4, p. 3133) — NOTE: this is 10× smaller than the CEC-standard 10,000×D budget.
- Statistics: nonparametric pairwise Wilcoxon (5% level) and Friedman tests; 39×6×51×3 = 35,802 data items analyzed (Sect. 5.1.1, p. 3133). MATLAB R2016a, i5-1135G7, 16 GB RAM (p. 3133).
- Application: AC/DC-ORPF with DGs + HVDC on modified IEEE 30- and 57-bus systems; objectives = active power loss, voltage deviation, L-index voltage stability (Sect. 2, pp. 3123–3126; 12 test cases, Sects. 5.2, pp. 3141 ff.).

## 5. Conservative findings

- **Friedman ranking of AGSK vs five FDBAGSK variants (Table 3, p. 3134): every FDB variant outranks AGSK in all six experiment blocks; Case-1 best (mean rank 2.83) vs AGSK worst (4.26).**
- **Wilcoxon pairwise (Table 4, p. 3135)**: e.g., Case-1 vs AGSK 20/9/0 (win/tie/loss) on CEC2017 D = 30; 17/11/1 at D = 50; 18/5/6 at D = 100; 8/2/0 on CEC2020 D = 30 and 50. FDB variants better than AGSK across all dimensions/suites.
- Function-type Friedman breakdown (Table 5, p. 3135): AGSK worst-ranked in unimodal, multimodal, hybrid, composition groups; Case-1 strongest overall, especially multimodal (e.g., 2.06–2.20 vs AGSK 4.41–4.48 on CEC2017 multimodal).
- Error statistics mean(SD) per function: Table 6 (pp. 3136 ff.). Box plots Figs. 4–5; convergence curves Fig. 6 (p. 3142): authors read AGSK as premature-converging; FDB variants more stable.
- **Algorithm complexity** (Sect. 5.1.3, Table 7/Fig. 7, p. 3141): FDBAGSK complexity "very close" to AGSK in all dimensions; FDB adds only slight overhead.
- ORPF: FDBAGSK reported best results against literature algorithms in the 12 AC/DC-ORPF cases (Sect. 5.2 tables; conclusion p. 3156).
- Conclusions (Sect. 6, pp. 3155–3156): FDBAGSK more stable/robust than competitors; source code at MathWorks File Exchange 129154 (p. 3156).

## 6. Limitations

- **Budget nonstandard: maxFEs = 1000×D** (p. 3133), not the CEC-official 10,000×D. FDBAGSK-vs-AGSK results are internally comparable but NOT directly comparable to family papers run at 10,000×D (mohamed2020gaining, jawad2024egsk, alfadli2025atmals).
- Benchmark comparison is only against AGSK (and the five in-house variants) — no GSK, APGSK, eGSK, or non-family algorithms on the suite side.
- The premature-convergence diagnosis of AGSK is interpretive (box plots/convergence curves at reduced budget).
- No D = 10 experiments; CEC2020 10 functions treated as "composition" block in Table 2's layout.
- ORPF results are power-system-specific; not evidence for general benchmark superiority.

## 7. Exact usable locators (claim → locator)

| Claim | Locator |
|---|---|
| FDB score definition, w = 0.5, normalization | Sect. 3.1, Eqs. (52)–(56), pp. 3127–3128 |
| Motivation: AGSK premature convergence / weak exploration | Sect. 3 intro, p. 3127; Sect. 3.3, p. 3131 |
| AGSK description as used here (pool, Kw_P, Eq. 57, K regimes) | Sect. 3.2, pp. 3128–3130, Algorithm 4 |
| Population reduction with popsize_init = 40×n, popsize_min = 12 | Eq. (62), pp. 3130–3131 |
| Five FDBAGSK variants; Case-1 = x_FDB replaces x_m in senior phase | Table 1 (Eqs. 63–72), p. 3131; Sect. 3.3 |
| Experimental protocol: 39 fns (CEC2017+CEC2020), D = 30/50/100, 51 runs, **maxFEs = 1000×D** | Sect. 4, p. 3133; Table 2, p. 3134 |
| Friedman: all FDB variants > AGSK; Case-1 best (2.83 vs 4.26) | Table 3, p. 3134 |
| Wilcoxon win/tie/loss counts vs AGSK | Table 4, p. 3135 |
| Function-type Friedman breakdown | Table 5, p. 3135 |
| Complexity ≈ AGSK (slight FDB overhead) | Sect. 5.1.3, Table 7, p. 3141 |
| ORPF scope (IEEE 30/57-bus, DG+HVDC, 3 objectives) | Sect. 2, pp. 3123–3126; Sect. 5.2 |
| Conclusions incl. code availability | Sect. 6, pp. 3155–3156 |

## 8. Supported uses

- Citing FDBAGSK (Case-1) as the fitness–distance-balance family baseline and describing its exact guide-replacement mechanism.
- Supporting the statement that FDB-based guide selection improved AGSK's exploration/balanced search on CEC2017+CEC2020 at D = 30/50/100 (51 runs, Friedman + Wilcoxon), **at a 1000×D budget**.
- Citing independent (non-Mohamed-group) evidence that AGSK exhibits premature convergence on multimodal/hybrid/composition problems (as this paper's diagnosis, at its budget).
- Noting jawad2024egsk and alfadli2025atmals adopt FDBAGSK **Case-1** as the representative variant (see those cards).

## 9. Unsupported / prohibited overextensions

- Do NOT compare FDBAGSK's error values numerically to family results computed at 10,000×D budgets — budgets differ by 10×.
- Do NOT claim FDBAGSK was compared to GSK, APGSK, or eGSK here — it was not (benchmark side compares AGSK only).
- Do NOT cite this paper's AGSK parameterization (popsize_init = 40×n, linear reduction) as the canonical AGSK — cite mohamed2020agsk for that.
- Do NOT use ORPF case results as general-purpose benchmark evidence.
- Do NOT claim D = 10 behavior — untested here.

## 10. Role in DT-GSK framing (Appendix B.1)

`fdbagsk2023` — FDB-AGSK and fitness-distance-balance family baseline: defines the FDBAGSK (Case-1) mechanism used in DT-GSK's family panel and provides third-party evidence of AGSK's exploration weakness.

## 11. Verification quotations (minimal)

- "For a fair comparison, all MHS algorithms use 1000*Dimension maximum function evaluations (maxFEs) as search process termination criteria." (Sect. 4, p. 3133)
- "the FDB-based algorithms outperformed the original AGSK in all experiments. Admittedly, among the FDBAGSK variants, Case-1 is the most successful." (Sect. 5.1.1, p. 3134)
- "In the senior gaining-sharing knowledge phase, xFDB is used instead of the xm vector" (Case-1, Table 1, p. 3131)
