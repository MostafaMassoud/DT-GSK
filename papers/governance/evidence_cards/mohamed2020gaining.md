# Evidence card — mohamed2020gaining

Group: family-panel (Appendix B.1 — Foundation and GSK family)
Prepared: 2026-07-10, Phase 1 tasks 4–5. Source read in full (method + results + conclusions), not abstract-only.

## 1. Verified bibliographic identity

- Title: "Gaining-sharing knowledge based algorithm for solving optimization problems: a novel nature-inspired algorithm"
- Authors: Ali Wagdy Mohamed, Anas A. Hadi, Ali Khater Mohamed
- Venue: International Journal of Machine Learning and Cybernetics; DOI 10.1007/s13042-019-01053-x (printed on page 1)
- Bib year 2020 matches the journal issue 11(7):1501–1529; identity status in `reference_inventory.csv`: **verified / readable / admissible**.
- Local file: `reference_papers/mohamed2020gaining.pdf`, 29 pages, Springer **online-first layout without journal pagination**.
- **Locator convention for this card: local PDF page numbers (p. 1–29) plus stable section/equation/table/figure numbers.** Do not cite journal page numbers (1501–1529) from this file; they are not printed in it.

## 2. Research question and context

Can a human-inspired metaheuristic that models the gaining and sharing of knowledge across the human life span (GSK) solve bound-constrained continuous optimization competitively with established metaheuristics? Context: authors survey four inspiration categories (evolutionary, swarm, physics, human; Fig. 1 and Tables 1–4, PDF pp. 2–5) and argue human-based algorithms are underexplored (PDF p. 4).

## 3. Method (the original GSK algorithm)

- Population of N persons, each with D dimensions ("fields of knowledge"); two stages: **junior** (beginning–intermediate) and **senior** (intermediate–expert) gaining–sharing phases (Sect. 2, PDF pp. 5–6).
- **Experience equation** Eq. (1), PDF pp. 6–7: `D(junior) = D × (1 − G/GEN)^k`, `D(senior) = D − D(junior)`; k > 0 is the knowledge rate; worked example in Table 5 (PDF p. 7, problem size 100, K = 2).
- **Junior scheme** (Sect. 2.1; pseudo-code Fig. 7, PDF p. 8): sort population ascending by fitness; for each x_i use nearest better x_{i−1}, nearest worse x_{i+1} (gaining) and a random individual x_r (sharing); update `x_new = x_i + kf·[(x_{i−1} − x_{i+1}) + (x_r − x_i)]` if f(x_i) > f(x_r), else with `(x_i − x_r)`; per-dimension gate `rand ≤ kr`. Edge handling: global best uses (x_best, x_best+1, x_best+2); global worst uses (x_worst−2, x_worst−1, x_worst) (PDF p. 8).
- **Senior scheme** (Sect. 2.2; pseudo-code Fig. 8, PDF p. 8): partition sorted population into top 100p% (best), middle N − 2·100p%, bottom 100p% (worst); update uses random x_p-best and x_p-worst (gaining) plus random middle x_m (sharing); "p ∈ [0,1], and p = 0.1, 10% of NP is suitable" (PDF p. 8).
- Parameters: kf > 0 (knowledge factor, amount of gained/shared knowledge added), kr ∈ [0,1] (knowledge ratio, gate probability) (PDF p. 8). Overall pseudo-code Fig. 9 and flow chart Fig. 10 (PDF p. 9); greedy per-vector survivor selection plus global-best update (Fig. 9 lines 9–10).

## 4. Experimental scope

- **CEC2017**: 30 test functions (unimodal f1–f3, simple multimodal f4–f10, hybrid f11–f20, composition f21–f30; PDF pp. 8–9); D = 10, 30, 50, 100; MaxFEs = 10,000×D; 51 independent runs; solution-error measure f(x) − f(x*); errors and SDs < 10⁻⁸ set to zero (Sect. 3.1–3.2, PDF pp. 8–10). **f2 excluded** from the score comparison "because it shows unstable behavior especially for higher dimensions" (PDF p. 11), leaving 29 functions.
- **CEC2011**: 22 real-world problems; MaxFEs = 150,000; 25 runs (PDF pp. 9–10).
- Comparators (10): TLBO, GWO, SFS, AMO, DE, BBO, ACO, ES, GA, PSO, with control parameters from original references (Table 6, PDF p. 10). **GSK setting: NP = 100, p = 0.1, kf = 0.5, kr = 0.9, K = 10** (Table 6, PDF p. 10).
- Evaluation: CEC2017 competition score metric (Score1 weighted error sums + Score2 weighted rank sums, weights 0.1/0.2/0.3/0.4 for D = 10/30/50/100; PDF pp. 10–11); multi-problem Wilcoxon signed-rank at α = 0.05 (p-values via SPSS v20, PDF pp. 11–12); Friedman ranking for CEC2011 (Table 27).

## 5. Conservative findings

- GSK-only results (best/median/mean/worst/SD) in Tables 7–10 (10D Table 7 PDF p. 11; 30D Table 8; 50D Table 9; 100D Table 10, PDF pp. 12–15). GSK found the optimum at least once for 6 problems at 10D, 4 at 30D, 3 at 50D, 1 at 100D (PDF p. 12).
- Head-to-head mean±SD comparison tables: 10D/30D Tables 11–14 (PDF pp. 13–17); 50D Tables 15–16 (PDF pp. 18–19); 100D Tables 17–18 (PDF pp. 20–21).
- **CEC2017 score ranking (Table 19, PDF p. 21): GSK first with Score = 97.17; DE second (60.37); AMO third (57.49); then SFS, TLBO, PSO, BBO, GA, GWO, ACO.**
- **CEC2011 Friedman ranks (Table 27, PDF p. 25): AMO first (3.27), SFS second (3.48), GSK third (3.80)**, then TLBO, BBO, DE, GA, GWO, PSO, ES, ACO.
- **CEC2011 Wilcoxon (Table 28, PDF p. 25)**: GSK R+ > R− against 9 of 10 competitors (exception AMO: R+ = 53, R− = 100, p = 0.266, decision ≈); significantly better than DE, GA, ES, GWO, PSO, ACO (p = 0.000); not significantly different from TLBO (p = 0.717), SFS (p = 0.528), BBO (p = 0.314) (narrative PDF p. 19).
- Convergence claims: fast early convergence, significant improvement in middle/late stages, based on supplemental Fig. S2 (PDF pp. 19–20).
- Conclusion (Sect. 4, PDF pp. 20–21): GSK "statistically superior to and competitive with" the compared algorithms "especially in high dimensions"; on the CEC2017 score metric "GSK gets the first ranking among all algorithms, followed by DE and AMO" (PDF p. 21).

## 6. Limitations

- Fixed control parameters (kf, kr, K, p, NP) — no adaptation; later family papers (AGSK/APGSK) treat this as the key weakness.
- Comparator panel excludes CEC-competition winners (no LSHADE-class algorithm on CEC2017); the "first ranking" holds only against these 10 general metaheuristics.
- On CEC2011, GSK is third by Friedman rank and never significantly better than AMO, SFS, TLBO, BBO.
- Score metric weights high dimensions (0.4 weight for 100D), so the headline score partly encodes the high-dimension emphasis.
- Convergence-curve evidence resides in a supplemental file not present in the local corpus.

## 7. Exact usable locators (claim → locator)

| Claim the DT-GSK manuscript may need | Locator |
|---|---|
| GSK definition, two-phase gaining/sharing metaphor | Sect. 2, PDF pp. 5–6 |
| Experience equation D(junior)/D(senior), role of k | Eq. (1), PDF pp. 6–7; Table 5, PDF p. 7 |
| Junior update rule + pseudo-code, best/worst edge rule | Sect. 2.1, Fig. 7, PDF p. 8 |
| Senior update rule + pseudo-code, top/bottom 100p% partition, p = 0.1 | Sect. 2.2, Fig. 8, PDF p. 8 |
| kf, kr definitions | PDF p. 8 |
| Full-algorithm pseudo-code / flow chart | Figs. 9–10, PDF p. 9 |
| CEC2017 protocol: 30 fns, D = 10/30/50/100, 10,000×D FEs, 51 runs, 1e−8 zeroing | Sect. 3.1–3.2, PDF pp. 8–10 |
| CEC2011 protocol: 22 problems, 150,000 FEs, 25 runs | Sect. 3.1–3.2, PDF pp. 9–10 |
| Baseline GSK parameters NP=100, kf=0.5, kr=0.9, K=10, p=0.1 | Table 6, PDF p. 10 |
| f2 exclusion | PDF p. 11 |
| CEC2017 score metric definition | PDF pp. 10–11 |
| GSK #1 by CEC2017 score (97.17), DE 2nd, AMO 3rd | Table 19, PDF p. 21 |
| GSK 3rd on CEC2011 Friedman; AMO 1st | Table 27, PDF p. 25 |
| CEC2011 Wilcoxon outcomes per competitor | Table 28, PDF p. 25; narrative PDF p. 19 |
| High-dimension strength claim (authors' wording) | Abstract PDF p. 1; Sect. 4, PDF pp. 20–21 |
| GSK per-dimension raw statistics | Tables 7–10, PDF pp. 11–15 |

## 8. Supported uses

- Citing GSK as the origin of the algorithm family and of the exact junior/senior mechanics that DT-GSK inherits (equations, parameters, sorting-based neighbor selection).
- Stating the original GSK reference protocol (suites, dims, runs, budgets, error zeroing) and reference parameter setting.
- Stating that original GSK ranked first on the CEC2017 score metric against 10 classical/recent metaheuristics, and third by Friedman on CEC2011 (with AMO/SFS ahead).
- Thematic framing: human-inspired algorithm taxonomy (Fig. 1, Tables 1–4).

## 9. Unsupported / prohibited overextensions

- Do NOT claim GSK outperformed CEC-competition winners or LSHADE-class algorithms — none were compared here.
- Do NOT claim GSK is best on CEC2011 — it ranked third (Table 27) and was ≈ to AMO/SFS/TLBO/BBO.
- Do NOT cite journal pagination (1501–1529) as locators for this local file (online-first copy).
- Do NOT attribute any parameter adaptation, population-size reduction, or local search to this paper — those appear only in later variants.
- "Significantly better ... especially with high dimensions" (abstract) is relative to the 10 compared algorithms only.

## 10. Role in DT-GSK framing (Appendix B.1)

`mohamed2020gaining` — GSK origin, inherited mechanics, thematic comparison. It anchors: (a) the mechanical definition of the GSK base DT-GSK descends from; (b) the family-panel baseline "GSK" rows; (c) the human-inspired-algorithm narrative positioning.

## 11. Verification quotations (minimal)

- "GSK gets the first ranking among all algorithms, followed by DE and AMO in second and third place" (Sect. 4, PDF p. 21 — CEC2017 score metric).
- "Note that f2 has been excluded because it shows unstable behavior especially for higher dimensions." (PDF p. 11)
- "where p ∈ [0,1], and p = 0.1, 10% of NP is suitable." (Sect. 2.2, PDF p. 8)
