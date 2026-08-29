# DT-GSK Acceptance-Readiness Review — 2026-08-28 (executed at pass-50 / v2.23; fixes landed as pass-51 / v2.24)

Instrument: `docs/prompt/change-register-acceptance-review.md`, executed as a
live audit at **maximal input** (full repository access). Every claim below
carries its evidence label: **VERIFIED** (checked against bytes/renders this
evening), **INFERRED** (follows from a verified record made at an earlier
pass over sources frozen since), or **NOT CHECKABLE** (needs information
outside the repository).

One deviation from the instrument, recorded here and in D-0056: the
instrument specifies report-then-fix; the session's standing author
instruction ("implement, do not merely report") inverted that. The five
surviving findings were fixed, validated and tagged **before** this report
was written, so their rows read FIXED rather than OPEN.

---

## 1. Inputs received

All inputs at maximal depth — repository working tree at pass-50 / v2.23,
commit `10282c1` (review start). Everything below was directly checkable,
so no finding in this report is NOT CHECKABLE unless explicitly labeled.

| Input | State at review | Used for |
|---|---|---|
| `DT-GSK-change-register.pdf` (92 passages) | VERIFIED | central change-by-change audit (§8) |
| `DT-GSK-changes-marked.pdf` (48 pp), supplementary marked (80 pp) | VERIFIED | context of each strike/add |
| `DT-GSK.pdf` (47 pp), `supplementary.pdf` (80 pp) | VERIFIED, re-extracted with pdftotext | rendered-text sweeps — the decisive input (two findings exist **only** in the render view) |
| `response_to_reviewers.md`, `cover_letter.tex/pdf` | VERIFIED | closure matrix, framing checks |
| All `.tex` sources + `references.bib` + 3 citation-control CSVs | VERIFIED | source-side sweeps, exact-quote anchors |
| Governance: decision log through D-0055, freeze + package manifests, attestation record, claims-evidence matrix | VERIFIED | numbers cross-checks, freeze integrity |
| Evidence releases `rel-2026-07-20-67d9345f9`, `rev-rel-2026-08-26-dd42d37eb`, `rev2-rel-2026-08-28-203c78744`, `g1-rel-2026-08-28-65b3d39e6` | VERIFIED (read-only) | E1–E5 and campaign number checks |
| Hash-gated shipped modules (`_dt_core.py` et al.) | VERIFIED | code-facing prose claims (§7.4) |
| Live test suite | VERIFIED (collected + executed ×2) | attestation currency (finding CR-F2) |

## 2. Executive assessment

**The revision is acceptance-ready.** The audit swept all 92 register
passages, re-extracted both final PDFs, and re-verified every load-bearing
number it touched. Roughly forty candidate defects were raised; **five
survived self-refutation** — a survival ratio consistent with this
instrument's four-round calibration history (~half of findings refute) —
and all five are now fixed, validated (13/13 gates ×2, `check_manifest`
15/15 + sources 2/2), minted as **pass-51**, tagged **v2.24**, pushed.

The five (details §8.1; governance D-0056 / CR-0031):

1. **CR-F1 (Major, internal contradiction, VERIFIED).** S6.5 still asserted
   the eigenbasis-vs-coordinate question "remains unidentified" eight lines
   above the same paragraph's statement that S9.1 answers it directly.
   Fourth member of the stale-open-claim family (§3.5 → pass-45,
   conclusions → pass-50, S6.5 → now). A hostile reader quoting these two
   sentences side by side had a genuine "the authors contradict themselves"
   comment.
2. **CR-F3a/b/c (policy, three sites, VERIFIED).** Three revision-process
   references ("added in revision", "carried out in revision", "the
   revision's") survived the pass-50 de-process sweep because each wraps
   across a source line break and none contains "reviewer". Found only in
   the rendered text; invisible to single-line source grep.
3. **CR-F2 (stale attestation, VERIFIED).** The environment attestation
   predated pass-49's `statistics.py` change and its five KATs: recorded
   613 tests at head `31fe38d` while the shipped suite collects 618 — so
   the supplement's "the software state itself is attested" sentence
   attested a superseded state. Re-minted green (618 ×2); count corrected.

**Likely editorial decision: ACCEPT**, with a realistic tail risk of a
short minor-revision round on wording. Every reviewer point R1.1–R2.7 is
closed with pre-registered, released, or directly quotable evidence; the
three adverse findings (basis harmful, D30 mis-specified, boundary
sensitivity at D30/D100) are stated plainly in the abstract, limitations,
and cover letter, which removes the classic rejection lever of discovered
overselling. Nothing in the repository blocks the 2026-09-01 upload.

## 3. Top 10 acceptance threats (IDs → risk register §9)

1. **T1** D=30 adverse profile (2nd/3rd behind EGSK; transplant shows shipped config beaten) — mitigated: disclosed everywhere, localized by E2/E3, extended by E5; claimed nowhere as a win.
2. **T2** E5 shows both D30 neighbours beat the shipped middle profile — mitigated: reported as boundary-level extension of the disclosed mis-specification; C2-as-narrowed untouched (D10/D50 insensitive).
3. **T3** Family-only comparison scope (R2.6) — mitigated: deliberate internal-validity trade, stated with the non-GSK material disclosed as unanalysed.
4. **T4** CEC2011 Holm-significant loss to EGSK — mitigated: printed in conclusions with p=4.2e-2; no aggregate-superiority claim anywhere.
5. **T5** Archived-vs-current run residual (Table A45) — now **closed**, not just bounded: demonstrated build difference via promoted release g1-rel-2026-08-28-65b3d39e6.
6. **T6** NP=5D vs comparators' 100 — closed by the matched-population control (S9.2) plus the LSGO fifty-fold disclosure.
7. **T7** Residual wording/consistency defects — the five found are fixed; the remaining surface is clean under both source and render sweeps.
8. **T8** Upload-day logistics: the repository is **private** and the DAS names its URL and tags — reviewers will click. Must be public before upload (author action).
9. **T9** The latexdiff-invisible retitle — mitigated: named explicitly in the cover letter and the response letter.
10. **T10** 80-page marked supplement navigability — accepted: MDPI requires full marked copies; the 25-page register is the reviewer-friendly entry point and is named in the letter.

## 4. Reviewer-point closure matrix

All eleven numbered concerns close. Anchors are to the current (v2.24) render.

| Point | Concern | Answer in the revision | Verdict |
|---|---|---|---|
| R1.1 | Abstract grammar/length | Rewritten; 195 texcount words; "scalar parameters", "selects its configuration" | CLOSED (VERIFIED) |
| R1.2 | "Adaptive control" terminology | Renamed Adaptive Configuration Engine / configuration selection throughout (register #01, #29, #53, #61, #64, #71) | CLOSED (VERIFIED) |
| R1.3 / R2.2 | NP fairness | E2 matched-population control, S9.2: first at D10, second at D30/50/100, paired difference significant only at D50/D100 — stated in the main text with the asymmetry | CLOSED (VERIFIED) |
| R1.4 | Omnibus convention | Iman–Davenport stated as the reported omnibus (SA01/SA02: D100 p=2.7e-2 — corrected from 3.5e-2) | CLOSED (VERIFIED) |
| R2.1 | Tiering vs tier-constant | E3, S9.3: tiering demonstrated against high-dim transplant at D10/D50; low-dim transplant beats shipped at D30 (p_Holm=5.5e-3) — C2 claimed accordingly | CLOSED (VERIFIED) |
| R2.3 | Refinement basis | E1, S9.1 three-arm isolation: polish supported, learned basis adverse (25/29, p_Holm=1.4e-4 at D50; D100 separated at 0.0489 under the canonical tie rule, superseded 0.054 disclosed) | CLOSED (VERIFIED) |
| R2.4 | Memory attribution | S6.5 null + wall-clock cost (+57.3/+36.3/+30.3%) + no_sgsm caveat + S9.1 basis separation; **S6.5's stale sentence fixed this pass** | CLOSED (VERIFIED) |
| R2.5 | Aggregate vs inference | Descriptive-aggregate qualification at every aggregate site (#36, #44, #56) | CLOSED (VERIFIED) |
| R2.6 | Family-only scope | Deliberate-trade paragraph + unanalysed non-GSK disclosure | CLOSED (VERIFIED) |
| R2.7 | Sensitivity (both halves) | E4 exploratory sweep (S9.4, n_eff column) **and** E5 pre-registered boundary study (S9.5/Table A47) — the half the first response lacked | CLOSED (VERIFIED) |

## 5. Experiment audits E1–E5

| Exp | Design | Registration → release | Result (Holm) | Integrity notes |
|---|---|---|---|---|
| E1 basis | 3-arm: eigenframe / coordinate / none | pre-registered → rev-rel-2026-08-26 | polish > none both dims; coordinate > eigenframe D50 1.4e-4; D100 0.0489 under canonical rule | decision flip 0.054→0.0489 is Amendments A5–A6, disclosed in prose; seed-verified |
| E2 NP | matched NP=100 replication | pre-registered → same release | first D10, second D30/50/100; separated only D50/D100 | pairing by seed; self-init departure disclosed |
| E3 transplant | tiered vs tier-constant | pre-registered → same release | tiering demonstrated D10/D50; shipped D30 beaten by low transplant 5.5e-3 | grounds C2 narrowing; direction stated adversely where adverse |
| E4 sensitivity | 7 constants × 2 levels, D30/D100, 15 reps | pre-registered → same release | descriptive only; declared exploratory and narrow | no hypothesis test claimed — correct |
| E5 boundary | tier-boundary shifts, 4 dims | **Amendment A4 registered before execution** → rev2-rel-2026-08-28 | D10 0.112 insensitive; D30 beaten from both tiers 0.0055/0.0022; D50 0.411; D100 T2-set better 0.0148, ordinal unchanged | shared cell with E2 (0.0055) is disclosed reuse, not duplication; C2-as-narrowed untouched |

## 6. Contribution matrix C1–C3

| Contribution | Claim as revised | Evidence state | Verdict |
|---|---|---|---|
| C1 deterministic final polish | Basis-neutral; polish beats no-refinement at both active dims; learned eigenbasis explicitly adverse | E1 + S6.5 + abstract/limitations; **S6.5 contradiction fixed this pass** | SOUND (VERIFIED) |
| C2 dimension-tiering | Claimed at D=10/50 where demonstrated; 20≤D<50 disclosed mis-specified; E5 extends the disclosure to boundary level | E3 + E5; wording consistent across abstract, §3.5, intro, conclusions, S9.3 (checked this evening) | SOUND (VERIFIED) |
| C3 determinism/reproducibility | Bit-reproducible runs, hash-gated modules, attested software state | attestation **re-minted at 618 tests** (was stale at 613); 13 gates ×2; tags v2.13…v2.24 all resolve | SOUND (VERIFIED) |

## 7. Cross-cutting audits

**7.1 Terminology residue — no surviving findings.** "Adaptive control"
count 0 in both renders; "eigenframe final polish" ×6 is settled mechanism
naming (the mechanism computes an eigenframe; claiming it as a *benefit* is
what was removed) — refuted as a finding, see §15.

**7.2 Superiority language — no surviving findings.** Every
"superior/dominates/outperforms" hit in both renders was context-checked;
each is either negated, adverse to DT-GSK, or a bounded per-cell statement
(§15).

**7.3 Revision-process references — three findings, FIXED.** Source-side
sweeps pass; the render-side sweep found the three line-wrapped survivors
(CR-F3a/b/c). Post-fix render count: 0 process references; the two
remaining "revision" tokens in main are the mandated GenAI/Acknowledgments
disclosures, and the supplement's two are the software-revision sense.
**Lesson institutionalized in D-0056: sweep the RENDER for phrase-level
policies, never only the source.**

**7.4 Code-facing prose — no surviving findings.** The sharpest check:
register #72 changed "non-positive" → "strictly negative" for the ACE
restricted-credit condition. Verified CORRECT against `_dt_core.py`: the
`s == 0` case returns before the restricted branch (line 1239 vs 1252), so
the branch condition is strict — the as-submitted wording was the
imprecise one. Other code-facing claims (#77, #79) are INFERRED-OK: the
four shipped modules are hash-gated and byte-identical since those claims
were verified at pass-41.

**7.5 Numbers cross-check — one finding (CR-F2), FIXED; all others hold.**
Verified against frozen exhibits this evening: +57.3/+36.3/+30.3%
wall-clock (S6.7 sites consistent); D100 omnibus 2.7e-2 (SA01, SA02);
Wilcoxon legend `$=$` matches table; conclusions' EGSK pairwise set
(0.0035 / 0.199 / 1.0 / 0.795), head-to-heads, CD 1.67, CEC2011
3.36/2.52 + 4.2e-2, CEC2020 5-of-24 cells, LSGO 3.13 tie — all consistent
with their releases (VERIFIED direct or via immutable-release INFERRED).
Test count 613 was stale → 618 (VERIFIED by execution ×2).

**7.6 Disclosure hygiene — no surviving findings.** LSGO fifty-fold NP
disclosure arithmetic checks; the 2026-07-24 vs 07-21 timing disclosure is
consistent with the recorded dates; exploratory SHADE-ILS/MOS/DECC-G ports
properly quarantined ("not analysed... no claim rests on them" — which
also keeps the non-comparable transformed-Ackley banks out of reach).

## 8. Change-by-change verdicts (93 passages at v2.24)

Audit method: all passages enumerated from the register's own machinery;
every passage read; the risk-bearing subset (claims of fact, numbers,
code-facing prose, new passages) individually re-verified as above.

- **#01–#27** (main.tex, abstract, DAS, intro, related-work,
  proposed-algorithm head): OK. Terminology, C1/C2 wording, DAS releases
  and tag, five-experiment enumeration all consistent.
- **#28** NP paragraph: content OK; carried CR-F3b ("carried out in
  revision") → **FIXED** (now "A common-$NP$ replication was carried out:",
  which also restores the dangling antecedent).
- **#29–#35**: OK. #31/#35 checked against E3/E1 verdict directions.
- **#36–#51**: OK. #38 legend, #41 robustness-variant scoping, #42/#87
  dangling dev-history SHAs removed, #45–#49 caption/shared-basis
  restructure, #50 cost numbers verified.
- **#52** attribution paragraph: content OK; carried CR-F3a ("added in
  revision") → **FIXED** ("the basis isolation (Supplementary Materials
  Section~S9.1)").
- **#53–#57**: OK. Conclusions numbers verified (§7.5); E5 limitation
  sentence matches the A47 verdicts.
- **#58** limitations rewrite: content OK; carried CR-F3c ("the
  revision's three-arm isolation") → **FIXED** ("a direct three-arm
  isolation (Supplementary Materials, Section~S9.1)").
- **#59–#71**: OK. Inventory S1→S9, retitle, ACE table, brittle line-number
  references dropped.
- **#72**: verified CORRECT (§7.4).
- **#73–#85**: OK. #81 carried CR-F2 (613) → **FIXED** (618, after
  attestation re-mint). #82/#83 omnibus convention + corrected p verified.
- **#86** S6.5 no_sgsm caveat: the passage itself OK — but the audit of its
  **unchanged neighbourhood** found CR-F1 three lines above → **FIXED**
  (new hunk; the register is now 93 passages, supplementary 33→34).
- **#87–#92**: OK. New disclosures (#88, #89) verified §7.6; S9 (#92)
  spot-verified at its five subsections, canonical D100 prose, A45–A47.

**New-problems section (defects in text the revision did NOT touch,
adjacent to what it did):** exactly one — CR-F1, described above. That is
the highest-value output of this audit: three of its four family members
were also in untouched-adjacent text, found only by auditing around the
diffs rather than only inside them.

## 9. Acceptance-risk register (residual, post-fix)

| ID | Risk | Sev × Lik | Mitigation | Owner |
|---|---|---|---|---|
| RR-1 | Repo still private on upload day; DAS links dead for reviewers | High × Low | Flip public before SuSy upload (checklist §14) | Author |
| RR-2 | Reviewer 2 pushes further on family-only scope | Med × Med | R2.6 paragraph + pre-drafted position in response letter | Done |
| RR-3 | A reviewer re-derives E1 D100 and asks about 0.054 vs 0.0489 | Low × Low | Superseded value disclosed in prose with A5–A6 | Done |
| RR-4 | Word resave of tracked DOCX before upload corrupts determinism | Med × Med | Do not open-save the tracked .docx; `check_manifest` before upload | Author |
| RR-5 | Purge ticket timing (dangling commits served by SHA) | Low × Med | File AFTER public flip (ready text in traffic record) | Author |
| RR-6 | Zero schedule slack (deadline = planned date) | Med × Low | Extension draft ready, unsent (author's call) | Author |

## 10. Experiment decision matrix

No further experiment is needed for this resubmission; each candidate was
weighed and declined for stated reasons:

| Candidate | Decision | Why |
|---|---|---|
| Re-specify the D30 tier and re-run | NO | New design work, not revision scope; disclosed as the localized open problem; E5 bounds it |
| Per-key transplant attribution at D30 | NO | Explicitly left open in the text; combinatorial cost; no reviewer asked for it |
| LSGO matched-NP control | NO | Disclosed as not run, CEC2017-only control named; suite is family-internal evidence only |
| Alternative learned bases (PCA on accepted moves, random rotations) | NO | Named as future work in S9.1's closing scope |
| Promote further identity re-executions | NO | g1 release demonstrates the build difference; more adds nothing (D-0051 closure) |

## 11. Simulated reviewers A–D

- **A (methods, R1-like):** checks terminology, NP fairness, omnibus
  convention. Finds the renamed engine, S9.2, Iman–Davenport stated. The
  one thing they could still quote — "carried out in revision" — is gone.
  → Accept.
- **B (statistics, R2-like):** re-derives a table, checks the tie rule,
  reads S9.4/S9.5. Finds the canonical rule implemented, the flip
  disclosed, sensitivity in both halves, boundary study registered before
  execution. → Accept; possible wording nit.
- **C (adversarial skeptic):** hunts for internal contradictions and
  overselling — the reviewer CR-F1 existed for. Post-fix, the S6.5
  paragraph is self-consistent and every superiority phrase is negated or
  adverse. The honest-adversity strategy leaves no quotable overclaim.
  → Cannot construct a rejection case from the text.
- **D (reproducibility):** clicks the DAS, resolves tags, checks the
  attestation. Finds v2.13…v2.24 resolving, six releases, 618-test green
  attestation matching the shipped suite. Risk is RR-1 (private repo), an
  author toggle, not a manuscript defect. → Accept.

**Overlap synthesis:** no two simulated reviewers converge on any
remaining defect — the converging complaints (process references, stale
counts, the S6.5 contradiction) were exactly the five findings, now fixed.

## 12. Editor decision + path to ACCEPT

Round-1 concerns answered with pre-registered experiments and released
evidence; adverse findings disclosed rather than discovered; both marked
copies + register + response letter complete and consistent at one tag.
**Expected: ACCEPT** (tail: minor revision on language). Path: author
uploads on 2026-09-01 per §14; no agent-side work remains.

## 13. Prioritized plan P0–P4

- **P0 — DONE (this pass, D-0056 / CR-0031, pass-51 / v2.24):** CR-F1
  scoping fix; CR-F3a/b/c process-reference removals; CR-F2 attestation
  re-mint + 618. All rebuilt, 13/13 gates ×2, minted, tagged, pushed.
- **P1 — Author, upload day (2026-09-01):** flip repo public → verify DAS
  links → SuSy upload (5 package files + 3 change documents + response
  letter) → re-enter title/keywords by hand → submit.
- **P2 — Author, optional:** send the prepared extension request if any
  upload-day risk materializes (draft beside the response letter).
- **P3 — Author, after the public flip:** file the GitHub purge ticket (ready text +
  full SHAs moved by the 2026-08-29 cleanup to the withheld `papers/review_2026_08_24/PRIVATE_OPS.md`;
  the traffic record keeps short prefixes and points there).
- **P4 — none.** No open agent-side items.

## 14. Final checklist (state at close, all VERIFIED)

- [x] Pass-51 minted; anchor `e8594c5`; close `f9b0718`; tag **v2.24** pushed; CFF 2.24 validates on all 24 tags (bump-before-tag followed)
- [x] `check_manifest` 15/15 + sources 2/2; thirteen ladder gates PASS ×2
- [x] Attestation green: 618 tests ×2 (616 passed + 2 skipped), six gates exit 0
- [x] Register 93 passages / 25 pp; marked PDFs 48 pp + 80 pp — all rebuilt against the pass-51 apply commit; counts synced (response letter, round-one record, REVISION_STATUS)
- [x] Rendered-text sweeps clean: 0 process references, 0 terminology residue, 0 unnegated superiority phrases
- [x] DAS names tag v2.24 + six releases; package manifest at v2.24 / `e8594c5`
- [ ] **Author:** repo public before upload (RR-1) — the one remaining gate to the DAS being live

## 15. Refuted-findings appendix (calibration)

Findings raised during this audit and refuted by the audit itself — kept
per the instrument's doctrine (four-round history: ~half of all findings
refute; a report without this section overstates its own precision):

1. "Superior/dominates" hits in both renders → every occurrence is negated
   ("no runtime-superiority claim is made in either direction"), adverse
   (EGSK/AGSK strengths), or per-cell bounded. REFUTED as findings.
2. "Eigenframe final polish" ×6 → settled mechanism naming; the mechanism
   *does* compute an eigenframe; only benefit-claims were policy targets.
   REFUTED.
3. Supplement "under the current revision" / "release-producing revision"
   → software-revision sense, not manuscript process. REFUTED.
4. E5-vs-E2 sharing p=0.0055 at D30 looked like double-counting → it is
   disclosed cell reuse under Amendment A4. REFUTED.
5. Register #72 "strictly negative" suspected wrong → verified CORRECT
   against `_dt_core.py` control flow; the *original* wording was the
   loose one. REFUTED (and the edit vindicated).
6. Wilcoxon legend `$\approx$`→`$=$` suspected mismatch with table body →
   table uses `$=$`; legend now matches. REFUTED.
7. "Table A47 appears only once in the render" flagged as a missing
   cross-reference → pdftotext merges the S9.5 body reference into a
   table-zone text run; the labeled table and its citation both render.
   REFUTED.
8. Attestation gates passing while renders were stale mid-pass suspected a
   gate hole → those gates compare renders among themselves (parity), by
   design; the freeze manifest is the source-vs-render gate, and it
   correctly read 11/15 until the rebuild. REFUTED (gate working as
   specified).
9. Register line numbers (#72 at "1568") not matching current file
   suspected register corruption → register line numbers index the diff at
   build time; the file gained S9 content; content-addressed search
   resolves every passage. REFUTED.
10. "sources 1/2" mid-pass suspected a new blind spot → supplementary.tex
    was edited and correctly tripped the source-hash gate added in pass-42's
    aftermath; that is the gate *working*. REFUTED.

— End of report. Governance: D-0056 / CR-0031. Next free ids: CR-0032 / D-0057.
