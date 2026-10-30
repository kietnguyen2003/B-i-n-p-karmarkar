"""[MS C06/M06; BC 4.2.6, (4.29)-(4.31)] Log-domain potential functions."""
import numpy as np


def potential(x: np.ndarray, c: np.ndarray) -> float:
    """[BC (4.29)] n*ln(cTx)-sum(ln x_i); strict domain, no log(product)."""
    x, c = np.asarray(x, dtype=float), np.asarray(c, dtype=float)
    if x.ndim != 1 or c.shape != x.shape or not np.isfinite(x).all() or not np.isfinite(c).all():
        raise ValueError("potential requires matching finite vectors")
    f = float(c@x)
    if not np.isfinite(f) or f <= 0 or np.any(x <= 0):
        raise ValueError("Phi undefined: x_i>0 and cTx>0 required")
    value = float(x.size*np.log(f)-np.log(x).sum())
    if not np.isfinite(value):
        raise ValueError("nonfinite potential")
    return value


def transformed_potential(a: np.ndarray, y: np.ndarray, c: np.ndarray) -> float:
    """[BC (4.31)] Transformed potential; differs from Phi(x) by sum(log a)."""
    a, y, c = np.asarray(a), np.asarray(y), np.asarray(c)
    if a.shape != y.shape or c.shape != y.shape or not np.isfinite(a).all() or np.any(a <= 0):
        raise ValueError("invalid reference for transformed potential")
    return potential(y, a*c)

