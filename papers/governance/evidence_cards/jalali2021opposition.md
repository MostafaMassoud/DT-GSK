# Evidence card — jalali2021opposition

## 1. Verified bibliographic identity
- **Citation key:** `jalali2021opposition`
- **Title (on source):** "An oppositional-Cauchy based GSK evolutionary algorithm with a novel deep ensemble reinforcement learning strategy for COVID-19 diagnosis"
- **Authors (on source):** Seyed Mohammad Jafar Jalali; Milad Ahmadian; Sajad Ahmadian; Abbas Khosravi; Mamoun Alazab; Saeid Nahavandi
- **Venue/year (on source):** Applied Soft Computing 111 (2021) 107675; DOI 10.1016/j.asoc.2021.107675
- **Identity status (inventory):** `minor_metadata_mismatch` — identity certain; bib given-name errors: 2nd author is **Milad** Ahmadian (bib "Maryam"), 3rd author is **Sajad** Ahmadian (bib "Saeed").
- **Source file:** `reference_papers/jalali2021opposition.pdf`, 18 pages, sha256 `42f40a7a7de18715f7690b509ad288155c57c283ba3491823913856d86632116`
- **Locator convention:** local PDF page 1 is an Elsevier COVID-19 resource-centre cover; the article's printed pages 1–17 are local PDF pages 2–18. Cite as "p. N (printed)"; local PDF page = printed page + 1.

## 2. Research question and context
Can the architecture/hyperparameters of deep CNN classifiers for COVID-19 chest X-ray diagnosis be designed automatically — instead of manual trial and error — by an improved GSK evolutionary algorithm (IGSK, adding opposition-based learning and Cauchy mutation to GSK), combined with a deep-Q/Q-learning reinforcement-learning selection of an optimal ensemble subset (framework "DNE-RL")? (Abstract, printed p. 1; contributions list, printed p. 2.)

## 3. Method
- **IGSK = GSK + OBL + Cauchy mutation** (Sec. 2.2, printed pp. 5–6; flowchart Fig 1, printed p. 6):
  - GSK recap: junior/senior stages; experience equations D(junior) = size·(1−G/GEN)^k, D(senior) = size − D(junior) (Eqs 6–7, printed p. 5); k = 2 per the original work.
  - Opposition-Based Learning: opposite number/point definitions (Eqs 8–9, printed pp. 5–6); applied at GSK's initialization stage to boost population diversity — "we use OBL technique to significantly boost its search space population diversity" (Sec. 2.3.2, printed p. 7); swap h with ĥ when f(h) > f(ĥ).
  - Cauchy mutation: density/CDF (Eqs 10–11, printed p. 6); perturbation x′_j = x_j + W_j·R with W the population-mean weight vector and R Cauchy-distributed (Eqs 12–13, printed p. 6); intended to escape local optima and speed convergence.
- **DNE-RL pipeline** (Sec. 2.3, printed pp. 6–8; Algorithm 1, printed p. 8): Bagging generates L = 10 base CNN classifiers; IGSK optimizes ELEVEN CNN hyperparameters per classifier (kernel size, number of filters, optimizer type, epochs, batch size, number of conv layers, max-pooling size, dropout rate, activation type, learning rate, momentum rate — Table 2, printed p. 9; discretization Eqs 14–16, printed p. 7); Q-learning (states = [#selected classifiers, ensemble accuracy]; reward Eq 20) selects the optimal classifier subset; majority voting (Eq 19) gives the final output.

## 4. Experimental scope
- **Benchmark-function validation of IGSK** (Sec. 3.3, printed p. 9): 15 benchmark functions (3 unimodal, 7 multimodal, 5 hybrid; Table 3, printed p. 10 — shifted/rotated functions with offsets 100–2100; the suite's provenance is not named in the text); D = 30; population 40; 1000 iterations; 40 runs; comparators GOA, SMA, GA, GWO, PSO, DE, BBO, and original GSK; Wilcoxon sign-rank test.
- **COVID-19 experiments** (Sec. 3.1–3.4, printed pp. 9–13): Mendeley dataset (1800 images: 1510 normal) and Kaggle dataset (1735 images: 825 COVID); images 224×224; IGSK run with max 20 iterations, population 30 (GPU cost constraint, printed p. 9); comparators: GA/DE/PSO/GSK-optimized ensembles and single MobileNet, VGGNet19, ResNet50, DenseNet12; metrics: accuracy, precision, recall, F-measure, AUC; T-test and Friedman ranking.

## 5. Findings (conservative)
- **Benchmark functions:** IGSK attains the best AVG on the reported functions and the smallest STDs among the nine algorithms (Table 4, printed p. 11); Wilcoxon sign-rank p-values < 0.05 vs all eight comparators on the 15 functions — including vs original GSK (Table 5, printed p. 11; text printed p. 9).
- **COVID classification:** DNE-RL best on all five metrics on both datasets — Mendeley: ACC 0.987742, precision 0.984334, recall 0.989123, F 0.984939, AUC 0.988466 (Table 6, printed p. 12); Kaggle: ACC 0.991441, precision 0.993568, recall 0.981445, F 0.989666, AUC 0.990337 (Table 7, printed p. 12). (The abstract, printed p. 1, associates these two metric sets with Kaggle and Mendeley respectively — consistent with Tables 6–7.)
- **Friedman ranking:** DNE-RL rank 1 on both datasets; DenseNet12/ResNet50 nearest followers; among GA/DE/PSO/GSK-optimized ensembles, original GSK ranks best (Tables 9–10, printed p. 15; boxplot discussion printed p. 11).
- **T-test:** p-values vs all benchmarks < 0.05 on both datasets (Table 8, printed p. 15).
- **Runtime:** DNE-RL lowest optimization/training/test times among compared models (Tables 11–12, printed p. 15).

## 6. Limitations
- IGSK modifications are lightweight and loosely specified: OBL applied at initialization and Cauchy perturbation around a population-mean weight vector; no ablation separating OBL vs Cauchy contributions.
- Benchmark suite provenance unnamed (function list resembles CEC-style shifted/rotated functions, but the paper does not identify the suite — do not label it CEC).
- COVID experiments use small evolutionary budgets (20 iterations, pop 30) justified by GPU cost; training/test split stated as 80/20 in Sec. 3.2 (printed p. 9) but 75/25 in Sec. 3.4 (printed p. 10) — internally inconsistent.
- Application-domain (image classification) evidence; ensemble + RL confound any claim about IGSK alone on the COVID results.

## 7. Usable locators (claim → locator)
| Claim | Locator |
|---|---|
| IGSK = GSK improved with OBL and Cauchy mutation | Abstract printed p. 1; Sec. 2.2, printed pp. 5–6 |
| OBL definitions and swap rule; applied at initialization | Eqs 8–9 printed pp. 5–6; Sec. 2.3.2 printed p. 7 |
| Cauchy mutation equations (x′ = x + W·R) | Eqs 10–13, printed p. 6 |
| GSK experience equations restated (k = 2, "as suggested by the original work") | Eqs 6–7, printed p. 5 |
| 15 benchmark functions, D=30, pop 40, 1000 iters, 40 runs, 8 comparators | Sec. 3.3, printed p. 9; Table 3, printed p. 10 |
| IGSK beats GSK and 7 others; Wilcoxon p < 0.05 on all 15 functions | Tables 4–5, printed p. 11 |
| 11 CNN hyperparameters optimized; search ranges | Sec. 2.3.2 printed p. 7; Table 2 printed p. 9 |
| Mendeley/Kaggle dataset sizes and DNE-RL headline metrics | Sec. 3.2 printed p. 9; Tables 6–7 printed p. 12 |
| Friedman rank 1 on both datasets; GSK best among the four EA-optimized ensembles | Tables 9–10, printed p. 15 |
| Q-learning ensemble-subset selection design | Sec. 2.3.3, printed pp. 7–8 |

## 8. Supported uses in the DT-GSK manuscript
- Related-work sentence: opposition-based learning and Cauchy mutation have been grafted onto GSK (IGSK) and reported significantly better than GSK and seven other metaheuristics on 15 benchmark functions (D=30, Wilcoxon p<0.05), and used inside a deep-RL CNN-ensemble pipeline for COVID-19 X-ray diagnosis.
- Evidence that GSK is used as a hyperparameter-optimization engine in applied ML pipelines.

## 9. Unsupported / prohibited overextensions
- Do NOT attribute the COVID classification accuracy to IGSK alone (ensemble + Q-learning are confounded contributors; the paper itself notes optimization does not guarantee best performance, printed p. 15).
- Do NOT name the 15-function benchmark a CEC suite; provenance is not stated in the source.
- Do NOT generalize IGSK superiority beyond the tested comparator set, budget (1000 iterations, D=30), and functions.
- Do NOT cite the bib's incorrect author given names; use the source-verified names.

## 10. Role in DT-GSK framing (Appendix B)
Appendix B.2 — "GSK variants and hybrids — related-work breadth only." Cite only where the verified mechanism (oppositional/Cauchy-modified GSK, or GSK for CNN hyperparameter tuning) is actually discussed.
