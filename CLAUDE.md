# CLAUDE.md

Auto-loaded every session, so it is deliberately short. It carries only what a session cannot
cheaply re-derive, and points at the one file the task actually needs. **Do not read the root
documents speculatively** — they total ~300 KB.

## What this repo is

DT-GSK (Dimension-Tiered Gaining-Sharing Knowledge): a single-algorithm research repo built around
one manuscript. Seven optimizers behind one contract — `gsk`, `agsk`, `apgsk`, `fdb-agsk`,
`atmals-gsk`, `egsk`, and the proposed `dt-gsk` — evaluated on five CEC suites (`cec2011`,
`cec2013`, `cec2013lsgo`, `cec2017`, `cec2020`) under one locked, budget-fair paired protocol.
Python package: `gsk_family` (under `src/`). Console entry points are `gsk-*`.

The repository exists to support a **published claim**, not to be a general framework. Most files
are frozen or hash-bound. Assume nothing is casually editable.

## Right now (2026-08-30)

**⏳ RESUBMISSION: the author submits TODAY, 2026-08-30 — two days ahead of the confirmed
2026-09-01 deadline** (the earlier zero-slack framing is obsolete: submitting early restores the
margin the deadline confirmation had removed). Both letters and the CFF are re-dated 2026-08-30.
Nothing in the repository blocks it — everything agent-side is complete. **The repo was set PRIVATE on 2026-08-28 (author, to finalize) and MUST be public again before
the upload** — the DAS names its URL and tags, and reviewers will click. Detail:
[REVISION_STATUS.md](REVISION_STATUS.md) Section 5 items 1 and 6.

**Current freeze: pass-62 / `v2.35`** — minted, tagged and **PUSHED** (2026-08-29); all 35
tags are on `origin`, and `v2.13`/`v2.35` — the two the DAS names — resolve there. The repo is still **PRIVATE** —
flipping it public is the remaining step before a referee can follow the DAS. Next free ids:
**CR-0043 / D-0068** — verify free at apply time.
**Pass-62 (2026-08-29, D-0067 / CR-0042) closes the crushed-back-matter family:** the Supplementary
Materials and Abbreviations statements — the last two users of mdpi.cls's 9/9 zero-leading
style — re-declared at 9/11.5 beside the four fixed at pass-61; the class's other 9/9 sites
verified to carry real leading via their own spacing/linespread wrappers. No pagination shift,
anchors verified, ladder green.
**Pass-61 (2026-08-29, D-0066 / CR-0041) is presentation part two:** the four mdpi.cls back-matter
statements re-declared at 9/11.5 (the class sets 9/9 — zero leading, visibly crushed), and the
Section 3 execution-order list gains item separation plus a keep-together guard (one block on
page 15). One page shift (Section 3.3 statement 16→15) — the letter's single reference updated
and rebuilt; all other anchors verified. Pages 49/83, ladder green.
**Pass-60 (2026-08-29, D-0065 / CR-0040) is an author-directed presentation pass:** the DAS keeps
the primary release inline and defers the five auxiliary release identifiers to the supplement
and the repository manifests (the inline hash-ID enumeration read as machine output), and
Algorithm 1 is re-rendered (sections/algorithm_pseudocode_render.tex — one line per step, no
orphaned anchors, compact closing note) with semantics and the frozen loop order unchanged and
the phase_03 canonical sources untouched. Pages 49/83, anchors re-verified, full ladder green.
**Pass-59 (2026-08-29, D-0064 / CR-0039):** the corresponding author's byline is the full name
**Mostafa Elsayed Ahmed Masoud**, initials **M.E.A.M.** in the address block, CRediT statement and
Conflicts of Interest, across twelve live documents (manuscript, supplement, cover letter,
plain-language summary, CITATION.cff, README, kit, letter and companions); historical records
untouched; every render rebuilt at its pinned epoch and double-built byte-identical, pages
unchanged 49/83, letter anchors re-verified; the DAS was bumped BEFORE the builds this time.
**Pass-58 (2026-08-29, D-0063 / CR-0038) is an author-directed author-metadata pass:** Ali Wagdy
Mohamed gains affiliation 2 (University of Science and Technology, Zewail City of Science and
Technology, 6th of October City, Giza 12588, Egypt) in the manuscript, the DOCX shim, the
supplement, CITATION.cff and the kit's portal table. All four gated renders were rebuilt at their
pinned epochs (page counts unchanged 49/83; main PDF double-built byte-identical; the response
letter's page anchors re-verified against the new render); the change register records the
affiliation passages. The same close repaired the severed public-flip sentence, the stale
next-free ids in this file, the package manifest's stale v2.28 DAS note and hand-typed
timestamp, and marked the What-remains items 3-5 done.
**Pass-57 (2026-08-29, D-0062 / CR-0037) closed the optional-queued and immutable-history items:**
artifact_binding's checksum column re-derived (84 stale pairs, two independent derivations in
agreement); Section 3.2 states protocol conformance (no suite protocol prescribes a population
size — verified for all five before generalizing); the freeze manifest's `immutable_history_note`
discloses the two unfixable history blemishes — rewriting pushed history would break the DAS and
violate D-0045, so disclosure IS the fix. **The heredoc backslash trap fired again** (a ref macro
shipped as a literal CR + 'ef' into the built PDF, caught in the render); line-ending audits must
check for LONE CR too, which the no-lone-LF assert misses.
**Pass-56 (2026-08-29, D-0061 / CR-0036) preceded it, closing the from-scratch five-instrument re-review:**
the cover letter's blanket 'before any result existed' pre-registration claim was false for E5
on its natural reading and now matches the response letter's precise chronology; the stale-claim
family's FIFTH recurrence (seven documents still called the E1 D = 100 contrast 'not separated'
against the canonical Holm 0.0489) is corrected; CITATION.cff gains the missing eGSK source;
`check_manifest.py` now gates commit-field RESOLVABILITY after the pass-55 mint recorded a
published_commit with an invented tail (caught live by the new gate); RS-12's quoted verbatim
matches the abstract locus; the three unbound shipped figures are bound. Mint scripts must
compute SHAs with `git rev-parse`, never type them.
**Pass-55 (2026-08-29, D-0060 / CR-0035) preceded it, closing the deferred register items 4-10
by author direction:** the abstract is 199 rendered words with the registered sentences byte-identical (two
candidate trims REFUTED in verification); one additive sentence scopes the inactive-at-D<=20
claim to the gating taxonomy; six verified supplement refinements landed (pooled-A12 compression,
the E3 constructed tie, the E5 2.34->1.97 movement, S7.1 port provenance, the S9.4 monotonicity
claim, W/T/L direction); three orphan tables gained refs while SEVEN alleged orphans were refuted
as range-covered; three clearpage flushes cured the float inversions (supplement now 83 pp);
87 algorithm-guide citations re-based; the register renders hunk context verbatim (a latent
tex_escape ordering bug fixed with it).
**Pass-54 (2026-08-29, D-0059 / CR-0034) preceded it:** five review instruments were
retuned and re-applied from scratch and three cross-audits run beside them; 67 findings, all
verified against bytes or the render before being acted on. Topmost, **both architecture tables
(Table 4 row 8, Table 5 row 9) still carried the retired C1 name** on pages whose own prose said
“deterministic final polish”, while the response letter promises the editor exactly that rename —
pass-53 had renamed six prose sites and recorded it done, and a source-side grep missed the table
cells because they use the same words in a different grammatical role. **Only the render catches
this class.** Second, the Supplementary invited a **commit-level pre-registration audit the public
repository fails** (the CEC2020 signing commit does not resolve; the squashed root postdates the
release it registers) — the claim now rests on the checksum binding, which holds, and the squash
is disclosed. Also: the abstract's “on that suite” followed two named suites and made a rank claim
false; the CEC2020 runner-up fact cited the APGSK paper at five sites; the tie-band and
single-unfavourable-cell claims were contradicted by the paper itself; C2's narrowing and E2's
adverse result reached the Conclusions; Amendment A3 is disclosed. `build_cover_letter.py` was
added (files[10] had no epoch-pinned builder), five mypy errors under five “clean” assertions were
fixed, and a hosted CI asserted by fourteen documents was retracted — it has never existed in any
commit. **New gate: `check_reproducibility_manifest.py`** — that manifest had gone stale INSIDE
its own pass three times, always refreshed before the artifacts were rebuilt, and nothing read it.
(Next free then: CR-0036 / D-0061; both long consumed — read the current pair off the freeze
paragraph at the top of this block.)
**Pass-53** was the previous remediation pass (D-0058 / CR-0033): the Supplementary's ninth
limitation still said the tier boundaries were “unvaried, so their sensitivity is untested” nine
pages before S9.5 varies them and finds against the shipped profile twice; the Conclusions now
state why ISM and its eigenbasis are retained (the configuration was checksum-locked before the
isolations ran, so the isolations correct the claims, not the method); C2's narrowing reached the
Introduction. **The deterministic PDF epoch had been absent from
`build_pdf.py`/`build_supplementary.py` since pass-51** — shipped PDFs carried wall-clock stamps
under a manifest claiming double-build identity; the epoch is now pinned inside both builders.
The chronicle since the round-two audit, newest last:
**pass-49** answered the external second-round audit: **E5
dimension-boundary sensitivity** ran (registered as Amendment A4 BEFORE execution; release
`rev2-rel-2026-08-28-203c78744`; S9.5 / Table A47 — D30's middle profile beaten from BOTH
neighbouring tiers, D100's upper profile beaten by the T2 set with the family ordinal unchanged,
D10/D50 insensitive; **C2 as narrowed is untouched**), the **canonical 1e-8 tie rule** the paper
stated but the revision analyzer skipped is implemented and regenerated (Amendments A5–A6; one
decision flip: E1 D100 eigenframe-vs-coordinate now SEPARATED, Holm 0.0489), the C1 heading is
basis-neutral, the tiering-thesis and causal-mis-specification prose is bounded, and the
submission package manifest matches the actual bytes. (**The “195 words” recorded here at the
time was wrong** — pass-54 measured the shipped abstract at 205 rendered words, already 204 at
v2.26, against a 200-word guideline. It was left untrimmed through pass-54 because the sentences
carrying the CEC2020 and CEC2013LSGO outcomes are bound to registered wording banks RS-12/RS-13;
pass-55 then closed the author decision by trimming UNREGISTERED material only, to 199 rendered
words, with the registered sentences byte-identical — see the pass-55 entry above. The false
count was removed from the response letter.)
**Pass-50 / v2.23 followed the same evening (author instruction: implement every reopened
item):** the D-0051 re-execution is PROMOTED and cited (`g1-rel-2026-08-28-65b3d39e6`; Table A45
now reports the residual as a demonstrated build difference), Figure 4 shades the within-one-CD
cohort instead of the detached ruler, the convergence captions state their shared protocol once
in the body, the cover letter leads with closure and reports the three adverse findings plainly
(re-dated 30 August 2026 at pass-63), references.bib is pruned to its 44 cited entries alongside the three
citation-control files, the change register is redesigned (TOC, badges, color-coded panels; 92
passages), and **every reviewer/revision-process reference is removed from the published
artifacts** — S9 is now “Mechanism-Isolation and Sensitivity Experiments”; pre-registration
language stays. The GitHub purge request is REOPENED to be filed after the public flip, and an
extension-request draft sits withheld beside the response letter (sending is the author's call).
**Pass-51 / v2.24 closed the evening (acceptance-readiness review, D-0056 / CR-0031):** the
tuned review instrument was executed at maximal input over all 92 register passages plus
rendered-text sweeps; five verified findings fixed — the S6.5 stale-open basis claim scoped to
S9.1's answer (fourth member of the stale-claim family), three LINE-WRAPPED revision-process
references the source-side sweep missed (sweep the RENDER for phrase policies, not the source),
and the environment attestation re-minted at 618 tests after pass-49's statistics.py change.
Register is rebuilt at each pass; read its passage count off its own front page.
**After pass-52 (2026-08-29, ordinary commits, freeze untouched):** the roadmap's B1–B4 ops
fixes landed (kit row-83 counts, package manifest at six releases, CFF date/abstract, and an
attestation re-mint — note that `git.dirty` is **always** true there and cannot be made false:
`make_environment_attestation.py` computes it from `git status --porcelain` while the mint's own
junit XMLs already sit in the tree), then the **public-release cleanup**: tracked docs no longer carry the private
bundle's path, the purge full SHAs, or reviewer-verbatim words — the operational identifiers
live ONLY in the withheld `papers/review_2026_08_24/PRIVATE_OPS.md`; results staging was
quarantined to `../DT-GSK_cleanup_2026-08-29/`. **The cleanup commits were held unpushed by
contract at first and pushed later the same day; as always, verify `git status -sb` against origin
before relying on remote state.**
**Pass-52 / v2.25 (2026-08-29, D-0057 / CR-0032) applied a fourteen-agent seven-lens panel review
of the response letter:** 28 confirmed findings fixed — topmost, the letter's quote of the revised
abstract said 'scalar control' where the shipped abstract says 'scalar parameters', and two E1
cells carried superseded exact-zero p-values (now canonical 6.8e-4 / 4.0e-6); SA01/SA02 became
the typeset Tables A23–A24; the cover letter's stale 84-passage count is now count-free wording
(both twins). The package manifest's recorded byte sizes had been silently stale since pass-51
(no gate checks them) — fixed. **D-0057 / CR-0032 are filed** (the then-next-free
CR-0033 / D-0058 were consumed by pass-53; the current pair lives in the freeze paragraph above). The paragraphs
below about passes 42–45 are kept because their *lessons* stand, not because they describe the
current tag.

**Pass-45 came out of a deep application of this project's own review instrument** (97 agents over
`papers/PAPER_REVIEW_PROMPT.md`, 14 stage-mapped dimensions, every finding adversarially verified).
It discharged two **Major** main-text defects the revision had missed — §3.5, the subsection
defining C1, still asserted the *pre-revision* position on the polish basis and routed to the
superseded S6.5; and the evidence-discipline paragraph stated a release count the Data Availability
Statement contradicts — plus four smaller items (CR-0028 / D-0053).

**The calibration is the durable lesson: 44 of 82 findings were REFUTED, and 75 of 82 proposed
remedies were unsafe as written.** That ratio now holds across four independent rounds. The
instrument finds real defects; **never apply its prescriptions unexamined.** In pass-45 even the
*report's own* safer remedy for the §3.5 fix was unsafe — it would have left one paragraph asserting
both that the question is open and that it is settled. **Every tag bump drags
`CITATION.cff`, `SUBMISSION_KIT.md` and `submission_package_manifest.json` with it**; the citation
file is gated and carries no leading `v`, so a `v2.1x` sweep misses it.

**Work on `main` — it is now the ONLY branch** (author decision, 2026-08-28). The private
development history — formerly the branches `archive/revision-pass-39-full` and
`revision/pass-39` — was moved whole into **the author's private history bundle**, kept outside
the repository (location recorded in the withheld `papers/review_2026_08_24/PRIVATE_OPS.md`;
restore-tested: both refs, matching tips, the withheld files and the two
GitHub-exposed commits all readable). The old rule transfers to the bundle: it carries the
reviewers' reports, the co-author handoff, the seven copyrighted PDFs, and commit messages
unsuitable for publication — so **never fetch it into a repo with a public remote, never merge
its refs into `main`, never copy the bundle into the repo tree or any public location.** Restore,
whenever needed, only into a detached private clone: `git init x && git -C x fetch <bundle>
"refs/heads/*:refs/heads/*"`. (`public/squash-candidate`, which held nothing not already on
`main`, was deleted the same day; its commit `02d1791` remains reachable as `main`'s squash
root.)

**What pass-42 did.** Twelve alleged defects were verified and then challenged in the opposite
direction; nine survived and are corrected (C1, C2, C3, C6, C7, C8+C9 merged, C10, C11, C12).
**C4 is refuted and deliberately not edited** — its proposed "fix" was a regression.
**Contribution C3 is NOT narrowed.** No number, rank, p-value or decision changed. Freeze pass-42,
CR-0025 / D-0050, `check_manifest` 15/15, thirteen gates green, all five artifacts byte-reproducible.

**The lesson that generalises:** the diagnoses were reliable, the prescriptions were not — 10 of 11
audited fixes were unsafe as written and had to be repaired before use. **Challenge a proposed fix,
not just the finding.** And read the built PDF: every defect this project has shipped was caught
there and nowhere else.

**The two author decisions that were open are now RESOLVED (pass-43, D-0051).**

1. The Supplementary no longer contradicts the response letter. The letter concedes the D = 100
   internal control does not hold; `supplementary.tex` had still asserted that no reported number
   depends on which revision is used. Both ship in one package, so both would have reached the
   referees. The exception is now recorded, pointed at the caption that already reports it as
   unresolved, and bounded — the archived release every reported number derives from is unchanged.
2. **A larger disclosure was drafted and REJECTED on challenge. Do not revive it.** It would have
   named CR-0015 as the one bit-identity certification not spanning cec2017 D = 100 — refutable
   from the register it cites, since **CR-0014, CR-0016 and CR-0018 all certify that cell**, the
   last in an 84-cell bit-for-bit ledger. It also named a cause while disclaiming one, and located
   it at contribution **C1**. **The standing rule holds: state the gap, never the causation.**

**ANSWERED 2026-08-27 by re-execution (D-0051): the residual is a BUILD difference, demonstrated.**
The five functions carrying it were re-run at CEC2017 D = 100, 51 runs each, under the current build
with threads pinned as the campaign driver pins them. 255 cells, zero seed mismatches. **On the 26
cells where the archive and the transplant arm differ, the fresh run reproduces the transplant arm
on all 26 and the archive on none; on the 229 where they agree it reproduces both.** So the current
build makes the transplant arm's values and the archive is what the earlier build made — between
builds, not within one.

**Two traps this experiment sets for anyone repeating it.** `run.py` does **not** pin threads (only
`run_campaign.py` does) and D = 100 is thread-sensitive, so an unpinned re-run is meaningless. And a
control drawn from cells where the two legs already *agree* cannot distinguish the builds — an early
reading here went wrong exactly that way; the discriminating cells are the ones that differ.

**No manuscript change follows.** The Supplementary already says the control re-executes archived
runs and does not reproduce them exactly, and the caption reports the residual as unresolved *in the
paper*; both stay true and are now evidenced. Claiming more would mean **promoting a diagnostic
staging run as cited evidence** — new release id, manifest, binding — since every reported number is
bound to a promoted release. **That promotion is CLOSED (author, 2026-08-28) and will not be done:**
the diagnostic stays diagnostic, cited nowhere, with no release id minted for it. It is not pending
work and should not be re-raised. Still recorded, and still
true: the campaign's identity evidence samples ~one run per (algorithm, suite, dimension), so a
27-in-1479 divergence sits below its resolution — those certifications are underpowered here, not
wrong.

**The hashed-render / unhashed-source blind spot is now gated.** The freeze hashed renders but only
`main.tex` among their sources, which is how pass-42 edited `cover_letter.tex`, skipped the rebuild,
and left the render matching its digest while the gate stayed green — on a letter that ships to the
editor. The manifest now carries `source_files` and `check_manifest` reports
`sources N/N` on its own line, so every recorded "15/15" stays true. Negative-tested: perturb a
source, leave its render, and `files` still reads 15/15 while `sources` drops and the gate exits 1.

## Read this first

**➡ [REVISION_STATUS.md](REVISION_STATUS.md) — current state, always.** The manuscript is under
**major revision** at *Algorithms* (MDPI) — the round-1 revision is complete and awaits author
resubmission. That file holds the review outcome, how each of the ten reviewer points was answered,
what each revision phase applied, the decisions already made, the open author decisions, and the
full trap table. Start there; it exists so you do not have to read the decision log end to end.

**Two submitted claims were falsified by the round-1 experiments and corrected in the paper.** The
learned ISM eigenbasis is *harmful*, not neutral — plain coordinate axes beat it at D = 50 — so C1
is renamed "a deterministic final polish" and claimed basis-neutrally. The polish itself survives: it
still beats no refinement at both active dimensions. And the 20 ≤ D < 50 tier is *mis-specified*, so
C2 is narrowed to the dimensions where tiering was shown, D = 10 and D = 50. Describing the mechanism
as computing an eigenbasis is still correct; presenting the eigenbasis as a contribution or a benefit
is not. Details: [REVISION_STATUS.md](REVISION_STATUS.md) §3, Phase 7.

Everything else in this file is a pointer.

## Never break these

1. **Four shipped DT-GSK modules are hash-gated**, not just one: `dt_gsk.py`, `_dt_core.py`,
   `_dt_profiles.py`, `_dt_rng.py` under `src/gsk_family/optimizers/`.
   `papers/scripts/validate_provenance_claims.py` hashes them on a SHIPPED list — **even a comment
   edit fails the gate.**
2. **`benchmarks/cec_reference_results/` is READ-ONLY** frozen evidence. Never "regenerate" it.
   Runners write under `results/` and nowhere else — `_run_all/` for the campaign, `_revision/` for
   the revision driver (`scripts/run_revision_experiments.py`), `_ablation*/` for ablations.
   `results/_revision/` is **untracked** (D-0049): it duplicates the promoted release, which is the
   citable evidence. (The accumulated staging was quarantined outside the repo by the 2026-08-29
   cleanup; future runs recreate the directory.)
3. **`papers/` is a frozen manuscript under change control.** Any edit voids the freeze manifest and
   belongs to a new freeze pass (see D-0045). Never edit the submitted state in place.
4. **Never author LaTeX or regex through a bash heredoc** — backslash collapse has already shipped
   corrupted macros into a released PDF. Use exact-match file editing.
5. **Line endings are per file**, and multi-line edits fail silently against the wrong one. Both
   freeze manifests and several `.tex` files are CRLF; others are LF. Check before editing.
6. **Append-only trees:** `papers/build_prompt_phases/`, `papers/review_2026_07_22/`,
   `papers/governance/remediation_2026_07_18/`. Stale content there is correct — do not "fix" it.
   One carve-out: `phase_09/evidence_binding_verification.csv` is a living verification output,
   refreshed in place at every pass by convention.
7. **Never run `papers/scripts/finalize_evidence.py`** (standing instruction).
8. **Work only in this repository checkout.** A divergent copy lives in the PhD-Projects monorepo;
   each freeze manifest hashes only its own tree, so both can report "15/15" while disagreeing.
9. **The repository is PUBLIC and some files are deliberately untracked** (D-0049). Pinned in
   `.gitignore`, present on disk, retained in git only on the never-pushed archive branch: both
   reviewers' reports, the point-by-point response (it quotes them), the co-author handoff
   (biographies marked as awaiting their subjects' approval), and seven copyrighted third-party
   PDFs. The **pre-registration is public on purpose** — the Supplementary Materials' claim that
   adverse-outcome wording predates the outcomes is uncheckable without it. Do not re-add any of
   the others, and never push a branch whose history contains them.
10. **A `.gitignore` glob that does not cross `/` is not an exclusion.** `reference_papers/*.pdf`
   silently matched nothing under `Academic_Research_Guidelines/` for the life of the repo, and
   38.8 MiB of copyrighted PDFs reached the public remote. Recursive form alongside it now; check
   `git check-ignore -v <path>` rather than trusting the pattern.

Full detail and the remaining traps: [REVISION_STATUS.md](REVISION_STATUS.md) §7.

## Where detail lives

| Need | File |
|---|---|
| **Current state, review, next steps** | **[REVISION_STATUS.md](REVISION_STATUS.md)** |
| Orientation, directory tree | [REPO_MAP.md](REPO_MAP.md) |
| Agent operating contract, commands | [SKILL.md](SKILL.md) |
| Step-by-step procedures | [runbook.md](runbook.md) |
| Project constitution, governance | [PROJECT_RULES.md](PROJECT_RULES.md) |
| Module structure, data flow | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Design principles, how to extend | [DESIGN_GUIDE.md](DESIGN_GUIDE.md) |
| Suite protocols, budgets, seeds | [BENCHMARK_RULES.md](BENCHMARK_RULES.md) |
| Style, determinism, KATs | [CODING_STANDARD.md](CODING_STANDARD.md) |
| Numba, threading, serial kernels | [PERFORMANCE_RULES.md](PERFORMANCE_RULES.md) |
| Runtime-acceleration method | `docs/development/ACCELERATION_CAMPAIGN_PROMPT.md` (Appendix A) |
| Decisions D-0001…D-0049 | `papers/governance/decision_log.md` |
| What is published vs withheld, and why | `papers/governance/decision_log.md` **D-0049** |
| Claim → evidence bindings | `papers/governance/claims_evidence_matrix.csv` |

⚠️ **[FINAL_RELEASE_REPORT.md](FINAL_RELEASE_REPORT.md) is historical** (CEC2017 only, pre-submission).
It ends on "PUBLISH READY", which is no longer the project's state. Do not read it for current status.

## Conventions

- Freeze passes and tags advance together: submitted at **pass-38 / v2.13**; the round-1 revision
  landed at **pass-41 / v2.14**, both **published**. A revision is always a new pass through change
  control, never an edit to a tagged state (D-0045).
- **Publication WAS a squash, through 2026-08-28.** The public history is one commit per
  published state up to that point, because the development history could not be published, so a
  commit SHA recorded by a governance record written before then — including older
  `anchor_commit` values — does **not** resolve. Since the private branches were bundled out and
  `main` became the only branch, ordinary commits are published as they are: `anchor_commit`
  now resolves (verify with `git cat-file -e` — tag-relative identities go stale every pass).
  `published_commit` names the PREVIOUS freeze's close, so its
  tree is deliberately not the current freeze's. Disclosed in `README.md`.
- Governance ids are sequential and must be verified free at apply time — read the CURRENT
  next-free pair off the "Right now" block above (this bullet has lagged it two passes running).
- Evidence releases are additive and non-superseding. Frozen analysis outputs are never re-minted;
  new findings get a new release id.
- Temporary files go in the session scratchpad, **outside** the repo. Never create scratch trees,
  plan folders, or agent scaffolding directories anywhere under this root.
