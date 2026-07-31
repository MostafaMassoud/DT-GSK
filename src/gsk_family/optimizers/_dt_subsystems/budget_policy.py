"""Budget, reliability and sample-protection helpers for TERRA-GSK."""
from __future__ import annotations

from dataclasses import dataclass
import math


def dimension_scaled_n_min(dim: int) -> int:
    """Dimension-scaled population floor used by sample-protected NLPSR."""
    d = max(1, int(dim))
    return max(12, int(math.ceil(2.5 * math.sqrt(float(d)) + math.log2(float(d) + 1.0))))


@dataclass(slots=True)
class SPNlpsrState:
    """Sample-Protected NLPSR floor governor (Phase-8 block).

    Tracks the number of subspace decisions (linkage accept-or-reject
    events) recorded since the start of the run. While that count is
    below ``min_subspace_samples`` *and* the budget fraction is below
    ``release_tau`` (default 0.70 = PTR refine boundary), NLPSR's NP
    target is clamped to at least ``dimension_scaled_n_min(dim) +
    extra_floor``.

    Once the sample budget is reached, or budget_frac >= release_tau,
    the floor is released and NLPSR may shrink per the standard
    L-SHADE convention.

    Pure-state object: no RNG draws, no baseline-selection effects, no
    boundary-repair changes. When ``enabled=False`` it is a strict
    pass-through (``clamp`` returns ``np_target`` unchanged).
    """

    enabled: bool = False
    dim: int = 1
    min_subspace_samples: int = 64
    release_tau: float = 0.70
    extra_floor: int = 0
    subspace_sample_count: int = 0

    @classmethod
    def create(
        cls,
        *,
        enabled: bool,
        dim: int,
        min_subspace_samples: int = 64,
        release_tau: float = 0.70,
        extra_floor: int = 0,
    ) -> "SPNlpsrState":
        return cls(
            enabled=bool(enabled),
            dim=int(dim),
            min_subspace_samples=max(0, int(min_subspace_samples)),
            release_tau=max(0.0, min(1.0, float(release_tau))),
            extra_floor=max(0, int(extra_floor)),
            subspace_sample_count=0,
        )

    def record_subspace_decision(self, count: int = 1) -> None:
        if not self.enabled:
            return
        if count <= 0:
            return
        self.subspace_sample_count += int(count)

    def floor(self, *, budget_frac: float) -> int:
        if not self.enabled:
            return 0
        tau = max(0.0, min(1.0, float(budget_frac)))
        if tau >= self.release_tau:
            return 0
        if self.subspace_sample_count >= self.min_subspace_samples:
            return 0
        base = dimension_scaled_n_min(self.dim)
        return int(base + max(0, int(self.extra_floor)))

    def clamp(self, np_target: int, *, budget_frac: float) -> int:
        f = self.floor(budget_frac=budget_frac)
        if f <= 0:
            return int(np_target)
        return int(max(int(np_target), f))


@dataclass(slots=True)
class LinkageReliabilityState:
    """Learned-vs-random linkage acceptance-lift ledger."""

    alpha: float = 1.0
    lcb_z: float = 1.64
    threshold: float = 0.0
    min_samples: int = 12
    learned_success: int = 0
    learned_total: int = 0
    random_success: int = 0
    random_total: int = 0
    last_lift: float = 0.0
    last_lcb: float = 0.0
    reliable: bool = False

    def update(self, *, learned_success: int = 0, learned_total: int = 0, random_success: int = 0, random_total: int = 0) -> None:
        self.learned_success += max(0, int(learned_success))
        self.learned_total += max(0, int(learned_total))
        self.random_success += max(0, int(random_success))
        self.random_total += max(0, int(random_total))

    def refresh(self) -> None:
        a = max(0.0, float(self.alpha))
        p_l = (self.learned_success + a) / max(1e-12, self.learned_total + 2.0 * a)
        p_r = (self.random_success + a) / max(1e-12, self.random_total + 2.0 * a)
        var_l = p_l * (1.0 - p_l) / max(1.0, float(self.learned_total + 2.0 * a))
        var_r = p_r * (1.0 - p_r) / max(1.0, float(self.random_total + 2.0 * a))
        self.last_lift = float(p_l - p_r)
        self.last_lcb = float(self.last_lift - float(self.lcb_z) * math.sqrt(max(0.0, var_l + var_r)))
        self.reliable = bool(
            self.learned_total >= int(self.min_samples)
            and self.random_total >= int(self.min_samples)
            and self.last_lcb > float(self.threshold)
        )

    def admit(self) -> bool:
        return bool(self.reliable)


@dataclass(slots=True)
class PredictedValueGate:
    """SRI-v2: Predictive Subspace Reliability gate.

    Replaces the LCB-only `LinkageReliabilityState.admit()` boolean with a
    *predicted-value* admission rule:

        predicted_improvement = lcb_lift * remaining_budget_frac * acceptance_per_eval

    where ``lcb_lift = max(0, p_learned - p_random - lcb_z * sigma)``.

    A subspace decision is admitted iff
    ``predicted_improvement > min_predicted_gain[phase]``.  Once admitted,
    the gate uses *hysteresis*: it stays admitted until the predicted gain
    drops below ``min_predicted_gain[phase] * hysteresis_factor`` (default
    0.5), at which point it exits subspace mode.

    Per the SRI-v2 design, five phase thresholds are
    configured:

    | phase_code | name      | default min_gain | reasoning                           |
    |---:|---:|---:|---|
    | 0 | explore   | 0.20 | Coarse phase; conservative              |
    | 1 | structure | 0.10 | Linkage signals start to be reliable    |
    | 2 | exploit   | 0.05 | Subspace pays off most here             |
    | 3 | refine    | 0.15 | Late-phase precision needs full coords  |
    | 4 | escape    | 1.00 | Effectively gates subspace OFF          |

    Pure-state object: no RNG draws, no baseline-selection effects, no
    boundary-repair changes.  When ``enabled=False`` the gate is a strict
    pass-through (``admit()`` defers to the caller's prior decision; in
    dt_gsk.py the call site uses the legacy LCB gate when SRI-v2 is off).

    The gate stores its own per-phase admission state so callers do not
    need to thread it through.  ``last_predicted_improvement`` is exposed
    for telemetry.
    """

    enabled: bool = False
    # Phase-conditional admission thresholds.
    min_gain_table: tuple[float, float, float, float, float] = (0.20, 0.10, 0.05, 0.15, 1.00)
    hysteresis_factor: float = 0.5
    # Evidence window: rolling samples for acceptance rate (0 = no window).
    evidence_window: int = 0
    # Telemetry.
    last_predicted_improvement: float = 0.0
    last_phase_code: int = 0
    last_admission: bool = False

    @classmethod
    def create(
        cls,
        *,
        enabled: bool,
        min_gain_explore: float = 0.20,
        min_gain_structure: float = 0.10,
        min_gain_exploit: float = 0.05,
        min_gain_refine: float = 0.15,
        min_gain_escape: float = 1.00,
        hysteresis_factor: float = 0.5,
        evidence_window: int = 0,
    ) -> "PredictedValueGate":
        return cls(
            enabled=bool(enabled),
            min_gain_table=(
                max(0.0, float(min_gain_explore)),
                max(0.0, float(min_gain_structure)),
                max(0.0, float(min_gain_exploit)),
                max(0.0, float(min_gain_refine)),
                max(0.0, float(min_gain_escape)),
            ),
            hysteresis_factor=max(0.0, min(1.0, float(hysteresis_factor))),
            evidence_window=max(0, int(evidence_window)),
            last_predicted_improvement=0.0,
            last_phase_code=0,
            last_admission=False,
        )

    def predict_improvement(
        self,
        *,
        lcb_lift: float,
        budget_frac: float,
        acceptance_per_eval: float,
    ) -> float:
        """Compute the predicted-improvement scalar."""
        # Clamp every input to a sane non-negative range so a caller cannot
        # accidentally inject negative budget or acceptance from telemetry.
        lift = max(0.0, float(lcb_lift))
        rb = 1.0 - max(0.0, min(1.0, float(budget_frac)))
        accept = max(0.0, float(acceptance_per_eval))
        return float(lift * rb * accept)

    def admit(
        self,
        *,
        lcb_lift: float,
        budget_frac: float,
        acceptance_per_eval: float,
        phase_code: int,
        legacy_admission: bool = False,
    ) -> bool:
        """Decide whether subspace mode is admitted under SRI-v2.

        When ``enabled=False`` the gate falls back to ``legacy_admission``
        (the caller's bare LCB decision) so the SRI-v2 wiring is a strict
        pass-through under the locked-headline byte-stability invariant.
        """
        if not self.enabled:
            self.last_predicted_improvement = 0.0
            self.last_phase_code = int(phase_code)
            self.last_admission = bool(legacy_admission)
            return bool(legacy_admission)
        pi = self.predict_improvement(
            lcb_lift=lcb_lift,
            budget_frac=budget_frac,
            acceptance_per_eval=acceptance_per_eval,
        )
        idx = max(0, min(4, int(phase_code)))
        threshold = float(self.min_gain_table[idx])
        # Hysteresis: once admitted, the exit threshold is tighter.
        if self.last_admission and idx == self.last_phase_code:
            exit_threshold = threshold * float(self.hysteresis_factor)
            admit = bool(pi > exit_threshold)
        else:
            admit = bool(pi > threshold)
        self.last_predicted_improvement = pi
        self.last_phase_code = idx
        self.last_admission = admit
        return admit


@dataclass(slots=True)
class BudgetPhaseDecision:
    phase_code: int
    local_search_allowed: bool
    escape_allowed: bool


def budget_phase_decision(
    *,
    budget_frac: float,
    remaining: int,
    pop_size: int,
    local_search_min_evals: int,
    heat: float,
    acceptance_rate: float,
    stagnation_gens: int,
    exploration_debt: float,
    min_evals_frac: float = 0.01,
    max_nfes: int = 1,
) -> BudgetPhaseDecision:
    """Deterministic budget-safe switch for LS/escape gates."""
    tau = max(0.0, min(1.0, float(budget_frac)))
    min_rem = max(int(2 * max(1, pop_size)), int(local_search_min_evals), int(float(min_evals_frac) * max(1, int(max_nfes))))
    enough = int(remaining) >= int(min_rem)
    phase = 0 if tau < 0.25 else 1 if tau < 0.55 else 2 if tau < 0.80 else 3
    escape = bool(enough and stagnation_gens >= 8 and exploration_debt > 0.05 and acceptance_rate <= 0.12 and heat >= 0.25 and tau < 0.92)
    ls = bool(enough and tau >= 0.70 and heat <= 0.45 and phase >= 2)
    if escape:
        phase = 4
    return BudgetPhaseDecision(phase_code=int(phase), local_search_allowed=ls, escape_allowed=escape)


__all__ = [
    "dimension_scaled_n_min",
    "LinkageReliabilityState",
    "PredictedValueGate",
    "SPNlpsrState",
    "BudgetPhaseDecision",
    "budget_phase_decision",
]
