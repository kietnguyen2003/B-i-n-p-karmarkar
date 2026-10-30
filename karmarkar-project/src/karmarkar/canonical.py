"""[MS C02/M02; BC 4.2.1,4.3.1] Validation and explicit theorem scope."""
from dataclasses import fields
import numpy as np
from .types import CanonicalLP, SolverConfig, ValidationReport, ProofStatus


def equality_residual(A: np.ndarray, x: np.ndarray) -> float:
    """[BC (4.2); MS 6.3] Absolute infinity-norm equality residual."""
    return float(np.max(np.abs(A @ x), initial=0))


def equality_threshold(A: np.ndarray, x: np.ndarray, tol: float) -> float:
    """[MS 6.3, GD] Scale equality tolerance by row norm and vector norm."""
    row_scale = float(np.max(np.sum(np.abs(A), axis=1), initial=0))
    return tol * max(1.0, row_scale * float(np.max(np.abs(x), initial=0)))


def feasible_witness(A: np.ndarray, c: np.ndarray, w: np.ndarray, tol: float) -> bool:
    """[BC (4.2); MS 2.2] Check a supplied feasible witness independently."""
    w = np.asarray(w)
    return bool(w.shape == c.shape and np.isfinite(w).all() and np.min(w) >= 0
                and abs(w.sum()-1) <= tol
                and equality_residual(A, w) <= equality_threshold(A, w, tol))


def validate_canonical(problem: CanonicalLP, config: SolverConfig) -> ValidationReport:
    """[BC (4.2),(4.7)-(4.8); MS C02,T01-T09] Validate without invoking an LP solver.

    Numerical certificate checks use float64 with declared tolerances, not exact
    rational arithmetic. A positive objective at the center alone proves nothing
    about the objective over the entire feasible set.
    """
    r = ValidationReport()
    for key in ("alpha", "epsilon", "feas_tol", "positive_tol", "projection_abs_tol",
                "projection_rel_tol", "potential_tol", "svd_rtol", "svd_atol"):
        value = getattr(config, key)
        if isinstance(value, bool) or not isinstance(value, (int, float, np.number)) or not np.isfinite(value):
            r.errors.append(f"{key} must be finite numeric")
        elif key == "alpha" and not 0 < value < 1:
            r.errors.append("alpha must lie strictly between 0 and 1")
        elif key == "epsilon" and value <= 0:
            r.errors.append("epsilon must be positive")
        elif key not in ("alpha", "epsilon") and value < 0:
            r.errors.append(f"{key} must be nonnegative")
    if isinstance(config.max_iter, bool) or not isinstance(config.max_iter, (int, np.integer)) or config.max_iter < 0:
        r.errors.append("max_iter must be an integer >= 0")
    for f in fields(config):
        if f.type is bool or f.name in ("require_nonnegative_certificate", "allow_unverified_demo", "monitor_potential", "verbose", "store_trajectory"):
            if not isinstance(getattr(config, f.name), bool):
                r.errors.append(f"{f.name} must be bool")
    try:
        A, c = np.asarray(problem.A, dtype=float), np.asarray(problem.c, dtype=float)
    except (TypeError, ValueError):
        r.errors.append("A,c must be real numeric arrays")
        return r
    if c.ndim != 1 or c.size < 2:
        r.errors.append("c must have shape (n,), n>=2")
    if A.ndim != 2 or c.ndim != 1 or A.shape[1] != c.size:
        r.errors.append("A must have shape (m,n), including (0,n)")
    if not np.isfinite(A).all() or not np.isfinite(c).all():
        r.errors.append("A,c must contain only finite values")
    if r.errors:
        return r
    r.n, r.m = c.size, A.shape[0]
    r.rank_A = int(np.linalg.matrix_rank(A)) if r.m else 0
    center = np.ones(r.n)/r.n
    if equality_residual(A, np.ones(r.n)) > equality_threshold(A, np.ones(r.n), config.feas_tol):
        r.errors.append("A@e != 0: center is not feasible; canonical preprocessing required")
    if float(c @ center) <= 0:
        r.errors.append("c@center must be strictly positive")
    if config.positive_tol >= 1/r.n:
        r.errors.append("positive_tol excludes the starting center")
    if r.rank_A < r.m:
        r.warnings.append("A has dependent rows; projection uses SVD")
    if np.min(c) >= 0:
        r.nonnegative = ProofStatus.PROVEN
    if problem.dual_multiplier is not None:
        lam = np.asarray(problem.dual_multiplier, dtype=float)
        beta = problem.dual_bound
        if lam.shape != (r.m,) or not np.isfinite(lam).all() or not np.isfinite(beta) or beta < 0:
            r.errors.append("invalid dual certificate")
        elif np.min(c-A.T@lam-beta) >= -config.feas_tol*max(float(np.max(np.abs(c))), float(np.max(np.abs(A.T@lam))), abs(beta)):
            r.nonnegative = ProofStatus.PROVEN
        else:
            r.errors.append("dual nonnegativity certificate fails")
    if problem.negative_witness is not None:
        w = np.asarray(problem.negative_witness, dtype=float)
        if feasible_witness(A, c, w, config.feas_tol) and c@w < 0:
            r.nonnegative = ProofStatus.DISPROVEN
            r.errors.append("feasible negative objective witness disproves nonnegativity")
        else:
            r.errors.append("invalid negative witness")
    if problem.zero_witness is not None:
        w = np.asarray(problem.zero_witness, dtype=float)
        if feasible_witness(A, c, w, config.feas_tol) and abs(c@w) <= config.feas_tol*float(np.max(np.abs(c))):
            r.zero_optimum_known = r.nonnegative == ProofStatus.PROVEN
        else:
            r.errors.append("zero-optimum witness is invalid")
    if r.nonnegative == ProofStatus.UNKNOWN:
        r.warnings.append("Global objective nonnegativity UNKNOWN; center check is insufficient")
    if not r.zero_optimum_known:
        r.warnings.append("Zero optimum unverified; objective<=epsilon is not an optimality-gap test")
    return r

