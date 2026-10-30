"""[MS 4/C01, M01; BC 4.3.1-4.3.5] Typed input, trace and stop contracts."""
from dataclasses import dataclass, field
from enum import Enum
import numpy as np


class StopReason(str, Enum):
    """[BC 4.3.5; MS 3.3] Approximation and failures have distinct meanings."""
    APPROX_TOL_REACHED = "approx_tol_reached"
    MAX_ITERATIONS = "max_iterations"
    NO_PROJECTED_DIRECTION = "no_projected_direction"
    NUMERICALLY_UNDETERMINED = "numerically_undetermined"
    INVALID_INPUT = "invalid_input"
    NUMERICAL_FAILURE = "numerical_failure"
    POTENTIAL_TEST_FAILED = "potential_test_failed"
    PRECONDITION_UNVERIFIED = "precondition_unverified"


class ProofStatus(str, Enum):
    """[MS 2.2] Checking the center alone does not prove global nonnegativity."""
    PROVEN = "PROVEN"
    DISPROVEN = "DISPROVEN"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class CanonicalLP:
    """[BC (4.2),(4.7)-(4.8)] Homogeneous equalities plus simplex constraints.

    zero_witness is independently checked for feasibility and zero objective.
    dual_multiplier/dual_bound certify c - A.T@lambda - beta*e >= 0, beta>=0.
    negative_witness can disprove objective nonnegativity on the feasible set.
    """
    A: np.ndarray
    c: np.ndarray
    name: str = "canonical_lp"
    zero_witness: np.ndarray | None = None
    negative_witness: np.ndarray | None = None
    dual_multiplier: np.ndarray | None = None
    dual_bound: float = 0.0


@dataclass(frozen=True)
class SolverConfig:
    """[BC 4.3.1; MS 2.2] Separate thresholds for feasibility, SVD and p."""
    alpha: float = 0.25
    epsilon: float = 1e-6
    max_iter: int = 1000
    feas_tol: float = 1e-10
    positive_tol: float = 0.0
    projection_abs_tol: float = 1e-14
    projection_rel_tol: float = 1e-12
    potential_tol: float = 1e-9
    svd_rtol: float = 1e-14
    svd_atol: float = 0.0
    require_nonnegative_certificate: bool = True
    allow_unverified_demo: bool = False
    monitor_potential: bool = False
    verbose: bool = False
    store_trajectory: bool = True


@dataclass
class ValidationReport:
    """[MS C02] Structured input issues and scope evidence."""
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    nonnegative: ProofStatus = ProofStatus.UNKNOWN
    zero_optimum_known: bool = False
    n: int = 0
    m: int = 0
    rank_A: int = 0

    @property
    def valid(self) -> bool:
        """[MS C02] Warnings are separate from invalid mathematical input."""
        return not self.errors


@dataclass
class StepRecord:
    """[BC (4.37)-(4.41); MS C07] Complete before/transformed/after evidence."""
    k: int
    x_before: np.ndarray
    D: np.ndarray
    B: np.ndarray
    v: np.ndarray
    p: np.ndarray
    d: np.ndarray | None = None
    y: np.ndarray | None = None
    x_after: np.ndarray | None = None
    f_before: float | None = None
    f_after: float | None = None
    phi_before: float | None = None
    phi_after: float | None = None
    status: StopReason | None = None
    diagnostics: dict = field(default_factory=dict)


@dataclass
class SolverResult:
    """[BC 4.3.5; MS C08] No exact OPTIMAL state is offered by this core."""
    x: np.ndarray
    objective: float
    iterations: int
    status: StopReason
    trace: list[StepRecord]
    message: str
    diagnostics: dict

