# GitHub exposure window and the clone record

Seven copyrighted third-party PDFs reached the public GitHub remote and were served from it for
about twenty days. This file records **how long that lasted** and **what GitHub's traffic counters
saw**, because those counters expire on a rolling 14-day window and cannot be reconstructed once
they roll off. The incident itself, and what is withheld from this repository and why, is
`papers/governance/decision_log.md` **D-0049**.

## The exposure window

Derived from the local reflog, which is the only surviving record of when `main` pointed where:

| Event | Local time (+0300) | UTC |
|---|---|---|
| `b9846e4` "Reference Papers" becomes the tip of `main` | 2026-08-07 23:45:59 | 2026-08-07 20:45:59 |
| `main` reset to `public/squash-candidate` (`02d1791`) | 2026-08-27 01:17:02 | 2026-08-26 22:17:02 |

`b9846e4` was `main`'s tip for that entire span -- the reflog shows no intervening move. So the
tree served to anyone who cloned the default branch between those two instants contained the seven
PDFs. **Roughly nineteen days and two hours; twenty UTC calendar days touched (08/07 through
08/26).**

The commit timestamp is a *lower bound* on when the tree reached the remote: it is when the commit
was authored locally, not when it was pushed. Nothing local can date the push more precisely.

## The capture

GitHub -> Insights -> Traffic, captured **2026-08-27**. Window shown: **08/13 -- 08/26** (14 days).

| Panel | Value |
|---|---|
| Clones in last 14 days | **11** |
| Unique cloners in last 14 days | **9** |
| Total views in last 14 days | **2** |
| Unique visitors in last 14 days | **2** |

Per-day, read off the plotted lines rather than from printed text:

| Day | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 | 21 | 22 | 23 | 24 | 25 | 26 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Clones | 1 | 0 | 2 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 1 | 1 | 2 | 1 |
| Unique cloners | 1 | 0 | 1 | 0 | 0 | 0 | 2 | 1 | 0 | 0 | 1 | 1 | 2 | 1 |

The clone row sums to 11, matching the printed total, which corroborates the reading. The unique
row sums to 10 against a printed period total of 9; that is expected, not a discrepancy -- GitHub
dedupes per day in the chart and across the whole window in the header, so at least one cloner
returned on a second day.

## What the capture covers, and what was already lost

**Every one of the 14 captured days falls inside the exposure window.** The window closed at
22:17 UTC on 08/26, so the final captured day is also the final day of exposure. No post-removal
traffic is mixed into these counts.

**Six days were already gone when the capture was taken: 08/07 (from 20:46 UTC) through 08/12.**
They had rolled off the 14-day window before anyone looked. Whatever cloned the tree in those six
days is unrecoverable -- not by the author, not by GitHub Support, not by any later capture. This
is a permanent gap in the record and should be stated as one rather than papered over.

So the honest summary is: **at least 9 distinct actors, and at least 11 clones, took a tree
containing the seven PDFs -- with six days of the exposure window unmeasured.** The true totals are
floors, not estimates.

## What this does not establish

- **It does not identify anyone.** GitHub's clone traffic is counts only; it exposes no usernames,
  no IP addresses, no organisations. "9 unique cloners" is a cardinality, nothing more.
- **It does not distinguish humans from machines.** CI runners, mirroring services, forks-by-clone
  and archival crawlers all register as clones. A count of 11 over twenty days is consistent with
  almost entirely automated traffic.
- **It does not measure browsing.** Web views over the same window were **2**, from 2 unique
  visitors. The PDFs were reachable by direct URL, but essentially nobody browsed the repository.
  Clone traffic, which takes the whole tree unconditionally, is the channel that matters here.
- **It does not close the incident.** The PDFs are off every ref -- verified: zero hits on `main`,
  `v2.13` and `v2.21` -- but remain fetchable by direct SHA from `b9846e4` until GitHub garbage-
  collects. That request to GitHub Support is still open (D-0049).

## Where the rest lives

- **The decision and the withholding policy:** `papers/governance/decision_log.md` D-0049.
- **The `.gitignore` trap that caused it:** `CLAUDE.md` "Never break these" item 10 -- a glob that
  does not cross `/` is not an exclusion. Verify with `git check-ignore -v <path>`, never by
  reading the pattern.
- **The branches that must never be pushed:** `archive/revision-pass-39-full` and
  `revision/pass-39` both carry this material in their histories.

---

# Remediation: the GitHub Support purge request -- CLOSED, WILL NOT BE FILED

**Status: closed by author decision, 2026-08-28. The request will not be made.** It was
deferred on 2026-08-27 and closed the following day. **This section is a record, not a
to-do: do not re-raise it, and do not act on it without the author saying so.**

It is kept rather than deleted because it documents a decision about material that is not
the author's alone -- seven third-party copyrighted PDFs and a co-author's biographical
data. Recording that the remediation was considered and declined is more honest than
leaving no trace of it. The state below does not change on its own: unreachable git
objects carry no expiry date, GitHub collects on an unannounced schedule with no
guarantee, and both commits were still served when this was closed.

## Scope -- TWO unreachable commits, not one

D-0049 and the Phase 0 work order originally named only `b9846e4`. Verified 2026-08-27, the
rewind left **two** commits unreachable from every branch and tag, and **both are still served**:

| Commit (full SHA is what Support needs) | Carries | Still served |
|---|---|---|
| `b9846e47024e48a0f8ce3e4f22bffbd794b2a355` | seven third-party copyrighted PDFs, 38.8 MiB, under `reference_papers/Academic_Research_Guidelines/` | **HTTP 206** |
| `bddfe24ede2dbf934bc76636a61b4f14ff3ff470` | `papers/submission/AUTHOR_DATA_HANDOFF.md` (16.9 KiB) -- co-author biographical data published before its subjects approved it | **HTTP 206** |

`bddfe24` is the parent of `b9846e4`. Purging only the child leaves the parent serving the
handoff, and the parent is the one carrying other people's personal data. **A request naming one
SHA is an incomplete request.**

The web UI also still renders the tree: `GET /tree/b9846e4.../reference_papers` returns **HTTP 200**.

Last good commit before the pair, and still on `main`: `de762a4745845e625c6c264df1e31a421c7634e0`.

## Why this request can actually succeed

Checked against the public API on 2026-08-27: **0 forks, `network_count` 0, 0 pull requests in any
state.** Nothing outside the repository holds a reference to these objects. Forks are the usual
reason a purge request fails -- objects in a fork network survive because another repository
legitimately references them, and GitHub will not delete another account's data. That failure mode
does not apply here, so a garbage collection should be complete.

This is **not** a DMCA matter. DMCA is for reporting someone else's infringement; here the
repository owner published the material and is asking for their own remediation.

## After the purge

Re-run the reachability check and expect **404** where it now returns 206:

    curl -s -o NUL -w "%{http_code}\n" -r 0-0 \
      https://raw.githubusercontent.com/MostafaMassoud/DT-GSK/<full-sha>/<path>

Until then, and permanently afterwards: **never push `archive/revision-pass-39-full` or
`revision/pass-39`.** Both carry this material in their histories, and pushing either would
re-anchor the very objects the request asks GitHub to collect -- making the purge pointless and
the second request harder to justify.

The two SHAs will stop resolving on GitHub once collected. They still resolve in any local clone
that has them, which is where the evidence for this record lives; nothing here depends on GitHub
continuing to serve them.
