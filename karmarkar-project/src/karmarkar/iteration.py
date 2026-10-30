"""[MS C07/M07; BC 4.3.2, (4.37)-(4.41)] One traceable projective step."""
import numpy as np
from .types import CanonicalLP, SolverConfig, StepRecord, StopReason
from .canonical import equality_residual, equality_threshold
from .geometry import simplex_geometry
from .projection import project_to_kernel
from .projective import from_projective
from .potential import potential


def _check_point(A: np.ndarray, x: np.ndarray, config: SolverConfig) -> dict:
    """[BC Proposition 4.3.1; MS 6.3] Check, never repair, a feasible interior point."""
    if not np.isfinite(x).all() or np.min(x) <= config.positive_tol:
        raise ValueError("nonfinite or nonpositive interior point")
    eq = equality_residual(A, x)
    if abs(x.sum()-1) > config.feas_tol or eq > equality_threshold(A, x, config.feas_tol):
        raise ValueError("simplex/equality feasibility violation")
    return {"min_x": float(x.min()), "sum_residual": float(abs(x.sum()-1)),
            "eq_residual": eq, "scaled_eq_residual": eq/equality_threshold(A, x, 1.0)}


def karmarkar_step(problem: CanonicalLP, x: np.ndarray, config: SolverConfig,
                   k: int = 0) -> StepRecord:
    """[BC (4.37)-(4.41); MS C07] Return full D,B,v,p,d,y,x_next and checks.

    INPUT: validated canonical LP and strictly feasible x. OUTPUT: StepRecord.
    CHECK: projection, step length, positivity, equalities, finite inverse.
    Failure returns a distinct status and diagnostics; no clipping or reference LP.
    """
    x = np.array(x, dtype=float, copy=True)
    A, c = np.asarray(problem.A, dtype=float), np.asarray(problem.c, dtype=float)
    rec = StepRecord(k=k, x_before=x, D=np.diag(x), B=np.empty((0, x.size)),
                     v=x*c, p=np.zeros_like(x))
    try:
        if not 0 < config.alpha < 1:
            raise ValueError("alpha must lie in (0,1)")
        center, r, _ = simplex_geometry(x.size)
        rec.diagnostics.update(_check_point(A, x, config))
        # [BC (4.37)] AD, not A, defines the new equality constraints.
        rec.B = np.vstack((A* x, np.ones((1, x.size))))
        rec.p, info = project_to_kernel(rec.B, rec.v, config.svd_rtol, config.svd_atol)
        rec.diagnostics.update(info)
        rec.f_before = float(c@x)
        if rec.f_before > 0:
            rec.phi_before = potential(x, c)
        pnorm = float(np.linalg.norm(rec.p))
        tiny = config.projection_abs_tol + config.projection_rel_tol*np.linalg.norm(rec.v)
        rec.diagnostics.update(p_norm=pnorm, p_threshold=float(tiny))
        if info["null_dim"] == 0 or pnorm == 0 or (np.all(c == c[0]) and np.all(x == x[0])):
            rec.status = StopReason.NO_PROJECTED_DIRECTION
            return rec
        if pnorm <= tiny:
            rec.status = StopReason.NUMERICALLY_UNDETERMINED
            return rec
        # [BC (4.38)-(4.40)] SVD projection, unit direction, safe radius.
        rec.d = -rec.p/pnorm
        rec.y = center + config.alpha*r*rec.d
        projected_error = np.linalg.norm(rec.B@rec.d)
        projected_tol = config.feas_tol*max(1, np.linalg.norm(rec.B, ord=np.inf))
        if projected_error > projected_tol:
            raise ValueError("projected direction violates equalities")
        _check_point(A*x, rec.y, config)
        step_length = float(np.linalg.norm(rec.y-center))
        if not np.isclose(step_length, config.alpha*r, atol=config.feas_tol, rtol=1e-10) or step_length >= r:
            raise ValueError("transformed step length outside interior ball")
        # [BC (4.41)] This normalization IS the inverse map, not a repair.
        denom = float(x@rec.y)
        rec.x_after = from_projective(x, rec.y)
        after = _check_point(A, rec.x_after, config)
        rec.f_after = float(c@rec.x_after)
        if rec.f_after > 0:
            rec.phi_after = potential(rec.x_after, c)
        rec.diagnostics.update({"after_"+key: value for key, value in after.items()})
        rec.diagnostics.update(direction_norm=float(np.linalg.norm(rec.d)),
                               direction_residual=float(projected_error),
                               step_length=step_length, inradius=r, denominator=denom,
                               transformed_eq_residual=equality_residual(A*x, rec.y),
                               recentered_eq_residual=equality_residual(A*x, center),
                               potential_decrease=(rec.phi_before-rec.phi_after
                                 if rec.phi_before is not None and rec.phi_after is not None else None))
    except (ValueError, FloatingPointError, np.linalg.LinAlgError, OverflowError) as exc:
        rec.status = StopReason.NUMERICAL_FAILURE
        rec.diagnostics["error"] = str(exc)
    return rec

