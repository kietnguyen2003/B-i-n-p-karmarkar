"""[MS C03/M03; BC 4.2.2, (4.9)-(4.12)] Simplex geometry and isometry."""
import numpy as np


def simplex_geometry(n: int) -> tuple[np.ndarray, float, float]:
    """[BC (4.4),(4.11)] Return center, inradius and circumradius, n>=2."""
    if isinstance(n, bool) or not isinstance(n, (int, np.integer)) or n < 2:
        raise ValueError("n must be an integer >= 2")
    return np.ones(n) / n, 1 / np.sqrt(n * (n - 1)), np.sqrt((n - 1) / n)


def simplex_embedding(u: np.ndarray) -> np.ndarray:
    """[BC Fig 4.3; MS 7.1] Isometrically map Delta_3 to a 2D plane.

    Columns are an orthonormal basis of e-perp. Coordinates are relative to a0.
    """
    basis = np.array([[1/np.sqrt(2), 1/np.sqrt(6)],
                      [-1/np.sqrt(2), 1/np.sqrt(6)], [0, -2/np.sqrt(6)]])
    return (np.asarray(u) - 1/3) @ basis

