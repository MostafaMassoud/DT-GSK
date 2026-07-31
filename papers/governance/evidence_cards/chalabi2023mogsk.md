# Evidence card: chalabi2023mogsk

## Verified bibliographic identity
- Title: "A Multi-Objective Gaining-Sharing Knowledge-Based Optimization Algorithm for Solving Engineering Problems"
- Authors: Nour Elhouda Chalabi, Abdelouahab Attia, Khalid Abdulaziz Alnowibet, Hossam M. Zawbaa, Hatem Masri, Ali Wagdy Mohamed
- Venue: Mathematics 2023, 11, 3092 (MDPI); DOI 10.3390/math11143092 (printed article p. 1)
- Identity status (reference_inventory.csv): **verified**.
- Pagination note: the 39-page local PDF has 2 leading TU Dublin repository cover pages; **printed article page N = local PDF page N+2**. Locators below use printed article pages (1–37).

## Research question and context
GSK is single-objective; human-related metaheuristics with multi-objective extensions are scarce. The paper proposes the "first extended version" of GSK for multiobjective optimization problems (MOPs), named MOGSK (Abstract, p. 1; Sect. 1, pp. 3–4). Motivated by GSK's track record and the NFL theorem (p. 4).

## Method
MOGSK = GSK search operators + standard a-posteriori MO machinery (Sect. 3, pp. 5–11; flowchart Fig. 4, p. 11; pseudocode Algorithm 4, p. 13):
1. **External archive** stores nondominated solutions found so far and guides solutions toward the Pareto set; archive capped at first N solutions (Sect. 3.2, p. 10).
2. **Fast nondominated sorting (FNS) + crowding distance (CD)** (both from NSGA-II) applied to New_sol = current population ∪ previous archive, to build the working set for gaining/sharing (Sects. 3.1.1–3.1.3, pp. 8–9; CD Eq. (10), p. 9).
3. **epsilon-dominance archive update**: box-identification vector B_i(f) = floor(log(f_i)/log(eps+1)) (Eq. (11), p. 10); box-level then regular dominance decides insertion/replacement (Algorithm 3, p. 12).
4. Junior/senior GSK phases retained unchanged from GSK (Algorithms 1–2, pp. 7; dimension split Eqs. (7)–(8), p. 6).
- Complexity stated as O(M·N^2), same as NSGA-II (p. 12).
- Parameters (Table 1, p. 8): N = 100, k = 10, kr = 0.1, kf = 0.9, 30 runs, Max_fe = 60,000. CAUTION: Sect. 4.1 (p. 13) states "30 independent runs, and there were 6000 function evaluations" — internal inconsistency with Table 1's 60,000; also Table 1's kr = 0.1 / kf = 0.9 swaps the conventional GSK values (kf = 0.5, kr = 0.9); cite the parameter table, flag the discrepancy if load-bearing.

## Experimental scope
- Experiment I: ZDT1–4, ZDT6 (biobjective) and DTLZ1–7 (three-objective) (Sect. 4.2, characteristics Table 2, p. 14).
- Experiment II: CEC 2021 real-world constrained multiobjective problems (RWMOPs), 50 problems: mechanical design (RWMOP1–21), chemical engineering (22–24), process design & synthesis (25–29), power electronics (30–35), power system optimization (36–50) (Sect. 4.3, Table 7, pp. 20–21). Run on PlatEMO (p. 13).
- Comparators (both experiments): MOEAD, eMOEA, MOPSO, NSGAII, SPEA2, KnEA, GrEA (Sect. 4.1, p. 13).
- Metrics: IGD (Eq. (12), p. 13) and HV (Eq. (13), p. 14) for Experiment I; HV only for Experiment II. Best/worst/average/median/std over 30 runs. **No Wilcoxon/Friedman significance tests.**

## Conservative findings
- ZDT (IGD, Table 3, p. 15): MOGSK best on ZDT1, ZDT2, ZDT6; 4th on ZDT3 (behind SPEA2, NSGAII, KnEA); 4th-from-best on ZDT4 where it "was stuck in a local optimum" (Sect. 4.2.1, p. 14; limitation restated p. 31).
- DTLZ (IGD, Sect. 4.2.2, pp. 17): best on 6 of 7 (DTLZ1, DTLZ2, DTLZ4, DTLZ5, DTLZ6, DTLZ7 — text lists "six out of seven"), last on DTLZ3.
- CEC 2021 RWMOPs (HV): mechanical design — best on 11 of 21 problems (RWMOP1, 4, 5, 6, 8, 12, 13, 14, 15, 18, 19; Sect. 4.3, pp. 21–22; Table 8, pp. 22–23). Process/design/synthesis — "gave 90% of the best results" (Limitation section, p. 32). Chemical engineering — good but not uniformly best (p. 32). Power electronics and power system problems — MOGSK "did not show good results" (p. 32); e.g., HV 0.00 on RWMOP42 and 0.205 average on RWMOP47 vs 1.00 for several comparators (Table 12, pp. 30–31).
- Authors' own overall claim is qualified: "good behavior ... in particular real-world optimization problems" (Abstract, p. 1).

## Limitations (author-stated and observed)
- Dedicated "Limitation" subsection (pp. 31–32): ZDT4 local-optimum trapping (deceptive concave front); ZDT3 premature convergence (covered only 3 of 5 discontinuous fronts, p. 14); power electronics (high nonconvexity) and power systems (many equality constraints) are weak spots; results are parameter-sensitive, and adaptive parameters exist only for single-objective GSK, not yet for MOGSK.
- No statistical significance testing; comparisons rest on descriptive statistics of 30 runs.
- Budget inconsistency (60,000 in Table 1 vs 6,000 in Sect. 4.1 text) and non-standard kf/kr values in Table 1 (see Method).
- Fixed epsilon and archive size; no ablation of the epsilon-dominance vs plain dominance choice.

## Exact usable locators (claim -> locator)
| Claim the DT-GSK manuscript may need | Locator (printed page = PDF page − 2) |
|---|---|
| First multiobjective extension of GSK (claim) | Abstract, p. 1; Sect. 1, p. 4 |
| GSK junior/senior restatement | Sect. 2.3, Algorithms 1–2, pp. 6–7 |
| Archive + FNS + CD + eps-dominance design | Sect. 3, pp. 7–10; Algorithm 3, p. 12; Fig. 4, p. 11 |
| eps-dominance box formula | Eq. (11), p. 10 |
| Complexity O(MN^2) (NSGA-II-like) | Sect. 3, p. 12 |
| Parameters (N=100, 30 runs, Max_fe=60,000) | Table 1, p. 8 (inconsistent 6,000-FE statement: Sect. 4.1, p. 13) |
| Test setup: ZDT/DTLZ + CEC2021 RWMOPs; 7 comparators; IGD/HV | Sect. 4.1, p. 13; Table 2, p. 14; Table 7, pp. 20–21 |
| ZDT IGD results (best on ZDT1/2/6) | Table 3, p. 15; Sect. 4.2.1, p. 14 |
| DTLZ IGD results (best on 6/7, last on DTLZ3) | Sect. 4.2.2, p. 17; Table 5 |
| Mechanical design: best HV on 11/21 | Sect. 4.3, pp. 21–22; Table 8, pp. 22–23 |
| Weakness on power electronics/power systems | Limitation, p. 32; Table 12, pp. 30–31 |
| Author-stated limitations incl. ZDT4/ZDT3 behavior | Limitation, pp. 31–32 |

## Supported uses in the DT-GSK manuscript
- Related-work breadth: the GSK family extends to multiobjective optimization via archive + FNS/CD + epsilon-dominance (first MO extension claim, verified mechanism).
- Evidence that GSK's operators transfer to MO settings with mixed results (strong on mechanical-design RWMOPs, weak on power electronics/systems) — usable, with locators, when delimiting the family's demonstrated scope.
- Evidence that parameter sensitivity is acknowledged inside the GSK family and adaptive parameters were an open MO direction as of 2023 (p. 32).

## Unsupported / prohibited overextensions
- Do NOT cite as statistically validated superiority — no hypothesis tests.
- Do NOT cite as evidence about single-objective GSK performance; all results are multiobjective.
- Do NOT quote a single evaluation budget without noting the 60,000 vs 6,000 internal inconsistency if the number is load-bearing.
- Do NOT claim MOGSK is best across all RWMOP categories (fails on power electronics/power systems, p. 32).
- Does not discuss DT-GSK; single-objective mechanism claims must not be sourced here.

## Role in DT-GSK framing (Appendix B)
Appendix B.2: related-work breadth only; use only where the verified MOGSK mechanism (MO extension of GSK) is actually discussed.

## Verification quotations
- "we suggest the first extended version of the recently introduced gaining–sharing knowledge optimization (GSK) algorithm ... named multiobjective gaining–sharing knowledge optimization (MOGSK)" (Abstract, p. 1)
- "power electronics problems and power system optimization problems were quite challenging for MOGSK ... for these two test series, MOGSK did not show good results" (Limitation, p. 32)
