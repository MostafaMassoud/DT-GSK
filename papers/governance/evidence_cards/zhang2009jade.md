# Evidence card — zhang2009jade

## Verified bibliographic identity
- Title: JADE: Adaptive Differential Evolution with Optional External Archive
- Authors: Jingqiao Zhang; Arthur C. Sanderson
- Venue/year: IEEE Transactions on Evolutionary Computation, 13(5):945–958, October 2009
- DOI: 10.1109/TEVC.2009.2014613 (printed on p. 945)
- Local file: `reference_papers/zhang2009jade.pdf` (14 pp., PDF p. 1 = printed p. 945; printed page = PDF page + 944)
- Inventory status: identity `verified`, readable, admissible. SHA-256 `756c086248ecfca671b4545ea7dba5956974f0ce545c791f61bd04b7d20945c6`.
- Locator convention in this card: printed journal pages (945–958).

## Research question and context
Can a greedy DE mutation strategy be made reliable by (a) generalizing DE/current-to-best to use any of the top 100p% solutions, (b) optionally exploiting an archive of recently explored inferior solutions as directional information, and (c) adapting F and CR from the record of recent successes — removing the need for user tuning of problem-dependent control parameters? (Abstract and Sec. I, pp. 945–946.)

Context: the paper classifies parameter control as deterministic / adaptive / self-adaptive (after Angeline; Eiben et al.) and places JADE in the adaptive class (Sec. I, p. 945). Sec. III (pp. 947–948) reviews DESAP, FADE, SaDE, and jDE as the adaptive-DE state of the art at the time.

## Method
- DE basics with binomial crossover and one-to-one selection (Sec. II, pp. 946–947). Boundary handling: violating components are reset to the midpoint of the violated bound and the parent component (Sec. II, pp. 946–947, unnumbered equations at top of p. 947).
- DE/current-to-pbest/1 without archive: Eq. (6), p. 948; x^p_best drawn at random from the top 100p% of the population, p ∈ (0,1].
- With archive: Eq. (7), p. 948; x̃_r2 drawn from P ∪ A, where A collects parents that fail selection; if |A| exceeds NP, random members are deleted (Sec. IV-A, p. 948; pseudocode Table I, p. 949).
- Parameter adaptation (Sec. IV-B, p. 949): CR_i = randn(μCR, 0.1) truncated to [0,1] (Eq. 8); μCR updated by (1−c)·μCR + c·meanA(S_CR) with arithmetic mean (Eq. 9). F_i = randc(μF, 0.1), a Cauchy draw truncated to 1 or regenerated if ≤ 0 (Eq. 10); μF updated with the Lehmer mean meanL(S_F) = ΣF²/ΣF (Eqs. 11–12).
- Rationale (Sec. IV-C, pp. 949–950): the Cauchy distribution diversifies mutation factors and avoids the premature convergence typical of greedy strategies; the Lehmer mean deliberately weights larger successful F values to counter the systematic downward drift an arithmetic mean would cause. The life span of a successful CR_i or F_i is roughly 1/c generations (p. 950).
- Parameter guidance (Sec. IV-D, p. 950; Sec. V-D, p. 956, Fig. 5): c and p are claimed problem-insensitive; JADE works best with 1/c ∈ [5,20] and p ∈ [5%,20%]; the standard initialization is μCR = μF = 0.5 (Sec. V-C, p. 956).

## Experimental scope
- 13 scalable classical benchmark functions (Yao et al. set; Table II, p. 950) at D = 30 and D = 100, plus 7 low-dimensional Dixon–Szegö functions (D = 2–6; Table III, p. 951).
- Comparators: jDE, SaDE (quasi-Newton local search disabled), DE/rand/1/bin (F=0.5, CR=0.9), canonical PSO; plus literature results for Adaptive LEP, Best Levy, NSDE, jDE (Table IX, p. 955).
- Settings: p = 0.05, c = 0.1 fixed in all simulations; NP = 30/100/400 for D ≤ 10 / D = 30 / D = 100; 50 independent runs (Sec. V, p. 950).
- Metrics: mean/std error tables (Tables IV–V, p. 953), success rate SR and FEs over successful runs FESS (Tables VI–VII, p. 954), convergence plots (Figs. 2–3, p. 952). NOT a CEC competition suite; no rank-based nonparametric testing is reported.

## Conservative findings (with locators)
1. JADE (with or without archive) had the best and second-best overall convergence rate on f1–f13; JADE without archive was best at D = 30, JADE with archive best at D = 100, plausibly because the archive adds diversity when NP = 400 is insufficient at high dimension (Sec. V-A, p. 951; Tables IV–V, p. 953).
2. jDE performed best on f8 and f9 with JADE competitive (Sec. V-A, p. 951); JADE's reliability (SR) was similar to jDE's across the 13 scalable functions (p. 951; Tables VI–VII, p. 954).
3. Ablation: rand-JADE (DE/rand/1 mutation) and nona-JADE (no parameter adaptation) both suffer frequent premature convergence or slow convergence; the full JADE indicates a "mutually beneficial cooperation" between the greedy strategy and parameter adaptation (Sec. V-B, pp. 951–954; Tables VI–VII, p. 954).
4. On low-dimensional Dixon–Szegö functions there is no obviously superior algorithm; adaptation "does not function efficiently within the small number of generations required to optimize these low dimensional problems" (Sec. V-A, p. 951; Table VIII, p. 955).
5. μF and μCR evolve to different values on different problems and at different stages (Fig. 4, p. 955; Sec. V-C, pp. 954–956): "there is no fixed parameter setting of F or CR that is suitable for various problems ... or at different evolution stages of a single problem" (pp. 955–956).
6. Initial value of μF has little effect; a moderate-to-large initial μCR is recommended for nonseparable functions (Sec. V-C, p. 956).

## Limitations
- Pre-CEC-benchmark evidence base: classical functions plus Dixon–Szegö, 50 runs, no significance tests, no rank statistics.
- Fixed NP per dimension bucket; population-size adaptation is not studied (that lineage begins with dynNP-jDE / L-SHADE).
- Findings about c and p ranges are empirical on this suite only.
- Archive benefit is demonstrated mainly at D = 100; at D = 30 the no-archive variant was better (Table IV, p. 953).

## Exact usable locators (claim → locator)
- Definition of DE/current-to-pbest/1 (no archive): Eq. (6), p. 948.
- Definition with external archive; archive maintenance rule: Eq. (7) and Sec. IV-A text, p. 948; Table I pseudocode, p. 949.
- CR normal / F Cauchy sampling and truncation rules: Eqs. (8), (10), p. 949.
- μCR arithmetic-mean update / μF Lehmer-mean update: Eqs. (9), (11), (12), p. 949.
- Why Cauchy + Lehmer (anti-premature-convergence rationale): Sec. IV-C, pp. 949–950.
- 1/c life-span interpretation: p. 950.
- Recommended ranges 1/c ∈ [5,20], p ∈ [5%,20%]: Sec. IV-D, p. 950 and Sec. V-D, p. 956 (Fig. 5).
- Boundary-repair midpoint rule: p. 946–947 (Sec. II).
- Headline comparative result: Sec. V-A, p. 951; Tables IV–VII, pp. 953–954.
- Low-D adaptation-inefficiency remark: Sec. V-A, p. 951.
- No-fixed-parameter observation: Abstract p. 945; Sec. V-C, pp. 955–956.

## Supported uses in the DT-GSK manuscript
- Citing JADE as the origin of (a) DE/current-to-pbest mutation, (b) the external archive of inferior solutions, and (c) success-based adaptation of F (Cauchy/Lehmer) and CR (normal/arithmetic) — the mechanism later inherited by SHADE/L-SHADE and by adaptive GSK variants.
- Supporting the general claim that fixed control-parameter settings are not suitable across problems or search stages (with the locators above).
- Supporting a narrow claim that success-history-style adaptation needs enough generations to act, which is strained at low dimension/short budgets (Sec. V-A, p. 951) — useful context for DT-GSK low-D discussion, phrased as JADE's observation on its own suite.

## Unsupported / prohibited overextensions
- Do NOT cite JADE for CEC2013/2014/2017 results or competition rankings (none here).
- Do NOT claim JADE proves archives help universally — the archive was worse at D = 30 on this suite.
- Do NOT attribute weighted (fitness-improvement) means or historical memories to JADE — those are Peng et al. and SHADE contributions.
- Do NOT use JADE to support statements about GSK-specific operators; JADE is DE lineage only.
- No statistical-significance claims can be sourced here (no tests reported).

## Role in DT-GSK framing (Appendix B.3)
`zhang2009jade` — adaptive DE and external-archive lineage. Method-lineage citation anchoring: adaptive parameter control in DE, current-to-pbest greediness control, and external archive; ancestor of the SHADE/L-SHADE line used as competitive context for the GSK family.

## Verification quotation (identity)
"JADE: Adaptive Differential Evolution with Optional External Archive — Jingqiao Zhang, Student Member, IEEE, and Arthur C. Sanderson, Fellow, IEEE" (p. 945); footer "IEEE TRANSACTIONS ON EVOLUTIONARY COMPUTATION, VOL. 13, NO. 5, OCTOBER 2009".
