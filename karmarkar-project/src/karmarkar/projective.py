"""[MS C04/M04; BC 4.2.4, (4.18)-(4.23)] Fixed-reference projective maps."""
import numpy as np


def _inputs(a: np.ndarray, point: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """[BC (4.19)-(4.21)] Validate positive reference and simplex point."""
    a, point = np.asarray(a, dtype=float), np.asarray(point, dtype=float)
    if a.ndim != 1 or a.size < 2 or point.shape != a.shape:
        raise ValueError("reference and point must be matching vectors, n>=2")
    if not np.isfinite(a).all() or not np.isfinite(point).all() or np.any(a <= 0) or np.any(point < 0):
        raise ValueError("reference must be strictly positive; point finite and nonnegative")
    if abs(a.sum()-1) > 1e-9 or abs(point.sum()-1) > 1e-9:
        raise ValueError("reference and point must have sum 1")
    return a, point


def to_projective(a: np.ndarray, x: np.ndarray) -> np.ndarray:
    """[BC (4.19),(4.21)] T_a(x), using ONE fixed positive reference a."""
    a, x = _inputs(a, x)
    with np.errstate(over="raise", divide="raise", invalid="raise"):
        ratios = x/a
        denom = float(ratios.sum())
    if not np.isfinite(denom) or denom <= 0:
        raise ValueError("invalid forward projective denominator")
    return ratios/denom


def from_projective(a: np.ndarray, y: np.ndarray) -> np.ndarray:
    """[BC (4.20),(4.28),(4.41)] Inverse; normalization is part of the formula."""
    a, y = _inputs(a, y)
    weighted = a*y
    denom = float(weighted.sum())
    if not np.isfinite(denom) or denom <= 0:
        raise ValueError("invalid inverse projective denominator")
    return weighted/denom

