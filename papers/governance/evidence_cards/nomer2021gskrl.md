# Evidence card — nomer2021gskrl

## 1. Verified bibliographic identity
- **Citation key:** `nomer2021gskrl`
- **Title (on source):** "GSK-RL: Adaptive Gaining-sharing Knowledge algorithm using Reinforcement Learning"
- **Authors (on source):** Hazem A. A. Nomer; Ali Wagdy Mohamed; Ahmed H. Yousef
- **BibTeX venue/year:** Proceedings of the 2021 NILES conference, 2021, DOI 10.1109/NILES53778.2021.9600551
- **Identity status (inventory):** `verified`. CAUTION: the local file is an **author version without conference branding** — venue, year, and DOI are NOT confirmable from the file itself; the six-page local pagination is the only valid locator basis.
- **Source file:** `reference_papers/nomer2021gskrl.pdf`, 6 pages, sha256 `485ddd6718420fa2712a48e8ad0cba58590824ff4d974bdc57b128c8e2b0312f`
- **Locator convention:** "local p. N" = PDF page N of the 6-page author version (no printed page numbers).

## 2. Research question and context
Can the two fixed GSK control parameters kf (knowledge factor) and kr (knowledge rate/ratio) be adapted online by a learned controller — a neural network policy trained with actor–critic reinforcement learning — instead of the fixed defaults of basic GSK, and does this improve performance? (Abstract + Sec. I, local p. 1.) The paper positions itself against statistical/random adaptation schemes (AGSK, APGSK cited as refs [14], [15], local p. 1) and against SHADE-style success-history adaptation (local pp. 1–2).

## 3. Method
- **GSK-RL controller** (Sec. III–IV, local pp. 2–4): a discrete pool of six mean pairs (µKf, µKr) = [(0.1,0.1), (0.1,0.9), (0.5,0.1), (0.5,0.9), (0.9,0.1), (0.9,0.9)] (local p. 3, item "Action (At)"). A feed-forward actor network (3 layers × 100 units; critic shares architecture/weights except linear output, local p. 4) selects one pair per generation; per-individual kf, kr are then sampled from normal distributions with those means (Eqs. 3–4, local p. 3) and standard deviations drawn from two H=100 memories updated with the SD of successful values (Eqs. 5–6, local p. 3).
- **MDP model** (Sec. IV, local pp. 3–4): state = fitness values, fitness histogram, moving average, and a 4-value run description (success rate, remaining FES budget, population SD, stagnation counter); reward = population-mean normalized improvement (Eqs. 7–8, local p. 4). Policy trained by actor–critic policy gradient (Eq. 9, local p. 4), Adam, lr 0.001, 200 epochs; the trained controller is then used **offline** during search (Fig. 1, local p. 2).
- **Basic GSK recap:** junior/senior mutation equations and the junior-dimension schedule DJ = D·((MAXNFES−NFES)/MAXNFES)^k are restated in Sec. III-A (Eqs. 1–2 and the two mutation rules, local p. 3).

## 4. Experimental scope
- **Suite:** CEC 2017 test functions; F2 excluded for instability; training used F1–F20, testing used all functions (Sec. V, local p. 4).
- **Dimensions:** D = 10 and D = 30 only; separate controllers trained per dimension (local p. 4).
- **Runs/budget:** 51 runs per function; termination at MAXNFES = D·10^4 FES or error < 1e−8 (local p. 5). GSK defaults NP = 100, p = 0.1, k = 10; H = 100 (local p. 4).
- **Comparator:** basic GSK with default parameters ONLY. The paper states explicitly the comparison "shows the significance of learning the GSK algorithm parameters and not to show the competence of GSK-RL with other control parameter adaption techniques" (Sec. V, local p. 4).

## 5. Findings (conservative)
- **D = 10** (Table I, local p. 5; summary local p. 5, Sec. VI): GSK-RL better on 14 functions, equal on 5, worse on 10 (out of 29).
- **D = 30** (Table II, local p. 5; summary local pp. 5–6): GSK-RL better on 16, equal on 4, worse on 9 (the 9 include F26, where GSK-RL is unstable: mean 1.70E+03 vs 3.00E+02 for basic GSK).
- **Degradation with dimension:** "performance started to degrade on 30 dimensional problems and it showed unstable behaviour on some functions that the controller has never been trained on before" (Abstract, local p. 1; Conclusion, local p. 6).
- **Authors' main conclusion:** neither the state definition nor the reward function was critical; the training functions and collected trajectories dominate the quality of an RL-based GSK parameter controller (Abstract local p. 1; Conclusion local p. 6).
- **Symbol convention warning:** in Tables I–II the Wilcoxon rank-sum column WR uses an INVERTED convention: "+, −, and ≈ indicates that GSK-RL performs significantly **worse, better** and similar to the Basic GSK" (local p. 5). Do not read "+" as a GSK-RL win.

## 6. Limitations
- Same-family comparison only (GSK-RL vs. basic GSK); no external comparators.
- Only D=10 and D=30; generalization failure documented on F26 at D=30.
- Author-version PDF: no archival venue/DOI/pagination on the document itself.
- Footnote 2 (local p. 4) claims a side run of "adaptive GSK" was "not significant compared with the Basic GSK" — an unsubstantiated aside, not usable as evidence about AGSK.
- The paper's own reference [26] for "CEC 2017" is the Wu/Mallipeddi/Suganthan CONSTRAINED CEC 2017 report (local p. 6, ref list) — a mis-citation inside the source; do not launder a CEC2017 bound-constrained suite definition through this paper.

## 7. Usable locators (claim → locator)
| Claim | Locator |
|---|---|
| GSK has two main control parameters kf, kr; basic GSK has no adaptation scheme | Abstract + Sec. I, local p. 1 |
| RL/neural (actor–critic) adaptation of kf, kr; pool of six (µKf, µKr) pairs | Sec. III-B + Sec. IV item 2, local p. 3 |
| kf, kr sampled from normal distributions, means from policy, σ from H-entry success memories | Eqs. 3–6, local p. 3 |
| State/reward definitions for the MDP | Sec. IV items 1 and 4, Eqs. 7–8, local pp. 3–4 |
| CEC2017, D∈{10,30}, 51 runs, MaxFES = D·10^4, F2 excluded, NP=100, p=0.1, k=10 | Sec. V, local pp. 4–5 |
| D10 result 14 better / 5 equal / 10 worse; D30 result 16 / 4 / 9 (F26 unstable) | Tables I–II + Sec. VI, local pp. 5–6 |
| Training functions/trajectories matter more than state or reward design | Conclusion, local p. 6 |

## 8. Supported uses in the DT-GSK manuscript
- Related-work sentence: an RL/actor–critic-learned controller has been proposed to adapt GSK's kf and kr, evaluated only against basic GSK on CEC2017 at D=10/30, with gains at low dimension and degradation/instability at D=30 and on unseen functions.
- Evidence that GSK-variant literature identifies fixed kf/kr as an adaptation target.

## 9. Unsupported / prohibited overextensions
- Do NOT claim GSK-RL outperforms other adaptive GSKs (AGSK/APGSK) or any non-GSK algorithm — never tested.
- Do NOT cite this paper for the CEC2017 bound-constrained suite definition (its own suite citation is to the constrained report; our `awad2016problem` is BLOCKED).
- Do NOT claim general RL superiority for parameter control; the authors themselves report instability and trainer-dependence.
- Do NOT use the footnote-2 "adaptive GSK not significant" aside as a claim about AGSK.

## 10. Role in DT-GSK framing (Appendix B)
Appendix B.2 — "GSK variants and hybrids — related-work breadth only." Cite only where the verified mechanism (RL-based kf/kr adaptation of GSK) is actually discussed; no obligatory one-sentence mention.
