# Panel review register — round 3 / FDR (2026-07-31, pass-28 / v2.3 basis)

Instrument: `papers/PAPER_REVIEW_PROMPT.md` with **Section 18 (forensic deep-review
layer)** active — its first application, including the first-ever execution of the
18.4 authorship-defensibility audit. Seven simulated forensic seats (LLM agents), every finding
adversarially verified refute-by-default (14 agents). Basis: pass-28, anchor
`70c51ba`, tag `v2.3`. Standings verified from the frozen release CSVs at every
seat that cites one; no number restated from memory.

**Round verdict: MINOR REVISION — no CRITICAL, no blocker.** 36 findings raised,
**35 CONFIRMED**, 1 REFUTED (the refutation itself enforcing a registered hedge —
see the cross-seat note below). Confirmed by final severity: **1 MAJOR, 5
MODERATE, 11 MINOR, 6 EDITORIAL, 12 ADVISORY**; by fix class: 24 manuscript (one
batch = pass-29 re-mint + superseding v2.4 tag), 6 repo-only, 1 author-side, 4
none (pattern observations). No finding touches a number, rank, p-value, test,
standing, or registered outcome.

**Authorship-defensibility result (18.4, first execution): overall risk LOW on
both documents; authenticity tri-state: AUTHOR-GROUNDED.** Zero hits on the
18.4.1 live risk-phrase library in either document (no transition monoculture, no
filler idioms, no unevidenced exploration–exploitation claims, no inflated
novelty, no unsupported significance/superiority — all 56 main-text 'significant'
uses trace to Holm-corrected tests or negations; all superiority vocabulary is
negation). The one genuine single-voice signature is the corrective-contrast
template ('X rather than Y' 47x main + 32x supplement; ', not Y' 34x;
'therefore' 26x) plus an unregistered honesty-meta-narration habit — recorded as
ADVISORY pattern observations (AUTH-02/03/05, AUTH-SUPP-01) with no scientific
weakness beneath them. Per 18.4.0/18.4.3: this rating is cumulative and
contextual; style alone can neither prove nor disprove authorship, and the
disclosed GenAI assistance (Claude Opus 4.6/4.8/5.0, AG-0007) played no part in
it.

**Notable: four findings are incompleteness of the ROUND-2 batch itself** —
CE-01/CITE-REP-02 (three residual loci of the pre-r2 NP=100 provenance claim, so
the shipped manuscript now self-contradicts on comparator provenance: the r2
S1-01 fix landed at its named loci but the sweep missed `performance.tex:140`,
`main.tex:383-384` COI, `proposed_algorithm.tex:719/758`) and REG-01/MATH-02 (the
m-vs-M arm-count rename left `proposed_algorithm.tex:814-815` and the scaffold
notation table on the old symbol, creating a live m/M self-contradiction). The
regression seat otherwise verified all 21 round-2 fixes correctly applied, the
committed blobs 15/15, both DOCX deterministic-build-signed, and both PDF header
blocks correct.

## Seat verdicts

| Seat | Verdict | Findings | Auth risk |
|---|---|---|---|
| AUTH-MAIN | READY_WITH_NITS | 5 | Low |
| AUTH-SUPP | READY | 2 | Low |
| MATH-17PT | MINOR_REVISION | 10 | Low |
| REGRESSION | MINOR_REVISION | 2 | Low |
| CLAIMS-EIC | MINOR_REVISION | 5 | Low |
| SEM-CONSIST | READY_WITH_NITS | 4 | — |
| CITE-REP | MINOR_REVISION | 8 | Low |

## Confirmed findings (severity order)

| # | Seat/id | Sev/Pri/Conf | Fix class | Locus | Finding | Suggested fix |
|---|---|---|---|---|---|---|
| 1 | CLAIMS-EIC/CE-01 | MAJOR/P1/Confirmed | manuscript | papers/sections/performance.tex:140; papers/main.tex:383-384; papers/sections/pr | Three residual loci retain the pre-round-2 comparator-configuration provenance claim that fix S1-01 corrected elsewhere, so the shipped manuscript now contradicts itself on where the comparators' NP=100 comes from. | One pass-29 batch (voids pass-28, v2.4-style superseding tag): performance.tex:140 -> 'comparator configurations follow the family's shipped reference implementations (Table 6; Section 3.7 discloses where these differ from the source papers |
| 2 | CITE-REP/CITE-REP-01 | MODERATE/P2/Confirmed | manuscript | papers/sections/performance.tex:42-44 (cited locus); pattern also at papers/sect | The manuscript attributes the fmincon solver detail to the eGSK publication — 'the original reference implementation uses a fmincon-based SQP solver~\cite{jawad2024egsk}' — and repeats 'published fmincon(-based) solver/polish' or 'published MATLAB fmincon polish' at five further loci, but the cited  | At performance.tex:42-44 anchor \cite{jawad2024egsk} to the SQP mechanism and attribute fmincon to the reference code, e.g. '...whereas the original algorithm's late refinement is a sequential-quadratic-programming polish~\cite{jawad2024egs |
| 3 | CITE-REP/CITE-REP-02 | MODERATE/P2/Confirmed | manuscript | papers/sections/proposed_algorithm.tex:718-719 and :758; papers/main.tex:382-383 | Three residual loci still attribute the comparators' run configuration to their publications after the r2 S1-01 fix: 'the six comparators run their published reference constants' (proposed_algorithm.tex:719); 'The exact numeric settings behind ``published constants'' are reproduced...' (:758, a self | proposed_algorithm.tex:719 → 'the six comparators run their reference-implementation constants'; :758 → 'The exact numeric settings behind ``reference-implementation constants'' are reproduced...'; main.tex:383 → 'every comparator was re-ex |
| 4 | MATH-17PT/MATH-01 | MODERATE/P2/Confirmed | manuscript | papers/supplementary.tex:1646 (S5 'Event-driven updates'); papers/build_prompt_p | The interaction-graph restart-decay trigger is misattributed: S5 says the retained graph is halved (x0.50) with a five-generation block cooldown 'after a deep-stall restart', and the detail table says it is 'applied on each BSE/deep-stall restart', but the code applies it ONLY on BSE escape events a | In supplementary.tex:1646 replace 'after a deep-stall restart' with 'after a budget-safe-escape event (a partial restart, or any Cauchy perturbation — including a successful rescue that cancels the restart)'; in parameter_table_detail.tex:6 |
| 5 | REGRESSION/REG-01 | MODERATE/P2/Confirmed | manuscript | papers/sections/proposed_algorithm.tex:814-815 (Sec. 3.8, DT-GSK.pdf p.22) + pap | The S1-06(c) arm-count disambiguation was applied incompletely, leaving the frozen pass-28 manuscript with two symbols for the ACE arm count and an explicit self-contradiction: Sections 3.3.1/3.3.2 were renamed to lowercase m ('$O(NP + m)$ for $m\in\{5,6\}$ arms'; '$O(m\cdot W_{\text{argp}})$') and  | Unify to one symbol, one meaning (voids pass-28 -> pass-29 re-mint + v2.4 tag). Cheapest coherent option A (per the register's own first alternative): keep M as the arm count everywhere — revert proposed_algorithm.tex:347/363 (and main_pand |
| 6 | SEM-CONSIST/SEM-01 | MODERATE/P2/Confirmed | manuscript | papers/supplementary.tex:1311-1411 (S5.4) vs papers/sections/conclusions.tex:86- | The limitation lists diverge: the conclusions carry the parameter-sensitivity limitation ("No parameter-sensitivity study was performed: the tier constants are frozen and hash-locked, and the individual influence of each is unmeasured. Neither ARGP nor the deep-stall restart is isolated by the remov | Supplement (preferred): insert into S5.4, before the 'Beyond these' coda: "Ninth, no parameter-sensitivity study was performed: the tier constants are frozen and hash-locked, and the individual influence of each is unmeasured; neither ARGP  |
| 7 | AUTH-MAIN/AUTH-01 | MINOR/P3/High | manuscript | papers/main.tex:162-165 (abstract) | The abstract clause "it is second behind eGSK at $D = 30$ and on CEC2011" is suite-ambiguous in the favorable direction: it immediately follows a compound naming BOTH CEC2017 (2.48) and CEC2013 (2.80), yet the "second at D=30" reading is true only on CEC2017; on CEC2013 at D=30 DT-GSK is THIRD, behi | Scope the clause to the primary suite, e.g. "it is second behind \egsk{} at CEC2017's $D = 30$ and on CEC2011" (+1 word against the ~204-word rendered abstract). This sentence is bound (RS-01 NARROWED) but is not a registered verbatim, so i |
| 8 | CITE-REP/CITE-REP-03 | MINOR/P2/Confirmed | manuscript | papers/references.bib:629 (kolda2003directsearch, doi field); rendered as DT-GSK | The kolda2003directsearch DOI is truncated — the bib and the rendered PDF print doi:10.1137/S003614450242889, missing the final '3' of the source-printed DOI 10.1137/S0036144502428893 — and the repo's own recorded resolution ('adopt source DOI') was never executed. | Correct references.bib:629 to doi = {10.1137/S0036144502428893} via the CR-0004-style metadata-correction pattern (admitted key, no corpus change); rebuild in the pass-29 batch. Kolda is cited at three manuscript loci, so the broken DOI is  |
| 9 | CITE-REP/CITE-REP-04 | MINOR/P3/High | manuscript | papers/sections/proposed_algorithm.tex:157-160 — 'the setting of the family's sh | The r2-reworded NP=100 passage makes a checkable factual claim about the comparators' source papers (dimension-scaled populations) with no citation, and supporting citations ARE available inside the closed corpus — no CR-gated admission is needed. | Append the in-corpus citations at the clause: '...differs from the dimension-scaled populations of their source papers~\cite{mohamed2020agsk,apgsk2021,fdbagsk2023} ---'. Zero-risk edit (all keys admitted, C1-C5 unaffected); batch into pass- |
| 10 | CITE-REP/CITE-REP-05 | MINOR/P3/Confirmed | repo-only | papers/governance/citation_usage_map.csv (142 data rows, spot-check note dated 2 | The citation usage map is stale relative to the pass-28 tree: it omits all five Amendment-3 apgsk2021 runner-up loci and carries drifted line numbers for at least 15 rows, while the C1-C5 gate reads the map without ever diffing it against the tex, so citation_controls stays green over a stale regist | Regenerate/append the usage-map rows for the five apgsk2021 loci (semantic_role 'APGSK/adaptive-parameter family baseline', context = the runner-up sentence) and refresh line numbers; optionally add a map-vs-tex \cite diff step to validate_ |
| 11 | CLAIMS-EIC/CE-02 | MINOR/P3/Confirmed | repo-only | papers/governance/claims_evidence_matrix.csv rows LM-05, CL-02, MT-02/MT-04/MT-0 | The claims-evidence matrix has drifted from the shipped post-round-2 wording at two templates and six stale code-line pins; the register the review prompt names as a claim authority no longer matches the manuscript it governs. | Update LM-05's template to the per-suite ceilings ('D<=100 on CEC2017, D<=50 on CEC2013, ...'), annotate CL-02 with a dated note binding it to the shipped R-0004 letter wording (or rewrite the template to the letter's actual headline senten |
| 12 | MATH-17PT/MATH-02 | MINOR/P2/Confirmed | manuscript | papers/build_prompt_phases/phase_03/equations.tex:197-198; notation_table_scaffo | The round-2 m-vs-M repair (S1-06(c)) is incomplete: M still carries two meanings (ACE arm-pool size in tab:notation-scaffold and the complexity paragraph; RNG child-seed modulus in Eq. (13), tab:notation-rng, and S5), and the arm count itself flips casing — m in the ACE/ARGP subsections and in E12's | Rename the modulus (e.g. $M_{\mathrm{seed}}$) at its four loci (E12 + its disclaimer, tab:notation-rng, supplementary.tex:1713) via the equation-registry CR path, and unify the arm count to M at proposed_algorithm.tex:347-348 and :363 (matc |
| 13 | MATH-17PT/MATH-03 | MINOR/P3/High | manuscript | papers/supplementary.tex:1860-1866 (S5 'Population-size floor and callback coupl | The callback-coupling reproducibility caveat is stale against the shipped module: the link-lift EMA read-back is stated to be 'updated inside the per-generation callback path' such that 'a callback-less direct invocation of the core would omit it and diverge at D>=100', but in the shipped _dt_core.p | Reword to the current fact: the link-lift EMA update runs unconditionally in the per-generation loop (moved out of the telemetry callback during the bit-identical-certified CR-0013..0018 campaign), so no callback-presence divergence is poss |
| 14 | MATH-17PT/MATH-04 | MINOR/P3/Confirmed | manuscript | papers/build_prompt_phases/phase_03/equations.tex:153 (rendered Eq. (10)); paper | Eq. (10) restricts the Cauchy rescue to 'unfrozen rows', but no main-document text defines what freezes a row: the elite-freeze rule (top round(0.05*NP) rows by fitness exempt from rescue and restart) exists only in Supplementary S5, and the main-text BSE prose says the rescue perturbs 'the worst r_ | Add one clause to Section 3.3.4 (proposed_algorithm.tex ~line 424): 'the top round(0.05 NP) rows by fitness are frozen — exempt from both the rescue and the restart (Supplementary S5)', anchoring Eq. (10)'s 'unfrozen'. |
| 15 | MATH-17PT/MATH-05 | MINOR/P3/Confirmed | manuscript | papers/build_prompt_phases/phase_03/equations.tex:105 + notation_table_scaffold. | Residual s-family symbol collisions across the two documents (not covered by round-2 S1-06): s_i means the arm drawn by individual i in main-text Eq. (7) and the scaffold notation table, but means the ISM per-move source weight (0 / 0.25 / 1) in S5; and the BSE Cauchy scale is r_s in the main text b | In S5 rename the ISM source weight (e.g. $\varsigma_i$ or $w^{\mathrm{src}}_i$) and replace the escape scale s with the main text's $r_s$ at supplementary.tex:1709 and :1789; add a defining clause for s_i ('where $s_i$ is the arm drawn by i |
| 16 | SEM-CONSIST/SEM-02 | MINOR/P2/Confirmed | manuscript | papers/sections/performance.tex:986-988 vs papers/supplementary.tex:671-676 and  | The main text promises supplement content that does not exist: "The complete function $\times$ dimension convergence sets for CEC2017, CEC2011 and CEC2013 are in the Supplementary Materials, Section~S3" — for CEC2013 (tested at D in {10,30,50}) this reads as 28x3 grids, but S3 carries and explicitly | Main: replace the sentence with "The complete convergence sets --- CEC2017 at all four dimensions, CEC2011 at native dimensions, and CEC2013 at the prespecified $D = 30$ --- are in the Supplementary Materials, Section~S3." Supplement: no ch |
| 17 | SEM-CONSIST/SEM-03 | MINOR/P3/Confirmed | manuscript | papers/supplementary.tex:187-190 vs papers/sections/performance.tex:78-81 and ta | The supplement's authoritative shared-protocol block ("Unless a caption states otherwise, the following frozen protocol applies throughout", supplementary.tex:176-177) states the evaluation budget for four of the five suites but omits CEC2013's MaxFES: the CEC2013 sentence gives only "28 functions,  | Supplement: extend supplementary.tex:187-190 to "...28 functions, $D \in \{10, 30, 50\}$, 51 runs per cell, and $\mathrm{MaxFES} = 10^{4} \cdot D$~\cite{liang2013cec2013}." Main: no change. Batch into the same pass-29 re-mint. |
| 18 | AUTH-MAIN/AUTH-04 | EDITORIAL/P4/High | manuscript | papers/main.tex:95-96,156-159,188 vs body; papers/sections/introduction.tex:148 | Contribution-name churn on the two headline contributions: (a) the title/abstract/keyword term "Deterministic (Final) Refinement" is never explicitly equated with the body's canonical "eigenframe final polish" (C1) — the bridge is only implicit; (b) introduction.tex:148 names C3 "the controlled, bud | Optional, batch-only (do not re-mint for this alone): one bridging clause at first use in Section 1 (e.g. "the deterministic refinement of the title, hereafter the eigenframe final polish") and align intro:148's C3 name to "the controlled,  |
| 19 | CLAIMS-EIC/CE-04 | EDITORIAL/P4/High | manuscript | papers/sections/performance.tex:1117-1119 | In the second alternative explanation, the relative clause 'which is a design choice inherited from the family's reference-implementation configuration' has a loose antecedent: read strictly it attributes DT-GSK's own NP=5D (or the whole five-fold difference) to the family reference implementations, | Only if a pass-29 batch opens for CE-01 (same passage family): '...against the comparators' NP=100 --- a five-fold difference at D=100. The comparators' value is the family's reference-implementation setting and the asymmetry was not a cont |
| 20 | CLAIMS-EIC/CE-05 | EDITORIAL/P4/Confirmed | manuscript | papers/cover_letter.tex:57 | The cover letter's opening result sentence contains a comma splice and a stranded 'To our knowledge' hedge that now qualifies a computed panel rank rather than the novelty claim it originally scoped. | Batch-only (cover_letter.pdf is manifest-tracked; author re-approval needed since R-0004 closed on this text): change the comma to a semicolon and either delete 'To our knowledge' or move it to the sentence's evaluative clause. Do not re-mi |
| 21 | MATH-17PT/MATH-06 | EDITORIAL/P4/Confirmed | manuscript | papers/sections/proposed_algorithm.tex:556-557 (vs :510-512 and :545-546) | Cadence-verb ambiguity: 'The graph itself is ... rebuilt every 5 generations at D=50 and every 20 at D=100' numerically matches the block re-EXTRACTION cadence (5/20), but 'rebuilt' invites the graph-update reading, which the same subsection states is every generation at D=50-99 and every 10th at D> | Replace 'rebuilt' with 're-extracted into blocks' at :556-557 so the three cadences carry three fixed verbs (updated / re-extracted / mask refreshed). |
| 22 | MATH-17PT/MATH-07 | EDITORIAL/P4/Confirmed | manuscript | papers/sections/proposed_algorithm.tex:481 | Undefined borrowed symbols in the differential-grouping cost 'of order O(n^2/m)': neither n nor m is defined in this paper; the paper's dimension symbol is D, and m is the ACE arm index everywhere else, compounding the MATH-02 collision. | Either gloss in place ('of order O(D^2/g) for g subcomponents, in the cited work's notation') or drop the formula ('a dedicated offline budget of pairwise probing evaluations, quadratic in dimension'). |
| 23 | MATH-17PT/MATH-08 | EDITORIAL/P4/Confirmed | manuscript | papers/supplementary.tex:1755-1757 (S5 'Senior widening and the differential-evo | Internal S5 wording slip: 'each arm's credit is the summed (not averaged) accepted improvement of the individuals that drew it' — the credit is actually the summed SIGNED fitness delta over ALL evaluated individuals that drew the arm (rejected/worsening trials contribute negatively), exactly as the  | Change 'summed (not averaged) accepted improvement' to 'summed (not averaged) signed fitness delta'. |
| 24 | AUTH-MAIN/AUTH-02 | ADVISORY/P4/Confirmed | none | global; densest in papers/sections/performance.tex (18+) and papers/sections/pro | The manuscript's one genuine rhetorical monoculture is the corrective-contrast template: "X rather than Y" (47 instances) plus the ", not Y" apposition (34 instances) plus consequence-drawing "therefore" (26 rendered instances) — a single sentence shape carrying most of the paper's scoping work. | None recommended. 18.4.0 forbids fixing by stylistic variation alone, and every instance is individually defensible; recorded for the Part-F register and the risk rating only. |
| 25 | AUTH-MAIN/AUTH-03 | ADVISORY/P4/Confirmed | none | papers/sections/performance.tex:17,180,522,631-633,872-874,894,991; papers/secti | An unregistered meta-narration habit sits ON TOP of the sanctioned disclosures: the text repeatedly narrates its own honesty ("is disclosed rather than implied", "discussed rather than skipped", "rather than hidden", "stated plainly", "recorded rather than presented as the check itself", "reported a | No pre-submission change recommended; if a future revision cycle opens for other reasons, two or three of the most self-referential clauses (e.g. "discussed rather than skipped") could be dropped without losing any disclosure content. |
| 26 | AUTH-MAIN/AUTH-05 | ADVISORY/P4/Confirmed | none | papers/sections/introduction.tex:148; papers/sections/proposed_algorithm.tex:224 | Three voice discontinuities: single-line unwrapped paragraphs in a denser, more defensive hedged register than the surrounding hard-wrapped prose (the ISM-demotion paragraph, the upper-tier cross-cutting note, and the APGSK-recovery disclosure), marking late-pass insertions. | No action required. If a pass-29 cycle opens anyway, re-wrap the three lines to house style and lightly harmonize intro:148's register; never introduce variation to imitate humanity. |
| 27 | AUTH-SUPP/AUTH-SUPP-01 | ADVISORY/P4/Confirmed | none | papers/supplementary.tex:234,544,1057,1180,1298-1299,1306,1330,1392,1431,1512,16 | One unregistered rhetorical construction recurs at high density across the S5-S8 prose: the defensive contrast "X rather than Y" (32 instances, clustering to 3 in the single paragraph at 1934-1947 and 2 in adjacent sentences at 2439-2440), alongside the companion vocabulary "disclosed/disclosure" (3 | No edit. 18.4.2 forbids fixing by stylistic variation alone, and there is no scientific weakness beneath any instance - each contrast is evidence-tied disclosure. Recorded so the pattern is on the register with honest counts; if any future  |
| 28 | CITE-REP/CITE-REP-06 | ADVISORY/P4/Confirmed | repo-only | papers/references.bib:697-708 (yang2008large) and :724-737 (zhong2023lmm); stale | references.bib holds 63 keys against the closed 61-key corpus: yang2008large (the DECC-G paper) and zhong2023lmm are outside allowed_citation_keys.txt and cited nowhere (no \cite/\nocite in any tex), so they never render — but their presence invites accidental future citation outside change control, | Either delete the two unadmitted entries from references.bib (git history preserves them; BibTeX output is unchanged) or add a dated comment recording their sanctioned dormancy and the CR that would govern any future citation; update the st |
| 29 | CITE-REP/CITE-REP-07 | ADVISORY/P4/High | repo-only | papers/sections/performance.tex:885-891 and papers/supplementary.tex:2417-2423 v | The registered LM-06 specialist sentence ('SHADE-ILS...and MOS...report substantially stronger published results on this suite than any GSK-family member') satisfies neither card's letter-level proviso — both sanction the LM-06 use 'PROVIDED the sentence quotes the published values' and does not set | Reconcile in governance, not prose: annotate the two role-map rows (and/or the cards) that adopted disclosure sentence (a) — qualitative, valueless, with the no-competitiveness disclaimer — is the sanctioned LM-06 instantiation, superseding |
| 30 | CITE-REP/CITE-REP-08 | ADVISORY/P4/Medium | repo-only | papers/sections/performance.tex:72-77 — 'receive the suite's standard infeasibil | The phrase 'the suite's standard infeasibility penalty' attributes the 10^30 convention to CEC2011, but the das2011cec2011 evidence card (the paragraph's citation anchor) sanctions no penalty convention; the value is grounded only in the repo's own constant, whose docstring asserts — unverified agai | Preferred: verify the 1e30 convention against the CEC2011 organisers' reference code and extend the das2011cec2011 card via the lockstep (repo-only; no manuscript change). If verification fails or is skipped, the wording fix 'the reference  |
| 31 | CLAIMS-EIC/CE-03 | ADVISORY/P4/High | author-side | papers/sections/performance.tex:1121-1123 vs papers/supplementary.tex:1279-1282  | The third alternative explanation asserts a temporally stronger development-history fact ('the single configuration was fixed on CEC2017 before either suite was seen') than the attested S5.3 disclosure ('no CEC2011 or CEC2013 result was consulted during configuration selection'), and the register no | Author verification item: confirm the temporal form is attestable (no CEC2011/CEC2013 result existed or was viewed before configuration freeze); if only non-consultation can be attested, align the clause to 'was fixed on CEC2017 without con |
| 32 | MATH-17PT/MATH-09 | ADVISORY/P4/Confirmed | manuscript | papers/supplementary.tex:1650-1656 (S5 'Graph-to-block extraction') vs src/gsk_f | The normative S5 adjacency rule omits a code fallback: when a row of the max-normalized graph has no edge >= max(phi, half its row max) — possible only when its row max is below phi=1e-4 — the code keeps that row's top-(b_max - 1) positive edges anyway, so phi is not a hard floor in that edge case. | Optional one-clause addition to S5: 'a row with no edge above the floor retains its strongest positive edges (at most b_max - 1) as a fallback'. May ride along with the MATH-01 batch or be dropped. |
| 33 | MATH-17PT/MATH-10 | ADVISORY/P4/Confirmed | manuscript | papers/build_prompt_phases/phase_03/algorithm_pseudocode.tex:35 vs papers/sectio | Algorithm 1 initializes the interaction graphs G_abs, G_signed <- 0 unconditionally (no D>=50 gate on that line), while the prose states the graph 'is allocated only at D>=50' and the complexity section states 'For D<50 no D^2 or D^3 interaction structure is allocated'; an implementer following the  | Prefix line 35 with 'if $D{\ge}50$:' (matching lines 55 and 60), or append '(allocated only at $D\ge50$)'. |
| 34 | REGRESSION/REG-02 | ADVISORY/P4/Confirmed | repo-only | PROJECT_RULES.md:4; PERFORMANCE_RULES.md:4; ARCHITECTURE.md:4,65; BENCHMARK_RULE | S4-8 is complete at all four registered loci (runbook.md:3, PROJECT_RULES.md:59/65, PERFORMANCE_RULES.md:78 verified fixed and correct), but the same defect class — the private monorepo workspace presented as current identity — survives at ~14 unregistered loci in the public tree, including the inte | One sweep commit before the repo goes public: replace the internal codename/paths with the standalone-repo identity (DT-GSK, repository root) or add the one-line provenance note the register already sanctioned ('these operating rules were w |
| 35 | SEM-CONSIST/SEM-04 | ADVISORY/P4/Confirmed | manuscript | papers/main.tex:156-159 (abstract) and papers/sections/conclusions.tex:19-21 vs  | Cross-document precision asymmetry on the ISM learning signal: the supplement opspec and cover letter uniformly say the memory accumulates from "strictly improving accepted moves" ("accumulated solely from strictly improving accepted moves"), while the abstract says "learned from accepted moves" and | If (and only if) a pass-29 batch happens anyway: conclusions.tex:20 -> "learned from the strictly improving moves the run has already accepted". The abstract locus is a frozen-abstract PROPOSAL per 18.2(i) ("learned from strictly improving  |

Duplicate cluster: CE-01 = CITE-REP-02 (same three residual NP-provenance loci);
REG-01 = MATH-02 (same incomplete m-vs-M rename, complementary loci lists). One
fix each discharges both rows.

## Refuted (audit record; do not action)

- **AUTH-SUPP/AUTH-SUPP-02** — The cover letter's headline sentence hedges a panel-internal computed fact with a literature-priority hedge: "To our knowledge" is the wrong scope for a rank that is fully determined by the study's own frozen CSV (verified: dt-gsk 2.482759, egsk 2.961207 in pa **Refutation:** Factually accurate (quote exact at cover_letter.tex:57; frozen CSV confirms dt-gsk 2.482759 / egsk 2.961207; per-dimension gaps 1.362069/0.206897/0.413793/0.344827 all < CD ~1.673) but inadmissible under the binding rules. The 'To our knowledge' hedge is a REGISTERED hedge: claims-matrix row CL-02 (papers/governance/claims_evidence_matrix.csv:48, status ACCEPTED_PHASE_6) records the cover-letter headline claim with r

**Cross-seat scoping note (binding for any fix):** the refutation of
AUTH-SUPP-02 establishes that the cover letter's 'To our knowledge' is the
REGISTERED CL-02 hedge. Confirmed CE-05 (same sentence) is therefore actionable
only in its comma-splice half; any repositioning of the hedge must preserve the
registered CL-02 scope, or go the amendment path.

## Repeated-phrase inventories (18.4.3, honest grep counts)

### AUTH-MAIN

| Count | Phrase | Loci |
|---|---|---|
| 47 | rather than (corrective contrast) | introduction.tex 3; related_work.tex 6; proposed_algorithm.tex 13; performance.tex 18; conclusions.tex 6; main |
| 34 | , not (corrective apposition, same template family) | all six files; densest in performance.tex and proposed_algorithm.tex |
| 28 | therefore | 26 rendered prose + 2 comments; performance.tex 15, proposed_algorithm.tex 7, conclusions.tex 2, introduction. |
| 1176 | --- (em-dash interpolated qualifier; raw count incl. comments/tables) | introduction 19; related_work 161; proposed_algorithm 405; performance 475; conclusions 19; main 97 |
| 75 | frozen | all files (governance register vocabulary; function words of the registered discipline, not filler) |
| 56 | significant / no significant difference | performance.tex and conclusions.tex; spot-verified — every instance is tied to a Holm-corrected test, an omnib |
| 36 | descriptive | performance.tex predominately (evidential-tier discipline) |
| 33 | registered | performance.tex, conclusions.tex (SAP-addendum vocabulary) |
| 32 | disclos* (disclosed/disclosure/discloses) | performance.tex 15, proposed_algorithm.tex 5, conclusions.tex 2, introduction.tex 2, main.tex back matter |
| 28 | this paper (incl. 'in this paper' x14) | all six files |
| 17 | claim-scoping formula (not claimed / no claim / is claimed) | proposed_algorithm.tex, performance.tex, related_work.tex, conclusions.tex |
| 8 | sentence-initial 'On CEC...' suite opener | performance.tex and conclusions.tex suite paragraphs (structural, mirrors registered suite-by-suite reporting) |
| 3 | internal-validity triad 'one code base/protocol/budget, one ..., one ...' | introduction.tex:141; performance.tex:30-31; conclusions.tex:120 |
| 0 | balance between exploration and exploitation (18.4.1 flagship risk phrase) | absent; sole adjacent use is the cited bandit framing 'dynamic exploration--exploitation problem' (related_wor |
| 0 | Furthermore / Moreover / Additionally / Consequently / In addition / not only... | absent from all six files (the classic transition monoculture does not exist here) |
| 0 | filler idioms (crucial, vital, delve, leverage, utilize, pivotal, in recent year | absent from all six files |
| 1 | state-of-the-art | related_work.tex:276 — a negated priority-claim disclaimer ('it is not a state-of-the-art priority claim'), i. |

### AUTH-SUPP

| Count | Phrase | Loci |
|---|---|---|
| 0 | Furthermore / Moreover / In addition (paragraph transitions) | none in rendered prose of supplementary.tex or cover_letter.tex - no transition monoculture |
| 1 | Additionally | supplementary.tex:1204 (adverbial 'additionally asserts' inside the provenance chain; not a paragraph transiti |
| 1 | Consequently | supplementary.tex:1299 (S5.3 selection-exposure paragraph; earned inferential connective) |
| 0 | valuable insights / opens new avenues / achieves a good balance between explorat | zero hits across both files - the 18.4.1(1)/(5)/(6) live risk phrases are entirely absent |
| 1 | novel | supplementary.tex:1795 ('basin-novelty pool' - technical component name, not a novelty claim) |
| 5 | superior / superiority | supplementary.tex:400,1345,1961,2632,2905 - every instance is a NEGATION ('no claim of superiority ... is made |
| 1 | outperform | supplementary.tex:2243 - stated as an open question ('whether the learned eigenbasis outperforms coordinate ax |
| 8 | significantly | supplementary.tex:433,934,948,962 (registered CEC2011-eGSK-loss disclosure, sanctioned multi-locus repetition) |
| 14 | robust / robustness | all refer to the registered robustness battery/variants (r01/r04, tie-band, floor-sensitivity, aggregate varia |
| 5 | guarantee | supplementary.tex:1070 x4 area + cover_letter.tex:57 - all negative-scope ('No byte-stability guarantee is ext |
| 32 | rather than (defensive contrast construction) | supplementary.tex:234,544,1057,1180,1298-1299,1306,1330,1392,1431,1512,1641,1646,1722,1726,1771,1849,1899,1934 |
| 33 | disclosed / disclosure(s) | distributed across S1-S8 prose and captions; the sanctioned disclosure machinery's vocabulary (registered hedg |
| 2 | we believe | supplementary.tex:2316 (hedged, attached to the controlled ISM negative result); cover_letter.tex:59 ('We beli |
| 5 | This section/appendix/subsection ... (section-opener template) | supplementary.tex:592,671,1065,1520,1979 - only 5 across 8 sections + 30 subsections; S1/S2/S4 open exhibit-fi |
| 16 | disclosed limitation (caption repetition) | S3 convergence captions - sanctioned self-contained-caption convention declared at supplementary.tex:168-171 |
| 11 | All panels carry (the full) 7/7 series (caption repetition) | S3 figure captions ('All panels carry'=6, '7/7 series'=11) - same sanctioned caption convention |
| 4 | significantly loses to eGSK (registered CEC2011 outcome disclosure) | supplementary.tex:433,934,948,962 - deliberate multi-locus repetition of a registered caveat; sanctioned |
| 3 | places third by Friedman mean rank (registered CEC2013-D30 disclosure) | supplementary.tex:456-457,975-976,986-987 - sanctioned registered repetition |
| 2 | no separation demonstrated, never as equivalence (registered power-disclosure fo | supplementary.tex:2520-2521 (S7), 2959-2960 (S8) - deliberate parallel of the pre-committed addendum Section 7 |
| 5 | Evidential tier: (registered tier label) | S7/S8 captions and prose - carries the addendum's registered tier discipline; sanctioned |

### CITE-REP

| Count | Phrase | Loci |
|---|---|---|
| 6 | published fmincon(-based) solver / published MATLAB fmincon polish | performance.tex:43 (only cited locus, \cite{jawad2024egsk}); proposed_algorithm.tex:721, 748-749; conclusions. |
| 3 | published (reference) constants / published configuration | proposed_algorithm.tex:719, 758; main.tex:383 (COI) — residues of the r2 S1-01 MAJOR fix (finding CITE-REP-02) |
| 5 | the CEC2020 competition in which it was the runner-up~\cite{apgsk2021} (and adja | conclusions.tex:61; performance.tex:801, 877-878; supplementary.tex:2860, 2887-2888; plus cite-free abstract ( |
| 4 | no runtime-superiority claim is made (anywhere in this paper) | performance.tex:49; conclusions.tex:104; supplementary.tex:1344-1345, 1960-1961 — registered LM-04 disclosure  |
| 2 | no competitiveness with such specialists is claimed here | performance.tex:890; supplementary.tex:2422 — registered FINAL_PUBLICATION_PLAN 0.4(a) verbatim, sanctioned; c |

## Disposition

**RESOLVED IN FULL, author-directed ("fix all", 2026-07-31).** All 33 unique
fixes applied at anchor commit dc33f1f (= pass-29 freeze anchor; mint in the
following commit; decision log D-0031). The four fix_class=none pattern
observations (AUTH-02/03/05, AUTH-SUPP-01) are recorded, unactioned by design.
The refuted S8-07-analogue (AUTH-SUPP-02) was not actioned; the registered
CL-02 hedge survives verbatim. Tag **v2.4** is the submission and
Release/Zenodo basis from this mint forward.
