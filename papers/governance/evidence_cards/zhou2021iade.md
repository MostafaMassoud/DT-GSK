# Evidence card — zhou2021iade

## Verified bibliographic identity
- Title: IADE: An Improved Differential Evolution Algorithm to Preserve Sustainability in a 6G Network
- Authors (source): Zhou Zhou, Mohammad Shojafar (corresponding), Jemal Abawajy, Ali Kashif Bashir — NOTE: bib first-author given name "Zeqiang" is wrong; source shows Zhou Zhou (reference_inventory.csv, identity_status = minor_metadata_mismatch).
- Venue (bib): IEEE Transactions on Green Communications and Networking, vol. 5, no. 4, 2021, pp. 1747–1760; DOI 10.1109/TGCN.2021.3104883.
- Local source: `reference_papers/zhou2021iade.pdf` (25 pp., AUTHOR PREPRINT in IEEE template; TGCN venue/pagination NOT visible locally). ALL locators below use the PREPRINT pagination 1–25.

## Research question and context
Standard DE suffers from slow late-iteration convergence, strong parameter dependence, and local-optimum entrapment; in an envisioned 6G networked-cloud/data-center setting these inefficiencies raise energy and power consumption. IADE proposes adaptive control of DE's parameters and strategies to serve as a "green" resource-allocation optimizer (Abstract, p. 1; Sec. I, pp. 2–3).

## Method (Sec. III, pp. 4–10)
Four modifications of standard DE:
1. Adaptive mutation factor F: cosine-shaped weight w(t) = (cos(|t−T|/T · π) + 1)/2 in [0.4, 1]; F(t) = Fmax − (Fmax−Fmin)·w(t), Fmax = 1, Fmin = 0.4 — large early (global search), decreasing later (local refinement) (Sec. III-B, pp. 5–6, Eqs. (1)–(2)).
2. Adaptive crossover factor CR: CR(t) = CRmin + (CRmax−CRmin)·w(t); text states CRmin = 0.6, CRmax = 0.9 (Sec. III-C, p. 7, Eq. (3)) — NOTE an internal inconsistency: parameter Table III (p. 12) lists IADE CR range as [0.3, 0.9].
3. Blended mutation strategy: u = 1 − (t/T)^2 weights a DE/rand/1-like and DE/best/1-like combination; refined with an "optimal difference" term and weight λ = 1 − sqrt(t/T): v_i = u·x_r1 + (1−u)·x_best + F·[λ(x_r2−x_r3) + (1−λ)(x_best−x_r4)] — rand-like early for diversity, best-like late for convergence (Sec. III-D, pp. 7–8, Eqs. (4)–(7)).
4. Extended selection: next generation selects the best-fitness individual among mutation vector v_i, crossover vector u_i, REVERSE crossover vector h_i, and target x_i (reverse crossover = complementary CR selection), to avoid destroying potentially optimal individuals (Sec. III-E, pp. 8–10, Eq. (8), Algorithm 1 p. 9, Fig. 2).
- Complexity: O(Gm × NP) (p. 11).

## Experimental scope (Sec. IV, pp. 11–22)
- Suite: CEC 2017, 30 functions F1–F30 (F2 reported as "/" everywhere because its results are unstable); classes unimodal F1–F3, simple multimodal F4–F10, hybrid F11–F20, composition F21–F30; search range [−100, 100]^D; D = 10, 30, 50, 100; 51 runs per function, mean of 51 runs reported (Sec. IV-A, p. 12).
- Environment: MATLAB 2016a, Windows 7, 4 GB RAM (Table II, p. 12). Parameters: NP = 100 for all; DE variants F = 0.5, CR = 0.9; IADE F ∈ [0.4, 1], CR ∈ [0.3, 0.9] (Table III, p. 12).
- Comparisons: (a) systematic IADE results at all four dims (Tables IV–V, pp. 13–14); (b) component ablation IADE-1..IADE-4 (each improvement in isolation) vs DE at D=30 with Wilcoxon (Tables VI–VIII, pp. 17–19); (c) vs state of the art at D=30: jSO ("JSO"), LSHADE-SPACMA, EBWO, EBLSHADE, EAGDE, with Wilcoxon (Tables IX–X, pp. 20–21); (d) cloud task-scheduling simulation (task sizes 5000–10000 MI, 10 VMs; execution time, workload balance, QoS) (pp. 21–22, Figs. 7–9, Table XI p. 21).

## Conservative findings
1. Ablation (D=30, Wilcoxon, Table VIII, p. 19): each single improvement beats standard DE — IADE-1 23+/2≈/5−, IADE-2 25/2/3, IADE-3 25/2/3, IADE-4 18/2/10.
2. Vs state of the art (D=30, Wilcoxon, Table X, p. 21): IADE LOSES decisively to jSO, LSHADE-SPACMA, EBWO, and EBLSHADE — 0+/1≈/29− against each; vs EAGDE it is marginal: 13+/3≈/12−, decided "+" by the authors. The text concedes: "for the other four algorithms under the CEC 2017 function set, the IADE algorithm presents some weaknesses in terms of convergence" (p. 18/814-line region, Sec. IV-C1 end, p. 18).
3. Cloud-scheduling simulation: EBWO best on total execution time; IADE fifth (better than EAGDE and DE only); same ordering pattern for workload balance and QoS (pp. 21–22, Figs. 7–9).
4. Abstract-level claim ("IADE surpasses the benchmark algorithms ... around 10%") is supported only against standard-DE-family baselines, not against the CEC winners (Abstract p. 1 vs Table X p. 21).
5. Conclusion claims better convergence/local-optimization ability than "other DE algorithms" (i.e., the DE-variant baselines) (Sec. VI, p. 23).

## Limitations
- Author preprint: published TGCN pagination unverifiable locally; locators must remain preprint-based.
- Internal inconsistency in CR range (text 0.6–0.9 vs Table III 0.3–0.9).
- No Friedman/multi-problem rank analysis; only Wilcoxon at D=30 is reported for cross-algorithm comparisons.
- The state-of-the-art comparison unambiguously favors the CEC winners over IADE (29 losses of 30 functions against each of four algorithms).
- Cloud/6G evaluation is a small simulation (10 VMs) with a bespoke QoS metric (Eq. (11), p. 22).

## Exact usable locators (bibkey, preprint page)
- DE weaknesses motivating adaptation (slow late convergence, parameter dependence, local optima): (zhou2021iade, Abstract p. 1; Sec. I pp. 2–3).
- Adaptive F via cosine weight (Fmax = 1, Fmin = 0.4): (zhou2021iade, Sec. III-B, pp. 5–6, Eqs. (1)–(2)).
- Adaptive CR (text range 0.6–0.9; Table III says [0.3, 0.9]): (zhou2021iade, Sec. III-C, p. 7, Eq. (3); Table III p. 12).
- Time-varying rand/1 ↔ best/1 mutation blend with λ-weighted optimal-difference term: (zhou2021iade, Sec. III-D, pp. 7–8, Eqs. (4)–(7)).
- Four-way selection incl. reverse crossover vector: (zhou2021iade, Sec. III-E, pp. 8–10, Algorithm 1 p. 9).
- CEC2017 protocol (30 functions, F2 unstable/excluded; D = 10/30/50/100; 51 runs; NP = 100): (zhou2021iade, Sec. IV-A, p. 12, Tables II–III).
- IADE raw results at all dims: (zhou2021iade, Tables IV–V, pp. 13–14).
- Component ablation Wilcoxon results: (zhou2021iade, Table VIII, p. 19).
- Losses to jSO/LSHADE-SPACMA/EBWO/EBLSHADE (0/1/29 each), near-tie with EAGDE (13/3/12): (zhou2021iade, Table X, p. 21; concession sentence Sec. IV-C1, p. 18).
- Cloud task-scheduling comparison (execution time / workload balance / QoS; IADE mid-pack): (zhou2021iade, pp. 21–22, Figs. 7–9).

## Supported uses in the DT-GSK manuscript
- Taxonomy/positioning: example of a 2021 adaptive-DE variant (time-varying F/CR, blended mutation, extended selection) evaluated on CEC2017 (D = 10–100, 51 runs).
- Supporting the general statement that time-varying/adaptive parameter control and strategy blending are standard DE-improvement patterns.
- Honest context that adaptive-DE variants of this class still lose comprehensively to CEC2017 winners (jSO, LSHADE-SPACMA) — usable when positioning the strength of competition-grade baselines.

## Unsupported / prohibited overextensions
- Do NOT cite IADE as a strong CEC2017 performer; its own Wilcoxon table shows 0/1/29 losses against each of four winner-class algorithms (Table X, p. 21).
- Do NOT cite the "around 10%" abstract claim without the qualifier that it refers to DE-family baselines.
- Do NOT cite TGCN page numbers for specific claims (preprint pagination only); do not rely on the bib's first-author given name.
- Do NOT use as CEC2017 protocol authority; do not use its 6G/cloud energy claims as evidence about optimization performance in general.

## Role in DT-GSK framing (Appendix B.5)
"Taxonomy/positioning only." Sanctioned for related-work breadth on adaptive DE variants and application-driven metaheuristic tuning; not part of the GSK/DE lineage citations (B.3 covers those), not a benchmark or statistics source.
