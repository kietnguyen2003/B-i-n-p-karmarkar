"""[MS C09/M09; BC 4.4.1-4.4.10, (4.42)-(4.57)] Source example and independent oracle."""
import numpy as np
from .types import CanonicalLP


def report_example_lp() -> CanonicalLP:
    """[BC (4.45)] min w=u2+u3; A has actual shape (0,3); z=2w."""
    return CanonicalLP(np.empty((0, 3)), np.array([0., 1., 1.]), "report_4_4",
                       zero_witness=np.array([1., 0., 0.]))


def original_to_u(x1: float, x2: float) -> np.ndarray:
    """[BC (4.44)] Add slack s, then divide all three coordinates by 2."""
    u = np.array([x1/2, x2/2, 1-(x1+x2)/2], dtype=float)
    if not np.isfinite(u).all() or np.min(u) < 0:
        raise ValueError("point is outside the original feasible triangle")
    return u


def u_to_original(u: np.ndarray) -> np.ndarray:
    """[BC (4.46)] Return original (x1,x2), keeping u distinct from x."""
    u = np.asarray(u, dtype=float)
    if u.shape != (3,) or not np.isfinite(u).all() or np.min(u) < 0 or abs(u.sum()-1) > 1e-9:
        raise ValueError("u must belong to Delta_3")
    return 2*u[:2]


def analytic_u(k: int) -> np.ndarray:
    """[BC (4.54)] Independent oracle (1,t,t)/(1+2t), t=0.7**k; never a solver step.

    Extremely large k can underflow t to zero; that is an oracle float limitation,
    not a claim that the finite mathematical sequence reaches the boundary.
    """
    if isinstance(k, bool) or not isinstance(k, (int, np.integer)) or k < 0:
        raise ValueError("k must be a nonnegative integer")
    t = np.exp(k*np.log(0.7))
    return np.array([1., t, t])/(1+2*t)


def analytic_objective(k: int) -> float:
    """[BC (4.55)] Original objective z, twice canonical w."""
    return float(2*analytic_u(k)[1:].sum())


def analytic_potential(k: int) -> float:
    """[BC (4.56)] Source potential with c=(0,1,1), not the scaled z objective."""
    analytic_u(k)  # validate k
    return float(3*np.log(2)+k*np.log(0.7))


def minimum_example_iterations(epsilon: float) -> int:
    """[BC (4.57)] Least k with ORIGINAL z(k)<=epsilon; source example only."""
    if not np.isfinite(epsilon) or epsilon <= 0:
        raise ValueError("epsilon must be finite and positive")
    if epsilon >= 4/3:
        return 0
    k = max(0, int(np.ceil((np.log(epsilon)-np.log(4-2*epsilon))/np.log(0.7))))
    # Boundary adjustment avoids a ceil error at an exact geometric threshold.
    while k > 0 and analytic_objective(k-1) <= epsilon:
        k -= 1
    while analytic_objective(k) > epsilon:
        k += 1
    return k

