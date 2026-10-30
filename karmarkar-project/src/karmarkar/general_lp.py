"""Interactive LP preprocessing and the PDF-faithful Karmarkar loop.

The mathematical core in :mod:`karmarkar.iteration` implements BC (4.37)-(4.41)
and only accepts the homogeneous simplex form.  This module is an explicitly
labelled [DX] adapter for small, bounded teaching problems entered as ordinary
linear programs.  It never calls another optimizer to create a Karmarkar step.

The adapter performs four jobs:

1. replace non-positive/free variables and add slack/surplus variables;
2. find strictly positive primal and dual starting points with objective-free Phase I;
3. minimize the primal-dual gap, which is nonnegative and has optimum zero;
4. embed that bounded system in a standard simplex and run every iteration through
   :func:`karmarkar_step`, preserving D, B, v, p,
   d, y and the inverse projective map for the HTML report.

The finite simplex embedding requires strictly positive primal/dual points and a
fixed positive weighted coordinate sum. Unsupported degenerate cases are rejected
with a specific message instead of silently returning a false solution.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np
from scipy.optimize import linprog
from scipy.linalg import qr

from .canonical import validate_canonical
from .iteration import karmarkar_step
from .projective import from_projective, to_projective
from .types import CanonicalLP, SolverConfig, StepRecord


_CONSTRAINT_SIGNS = {"<=", ">=", "="}
_VARIABLE_SIGNS = {">=0", "<=0", "free"}


@dataclass(frozen=True)
class GeneralLP:
    """A small teaching LP as entered by a notebook user.

    ``objective_constant`` is displayed and included in the reported value but
    does not affect the directions.  ``sense`` is either ``"min"`` or ``"max"``.
    """

    objective: np.ndarray
    constraints: np.ndarray
    rhs: np.ndarray
    constraint_signs: tuple[str, ...]
    variable_signs: tuple[str, ...]
    sense: str = "min"
    objective_constant: float = 0.0
    name: str = "Bài toán nhập từ bàn phím"


@dataclass(frozen=True)
class StandardFormLP:
    """Equality form ``E z = b, z >= 0`` plus the original-variable map."""

    E: np.ndarray
    b: np.ndarray
    c: np.ndarray
    constant: float
    original_map: np.ndarray
    original_offset: np.ndarray
    standard_labels: tuple[str, ...]
    row_labels: tuple[str, ...]
    sense_factor: float


@dataclass(frozen=True)
class SimplexEmbedding:
    """Data needed to move between standard variables and the canonical simplex."""

    general: GeneralLP
    standard: StandardFormLP
    input_standard: StandardFormLP
    solution_map: np.ndarray
    solution_offset: np.ndarray
    embedding_mode: str
    interior: np.ndarray
    interior_margin: float
    weights: np.ndarray
    weighted_total: float
    dimension: int
    scale: np.ndarray
    simplex_start: np.ndarray
    homogeneous_A: np.ndarray
    canonical: CanonicalLP
    phase_one_message: str
    bound_message: str
    zero_witness_message: str
    initial_objective_zero: bool = False


@dataclass(frozen=True)
class GeneralSolverConfig:
    """Controls for the interactive adapter; alpha remains the PDF parameter."""

    alpha: float = 0.25
    max_iter: int = 300
    objective_tolerance: float = 1e-9
    feasibility_tolerance: float = 1e-9
    projection_abs_tol: float = 1e-14
    projection_rel_tol: float = 1e-12
    svd_rtol: float = 1e-14
    max_canonical_dimension: int = 120


@dataclass(frozen=True)
class GeneralIterationRow:
    """Readable values derived from one actual Karmarkar iterate."""

    k: int
    objective: float
    internal_min_objective: float
    canonical_objective: float
    original_x: np.ndarray
    standard_z: np.ndarray
    canonical_u: np.ndarray
    equality_residual: float
    minimum_coordinate: float
    relative_change: float | None


@dataclass
class GeneralKarmarkarResult:
    """Full interactive result; the trace contains the PDF's intermediate arrays."""

    embedding: SimplexEmbedding
    x: np.ndarray
    z: np.ndarray
    u: np.ndarray
    objective: float
    iterations: int
    status: str
    message: str
    trace: list[StepRecord] = field(default_factory=list)
    history: list[GeneralIterationRow] = field(default_factory=list)


@dataclass(frozen=True)
class ReferenceResult:
    """Optional post-run HiGHS comparison; never used to form Karmarkar steps."""

    success: bool
    status: str
    message: str
    x: np.ndarray | None
    objective: float | None


@dataclass(frozen=True)
class ProblemClassification:
    """Pre-run classification of the ordinary LP entered by the user."""

    status: str
    message: str
    objective_value: float | None
    x: np.ndarray | None = None
    alternative_x: np.ndarray | None = None

    @property
    def terminal(self) -> bool:
        """Only a finite optimum proceeds to the projective Karmarkar loop."""
        return self.status != "FINITE_OPTIMUM"


def _as_float_array(value, *, ndim: int, name: str) -> np.ndarray:
    try:
        array = np.asarray(value, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} phải chứa các số hợp lệ") from exc
    if array.ndim != ndim or not np.isfinite(array).all():
        raise ValueError(f"{name} phải là mảng {ndim} chiều và chỉ chứa số hữu hạn")
    return array


def validate_general_lp(problem: GeneralLP) -> GeneralLP:
    """Validate and return a normalized immutable copy of the entered problem."""
    c = _as_float_array(problem.objective, ndim=1, name="Hàm mục tiêu")
    A = _as_float_array(problem.constraints, ndim=2, name="Ma trận ràng buộc")
    b = _as_float_array(problem.rhs, ndim=1, name="Vế phải")
    if c.size < 1:
        raise ValueError("Cần ít nhất một biến")
    if A.shape != (b.size, c.size):
        raise ValueError("Số hàng/cột ràng buộc không khớp số ràng buộc và số biến")
    signs = tuple(str(s).strip().lower() for s in problem.constraint_signs)
    variable_signs = tuple(str(s).strip().lower() for s in problem.variable_signs)
    if len(signs) != b.size or any(s not in _CONSTRAINT_SIGNS for s in signs):
        raise ValueError("Mỗi ràng buộc phải có đúng một dấu trong <=, >=, =")
    if len(variable_signs) != c.size or any(s not in _VARIABLE_SIGNS for s in variable_signs):
        raise ValueError("Mỗi biến phải có điều kiện >=0, <=0 hoặc free")
    sense = str(problem.sense).strip().lower()
    if sense not in {"min", "max"}:
        raise ValueError("Chiều tối ưu phải là min hoặc max")
    constant = float(problem.objective_constant)
    if not np.isfinite(constant):
        raise ValueError("Hằng số của hàm mục tiêu phải hữu hạn")
    return GeneralLP(c, A, b, signs, variable_signs, sense, constant, problem.name)


def classify_general_lp(problem: GeneralLP) -> ProblemClassification:
    """Classify the input as finite, infeasible or unbounded before Karmarkar.

    This check works in the user's original coordinates, so it can also classify
    free variables and empty constraint sets.  HiGHS is used only as a status
    certificate; no point from this check is used to form a Karmarkar iteration.
    """
    problem = validate_general_lp(problem)
    c = problem.objective if problem.sense == "min" else -problem.objective
    upper_rows: list[np.ndarray] = []
    upper_rhs: list[float] = []
    equal_rows: list[np.ndarray] = []
    equal_rhs: list[float] = []
    for row, sign, rhs in zip(
        problem.constraints, problem.constraint_signs, problem.rhs
    ):
        if sign == "<=":
            upper_rows.append(row)
            upper_rhs.append(float(rhs))
        elif sign == ">=":
            upper_rows.append(-row)
            upper_rhs.append(float(-rhs))
        else:
            equal_rows.append(row)
            equal_rhs.append(float(rhs))
    bounds = [
        (0, None) if sign == ">=0" else (None, 0) if sign == "<=0" else (None, None)
        for sign in problem.variable_signs
    ]
    result = linprog(
        c,
        A_ub=np.asarray(upper_rows) if upper_rows else None,
        b_ub=np.asarray(upper_rhs) if upper_rows else None,
        A_eq=np.asarray(equal_rows) if equal_rows else None,
        b_eq=np.asarray(equal_rhs) if equal_rows else None,
        bounds=bounds,
        method="highs",
    )
    if result.status == 0 and result.x is not None:
        x = np.asarray(result.x, dtype=float)
        value = float(problem.objective @ x + problem.objective_constant)
        optimum_row = np.asarray(problem.objective, dtype=float)
        optimum_rhs = value - problem.objective_constant
        optimum_equal_rows = [*equal_rows, optimum_row]
        optimum_equal_rhs = [*equal_rhs, optimum_rhs]
        optimum_A_eq = np.asarray(optimum_equal_rows)
        optimum_b_eq = np.asarray(optimum_equal_rhs)
        coordinate_tolerance = 1e-8 * max(1.0, float(np.linalg.norm(x, ord=np.inf)))
        alternative: np.ndarray | None = None
        for j in range(problem.objective.size):
            unit = np.zeros(problem.objective.size)
            unit[j] = 1.0
            for direction in (unit, -unit):
                extreme = linprog(
                    direction,
                    A_ub=np.asarray(upper_rows) if upper_rows else None,
                    b_ub=np.asarray(upper_rhs) if upper_rows else None,
                    A_eq=optimum_A_eq,
                    b_eq=optimum_b_eq,
                    bounds=bounds,
                    method="highs",
                )
                if extreme.status == 0 and extreme.x is not None:
                    candidate = np.asarray(extreme.x, dtype=float)
                    if abs(candidate[j] - x[j]) > coordinate_tolerance:
                        alternative = candidate
                        break
                elif extreme.status == 3:
                    # The optimal face is unbounded in this coordinate.  Ask for
                    # one finite point at least one unit away to display in HTML.
                    separation = np.zeros(problem.objective.size)
                    if direction[j] > 0:  # minimizing x_j: request x_j <= x*_j-1
                        separation[j] = 1.0
                        separation_rhs = x[j] - 1.0
                    else:  # minimizing -x_j: request x_j >= x*_j+1
                        separation[j] = -1.0
                        separation_rhs = -(x[j] + 1.0)
                    separated_A_ub = [*upper_rows, separation]
                    separated_b_ub = [*upper_rhs, separation_rhs]
                    witness = linprog(
                        np.zeros(problem.objective.size),
                        A_ub=np.asarray(separated_A_ub),
                        b_ub=np.asarray(separated_b_ub),
                        A_eq=optimum_A_eq,
                        b_eq=optimum_b_eq,
                        bounds=bounds,
                        method="highs",
                    )
                    if witness.status == 0 and witness.x is not None:
                        alternative = np.asarray(witness.x, dtype=float)
                        break
            if alternative is not None:
                break
        if alternative is not None:
            return ProblemClassification(
                "MULTIPLE_OPTIMA",
                "Tìm được ít nhất hai nghiệm tối ưu khác nhau; vì miền là lồi nên bài toán có vô số nghiệm tối ưu.",
                value,
                x,
                alternative,
            )
        return ProblemClassification(
            "FINITE_OPTIMUM",
            "Miền chấp nhận được không rỗng và nghiệm tối ưu là duy nhất trong sai số kiểm tra.",
            value,
            x,
        )
    if result.status == 2:
        value = float("inf") if problem.sense == "min" else float("-inf")
        return ProblemClassification(
            "INFEASIBLE",
            "Miền chấp nhận được rỗng nên bài toán vô nghiệm.",
            value,
        )
    if result.status == 3:
        value = float("-inf") if problem.sense == "min" else float("inf")
        direction = "giảm" if problem.sense == "min" else "tăng"
        return ProblemClassification(
            "UNBOUNDED",
            f"Miền có điểm chấp nhận được nhưng hàm mục tiêu có thể {direction} không giới hạn.",
            value,
        )
    return ProblemClassification(
        "UNDETERMINED",
        "Không thể phân loại chắc chắn do bộ kiểm tra số trả về: " + result.message,
        None,
    )


def classify_preparation_failure(
    classification: ProblemClassification,
    error: Exception,
) -> ProblemClassification:
    """Turn an unsupported Karmarkar initialization into a reportable result."""
    return ProblemClassification(
        "KARMARKAR_PRECONDITION_FAILED",
        "Bài toán có nghiệm tối ưu hữu hạn nhưng không dựng được điểm trong cho phép lặp "
        f"xạ ảnh: {error}",
        classification.objective_value,
        classification.x,
        classification.alternative_x,
    )


def to_standard_form(problem: GeneralLP) -> StandardFormLP:
    """Convert entered signs to ``E z=b, z>=0`` without optimizing the objective."""
    problem = validate_general_lp(problem)
    n = problem.objective.size
    offset = np.zeros(n)

    def add_slacks(base: np.ndarray, labels: list[str]):
        slack_columns: list[np.ndarray] = []
        for i, sign in enumerate(problem.constraint_signs):
            if sign == "=":
                continue
            column = np.zeros(base.shape[0])
            column[i] = 1.0 if sign == "<=" else -1.0
            slack_columns.append(column)
            labels.append(("s" if sign == "<=" else "r") + str(i + 1))
        equality = np.column_stack([base, *slack_columns]) if slack_columns else base.copy()
        return equality, len(slack_columns)

    # A temporary plus/minus representation is used only to find finite lower
    # bounds for free variables.  This is preprocessing, not the objective solve.
    if "free" in problem.variable_signs:
        temp_columns: list[np.ndarray] = []
        for j, sign in enumerate(problem.variable_signs):
            unit = np.zeros(n)
            unit[j] = 1.0
            if sign == ">=0":
                temp_columns.append(unit)
            elif sign == "<=0":
                temp_columns.append(-unit)
            else:
                temp_columns.extend((unit, -unit))
        temp_transform = np.column_stack(temp_columns)
        temp_E, _ = add_slacks(problem.constraints @ temp_transform, [])
        temp_rhs = problem.rhs.copy()
        for j, sign in enumerate(problem.variable_signs):
            if sign != "free":
                continue
            base_direction = temp_transform.T @ np.eye(n)[j]
            direction = np.r_[base_direction, np.zeros(temp_E.shape[1] - base_direction.size)]
            bound = linprog(
                direction,
                A_eq=temp_E if temp_E.shape[0] else None,
                b_eq=temp_rhs if temp_E.shape[0] else None,
                bounds=[(0, None)] * temp_E.shape[1],
                method="highs",
            )
            if not bound.success:
                raise ValueError(
                    f"Biến tự do x{j + 1} không có cận dưới hữu hạn; "
                    "hãy bổ sung ràng buộc chặn biến."
                )
            offset[j] = float(bound.fun)

    columns: list[np.ndarray] = []
    labels: list[str] = []
    for j, sign in enumerate(problem.variable_signs):
        unit = np.zeros(n)
        unit[j] = 1.0
        if sign == ">=0":
            columns.append(unit)
            labels.append(f"x{j + 1}")
        elif sign == "<=0":
            columns.append(-unit)
            labels.append(f"x{j + 1}_am")
        else:
            columns.append(unit)
            labels.append(f"x{j + 1}_dich")
    transform = np.column_stack(columns)
    rhs = problem.rhs - problem.constraints @ offset
    base = problem.constraints @ transform
    E, slack_count = add_slacks(base, labels)
    original_map = np.column_stack((transform, np.zeros((n, slack_count))))
    factor = 1.0 if problem.sense == "min" else -1.0
    c = factor * (original_map.T @ problem.objective)
    constant = factor * (problem.objective @ offset + problem.objective_constant)
    row_labels = tuple(
        f"R{i + 1}: dấu {sign} được đổi thành đẳng thức"
        for i, sign in enumerate(problem.constraint_signs)
    )
    return StandardFormLP(E, rhs, c, constant, original_map, offset, tuple(labels), row_labels, factor)


def _find_strict_interior(standard: StandardFormLP, tol: float) -> tuple[np.ndarray, float, str]:
    """Phase I: find a positive standard point, ignoring the objective.

    The auxiliary margin only needs to be positive.  Capping ``t`` at one
    prevents a feasible ray from making the Phase-I objective unbounded; an
    optimum ``t=1`` is already a complete strict-interior certificate.
    """
    p = standard.c.size
    phase_c = np.r_[np.zeros(p), -1.0]
    A_eq = np.column_stack((standard.E, np.zeros(standard.E.shape[0])))
    A_ub = np.column_stack((-np.eye(p), np.ones(p)))
    result = linprog(
        phase_c,
        A_ub=A_ub,
        b_ub=np.zeros(p),
        A_eq=A_eq if standard.E.shape[0] else None,
        b_eq=standard.b if standard.E.shape[0] else None,
        bounds=[(0, None)] * p + [(0, 1)],
        method="highs",
    )
    if not result.success:
        raise ValueError("Không tìm được điểm khả thi dương để bắt đầu: " + result.message)
    z = np.asarray(result.x[:p], dtype=float)
    margin = float(result.x[-1])
    if margin <= tol or np.min(z) <= tol:
        raise ValueError(
            "Miền không có điểm trong với mọi biến chuẩn dương. "
            "Thuật toán điểm trong không thể khởi tạo trực tiếp cho trường hợp này."
        )
    residual = float(np.max(np.abs(standard.E @ z - standard.b), initial=0.0))
    if residual > tol * max(1.0, np.linalg.norm(standard.b, ord=np.inf)):
        raise ValueError("Điểm khởi tạo ở Giai đoạn I không đạt sai số đẳng thức yêu cầu")
    return z, margin, f"Giai đoạn I primal thành công; tọa độ nhỏ nhất={margin:.6g}; sai số={residual:.3g}."


def _independent_equalities(standard: StandardFormLP, tol: float) -> StandardFormLP:
    """Remove dependent equality rows so dual variables do not contain a free null direction."""
    m = standard.E.shape[0]
    if m == 0:
        return standard
    _, diagonal, pivots = qr(standard.E.T, mode="economic", pivoting=True)
    scale = float(np.max(np.abs(diagonal), initial=0.0))
    rank = int(np.sum(np.abs(np.diag(diagonal)) > tol * max(1.0, scale))) if diagonal.ndim == 2 else 0
    selected = np.sort(np.asarray(pivots[:rank], dtype=int))
    if rank == m:
        return standard
    if rank == 0:
        if np.max(np.abs(standard.b), initial=0.0) > tol:
            raise ValueError("Hệ đẳng thức phụ thuộc nhưng vế phải không tương thích")
        selected = np.empty(0, dtype=int)
    reduced_E = standard.E[selected, :]
    reduced_b = standard.b[selected]
    # Confirm the reduced system represents the original one on a feasible point.
    feasibility = linprog(
        np.zeros(standard.c.size),
        A_eq=reduced_E if rank else None,
        b_eq=reduced_b if rank else None,
        bounds=[(0, None)] * standard.c.size,
        method="highs",
    )
    if not feasibility.success or np.max(np.abs(standard.E @ feasibility.x - standard.b), initial=0.0) > tol * 10:
        raise ValueError("Không thể loại hàng ràng buộc phụ thuộc một cách nhất quán")
    labels = tuple(standard.row_labels[i] for i in selected)
    return StandardFormLP(
        reduced_E,
        reduced_b,
        standard.c,
        standard.constant,
        standard.original_map,
        standard.original_offset,
        standard.standard_labels,
        labels,
        standard.sense_factor,
    )


def _find_strict_dual(standard: StandardFormLP, tol: float) -> tuple[np.ndarray, np.ndarray, str]:
    """Find y with c-E.T y>0; this is objective-free dual Phase I."""
    m, p = standard.E.shape
    if m == 0:
        slack = standard.c.copy()
        if np.min(slack) <= tol:
            raise ValueError("Đối ngẫu không có điểm trong dương")
        return np.empty(0), slack, f"Dual có biến dư dương; biến dư nhỏ nhất={np.min(slack):.6g}."
    phase_c = np.r_[np.zeros(m), -1.0]
    A_ub = np.column_stack((standard.E.T, np.ones(p)))
    result = linprog(
        phase_c,
        A_ub=A_ub,
        b_ub=standard.c,
        bounds=[(None, None)] * m + [(0, None)],
        method="highs",
    )
    if result.status == 3:
        # Any unit margin is sufficient when the maximum is unbounded.
        fixed = linprog(
            np.zeros(m),
            A_ub=standard.E.T,
            b_ub=standard.c - 1.0,
            bounds=[(None, None)] * m,
            method="highs",
        )
        if not fixed.success:
            raise ValueError("Không dựng được điểm dual có biến dư dương")
        dual = np.asarray(fixed.x, dtype=float)
    elif result.success and result.x[-1] > tol:
        dual = np.asarray(result.x[:m], dtype=float)
    else:
        raise ValueError(
            "Bài toán dual không có điểm trong với biến dư dương. "
            "Dạng Karmarkar điểm-trong hiện tại không thể khởi tạo trường hợp suy biến này."
        )
    slack = standard.c - standard.E.T @ dual
    if np.min(slack) <= tol:
        raise ValueError("Điểm đối ngẫu tìm được không đủ dương")
    return dual, slack, f"Giai đoạn I dual thành công; biến dư nhỏ nhất={np.min(slack):.6g}."


def _build_primal_dual_gap_problem(
    problem: GeneralLP,
    primal: StandardFormLP,
    primal_start: np.ndarray,
    dual_start: np.ndarray,
    dual_slack: np.ndarray,
) -> tuple[GeneralLP, np.ndarray, np.ndarray, float, str]:
    """Build a zero-optimum LP whose objective is the primal-dual gap."""
    m, p = primal.E.shape
    gap_at_start = float(primal.c @ primal_start - primal.b @ dual_start)
    if gap_at_start <= 0:
        gap_at_start = max(1.0, float(np.linalg.norm(primal.c) + np.linalg.norm(primal.b)))
    gap_budget = max(1.0, gap_at_start + max(1.0, .5 * gap_at_start))
    # Variables w=(z, dual_y, dual_slack_s, gap_slack_t).
    total_variables = p + m + p + 1
    rows: list[np.ndarray] = []
    rhs: list[float] = []
    for i in range(m):
        row = np.zeros(total_variables)
        row[:p] = primal.E[i]
        rows.append(row)
        rhs.append(float(primal.b[i]))
    for j in range(p):
        row = np.zeros(total_variables)
        row[p:p + m] = primal.E[:, j]
        row[p + m + j] = 1.0
        rows.append(row)
        rhs.append(float(primal.c[j]))
    gap_row = np.zeros(total_variables)
    gap_row[:p] = primal.c
    gap_row[p:p + m] = -primal.b
    gap_row[-1] = 1.0
    rows.append(gap_row)
    rhs.append(gap_budget)
    gap_objective = gap_row.copy()
    gap_objective[-1] = 0.0
    signs = tuple([">=0"] * p + ["free"] * m + [">=0"] * p + [">=0"])
    joint = make_problem(
        gap_objective,
        np.asarray(rows),
        np.asarray(rhs),
        ["="] * len(rows),
        signs,
        sense="min",
        objective_constant=0.0,
        name="Nhúng primal-dual: tối thiểu hóa độ chênh lệch",
    )
    solution_map = np.zeros((problem.objective.size, total_variables))
    solution_map[:, :p] = primal.original_map
    solution_offset = primal.original_offset.copy()
    message = (
        f"Ghép primal và dual; độ chênh lệch ban đầu={gap_at_start:.6g}, "
        f"giới hạn khởi tạo={gap_budget:.6g}. Độ chênh lệch luôn không âm và tiến về 0 tại tối ưu."
    )
    return joint, solution_map, solution_offset, gap_budget, message


def _positive_rowspace_weights(standard: StandardFormLP) -> tuple[np.ndarray, float, str]:
    """Find q=E.T lambda>0, proving a fixed positive weighted sum on the feasible set."""
    m, p = standard.E.shape
    if m == 0:
        raise ValueError(
            "Không có ràng buộc đẳng thức để tạo tổng cố định. "
            "Bài toán chưa thể đưa vào đơn giác chuẩn."
        )
    result = linprog(
        np.zeros(m),
        A_ub=-standard.E.T,
        b_ub=-np.ones(p),
        bounds=[(None, None)] * m,
        method="highs",
    )
    if not result.success:
        raise ValueError(
            "Không tìm được tổng có trọng số dương cố định; miền có thể không bị chặn. "
            "Hãy bổ sung các ràng buộc chặn biến."
        )
    multiplier = np.asarray(result.x, dtype=float)
    weights = standard.E.T @ multiplier
    total = float(multiplier @ standard.b)
    if np.min(weights) <= 0 or total <= 0:
        raise ValueError("Chứng cứ tổng có trọng số dương không hợp lệ")
    return weights, total, (
        f"Tìm được một bộ trọng số dương. Tổng có trọng số của mọi điểm hợp lệ "
        f"luôn bằng S={total:.6g}."
    )


def _dual_nonnegative_certificate(A: np.ndarray, c: np.ndarray) -> np.ndarray:
    """Find lambda with c-A.T lambda>=0, a numerical certificate for c.T u>=0."""
    m, n = A.shape
    if m == 0:
        if np.min(c) < -1e-10:
            raise ValueError("Không chứng minh được mục tiêu không âm trên đơn giác")
        return np.empty(0)
    result = linprog(
        np.zeros(m),
        A_ub=A.T,
        b_ub=c,
        bounds=[(None, None)] * m,
        method="highs",
    )
    if not result.success:
        raise ValueError(
            "Có điểm mục tiêu 0 nhưng chưa tìm được chứng chỉ mục tiêu không âm trên toàn miền. "
            "Không chạy vì điều kiện khởi tạo quan trọng chưa được xác minh."
        )
    return np.asarray(result.x, dtype=float)


def _zero_objective_witness(
    standard: StandardFormLP,
    tol: float,
) -> tuple[np.ndarray, str] | None:
    """Return a feasible zero-objective point without optimizing the entered objective."""
    p = standard.c.size
    result = linprog(
        np.zeros(p),
        A_eq=np.vstack((standard.E, standard.c[None, :])),
        b_eq=np.r_[standard.b, -standard.constant],
        bounds=[(0, None)] * p,
        method="highs",
    )
    if not result.success:
        return None
    witness = np.asarray(result.x, dtype=float)
    residual = max(
        float(np.max(np.abs(standard.E @ witness - standard.b), initial=0.0)),
        abs(float(standard.c @ witness + standard.constant)),
    )
    if residual > tol * max(1.0, np.linalg.norm(standard.b, ord=np.inf)):
        return None
    return witness, (
        "Bài toán sau chuẩn hóa đã có mục tiêu không âm và có một điểm hợp lệ "
        f"đạt mục tiêu 0; sai số kiểm tra={residual:.3g}."
    )


def _try_direct_canonical_embedding(
    problem: GeneralLP,
    standard: StandardFormLP,
    start: np.ndarray,
    margin: float,
    phase_message: str,
    config: GeneralSolverConfig,
) -> SimplexEmbedding | None:
    """Use the report's direct simplex normalization when its zero-objective scope holds.

    This is the path used by the two-variable source example: add its slack,
    divide by the fixed total, start at e/n, and run the core iteration without
    introducing primal-dual coordinates that would change the displayed trace.
    """
    zero_data = _zero_objective_witness(standard, config.feasibility_tolerance)
    if zero_data is None:
        return None
    zero_standard, zero_message = zero_data
    try:
        weights, weighted_total, bound_message = _positive_rowspace_weights(standard)
    except ValueError:
        return None
    dimension = start.size
    if dimension > config.max_canonical_dimension:
        return None
    scale = weighted_total / weights
    simplex_start = weights * start / weighted_total
    if not np.all(simplex_start > 0) or not np.isclose(simplex_start.sum(), 1.0, atol=1e-9):
        return None
    homogeneous_A = standard.E * scale - standard.b[:, None]
    canonical_A = homogeneous_A * simplex_start
    simplex_objective = standard.c * scale + standard.constant
    canonical_c = simplex_start * simplex_objective
    # Positive scaling does not change p/||p||.  Normalize it so the source
    # example becomes exactly c=(0,1,1), including the report's potential values.
    positive_scale = float(np.max(np.abs(canonical_c), initial=0.0))
    if positive_scale <= config.feasibility_tolerance:
        return None
    canonical_c = canonical_c / positive_scale
    zero_simplex = weights * zero_standard / weighted_total
    zero_canonical = to_projective(simplex_start, zero_simplex)
    try:
        dual_multiplier = _dual_nonnegative_certificate(canonical_A, canonical_c)
    except ValueError:
        return None
    canonical = CanonicalLP(
        canonical_A,
        canonical_c,
        name="direct_zero_objective_simplex",
        zero_witness=zero_canonical,
        dual_multiplier=dual_multiplier,
        dual_bound=0.0,
    )
    validation_config = SolverConfig(
        alpha=config.alpha,
        max_iter=config.max_iter,
        feas_tol=config.feasibility_tolerance,
        projection_abs_tol=config.projection_abs_tol,
        projection_rel_tol=config.projection_rel_tol,
        svd_rtol=config.svd_rtol,
        require_nonnegative_certificate=True,
        allow_unverified_demo=False,
    )
    validation = validate_canonical(canonical, validation_config)
    if not validation.valid or not validation.zero_optimum_known:
        return None
    centre = np.ones(dimension) / dimension
    recovered = scale * from_projective(simplex_start, centre)
    if not np.allclose(recovered, start, atol=config.feasibility_tolerance, rtol=1e-9):
        return None
    original_n = problem.objective.size
    return SimplexEmbedding(
        problem,
        standard,
        standard,
        np.eye(original_n),
        np.zeros(original_n),
        "direct_canonical",
        start,
        margin,
        weights,
        weighted_total,
        dimension,
        scale,
        simplex_start,
        homogeneous_A,
        canonical,
        phase_message,
        bound_message,
        zero_message,
        False,
    )


def prepare_simplex_embedding(
    problem: GeneralLP,
    config: GeneralSolverConfig | None = None,
) -> SimplexEmbedding:
    """Build a primal-dual zero-gap LP, then normalize it to the PDF's simplex form."""
    config = config or GeneralSolverConfig()
    problem = validate_general_lp(problem)
    input_standard = _independent_equalities(
        to_standard_form(problem), config.feasibility_tolerance
    )
    primal_start, primal_margin, primal_message = _find_strict_interior(
        input_standard, config.feasibility_tolerance
    )
    direct = _try_direct_canonical_embedding(
        problem,
        input_standard,
        primal_start,
        primal_margin,
        primal_message,
        config,
    )
    if direct is not None:
        return direct
    dual_start, dual_slack, dual_message = _find_strict_dual(
        input_standard, config.feasibility_tolerance
    )
    joint_problem, solution_map, solution_offset, _, gap_message = _build_primal_dual_gap_problem(
        problem, input_standard, primal_start, dual_start, dual_slack
    )
    standard = _independent_equalities(
        to_standard_form(joint_problem), config.feasibility_tolerance
    )
    z0, margin, joint_phase_message = _find_strict_interior(
        standard, config.feasibility_tolerance
    )
    weights, weighted_total, bound_message = _positive_rowspace_weights(standard)
    phase_message = f"{primal_message} {dual_message} {joint_phase_message}"
    zero_message = gap_message
    dimension = z0.size
    if dimension > config.max_canonical_dimension:
        raise ValueError(
            f"Phép nhúng cần {dimension} tọa độ, vượt giới hạn trình bày "
            f"{config.max_canonical_dimension}. Hãy thêm cận biến chặt hơn."
        )
    scale = weighted_total / weights
    simplex_start = weights * z0 / weighted_total
    if not np.all(simplex_start > 0) or not np.isclose(simplex_start.sum(), 1.0, atol=1e-9):
        raise ValueError("Điểm khởi tạo chưa được chuẩn hóa đúng vào đơn giác")
    # x_simplex = diag(weights/total) z and E z=b become A0 x=0 on sum(x)=1.
    homogeneous_A = standard.E * scale - standard.b[:, None]
    if np.max(np.abs(homogeneous_A @ simplex_start), initial=0.0) > config.feasibility_tolerance:
        raise ValueError("Điểm đơn giác ban đầu không thỏa hệ thuần nhất")
    # One projective recentering maps simplex_start to e/n.  The PDF loop then starts exactly at e/n.
    canonical_A = homogeneous_A * simplex_start
    simplex_objective = standard.c * scale + standard.constant
    canonical_c = simplex_start * simplex_objective
    dual_multiplier = _dual_nonnegative_certificate(canonical_A, canonical_c)
    initial_objective_zero = bool(abs(float(canonical_c @ (np.ones(dimension) / dimension))) <= config.feasibility_tolerance)
    canonical = CanonicalLP(
        canonical_A,
        canonical_c,
        name="projectively_recentered_primal_dual_gap_lp",
        dual_multiplier=dual_multiplier,
        dual_bound=0.0,
    )
    validation_config = SolverConfig(
        alpha=config.alpha,
        max_iter=config.max_iter,
        feas_tol=config.feasibility_tolerance,
        projection_abs_tol=config.projection_abs_tol,
        projection_rel_tol=config.projection_rel_tol,
        svd_rtol=config.svd_rtol,
        require_nonnegative_certificate=True,
        allow_unverified_demo=True,
    )
    validation = validate_canonical(canonical, validation_config)
    if not initial_objective_zero and not validation.valid:
        raise ValueError("Phép nhúng không đạt kiểm tra dạng chuẩn: " + "; ".join(validation.errors))
    centre = np.ones(dimension) / dimension
    recovered_simplex = from_projective(simplex_start, centre)
    recovered = scale * recovered_simplex
    if not np.allclose(recovered, z0, atol=config.feasibility_tolerance, rtol=1e-9):
        raise ValueError("Tâm đơn giác không đổi ngược về đúng điểm khởi tạo")
    return SimplexEmbedding(
        problem,
        standard,
        input_standard,
        solution_map,
        solution_offset,
        "primal_dual_gap",
        z0,
        margin,
        weights,
        weighted_total,
        dimension,
        scale,
        simplex_start,
        homogeneous_A,
        canonical,
        phase_message,
        bound_message,
        zero_message,
        initial_objective_zero,
    )


def recover_standard(embedding: SimplexEmbedding, u: np.ndarray) -> np.ndarray:
    """Recover nonnegative equality-form variables from a canonical simplex point."""
    u = np.asarray(u, dtype=float)
    if u.shape != (embedding.dimension,):
        raise ValueError("Sai kích thước tọa độ đơn giác")
    simplex_point = from_projective(embedding.simplex_start, u)
    return embedding.scale * simplex_point


def recover_original(embedding: SimplexEmbedding, u: np.ndarray) -> np.ndarray:
    """Recover the variables exactly as entered by the user."""
    embedded_variables = (
        embedding.standard.original_offset
        + embedding.standard.original_map @ recover_standard(embedding, u)
    )
    return embedding.solution_offset + embedding.solution_map @ embedded_variables


def original_objective(embedding: SimplexEmbedding, u: np.ndarray) -> float:
    """Evaluate the user's min/max objective, including its constant term."""
    x = recover_original(embedding, u)
    return float(embedding.general.objective @ x + embedding.general.objective_constant)


def _history_row(
    embedding: SimplexEmbedding,
    u: np.ndarray,
    k: int,
    previous_objective: float | None,
) -> GeneralIterationRow:
    z = recover_standard(embedding, u)
    embedded_variables = embedding.standard.original_offset + embedding.standard.original_map @ z
    x = embedding.solution_offset + embedding.solution_map @ embedded_variables
    objective = float(embedding.general.objective @ x + embedding.general.objective_constant)
    internal = float(embedding.standard.c @ z + embedding.standard.constant)
    canonical_objective = float(embedding.canonical.c @ u)
    residual = float(np.max(np.abs(embedding.standard.E @ z - embedding.standard.b), initial=0.0))
    relative = None
    if previous_objective is not None:
        relative = abs(objective - previous_objective) / max(1.0, abs(previous_objective), abs(objective))
    return GeneralIterationRow(
        k,
        objective,
        internal,
        canonical_objective,
        x,
        z,
        np.asarray(u, dtype=float).copy(),
        residual,
        float(np.min(u)),
        relative,
    )


def solve_general_karmarkar(
    embedding: SimplexEmbedding,
    config: GeneralSolverConfig | None = None,
) -> GeneralKarmarkarResult:
    """Run the exact six PDF steps on the prepared canonical embedding.

    Preparation has already supplied a checked zero witness and a numerical
    nonnegative lower-bound certificate.  Stopping still means only that the
    transformed objective is below the requested tolerance, never exact equality.
    """
    config = config or GeneralSolverConfig()
    if embedding.dimension > config.max_canonical_dimension:
        raise ValueError("Kích thước đơn giác vượt giới hạn cấu hình")
    core_config = SolverConfig(
        alpha=config.alpha,
        epsilon=max(config.objective_tolerance, 1e-15),
        max_iter=config.max_iter,
        feas_tol=config.feasibility_tolerance,
        projection_abs_tol=config.projection_abs_tol,
        projection_rel_tol=config.projection_rel_tol,
        svd_rtol=config.svd_rtol,
        require_nonnegative_certificate=True,
        allow_unverified_demo=True,
        monitor_potential=False,
        store_trajectory=True,
    )
    u = np.ones(embedding.dimension) / embedding.dimension
    trace: list[StepRecord] = []
    history = [_history_row(embedding, u, 0, None)]
    status = "MAX_ITERATIONS"
    message = "Đã dùng hết số vòng cho phép; đây là nghiệm gần đúng tốt nhất đã tính."
    if abs(history[0].internal_min_objective) <= config.objective_tolerance:
        status = "APPROX_TOL_REACHED"
        message = "Điểm khởi tạo đã đạt ngưỡng mục tiêu 0; không cần thực hiện vòng lặp."
    for k in range(config.max_iter):
        if status == "APPROX_TOL_REACHED":
            break
        with np.errstate(over="raise", divide="raise", invalid="raise"):
            record = karmarkar_step(embedding.canonical, u, core_config, k)
        trace.append(record)
        if record.status is not None or record.x_after is None:
            status = record.status.value.upper() if record.status is not None else "NUMERICAL_FAILURE"
            message = record.diagnostics.get("error", "Không còn hướng chiếu đủ ổn định để tiếp tục.")
            break
        previous = history[-1].objective
        u = record.x_after.copy()
        row = _history_row(embedding, u, k + 1, previous)
        history.append(row)
        if -config.objective_tolerance <= row.internal_min_objective <= config.objective_tolerance:
            status = "APPROX_TOL_REACHED"
            message = (
                "Mục tiêu chuẩn đã xuống dưới ngưỡng yêu cầu; đây là nghiệm gần đúng "
                "theo điều kiện dừng của chương trình, không phải chứng nhận tối ưu chính xác."
            )
            break
    final_z = recover_standard(embedding, u)
    final_embedded = embedding.standard.original_offset + embedding.standard.original_map @ final_z
    final_x = embedding.solution_offset + embedding.solution_map @ final_embedded
    final_objective = float(embedding.general.objective @ final_x + embedding.general.objective_constant)
    return GeneralKarmarkarResult(
        embedding,
        final_x,
        final_z,
        u,
        final_objective,
        len(history) - 1,
        status,
        message,
        trace,
        history,
    )


def solve_reference(problem: GeneralLP) -> ReferenceResult:
    """Solve only for a post-run comparison; the result never enters preprocessing."""
    try:
        classification = classify_general_lp(problem)
        if classification.status != "FINITE_OPTIMUM":
            return ReferenceResult(
                False,
                classification.status,
                classification.message,
                None,
                classification.objective_value,
            )
        return ReferenceResult(
            True,
            "OPTIMAL_REFERENCE",
            classification.message,
            classification.x,
            classification.objective_value,
        )
    except Exception as exc:  # report comparison failures without hiding Karmarkar output
        return ReferenceResult(False, "REFERENCE_ERROR", str(exc), None, None)


def make_problem(
    objective: Sequence[float],
    constraints: Sequence[Sequence[float]],
    rhs: Sequence[float],
    constraint_signs: Sequence[str],
    variable_signs: Sequence[str],
    *,
    sense: str = "min",
    objective_constant: float = 0.0,
    name: str = "Bài toán nhập từ bàn phím",
) -> GeneralLP:
    """Convenient public constructor used by tests, scripts and the notebook."""
    c = np.asarray(objective, dtype=float)
    A = np.asarray(constraints, dtype=float)
    if A.size == 0:
        A = np.empty((0, c.size), dtype=float)
    return validate_general_lp(
        GeneralLP(
            c,
            A,
            np.asarray(rhs, dtype=float),
            tuple(constraint_signs),
            tuple(variable_signs),
            sense,
            objective_constant,
            name,
        )
    )

