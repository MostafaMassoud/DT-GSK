# Evidence card — navaneetha2022gskde

## 1. Verified bibliographic identity
- **Citation key:** `navaneetha2022gskde`
- **Title (on source):** "Multi-objective task scheduling in fog computing using improved gaining sharing knowledge based algorithm"
- **Authors (on source):** Malathy Navaneetha Krishnan; Revathi Thiyagarajan (Mepco Schlenk Engineering College, Sivakasi, India)
- **Venue/year (on source):** Concurrency and Computation: Practice and Experience 2022; 34(24): e7227; DOI 10.1002/cpe.7227 (p. 1)
- **Identity status (inventory):** `minor_metadata_mismatch` — identity certain; bib given-name errors: authors are **Malathy** Navaneetha Krishnan and **Revathi** Thiyagarajan (bib: "Mukila", "Ravichandran").
- **Source file:** `reference_papers/navaneetha2022gskde.pdf`, 22 pages, sha256 `7257c30a4687babd2909174d7cd7a6af22b5295f5e94ef875f297af323d92fd3`
- **Locator convention:** local PDF page N = printed page "N of 22"; cite as "p. N".

## 2. Research question and context
How to schedule IoT/DAG workflow tasks on heterogeneous fog nodes so as to minimize both makespan and energy consumption — treated as an NP-complete scheduling problem — using an "improved GSK" (IGSK) that hybridizes GSK with DE, plus DVFS for energy saving (Abstract p. 1; Sec. 1, pp. 1–2).

## 3. Method
- **Two-phase list scheduling** (Sec. 4, p. 6): (1) task ordering by HEFT ranks computed bottom-up over the DAG (Eq 10–13, pp. 6–7); (2) task-to-fog-node assignment optimized by IGSK.
- **Objective:** weighted-sum scalarization Minimize f = W1·mks + W2·Etot with W1 + W2 = 1 (Eq 9, p. 6); both weights set to 0.5 (p. 11). Makespan Eqs 1–3 (pp. 3, 5); energy model with DVFS, busy/idle split, Eqs 4–8 (pp. 5–6).
- **IGSK = GSK + DE** (Sec. 4.2.3, pp. 9–11; Algorithm 2, p. 13): integer population encodes task→node assignments (Eq 21, p. 10); GSK junior phase (Eq 16, p. 8) and senior phase (Eq 17, p. 9) are applied, then DE mutation (Eq 18), single-point binary crossover (Eq 19) and greedy selection (Eq 20) are applied **after the senior phase** "to boost the exploitation and exploration tendency of GSK and to provide the global optimum solution" (p. 9) / "to improve the exploitation ability of the GSK algorithm and to avoid the local optimum solution" (p. 11).
- **DVFS** applied post-assignment to lower frequency/voltage in slack times without missing deadlines (Sec. 4.2.3 "Applying the DVFS method", p. 11; slack time Eq 22).
- **GSK recap:** junior/senior phases and the D(junior) schedule (Eqs 14–15, p. 8), citing Mohamed et al. as ref [42].

## 4. Experimental scope
- **Simulator:** iFogSim with WorkflowSim (Sec. 5.1, p. 13).
- **Workloads:** scientific workflows Montage, CyberShake, Epigenomics, LIGO at task sizes ~50/100/1000 (Table 4, p. 14); fog nodes 16–50; simulation parameters Table 5 (p. 15).
- **Repetitions:** experiment repeated 50 times; averages plotted (p. 13).
- **Algorithm parameters (Table 6, p. 15):** IGSK — population 50, knowledge factor 0.5, knowledge ratio 0.9, knowledge rate 10, p ("number of chosen individual") 0.1, DE mutation factor 0.3, W1 = W2 = 0.5.
- **Comparators:** TS-GA, TS-PSO, TS-GSK (plain GSK scheduler), EM-MCC, EM-MOO (pp. 13, 15).

## 5. Findings (conservative)
- **Makespan (Epigenomics, 1000 tasks):** IGSK improves by 36%, 30%, 21%, 5%, 2% vs TS_GA, TS_PSO, TS_GSK, EM-MCC, EM-MOO respectively (Sec. 5.2.1, p. 15; Figs 10–13, pp. 16–17).
- **Energy (Epigenomics, 1000 tasks):** improvement 20%, 13%, 8%, 2%, 1% vs GA, PSO, GSK, EM-MCC, EM-MOO (Sec. 5.2.2, p. 18; PIR definition Eq 23, pp. 18–19; Figs 14–17, pp. 17–18).
- **Statistics:** lowest relative error among comparators (Fig 18, p. 19); 95% confidence intervals (Figs 19–20, p. 19); one-way ANOVA rejects "no difference" for both makespan (F = 33.09, p ≈ 2.4e−11; Table 7, p. 20) and energy (F = 8.77, p ≈ 3.3e−5; Table 8, p. 20).
- **Attribution:** gains credited to integration of HEFT + GSK + DE (faster convergence) and DVFS (energy) (pp. 15, 18; Conclusion p. 20).

## 6. Limitations
- Domain-specific application (fog-computing scheduling), simulation only; no continuous-optimization benchmark evidence at all.
- "Multi-objective" is a fixed weighted-sum scalarization (W1 = W2 = 0.5), not Pareto-based optimization.
- Improvement percentages are quoted for one workflow/size (Epigenomics-1000); other cases only shown graphically.
- Conclusion wording "IGSK reduces the convergence rate" (p. 20) means faster convergence in context — do not quote literally.
- The generic 3-vs-5 significance framing relies on ANOVA across algorithm groups, not per-pair tests.

## 7. Usable locators (claim → locator)
| Claim | Locator |
|---|---|
| IGSK = hybridization of GSK and DE for fog task scheduling | Abstract p. 1; Sec. 4.2, p. 7; Sec. 4.2.3, pp. 9–11 |
| DE applied after GSK senior phase to boost exploitation / escape local optima | pp. 9, 11; Algorithm 2 step 7c, p. 13 |
| GSK junior/senior equations and D(junior)/D(senior) schedule (as restated) | Eqs 14–17, pp. 8–9 |
| Weighted-sum objective W1·mks + W2·Etot, W1=W2=0.5 | Eq 9 p. 6; p. 11 |
| Setup: iFogSim, 4 scientific workflows, 50–1000 tasks, 16–50 fog nodes, 50 repetitions | Sec. 5.1–5.2, pp. 13–15; Tables 4–6 |
| Epigenomics-1000 makespan gains 36/30/21/5/2% vs GA/PSO/GSK/EM-MCC/EM-MOO | Sec. 5.2.1, p. 15 |
| Epigenomics-1000 energy gains 20/13/8/2/1% | Sec. 5.2.2, p. 18 |
| ANOVA significance for makespan and energy | Tables 7–8, p. 20 |

## 8. Supported uses in the DT-GSK manuscript
- Related-work sentence: GSK has been hybridized with DE operators (IGSK) for multi-objective (weighted-sum) task scheduling in fog computing, outperforming GA/PSO/GSK schedulers and two energy-makespan baselines in iFogSim simulations.
- Evidence that GSK has been carried into discrete/combinatorial application domains via integer encodings.

## 9. Unsupported / prohibited overextensions
- Do NOT use as evidence about GSK behavior on continuous benchmark suites (none tested).
- Do NOT describe IGSK as a Pareto multi-objective method.
- Do NOT generalize the quoted percentage gains beyond the Epigenomics-1000 case.
- Do NOT attribute the energy savings to GSK/DE alone — DVFS is a separate mechanism in the pipeline.

## 10. Role in DT-GSK framing (Appendix B)
Appendix B.2 — "GSK variants and hybrids — related-work breadth only." Cite only where the verified mechanism (GSK+DE hybrid applied to fog scheduling) is actually discussed; do not insert a decorative mention.
