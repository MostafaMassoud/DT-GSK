# Cover Letter — Algorithms (MDPI)

**To:** Editorial Office, *Algorithms* (MDPI)
**Manuscript:** *DT-GSK: Dimension-Tiered Adaptive Control and Deterministic Refinement for Gaining-Sharing Knowledge Optimization*
**Authors:** Mostafa Elsayed Masoud (corresponding author), Heba Sayed Mohamed Roshdy, Ali Wagdy Mohamed
**Corresponding author:** moustafa.masoud@gmail.com
**Date:** 31 July 2026

<!-- R-0004 clearance (2026-07-11): rewritten for the frozen target journal
     (MDPI Algorithms, decision D-0010). Scientific core is bound to the
     accepted claim set: CL-02 wording, contribution scopes C1-C3
     (phase_04/contribution_matrix.md), and the family-panel bound.
     The prior Swarm-and-Evolutionary-Computation letter is superseded and its
     rendered PDF was removed from the tree; the retarget history survives in
     these comments and in git history (round-2 finding S8-05). -->

---

Dear Editors,

We are pleased to submit our manuscript, *DT-GSK: Dimension-Tiered Adaptive Control and Deterministic Refinement for Gaining-Sharing Knowledge Optimization*, for consideration in *Algorithms*.

To our knowledge, DT-GSK attains the best overall CEC2017 Friedman mean rank on the seven-algorithm GSK-family panel (2.48, the unweighted mean of the four per-dimension ranks — a descriptive aggregate; eGSK is second at 2.96; the two are never Nemenyi-separable at any CEC2017 dimension, DT-GSK is second behind eGSK at D = 30 and on CEC2011; the CEC2011 loss is Holm-significant, and CEC2017 was configuration-selection exposed), evaluated under a release-locked protocol, with byte-stable determinism for DT-GSK in the declared supported environment. The paper makes three contributions. First, a **deterministic, RNG-free eigenframe final polish** executed once in the final budget slice on a learned interaction eigenbasis; no convergence guarantee is claimed. Second, a **dimension-tiered adaptive scaffold** — a bandit-style operator-configuration selector with acceptance-gated arm pruning, a tier-floored population-size reduction schedule, a hard-capped stagnation escape, and a deep-stall restart that preserves the global best — presented as an honestly labeled modified/original composite over published GSK-family mechanisms, never as a new base operator. Third, the **evaluation-integrity infrastructure** that makes the study checkable: a 13-substream, prefix-locked random-number layer, a paired optimizer-independent seed schedule, a hash-frozen configuration, and promoted, read-only evidence releases to which every reported number is bound. A supporting mechanism — the **interaction-structure memory**, a decaying, confidence- and evidence-gated coordinate-pair graph accumulated solely from strictly improving accepted moves at no extra objective evaluations — supplies the polish eigenbasis and the linkage blocks of the block crossover at dimensions of 50 and above; its direct isolation is reported transparently as a controlled negative result (no significant standalone benefit at its active tiers), and we do not claim it recovers the objective's separability structure. All comparative claims in the manuscript are scoped to this GSK-family panel; we make no field-wide performance claims.

We believe this fits *Algorithms* well: the manuscript is an algorithmic contribution with a fully specified mechanism, a reproducible artifact chain, and panel-scoped empirical evidence. In the same spirit, the paper includes a direct component isolation of the interaction-structure memory and reports its outcome transparently: the isolation finds no detectable standalone benefit from the memory at its active tiers, and we are careful not to over-attribute performance to any mechanism the isolation does not separate — the deterministic compass endgame is evaluated as a whole, and the added value of the learned basis over coordinate or random directions remains unresolved.

We confirm that this manuscript is original, has not been published previously, and is not under consideration by any other journal. All authors have read and approved the submitted version. For transparency, we note that A.W.M. is the originator of the baseline GSK algorithm and a co-author of several of the family variants used as comparators, one of which (eGSK) is also co-authored by H.S.M.R.; these relationships are declared in the manuscript's conflicts-of-interest statement. During the preparation and revision of this manuscript, the authors used two generative-AI assistants, Claude (Opus 4.6, 4.8 and 5.0; Anthropic) and ChatGPT (5.5; OpenAI), for language editing and rephrasing, for the drafting of expository prose restating findings the authors had already established from the frozen evidence, for structural review, consistency checking and review of the statistical and methodological descriptions, and for software-engineering support during implementation and tooling work, in accordance with the MDPI policy on the use of generative artificial intelligence. The algorithm design and the experimental protocol are the authors' own, and every reported number was produced by the authors' deterministic analysis pipeline from a version-locked evidence archive: no AI system designed an experiment, produced data, computed a statistic, or generated a scientific claim, result, or conclusion, and no AI system is an author of this work. The authors have reviewed, verified, and edited all AI-assisted text and take full responsibility for the content of this publication.

Thank you for your consideration. We look forward to the reviewers' feedback.

Sincerely,

Mostafa Elsayed Masoud (corresponding author)
Heba Sayed Mohamed Roshdy
Ali Wagdy Mohamed

<!-- AUTHOR-FILL (not rendered): MDPI Algorithms collects proposed and excluded
     reviewers through the submission system, not in the cover letter, so no
     reviewer block appears here. At submission the authors must supply names,
     affiliations, and institutional email addresses in the journal's
     submission form. Do not auto-generate names. Authors of the GSK-family
     comparator papers should be avoided given the declared relationship. -->
