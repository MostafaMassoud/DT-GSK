# Cover Letter — Algorithms (MDPI)

**To:** Editorial Office, *Algorithms* (MDPI)
**Manuscript:** *DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic Refinement for Gaining-Sharing Knowledge Optimization* — algorithms-4507562, revision 1
**Authors:** Mostafa Elsayed Ahmed Masoud (corresponding author), Heba Sayed Mohamed Roshdy, Ali Wagdy Mohamed
**Corresponding author:** moustafa.masoud@gmail.com
**Date:** 30 August 2026

<!-- R-0004 clearance (2026-07-11): rewritten for the frozen target journal
     (MDPI Algorithms, decision D-0010). Scientific core is bound to the
     accepted claim set: CL-02 wording, contribution scopes C1-C3
     (phase_04/contribution_matrix.md), and the family-panel bound.
     The prior Swarm-and-Evolutionary-Computation letter is superseded and its
     rendered PDF was removed from the tree; the retarget history survives in
     these comments and in git history (round-2 finding S8-05). -->

---

Dear Editors,

We are pleased to submit the revised version of our manuscript, *DT-GSK: Dimension-Tiered Adaptive Configuration Selection and Deterministic Refinement for Gaining-Sharing Knowledge Optimization* (algorithms-4507562). All ten reviewer comments are addressed. Four called for new evidence; we answered them with five pre-registered experiments (34,191 optimizer runs in total), each with its design, statistical conventions and adverse-outcome wording committed to the public repository in advance — four experiments before any result existed, and the fifth (the dimension-boundary study) registered by amendment before any of its new runs executed. Accompanying this letter are the point-by-point response, a marked-up main manuscript, a marked-up Supplement, and a change register listing every changed passage as submitted against as revised. One change the marked copies cannot show is the title page itself: the retitle Reviewer 1 requested sits in the document preamble, which latexdiff records without displaying, so we flag it here.

The revision strengthened what holds. The deterministic final refinement earns its place at both dimensions where it is active; the family standing survives a matched-initial-population control, staying in the top two at every CEC2017 dimension; and the dimension-tier boundaries are insensitive to perturbation at D = 10 and D = 50 --- exactly where the narrowed contribution claims them. DT-GSK attains the best descriptive family-rank aggregate on CEC2017 (2.48) and CEC2013 (2.80), with the paper stating plainly that Holm-corrected tests separate it from the strongest baseline only at D = 10.

Three findings went against our submitted claims, and all three are in the paper rather than only in this letter. The learned eigenframe basis is outperformed by plain coordinate axes at both active dimensions under the manuscript's stated tie rule, so the refinement contribution is now claimed basis-neutrally and the eigenbasis is reported as a controlled negative result. The shipped 20 ≤ D < 50 profile is beaten from both neighbouring tiers at D = 30, extending a weakness the submitted manuscript had disclosed descriptively. And fixing the initial population at the comparators' value costs DT-GSK its first place at D = 50 and D = 100, so those two rank claims are qualified as resting in part on the population rule. We believe reporting these outcomes plainly makes the paper more useful, not weaker.

We believe the manuscript fits *Algorithms* well: an algorithmic contribution with a fully specified mechanism, a reproducible artifact chain in a public, tagged repository, and empirical claims scoped throughout to the seven-algorithm GSK family --- we make no field-wide performance claims.

We confirm that this manuscript is original, has not been published previously, and is not under consideration by any other journal. All authors have read and approved the submitted version. For transparency, we note that A.W.M. is the originator of the baseline GSK algorithm and a co-author of several of the family variants used as comparators, one of which (eGSK) is also co-authored by H.S.M.R.; these relationships are declared in the manuscript's conflicts-of-interest statement. During the preparation and revision of this manuscript, the authors used two generative-AI assistants, Claude (Opus 4.6, 4.8 and 5.0; Anthropic) and ChatGPT (OpenAI), for language editing and rephrasing, for the drafting of expository prose restating findings the authors had already established from the frozen evidence, for structural review, consistency checking and review of the statistical and methodological descriptions, and for software-engineering support during implementation and tooling work, in accordance with the MDPI policy on the use of generative artificial intelligence. The algorithm design and the experimental protocol are the authors' own, and every reported number was produced by the authors' deterministic analysis pipeline from a version-locked evidence archive: no AI system designed an experiment, produced data, computed a statistic, or generated a scientific claim, result, or conclusion, and no AI system is an author of this work. The authors have reviewed, verified, and edited all AI-assisted text and take full responsibility for the content of this publication.

Sincerely,

Mostafa Elsayed Ahmed Masoud (corresponding author)
Heba Sayed Mohamed Roshdy
Ali Wagdy Mohamed

<!-- AUTHOR-FILL (not rendered): MDPI Algorithms collects proposed and excluded
     reviewers through the submission system, not in the cover letter, so no
     reviewer block appears here. At submission the authors must supply names,
     affiliations, and institutional email addresses in the journal's
     submission form. Do not auto-generate names. Authors of the GSK-family
     comparator papers should be avoided given the declared relationship. -->
