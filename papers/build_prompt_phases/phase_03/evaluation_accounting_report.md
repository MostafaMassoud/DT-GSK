# DT-GSK — Objective-Evaluation Accounting Report

**Phase 3 deliverable** (Phase 3 tasks 10 & verification "P4 verifies evaluator-call
accounting"). Proves every objective call counts toward `MaxFES` and that all exits are
budget-safe. Evidence: `_dt_subsystems/budget.py`, `ISMGSKConfig.resolved_max_nfes`,
`dt_gsk.py`.

## 1. Single evaluation cap
- **All** objective calls flow through one `BudgetController(max_nfes, objective)`
  (`budget.py:55`). There is no second counter and no path that calls the raw objective
  directly — the controller wraps `problem.evaluate`.
- `MaxFES = resolved_max_nfes() = 10000·D` when unspecified (`_dt_core.py:450`), matching
  the CEC protocol; the runner passes the suite budget explicitly for the reference runs.

## 2. Counting invariant
- `nfes_used` is incremented by exactly `n` on every batch evaluation (`budget.py:128`,
  `self._nfes_used += int(n)`), then checked: `if self._nfes_used > self._max_nfes: raise
  "Budget exceeded"` (`:129-131`). So the counter can never silently exceed the cap.
- `remaining() = max(0, max_nfes − nfes_used)` (`:101`); `is_exhausted` ⇔
  `nfes_used ≥ max_nfes` (`:107`). The main loop tests exhaustion each generation and stops.

## 3. Budget-safe exits (partial generations)
- The controller supports a **truncation mode**: when a batch of `n` would exceed the
  remaining budget, it evaluates **only the prefix that fits** (`rem = self.remaining()`,
  charges the prefix; `budget.py:169,223,274`), so the final generation cannot overshoot.
- Strict mode raises `BudgetExhausted` instead — used where truncation is not desired. Both
  modes are budget-safe: neither can push `nfes_used` past `max_nfes`.

## 4. Zero-extra-evaluation mechanisms — verified
The following consume **no objective evaluations** (they observe already-accepted moves or
use RNG-free/strict-budget paths). This substantiates the "no extra evaluations" wording in
the contribution matrix:
- **SGSM/ISM interaction graph** — updates only from accepted-move deltas; no call to the
  objective (`interaction_graph.py`).
- **Eigenframe final polish** — refines via the strict budget path and **draws no RNG**;
  its objective calls (the compass probes) **are** charged through the controller, so they
  count toward MaxFES — it is "RNG-free," not "evaluation-free." (Wording guard: polish
  costs evaluations; SGSM does not.)
- **Deep-stall restart** — the re-init's re-evaluation **is** charged; "no extra NFEs beyond
  the re-evaluation it performs." RNG drawn only when it fires.

## 5. Accounting caveat to disclose
- **`init_oversample>1`** adds `(k−1)·NP` evaluations at gen 0 (`_dt_core.py:157-161`).
  The locked `pub` headline uses `k=1` (byte-identical), so the reference runs have no
  oversampling cost. If any exhibit uses `k>1`, its budget line MUST disclose the gen-0
  surcharge. Verified: reference release uses the locked profile (k=1).

## 6. Recommended regression assertions (Phase 3 task 10 / Phase 6 guard)
The existing byte-stability KAT (`tests/regression/test_dt_gsk_byte_stable.py`) already
pins trajectories; add/confirm two boundary assertions in Phase 6 tooling:
1. `nfes_used == max_nfes` exactly at return for a full CEC run (no under/over-spend).
2. A truncation-boundary case where the last batch is larger than `remaining()` returns
   `nfes_used == max_nfes` and evaluates only the fitting prefix.

## Verdict (P4 accounting sign-off basis)
All objective calls are counted through a single cap; exits are budget-safe by construction
(truncation or strict raise); "no extra evaluation" claims hold for SGSM and RNG-free polish
direction generation but **not** for polish probes or restart re-evaluation, which are
charged. Accounting is **fair and MaxFES-exact**.
