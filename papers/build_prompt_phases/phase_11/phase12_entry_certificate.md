# Phase-12 Entry Certificate — Gate-11 Signed

**Certificate type:** Pre-ablation freeze + Phase-12 authorization (PAPER_BUILD_PROMPT.md
§Phase 11, tasks 12–13 / Gate 11).

- **Anchor commit:** `cffcbb48153fd6395c67bb35ece0107269c15694`
- **Evidence release in force:** `rel-2026-07-10-262fc16c9` (immutable, read-only)
- **Issued (UTC):** 2026-07-11
- **Gate-11 verdict:** **PASS — no blocker.**

---

## 1. Statement of completion

By the checksums and gate records below, the following program stages are **COMPLETE and
FROZEN**:

- **Algorithm development** — the DT-GSK frozen core and `pub` profile are hash-locked
  (Phase 3).
- **Primary benchmarking** — the immutable evidence release over the 3,409-file reference tree
  is selected and bound (Phase 2).
- **Statistical validation** — the pre-registered analysis plan was executed deterministically
  under the strict-source guard; all six standing rank claims re-derived and confirmed (Phase 6).
- **Manuscript preparation** — the evidence-first main text and pre-ablation supplement were
  drafted from claim IDs with every number bound (Phases 4, 5, 7, 8).
- **Dual-format production** — native PDF + editable Word (OMML equations, native tables) built,
  validated, and byte-deterministic (Phase 9).
- **Adversarial review + finalization** — six hostile reviews dispositioned; pre-ablation freeze
  manifests, certificate, and correction-exception protocol issued (Phases 10, 11).

The **scientific content of the primary manuscript is `FROZEN_BEFORE_ABLATION`.** No Phase-12
ablation result may alter any number, claim, equation, label, or figure in the shipped artifacts;
the only permitted Phase-12 action against frozen text is one-directional narrowing per
`correction_exception_protocol.md` (G0 guard).

---

## 2. Prior gates — FROZEN status + key checksums

| Gate | Phase | State | Key checksum / anchor |
|---|---|:---:|---|
| 0 | Governance preflight & authority freeze | **FROZEN** | git-status snapshot `14f31984…6dc224`; anchor `262fc16c9` |
| 1 | Closed literature-corpus audit | **FROZEN** | 57/57 BibTeX keys; 57-file SHA-256 corpus re-hash matched |
| 2 | Immutable empirical evidence & provenance | **FROZEN** | release `rel-2026-07-10-262fc16c9`; `evidence_release_manifest.json` = `588e89c2a66d4b1ff153a98f9de886d84c53b3833ca9f5a3ee49f2dd72904127` (3,409 files / 712,038,425 B) |
| 3 | Method reconstruction & algorithm freeze | **FROZEN** | `algorithm_freeze_manifest.json` = `88dbabd40a3b1c37b62b25287661c36db26efa46fa309a44066fabf07a314c7c`; core `dt_gsk.py` a274e0f8 / `_dt_core.py` 1ef815ce / `_dt_profiles.py` c3dcdce3 / `_dt_rng.py` db1cc028 / subsystems merkle e532fc44 |
| 4 | Thesis, contributions, journal, claims freeze | **FROZEN** | `claims_evidence_matrix.csv` 50 rows; journal MDPI *Algorithms* (D-0010); S6 ablation RESERVED Phase-12 |
| 5 | Statistical-analysis & exhibit-design freeze | **FROZEN** | 59-family analysis registry; ablation pre-registered `PHASE_12_ONLY` (7 scaffold + 4 overlay) |
| 6 | Primary evidence computation & stat validation | **FROZEN** | analysis bundle `analysis_checksums.sha256` = `ee2cd91f3960f7ac140a6d23708699137755df1bc7d60275eca7896cd933e5aa`; 108/108 outputs byte-identical on re-run; zero ablation reads |
| 7 | Tables, figures, equations, method artifacts | **FROZEN** | `artifact_binding.csv` 55 artifact rows, full SHA-256 chains; 4,349 value comparisons 0 unexplained mismatch |
| 8 | Main-manuscript + supplement drafting | **FROZEN** | number-binding audit 0 unbound/0 forbidden; no-ablation scan clean |
| 9 | Dual-format PDF/Word production | **FROZEN** | `DT-GSK.pdf` 928,688 B / `supplementary.pdf` 889,540 B / `DT-GSK.docx` 3,061,644 B / `supplementary.docx` 12,837,665 B; validate_docx 33/33; parity 0 FAIL |
| 10 | Adversarial review | **FROZEN** | 35 tickets dispositioned (17 fixed, 12 deferred-change-controlled, 3 rejected-invalid, 3 Word-cosmetic); 0 open critical/major; `ablation_correction_triggers.md` G0 registered |
| 11 | Primary finalization & pre-ablation freeze | **PASS (this certificate)** | freeze manifests: main `55f01328acda61e39f79bb9c3a6a9a8d5ecb2bd10b4678622a68af45df40ca8d`; primary `d5816e871d8e02f63983d3ec507d527ec44dadd00054833a3d53d34f9b0f07b6`; supplement `72cb56af64bbd344e920b869c7d8563d05db9d6dfb817d774560b82e1e6894c3` |

*(Approver quorums per `phase_gate_register.csv`; anchor `262fc16c9` identical across all
Phase 0–2 authority artifacts. Phase-3 freeze was captured at its own anchor `708a927bf…` and is
carried forward unchanged.)*

---

## 3. Freeze-manifest set issued at this gate

- `papers/governance/main_manuscript_freeze_manifest.json`
  (`55f01328acda61e39f79bb9c3a6a9a8d5ecb2bd10b4678622a68af45df40ca8d`) — 14 files:
  `main.tex`, 7 `sections/*.tex`, `DT-GSK.pdf`, `DT-GSK.docx`, `claims_evidence_matrix.csv`,
  `citation_usage_map.csv`, `artifact_binding.csv`, `references.bib`; content
  `FROZEN_BEFORE_ABLATION`.
- `papers/governance/primary_freeze_manifest.json`
  (`d5816e871d8e02f63983d3ec507d527ec44dadd00054833a3d53d34f9b0f07b6`) — release id + evidence
  manifest hash + analysis-bundle hash + source-use audit reference + artifact-binding coverage
  (55 rows).
- `papers/governance/pre_ablation_supplement_freeze_manifest.json`
  (`72cb56af64bbd344e920b869c7d8563d05db9d6dfb817d774560b82e1e6894c3`) — `supplementary.{tex,pdf,docx}`
  + 40 bound figure assets; S6 reserved comment-only slot verified to render nothing.

---

## 4. Verification hooks satisfied (Phase 11)

- **Page budget:** `DT-GSK.pdf` B1 = 32 main-text pages ≤ 34 hard cap → PASS; supplement 32 pp.
- **Determinism:** all four artifacts rebuilt byte-identical to frozen (sizes in §2, Gate 9).
- **No-ablation scan:** zero rendered ablation content in both PDFs and both DOCX; the sole
  rendered token is the IN-02 disavowal ("not as a measured component contribution"); reserved S6
  comment renders nothing; orphan `sections/supplementary_content.tex` is unbuilt
  (`no_ablation_scan.md`).
- **Phase-12 prerequisites:** 6/6 GREEN (`phase12_prerequisites.md`) — freeze manifest intact,
  pre-registration + toggle audit complete, promotion tool operational, 7-cell staging present with
  validated baseline-D100 repair, no historical-result leakage.
- **Deferred figure defects R4-T1/T2:** documented as change-controlled, non-blocking pre-rendered
  checksum-bound assets scheduled for the post-Phase-12 fix pass (Gate-10 disposition); content
  freeze is **not** blocked.
- **D-WORD-01 (Gate-9 exception):** Microsoft Word unavailable non-interactively → open-save-open +
  DOCX→PDF export remain a recorded author-side pre-submission step (not driven here).

---

## 5. Authorization

**Phase 12 (frozen-algorithm ablation, supplementary integration, final verification, and
publication packaging) is AUTHORIZED to begin.** Entry is granted subject to the standing
constraints: the ablation reads only from a Section-2.4-promoted immutable release; no ablation
number, rank, p-value, effect size, or component-causality/efficacy claim may enter the frozen
main manuscript; ablation prose is admissible in the **supplement build only** (the reserved S6
slot); and any correction to frozen text must follow `correction_exception_protocol.md`.

**Gate-11 approvers (per `phase_gate_register.csv`): P1; P10.** The gate-state flip in
`phase_gate_register.csv` and the freeze commit are reserved to the gate owner.

*Certificate issued at anchor `cffcbb48153fd6395c67bb35ece0107269c15694`, release
`rel-2026-07-10-262fc16c9`. Reopening any Phase 0–11 gate requires a
`change_request_register.csv` row per Section 12.2.*
