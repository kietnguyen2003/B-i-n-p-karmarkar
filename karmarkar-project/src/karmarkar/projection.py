"""[MS C05/M05; BC 4.2.3,4.2.5, (4.15)-(4.17),(4.25)] SVD kernel projection."""
import numpy as np
from scipy.linalg import svd


def project_to_kernel(B: np.ndarray, v: np.ndarray, rtol: float = 1e-14,
                      atol: float = 0.0) -> tuple[np.ndarray, dict]:
    """[BC (4.16),(4.25); MS T16-T21] Project v with a full orthonormal null basis.

    Rank cutoff is max(atol, rtol*s_max). Handles dependent rows and empty
    kernels. No inverse of BB^T is formed. Return rank/nullity and residuals.
    """
    B, v = np.asarray(B, dtype=float), np.asarray(v, dtype=float)
    if B.ndim != 2 or v.ndim != 1 or B.shape[1] != v.size:
        raise ValueError("B,v shapes mismatch")
    if not np.isfinite(B).all() or not np.isfinite(v).all() or min(rtol, atol) < 0:
        raise ValueError("finite inputs and nonnegative cutoffs required")
    _, s, vh = svd(B, full_matrices=True)
    cutoff = max(atol, rtol*float(s.max(initial=0)))
    rank = int(np.count_nonzero(s > cutoff))
    N = vh[rank:].T
    p = N @ (N.T @ v) if N.shape[1] else np.zeros_like(v)
    return p, {"rank": rank, "null_dim": N.shape[1], "svd_cutoff": cutoff,
               "singular_values": s, "equality_residual": float(np.linalg.norm(B@p)),
               "orthogonality_residual": float(np.linalg.norm(N.T@(v-p))),
               "p_orthogonal_remainder": float(abs((v-p)@p))}

