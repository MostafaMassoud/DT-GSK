# Evidence card: apgsk_imode2024

## Verified bibliographic identity
- Title: "Optimizing switch placement and status for sustainable grid operation and effective distributed generation integration using the APGSK-IMODE algorithm"
- Source authors (bib given names corrected from source): Mehrdad Ahmadi Kamarposhti, Hassan Shokouhandeh, Yeonwoo Lee, Sun-Kyoung Kang, Ilhami Colak, El Manaa Barhoumi
- Venue: International Journal of Low-Carbon Technologies 19 (2024) 2676–2686; **source DOI 10.1093/ijlct/ctae231** (printed p. 2676) — the bib's DOI 10.1093/ijlct/ctae157 is wrong.
- Identity status (reference_inventory.csv): **minor_metadata_mismatch, admissible** — identity certain by exact title and journal header; bib author list heavily garbled and DOI wrong (corrections recorded in the inventory notes).
- 11-page PDF; **printed page N = local PDF page N+2675** (PDF p. 1 = printed p. 2676). Locators use printed pages.

## Research question and context
In radial electricity distribution grids, which switch locations and open/closed statuses (with and without distributed generation, DG) best improve the voltage profile and reliability (ENS, outage time)? The paper applies the hybrid APGSK-IMODE metaheuristic and compares it with DE and PSO (Abstract, p. 2676; Sect. 1, pp. 2676–2677).

## Method
- **Application paper, not an algorithm paper.** APGSK-IMODE is described only qualitatively (Sect. 4, pp. 2679–2680): a hybrid combining adaptive parameter adjustment, gaining-sharing knowledge-based mechanisms, and improved multi-operator differential evolution; the section then reviews generic DE mutation/crossover (Eqs. (23)–(24), p. 2680, from Storn & Price [24]). **No APGSK-IMODE update equations, pseudocode, or hyperparameters are given**; the algorithm is credited to Mohamed et al., CEC 2021 (reference [25], p. 2686). Table 2 (p. 2682) lists a parameter-header row for APGSK-IMODE with no printed values.
- Optimization model: weighted objective f = alpha·f1 + beta·f2 with f1 = system unreliability (MTTF/MTTR-based, Eq. (13)) and f2 = sum of |v_i − v_nom| voltage deviations (Eq. (14)) (Sect. 3, p. 2678); constraints: line thermal limits (Eq. (15)), DG active power 0–3 MW (Eq. (16)), reactive 0–2 MW (Eq. (17)), max 3 DGs (Eq. (18)), bus-voltage bounds (Eq. (19)) (pp. 2678–2679); scenario 3 weights omega1 = 1, omega2 = 1000 (p. 2683).
- Reliability indices defined: ENS (Eq. (1)), ECOST (Eq. (3)), SAIFI/CAIDI/ASAI/ASUI/AENS (Eqs. (4)–(11)) (Sect. 2, pp. 2677–2678). Load flow: forward–backward sweep (Sect. 3.1, p. 2679). Reliability computed via minimum cut sets, not Monte Carlo (Sect. 5, p. 2680).

## Experimental scope
- Single test system: IEEE 33-bus radial feeder, 11 kV, 11 switches (all initially closed), 3 DGs of 560/525/585 kVA at buses 31–33 (Sect. 5, p. 2681; single-line diagram Fig. 3, p. 2681; feeder equipment data Table 1, p. 2681).
- Baseline: unreliability 9.2926e-4, outage 8.14 h/yr, ENS 29,536.16 kWh/yr (p. 2681).
- Three scenarios: (1) voltage-profile improvement, (2) reliability maximization, (3) both simultaneously; each with and without DG (Sect. 5, pp. 2681–2684).
- Comparators: DE and PSO (population 100, 50 iterations each, Table 2, p. 2682). **No run counts, no variance/std, no statistical tests reported** — single reported solution per algorithm/scenario.

## Conservative findings
- Scenario 1 (voltage, Table 3, p. 2682): APGSK-IMODE voltage-function value 0.5732 with DG (vs DE 0.5820, PSO 0.6023) and 1.0603 without DG (vs DE 1.0619, PSO 1.077); ENS 13,421.32 kWh with DG.
- Scenario 2 (reliability, Table 5, p. 2683): APGSK-IMODE unreliability 4.83e-4, outage 4.30 h/yr, ENS 8019.21 kWh with DG (vs DE 4.95e-4 / 4.34 h / 8059.38; PSO 6.40e-4 / 5.61 h / 10,417.77). ENS reduced to under one third of the baseline (p. 2684).
- Scenario 3 (combined, Table 7, p. 2684): APGSK-IMODE objective 1.37 with DG (vs DE 1.39, PSO 1.48); 1.918 without DG.
- Reliability-index tables per scenario: Tables 4, 6, 8 (pp. 2683–2684). DG integration itself improves both voltage profile and reliability in every scenario (Conclusion, p. 2686).
- Margins over DE are small (e.g., 0.5732 vs 0.5820; 4.83e-4 vs 4.95e-4); the paper claims superior "accuracy and effectiveness" (Conclusion, p. 2686) without uncertainty quantification.

## Limitations (observed; none author-stated)
- No APGSK-IMODE algorithmic detail or parameter values (Table 2's APGSK-IMODE row is empty); the algorithm must be cited from Mohamed et al. 2021 (their ref. [25]), not from this paper.
- Single 33-bus system; no run statistics, no significance tests, no convergence data for APGSK-IMODE.
- Production defects in the published version: Fig. 6 contains a "PLEASE PROVIDE PANEL 6B" placeholder (p. 2684); scenario-2 text swaps "with/without DG" labels relative to Table 5 in places (p. 2683); SAIFI/SAIDI table row-block labels in Tables 4 vs 6 are inconsistently ordered ("Without DG"/"With DG" blocks carry identical base rows).
- Weight coefficients (alpha, beta; omega2 = 1000) are asserted, not justified.

## Exact usable locators (claim -> locator)
| Claim the DT-GSK manuscript may need | Locator (printed pages) |
|---|---|
| APGSK-IMODE applied to a power-distribution switch-placement problem | Abstract, p. 2676; Sect. 4, pp. 2679–2680 |
| Qualitative description of APGSK-IMODE as APGSK + IMODE hybrid | Sect. 4, p. 2679 (first paragraph) |
| Attribution of APGSK-IMODE to Mohamed et al. CEC 2021 | Ref. [25], p. 2686 |
| Objective model (f = alpha·f1 + beta·f2) and constraints | Eqs. (12)–(19), pp. 2678–2679 |
| 33-bus system + baseline reliability figures | Sect. 5, p. 2681 |
| Scenario 1 results (voltage 0.5732 with DG, best of 3) | Table 3, p. 2682 |
| Scenario 2 results (unreliability 4.83e-4; ENS 8019.21 kWh) | Table 5, p. 2683 |
| Scenario 3 results (objective 1.37 with DG) | Table 7, p. 2684 |
| Overall conclusion (APGSK-IMODE outperformed DE and PSO) | Sect. 6, p. 2686 |

## Supported uses in the DT-GSK manuscript
- Related-work breadth only: evidence that the APGSK-IMODE hybrid (a GSK-family CEC-2021 winner) has been applied to a real-world-style power-distribution optimization problem and reported better objective values than DE and PSO on an IEEE 33-bus case.
- Nothing more: the paper contains no reusable algorithmic specification of APGSK-IMODE.

## Unsupported / prohibited overextensions
- Do NOT cite this paper for APGSK-IMODE's mechanism, equations, or parameters — it does not contain them (and the paper is not by the algorithm's authors).
- Do NOT describe the DE/PSO comparison as statistically supported (no run counts, no variance, no tests).
- Do NOT generalize beyond the single 33-bus scenario set.
- Do NOT copy the bib's author list or DOI — both are wrong; use the source-corrected metadata above (inventory notes).
- Does not discuss DT-GSK.

## Role in DT-GSK framing (Appendix B)
Appendix B.2: related-work breadth only. Suitable at most for one clause noting APGSK-IMODE's application to grid switch-placement optimization.

## Verification quotations
- "The APGSK-IMODE is a hybrid optimization algorithm that combines adaptive parameter adjustment, gaining-sharing knowledge-based mechanisms, and improved multioperator differential evolution." (Sect. 4, p. 2679)
- "a comparative analysis of the optimization algorithms revealed that the APGSK-IMODE algorithm outperformed the other two algorithms in terms of accuracy and effectiveness." (Sect. 6, p. 2686)
