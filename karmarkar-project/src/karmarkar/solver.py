"""[MS C08/M08; BC 4.3.3-4.3.5] Controller of Algorithm 4.1, no LP dependency."""
import numpy as np
from .types import CanonicalLP, SolverConfig, SolverResult, StopReason, ProofStatus
from .canonical import validate_canonical
from .iteration import karmarkar_step


def solve_karmarkar(problem: CanonicalLP, config: SolverConfig | None = None) -> SolverResult:
    """[BC Algorithm 4.1; MS C08] Validate, iterate, monitor, return a precise reason.

    Absolute epsilon applies to cTx ONLY when a feasible zero witness plus a
    nonnegative lower bound have been checked. Unverified demos never acquire
    an optimality claim. Exact optimality certification is outside this core.
    """
    config = config or SolverConfig()
    validation = validate_canonical(problem, config)
    x = np.ones(validation.n)/validation.n if validation.n else np.array([])
    try:
        c = np.asarray(problem.c, dtype=float)
    except (TypeError, ValueError):
        c = np.array([])
    trace, completed = [], 0
    scoped = (validation.nonnegative == ProofStatus.PROVEN and validation.zero_optimum_known
              and config.alpha == 0.25)
    diag = {"validation": validation, "theorem_scope": "zero-optimum conditions checked numerically" if scoped else "UNVERIFIED",
            "exact_optimality_certificate": False, "epsilon_objective": "canonical cTx"}

    def finish(reason: StopReason, message: str) -> SolverResult:
        """[MS 3.3] Preserve last valid iterate and all enabled trace records."""
        f = float(c@x) if x.size and x.shape == c.shape else float("nan")
        return SolverResult(x.copy(), f, completed, reason, trace, message, diag)

    if not validation.valid:
        return finish(StopReason.INVALID_INPUT, "; ".join(validation.errors))
    if validation.nonnegative != ProofStatus.PROVEN and config.require_nonnegative_certificate and not config.allow_unverified_demo:
        return finish(StopReason.PRECONDITION_UNVERIFIED, "Nonnegativity is unverified; explicitly enable educational demo to continue")
    if config.monitor_potential and not scoped:
        return finish(StopReason.PRECONDITION_UNVERIFIED, "Potential threshold monitor requires alpha=1/4 and verified zero-optimum context")
    for k in range(config.max_iter+1):
        f = float(c@x)
        if validation.zero_optimum_known and 0 <= f <= config.epsilon:
            return finish(StopReason.APPROX_TOL_REACHED, "Canonical objective threshold reached; no exact optimum certificate")
        if k == config.max_iter:
            break
        with np.errstate(over="raise", divide="raise", invalid="raise"):
            rec = karmarkar_step(problem, x, config, k)
        if config.store_trajectory:
            trace.append(rec)
        if rec.status is not None:
            return finish(rec.status, rec.diagnostics.get("error", "Projected direction is absent or numerically too small"))
        x = rec.x_after.copy()
        completed += 1
        if config.verbose:
            print(f"k={completed}: cTx={rec.f_after:.8g}, decrease={rec.diagnostics['potential_decrease']}")
        decrease = rec.diagnostics["potential_decrease"]
        if config.monitor_potential and decrease is not None and decrease < 1/8-config.potential_tol:
            rec.status = StopReason.POTENTIAL_TEST_FAILED
            return finish(StopReason.POTENTIAL_TEST_FAILED, "Potential monitor failed; this is NOT a positive-optimum certificate")
    return finish(StopReason.MAX_ITERATIONS, "Maximum iterations reached without the requested approximation threshold")

