"""Self-contained Vietnamese HTML report for the interactive Karmarkar notebook.

All images are embedded as base64 PNG data.  The report intentionally separates
input, preprocessing, the six PDF steps, numerical output and the optional
post-run reference comparison so a non-programmer can follow the calculation.
"""

from __future__ import annotations

import base64
from html import escape
from io import BytesIO
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon, FancyBboxPatch
import numpy as np
from scipy.optimize import linprog

from .general_lp import (
    GeneralLP,
    GeneralKarmarkarResult,
    ProblemClassification,
    ReferenceResult,
    SimplexEmbedding,
)
from .geometry import simplex_embedding, simplex_geometry
from .projective import from_projective


COLORS = {
    "navy": "#17324d",
    "blue": "#2d6cdf",
    "teal": "#16837a",
    "orange": "#e48632",
    "red": "#c74440",
    "pale": "#eaf2fb",
    "green": "#2f855a",
}


def _number(value: float, digits: int = 8) -> str:
    value = float(value)
    if value == 0:
        return "0"
    if abs(value) < 1e-5 or abs(value) >= 1e6:
        return f"{value:.6e}"
    return f"{value:.{digits}g}"


def _table_number(value: float) -> str:
    """Use report-style six decimals without hiding genuinely tiny values."""
    value = float(value)
    if value != 0 and abs(value) < 0.5e-6:
        return f"{value:.6e}"
    return f"{value:.6f}"


def _status_vietnamese(status: str) -> str:
    labels = {
        "APPROX_TOL_REACHED": "Đạt ngưỡng gần đúng",
        "MAX_ITERATIONS": "Đã dùng hết số vòng",
        "NO_PROJECTED_DIRECTION": "Không còn hướng chiếu",
        "NUMERICALLY_UNDETERMINED": "Chưa xác định được do sai số số học",
        "INVALID_INPUT": "Dữ liệu đầu vào không hợp lệ",
        "NUMERICAL_FAILURE": "Lỗi tính toán số",
        "POTENTIAL_TEST_FAILED": "Kiểm tra hàm thế không đạt",
        "PRECONDITION_UNVERIFIED": "Chưa xác minh đủ điều kiện",
        "approx_tol_reached": "đạt ngưỡng gần đúng",
        "max_iterations": "đã dùng hết số vòng",
        "no_projected_direction": "không còn hướng chiếu",
        "numerically_undetermined": "chưa xác định được do sai số số học",
        "invalid_input": "dữ liệu đầu vào không hợp lệ",
        "numerical_failure": "lỗi tính toán số",
        "potential_test_failed": "kiểm tra hàm thế không đạt",
        "precondition_unverified": "chưa xác minh đủ điều kiện",
    }
    return labels.get(status, status)


def _vector(values: np.ndarray, limit: int = 20) -> str:
    values = np.asarray(values, dtype=float).ravel()
    shown = values[:limit]
    text = "[" + ", ".join(_number(v) for v in shown) + "]"
    if values.size > limit:
        text += f" … ({values.size} phần tử)"
    return escape(text)


def _latex_vector(values: np.ndarray, limit: int = 16) -> str:
    """Format a numeric vector as inline LaTeX for MathJax."""
    values = np.asarray(values, dtype=float).ravel()
    shown = values[:limit]
    body = r",\;".join(_number(v) for v in shown)
    if values.size > limit:
        body += r",\;\ldots"
    return rf"\left({body}\right)^{{\mathsf{{T}}}}"


def _matrix_table(values: np.ndarray, limit: int = 12) -> str:
    values = np.asarray(values, dtype=float)
    if values.ndim == 1:
        values = values[None, :]
    rows, cols = values.shape
    rmax, cmax = min(rows, limit), min(cols, limit)
    body = []
    for row in values[:rmax, :cmax]:
        body.append("<tr>" + "".join(f"<td>{escape(_number(v))}</td>" for v in row) + "</tr>")
    note = ""
    if rows > limit or cols > limit:
        note = f"<p class='muted'>Đang xem góc {rmax}×{cmax}; kích thước đầy đủ {rows}×{cols}.</p>"
    return note + "<div class='table-wrap'><table class='matrix'>" + "".join(body) + "</table></div>"


def _figure_data(fig) -> str:
    stream = BytesIO()
    fig.savefig(stream, format="png", dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return "data:image/png;base64," + base64.b64encode(stream.getvalue()).decode("ascii")


def _plot_flow() -> str:
    fig, ax = plt.subplots(figsize=(12, 4.8))
    positions = [(0.03, .62), (.36, .62), (.69, .62), (.69, .18), (.36, .18), (.03, .18)]
    labels = [
        "$x^{(k)}\\in P^\\circ$\nĐiểm hiện tại",
        "$a_0=T_{x^{(k)}}(x^{(k)})$\nĐưa về trọng tâm",
        "$p_k=\\Pi_{B_k}(D_kc)$\nChiếu trực giao",
        "$y^{(k)}=a_0-\\alpha r p_k/\\Vert p_k\\Vert_2$\nBước trong quả cầu",
        "$x^{(k+1)}=T^{-1}_{x^{(k)}}(y^{(k)})$\nBiến đổi ngược",
        "$x^{(k+1)}\\in P^\\circ$\nKiểm tra hàm thế",
    ]
    for (x, y), label in zip(positions, labels):
        ax.add_patch(FancyBboxPatch(
            (x, y), .26, .2, boxstyle="round,pad=0.012",
            facecolor=COLORS["pale"], edgecolor=COLORS["navy"], linewidth=1.3,
        ))
        ax.text(x + .13, y + .1, label, ha="center", va="center", fontsize=9)
    edges = [
        ((.29, .72), (.36, .72)), ((.62, .72), (.69, .72)), ((.82, .62), (.82, .38)),
        ((.69, .28), (.62, .28)), ((.36, .28), (.29, .28)), ((.16, .38), (.16, .62)),
    ]
    for start, end in edges:
        ax.annotate("", end, start, arrowprops={"arrowstyle": "->", "lw": 1.7, "color": COLORS["teal"]})
    ax.text(.03, .48, "lặp tiếp", color=COLORS["teal"], fontsize=9)
    ax.set_title("Sơ đồ hình học của một vòng lặp Karmarkar", fontsize=13)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    return _figure_data(fig)


def _plot_simplex(result: GeneralKarmarkarResult) -> str | None:
    n = result.embedding.dimension
    points = np.array([row.canonical_u for row in result.history])
    if n == 3:
        vertices = simplex_embedding(np.eye(3))
        xy = simplex_embedding(points)
        _, radius, outer = simplex_geometry(3)
        fig, ax = plt.subplots(figsize=(7, 6))
        ax.add_patch(Polygon(vertices, facecolor="#edf5fc", edgecolor=COLORS["navy"], linewidth=1.5))
        ax.add_patch(Circle((0, 0), radius, fill=False, color=COLORS["blue"], linewidth=2, label="Cầu nội tiếp r"))
        ax.add_patch(Circle((0, 0), outer, fill=False, color=COLORS["orange"], linestyle="--", label="Cầu ngoại tiếp R"))
        ax.plot(xy[:, 0], xy[:, 1], "-o", color=COLORS["red"], markersize=2.5, linewidth=1, label="Các điểm lặp")
        ax.plot(0, 0, "ko", markersize=4)
        ax.text(.02, .03, "tâm e/3")
        for vertex, label in zip(vertices, ("e1", "e2", "e3")):
            ax.text(vertex[0] + .03, vertex[1] + .03, label)
        ax.set_title("Đơn giác chuẩn, quả cầu nội tiếp và đường đi thực của thuật toán")
        ax.set_aspect("equal")
        ax.axis("off")
        ax.legend(loc="upper right", fontsize=8)
        return _figure_data(fig)
    if n == 4:
        vertices = .5 * np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=float)
        xyz = points @ vertices
        fig = plt.figure(figsize=(7.5, 6.5))
        ax = fig.add_subplot(111, projection="3d")
        for i in range(4):
            for j in range(i + 1, 4):
                ax.plot(*zip(vertices[i], vertices[j]), color="#8095a8", linewidth=.8)
        ax.plot(xyz[:, 0], xyz[:, 1], xyz[:, 2], "-o", color=COLORS["red"], markersize=2, linewidth=1)
        ax.scatter([0], [0], [0], color="black", s=22, label="tâm e/4")
        ax.set_title("Đơn giác chuẩn 4 tọa độ (tứ diện) và đường đi thực")
        ax.set_axis_off()
        ax.legend()
        return _figure_data(fig)
    # Higher-dimensional simplexes cannot be shown faithfully on a flat page.
    # Draw a clearly labelled 2D principle diagram and print the real radius.
    vertices = np.array([[0, 1], [-np.sqrt(3) / 2, -.5], [np.sqrt(3) / 2, -.5]])
    real_radius = 1 / np.sqrt(n * (n - 1))
    fig, ax = plt.subplots(figsize=(7, 5.8))
    ax.add_patch(Polygon(vertices, facecolor="#edf5fc", edgecolor=COLORS["navy"], linewidth=1.5))
    ax.add_patch(Circle((0, 0), .42, fill=False, color=COLORS["blue"], linewidth=2))
    ax.add_patch(Circle((0, 0), .105, fill=False, color=COLORS["teal"], linestyle="--", linewidth=1.5))
    ax.plot(0, 0, "ko", markersize=4)
    ax.annotate("", (.09, -.055), (0, 0), arrowprops={"arrowstyle": "->", "color": COLORS["red"], "lw": 2})
    ax.text(.11, -.08, "bước alpha*r", color=COLORS["red"])
    ax.text(0, .08, "tâm e/n", ha="center")
    ax.text(0, -.82, f"Kích thước thật n={n}; r=1/sqrt(n(n-1))={real_radius:.6g}; alpha*r={.25*real_radius:.6g}", ha="center")
    ax.set_title("Minh họa nguyên lý: đơn giác chuẩn và quả cầu nội tiếp")
    ax.set_aspect("equal")
    ax.set_xlim(-1.05, 1.05)
    ax.set_ylim(-.95, 1.15)
    ax.axis("off")
    fig.text(.5, .015, "Sơ đồ 2D không theo tỷ lệ; đơn giác thực có nhiều hơn 4 tọa độ nên không thể vẽ trực tiếp.", ha="center", fontsize=8.5)
    return _figure_data(fig)


def _plot_projective_recenter(embedding: SimplexEmbedding) -> str:
    """Schematic of the initial projective map; exact coordinates remain in the HTML tables."""
    triangle = np.array([[0, 1], [-.86, -.5], [.86, -.5]])
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for ax, title in zip(axes, ("Trước xạ ảnh: điểm khả thi a", "Sau xạ ảnh: T_a(a)=e/n")):
        ax.add_patch(Polygon(triangle, facecolor="#edf5fc", edgecolor=COLORS["navy"], linewidth=1.4))
        ax.set_title(title)
        ax.set_aspect("equal")
        ax.set_xlim(-1.05, 1.05)
        ax.set_ylim(-.75, 1.15)
        ax.axis("off")
    axes[0].plot(.28, -.08, "o", color=COLORS["red"], markersize=8)
    axes[0].text(.34, -.08, "a", color=COLORS["red"])
    axes[1].plot(0, 0, "o", color=COLORS["green"], markersize=8)
    axes[1].text(.05, .02, "e/n", color=COLORS["green"])
    fig.suptitle("Phép xạ ảnh ban đầu đưa điểm đang có về trọng tâm")
    fig.text(.5, .045, "T_a(x)=D_a^{-1}x / (e^T D_a^{-1}x) - sơ đồ nguyên lý; số liệu thật được ghi trong mục chuẩn hóa.", ha="center", fontsize=9)
    fig.text(.5, .01, f"Bài toán sau nhúng có {embedding.dimension} tọa độ.", ha="center", fontsize=8.5)
    fig.tight_layout(rect=(0, .08, 1, .92))
    return _figure_data(fig)


def _variable_plot_bounds(embedding: SimplexEmbedding) -> tuple[np.ndarray, np.ndarray] | None:
    if embedding.general.objective.size != 2:
        return None
    standard = embedding.input_standard
    lows, highs = [], []
    for index, row in enumerate(standard.original_map):
        low = linprog(row, A_eq=standard.E, b_eq=standard.b,
                      bounds=[(0, None)] * standard.c.size, method="highs")
        high = linprog(-row, A_eq=standard.E, b_eq=standard.b,
                       bounds=[(0, None)] * standard.c.size, method="highs")
        if not low.success or not high.success:
            return None
        lows.append(float(standard.original_offset[index] + low.fun))
        highs.append(float(standard.original_offset[index] - high.fun))
    return np.asarray(lows), np.asarray(highs)


def _feasible_mask(embedding: SimplexEmbedding, X: np.ndarray, Y: np.ndarray) -> np.ndarray:
    problem = embedding.general
    values = problem.constraints[:, 0, None, None] * X + problem.constraints[:, 1, None, None] * Y
    mask = np.ones_like(X, dtype=bool)
    for i, sign in enumerate(problem.constraint_signs):
        if sign == "<=":
            mask &= values[i] <= problem.rhs[i] + 1e-9
        elif sign == ">=":
            mask &= values[i] >= problem.rhs[i] - 1e-9
        else:
            mask &= np.abs(values[i] - problem.rhs[i]) <= 1e-5
    for index, sign in enumerate(problem.variable_signs):
        coordinate = X if index == 0 else Y
        if sign == ">=0":
            mask &= coordinate >= -1e-9
        elif sign == "<=0":
            mask &= coordinate <= 1e-9
    return mask


def _plot_original_2d(result: GeneralKarmarkarResult, reference: ReferenceResult | None) -> str | None:
    bounds = _variable_plot_bounds(result.embedding)
    if bounds is None:
        return None
    low, high = bounds
    span = np.maximum(high - low, 1.0)
    low = low - .12 * span
    high = high + .12 * span
    xs = np.linspace(low[0], high[0], 320)
    ys = np.linspace(low[1], high[1], 320)
    X, Y = np.meshgrid(xs, ys)
    mask = _feasible_mask(result.embedding, X, Y)
    objective = (
        result.embedding.general.objective[0] * X
        + result.embedding.general.objective[1] * Y
        + result.embedding.general.objective_constant
    )
    path = np.array([row.original_x for row in result.history])
    fig, ax = plt.subplots(figsize=(7.5, 6))
    ax.contourf(X, Y, mask.astype(float), levels=[.5, 1.5], colors=["#dceef7"], alpha=.9)
    if np.ptp(objective[mask]) > 1e-12:
        levels = np.linspace(np.min(objective[mask]), np.max(objective[mask]), 6)
        ax.contour(X, Y, objective, levels=levels, colors="#b67636", linewidths=.7, linestyles="--")
    ax.plot(path[:, 0], path[:, 1], "-o", color=COLORS["red"], linewidth=1.4, markersize=3, label="Điểm Karmarkar")
    ax.scatter(path[0, 0], path[0, 1], color=COLORS["blue"], s=45, zorder=5, label="Điểm bắt đầu")
    ax.scatter(path[-1, 0], path[-1, 1], color=COLORS["green"], s=55, zorder=5, label="Điểm cuối")
    if reference and reference.success and reference.x is not None:
        ax.scatter(reference.x[0], reference.x[1], marker="*", color="black", s=110, label="Đối chứng HiGHS")
    ax.set(xlabel="x1", ylabel="x2", title="Miền khả thi và đường đi trong tọa độ người dùng nhập")
    ax.grid(alpha=.2)
    ax.legend(fontsize=8)
    return _figure_data(fig)


def _plot_convergence(result: GeneralKarmarkarResult) -> str:
    iterations = np.array([row.k for row in result.history])
    objectives = np.array([row.objective for row in result.history])
    internal = np.array([row.internal_min_objective for row in result.history])
    residuals = np.array([row.equality_residual for row in result.history])
    minimum = np.array([row.minimum_coordinate for row in result.history])
    fig, axes = plt.subplots(2, 1, figsize=(8.5, 7), sharex=True)
    axes[0].plot(iterations, objectives, label="Mục tiêu người dùng", color=COLORS["navy"])
    internal_label = (
        "Mục tiêu chuẩn"
        if result.embedding.embedding_mode == "direct_canonical"
        else "Độ chênh lệch primal-dual"
    )
    axes[0].plot(iterations, internal, "--", label=internal_label, color=COLORS["orange"])
    axes[0].axhline(0, color="#888", linewidth=.7)
    axes[0].set_ylabel("Giá trị mục tiêu")
    axes[0].set_title("Mục tiêu qua từng vòng lặp thực")
    axes[0].legend(fontsize=8)
    axes[0].grid(alpha=.2)
    axes[1].semilogy(iterations, np.maximum(residuals, 1e-18), label="Sai số đẳng thức", color=COLORS["blue"])
    axes[1].semilogy(iterations, np.maximum(minimum, 1e-18), label="Tọa độ nhỏ nhất", color=COLORS["teal"])
    axes[1].set(xlabel="Vòng k", ylabel="Thang log")
    axes[1].legend(fontsize=8)
    axes[1].grid(alpha=.2)
    fig.tight_layout()
    return _figure_data(fig)


def _linear_latex(coefficients: np.ndarray, constant: float = 0.0) -> str:
    """Build a readable LaTeX linear expression with proper signs and subscripts."""
    terms: list[str] = []
    for i, coefficient in enumerate(np.asarray(coefficients, dtype=float)):
        if abs(coefficient) <= 1e-15:
            continue
        magnitude = abs(float(coefficient))
        factor = "" if np.isclose(magnitude, 1.0) else _number(magnitude)
        term = rf"{factor}x_{{{i + 1}}}"
        if not terms:
            terms.append(("-" if coefficient < 0 else "") + term)
        else:
            terms.append((" - " if coefficient < 0 else " + ") + term)
    if abs(constant) > 1e-15 or not terms:
        magnitude = _number(abs(constant))
        if not terms:
            terms.append(("-" if constant < 0 else "") + magnitude)
        else:
            terms.append((" - " if constant < 0 else " + ") + magnitude)
    return "".join(terms)


def _problem_objective_latex(problem: GeneralLP) -> str:
    operator = r"\min" if problem.sense == "min" else r"\max"
    return operator + r"\; f(x)=" + _linear_latex(
        problem.objective, problem.objective_constant
    )


def _objective_latex(embedding: SimplexEmbedding) -> str:
    return _problem_objective_latex(embedding.general)


def _problem_input_section(problem: GeneralLP) -> str:
    rows = []
    for i, (coefficients, sign, rhs) in enumerate(zip(problem.constraints, problem.constraint_signs, problem.rhs)):
        expression = _linear_latex(coefficients)
        latex_sign = {"<=": r"\le", ">=": r"\ge", "=": "="}[sign]
        rows.append(
            f"<tr><td>R{i + 1}</td><td>\\({expression}\\)</td>"
            f"<td>\\({latex_sign}\\)</td><td>\\({_number(rhs)}\\)</td></tr>"
        )
    sign_latex = {">=0": r"\ge 0", "<=0": r"\le 0", "free": r"\text{ tự do}"}
    variables = "<br>".join(
        f"\\(x_{{{i + 1}}}{sign_latex[sign]}\\)"
        for i, sign in enumerate(problem.variable_signs)
    )
    return f"""
    <section id="input">
      <h2>1. Dữ liệu đầu vào</h2>
      <div class="callout"><b>Hàm mục tiêu:</b> \\({_problem_objective_latex(problem)}\\)</div>
      <div class="table-wrap"><table><thead><tr><th>Ràng buộc</th><th>Vế trái</th><th>Dấu</th><th>Vế phải</th></tr></thead><tbody>{''.join(rows)}</tbody></table></div>
      <p><b>Điều kiện biến:</b><br>{variables}</p>
    </section>
    """


def _input_section(embedding: SimplexEmbedding) -> str:
    return _problem_input_section(embedding.general)


def _normalization_section(embedding: SimplexEmbedding) -> str:
    standard = embedding.input_standard
    if embedding.embedding_mode == "direct_canonical":
        return fr"""
    <section id="normalize">
      <h2>2. Chuẩn hóa dữ liệu trước khi lặp</h2>
      <p><b>Mục tiêu:</b> đổi mọi biến về không âm, thêm biến dư hoặc biến thừa và viết hệ dưới dạng \(Ez=b,\;z\ge0\).</p>
      <p><b>Tên các biến chuẩn:</b> {escape(', '.join(standard.standard_labels))}</p>
      <h3>Ma trận \(E\) và vectơ \(b\)</h3>
      {_matrix_table(standard.E)}
      <p>\(b={_latex_vector(standard.b)}\)</p>

      <h3>Tìm điểm hợp lệ để bắt đầu</h3>
      <p><b>Mục tiêu:</b> tìm một điểm nằm hẳn bên trong miền để mọi tọa độ dùng trong phép xạ ảnh đều dương.</p>
      <ol>
        <li>Thêm \(t\) đại diện cho tọa độ nhỏ nhất.</li>
        <li>Tìm \(t\) lớn nhất với \(Ez=b\), \(z_i\ge t\) và \(0\le t\le1\).</li>
        <li>Nếu \(t>0\), nhận được điểm khởi tạo hợp lệ \(z^{{(0)}}>0\).</li>
      </ol>
      <div class="ok"><b>Kết quả tìm điểm bắt đầu:</b> {escape(embedding.phase_one_message)}</div>
      <p>\(z^{{(0)}}={_latex_vector(embedding.interior)}\)</p>

      <div class="ok"><b>Đưa trực tiếp về đơn giác:</b> {escape(embedding.bound_message)}</div>
      <p>Tìm \(q=E^{{\mathsf T}}\lambda>0\) và \(S=\lambda^{{\mathsf T}}b\), rồi đặt
      \(u=\operatorname{{diag}}(q/S)z\). Điểm khởi tạo trong đơn giác là:</p>
      <p>\(q={_latex_vector(embedding.weights)}\)<br>
      \(S={escape(_number(embedding.weighted_total))}\)<br>
      \(u^{{(0)}}={_latex_vector(embedding.simplex_start)}\)</p>
      <div class="ok"><b>Kiểm tra mục tiêu chuẩn:</b> {escape(embedding.zero_witness_message)}</div>
    </section>
    """
    return fr"""
    <section id="normalize">
      <h2>2. Chuẩn hóa dữ liệu trước khi lặp</h2>
      <p><b>Mục tiêu:</b> đổi mọi biến về không âm, thêm biến dư hoặc biến thừa và viết hệ dưới dạng \(Ez=b,\;z\ge 0\).</p>
      <p><b>Tên các biến chuẩn:</b> {escape(', '.join(standard.standard_labels))}</p>
      <h3>Ma trận \(E\) và vectơ \(b\)</h3>
      {_matrix_table(standard.E)}
      <p>\(b={_latex_vector(standard.b)}\)</p>

      <h3>Tìm điểm hợp lệ để bắt đầu</h3>
      <p><b>Mục tiêu:</b> tìm một điểm nằm hẳn bên trong miền, tức là mọi tọa độ cần dùng trong phép xạ ảnh đều dương.</p>
      <ol>
        <li>Thêm một biến \(t\) đại diện cho tọa độ nhỏ nhất.</li>
        <li>Tìm \(t\) lớn nhất với \(Ez=b\), \(z_i\ge t\) và \(0\le t\le1\).</li>
        <li>Nếu \(t>0\), ta có điểm primal hợp lệ \(z^{{(0)}}>0\).</li>
        <li>Làm tương tự ở phía dual để các biến dư dual cũng dương.</li>
        <li>Ghép hai điểm rồi chạy lại kiểm tra Giai đoạn I trước khi đưa về đơn giác.</li>
      </ol>
      <div class="ok"><b>Kết quả tìm điểm bắt đầu:</b> {escape(embedding.phase_one_message)}</div>
      <p>Điểm khởi tạo sau khi ghép: \(z^{{(0)}}={_latex_vector(embedding.interior)}\)</p>

      <div class="ok"><b>Đưa về đơn giác:</b> {escape(embedding.bound_message)}</div>
      <p>Tìm \(q=E^{{\mathsf T}}\lambda>0\) để \(q^{{\mathsf T}}z=\lambda^{{\mathsf T}}b=S\) luôn không đổi.
      Sau đó đặt \(x_{{\mathrm{{đơn\;giác}}}}=\operatorname{{diag}}(q/S)z\).</p>
      <p>\(q={_latex_vector(embedding.weights)}\)<br>
      \(S={escape(_number(embedding.weighted_total))}\)<br>
      \(a={_latex_vector(embedding.simplex_start)}\)</p>
      <p>Phép xạ ảnh ban đầu đưa \(a\) về trọng tâm: \(T_a(a)=e/n\).</p>

      <div class="ok"><b>Đưa mục tiêu về 0 bằng độ chênh lệch primal-dual:</b> {escape(embedding.zero_witness_message)}</div>
      <p>Đại lượng được giảm là \(\Delta=c^{{\mathsf T}}z-b^{{\mathsf T}}y\). Ta luôn có \(\Delta\ge0\),
      và \(\Delta\) tiến về 0 khi nghiệm primal và dual tiến đến tối ưu.</p>
    </section>
    """


def _algorithm_section(flow_image: str) -> str:
    return fr"""
    <section id="algorithm">
      <h2>3. Thuật toán Karmarkar dưới dạng các bước toán học</h2>
      <p><b>Mục tiêu:</b> bắt đầu từ trọng tâm của đơn giác chuẩn, chiếu hướng giảm vào
      không gian không phá ràng buộc, đi một bước an toàn trong quả cầu nội tiếp rồi
      biến đổi ngược về hệ tọa độ trước đó.</p>
      <div class="algorithm-card">
        <h3>Phép lặp xạ ảnh Karmarkar (phần cốt lõi)</h3>
        <p class="algorithm-step"><b>Bước 1. Xuất phát.</b>
          Đặt \(x^{{(0)}}=a_0=e/n\), \(k=0\); chọn \(0&lt;\alpha&lt;1\).</p>
        <p class="algorithm-step"><b>Bước 2. Thay đổi tọa độ.</b>
          Từ \(x^{{(k)}}\), lập
          \(D_k=\operatorname{{diag}}(x^{{(k)}})\) và
          \(B_k=\begin{{bmatrix}}AD_k\\e^{{\mathsf T}}\end{{bmatrix}}\).</p>
        <p class="algorithm-step"><b>Bước 3. Chiếu và chuẩn hóa hướng.</b>
          Tính \(p_k=\Pi_{{\ker(B_k)}}(D_kc)\). Nếu \(p_k\ne0\), đặt
          \(d_k=-p_k/\lVert p_k\rVert_2\).</p>
        <p class="algorithm-step"><b>Bước 4. Tìm điểm trong hệ mới.</b>
          Với \(r=1/\sqrt{{n(n-1)}}\), lấy
          \(y^{{(k)}}=a_0+\alpha r d_k\).</p>
        <p class="algorithm-step"><b>Bước 5. Trở về hệ cũ.</b>
          Tính
          \(x^{{(k+1)}}=D_ky^{{(k)}}/(e^{{\mathsf T}}D_ky^{{(k)}})\).</p>
        <p class="algorithm-step"><b>Bước 6. Đánh giá.</b>
          Theo dõi \(\Phi(x^{{(k+1)}})-\Phi(x^{{(k)}})\), giá trị mục tiêu,
          tính khả thi và điều kiện dừng. Nếu tiếp tục, đặt \(k\leftarrow k+1\)
          rồi quay lại Bước 2.</p>
      </div>
      <h3>Sơ đồ hình học của một vòng lặp</h3>
      <img class="figure" src="{flow_image}" alt="Sơ đồ sáu bước Karmarkar">
      <div class="callout"><b>Các kiểm tra bắt buộc:</b> hướng chiếu phải thuộc
      \(\ker(B_k)\); điểm mới phải dương, có tổng bằng 1 và còn thỏa các đẳng thức;
      nếu \(p_k=0\) thì không chia cho 0 mà dừng với thông báo không còn hướng chiếu.</div>
    </section>
    """


def _visual_section(images: list[tuple[str, str]]) -> str:
    if not images:
        return ""
    blocks = "".join(f"<figure><img class='figure' src='{src}' alt='{escape(caption)}'><figcaption>{escape(caption)}</figcaption></figure>" for caption, src in images)
    return f"<section id='visuals'><h2>4. Hình minh họa được tạo từ lần chạy này</h2>{blocks}</section>"


def _history_table(result: GeneralKarmarkarResult) -> str:
    rows = []
    for row in result.history:
        xtext = ", ".join(_table_number(v) for v in row.original_x)
        rows.append(
            "<tr>"
            f"<td>{row.k}</td><td>{escape(xtext)}</td><td>{escape(_table_number(row.objective))}</td>"
            f"<td>{escape(_table_number(row.canonical_objective))}</td><td>{escape(_number(row.equality_residual))}</td>"
            f"<td>{escape(_table_number(row.minimum_coordinate))}</td></tr>"
        )
    internal_label = (
        "Mục tiêu chuẩn"
        if result.embedding.embedding_mode == "direct_canonical"
        else "Độ chênh lệch primal-dual"
    )
    return (
        "<div class='table-wrap'><table><thead><tr><th>k</th><th>Biến gốc x</th><th>Mục tiêu</th>"
        f"<th>{internal_label}</th><th>Sai số ràng buộc</th><th>Tọa độ nhỏ nhất</th></tr></thead>"
        f"<tbody>{''.join(rows)}</tbody></table></div>"
    )


def _step_details(result: GeneralKarmarkarResult) -> str:
    blocks = []
    for record in result.trace:
        status = _status_vietnamese(record.status.value) if record.status is not None else "hoàn thành"
        after = "-" if record.x_after is None else _latex_vector(record.x_after)
        direction = "-" if record.d is None else _latex_vector(record.d)
        y = "-" if record.y is None else _latex_vector(record.y)
        phi_before = "không xác định" if record.phi_before is None else _number(record.phi_before)
        phi_after = "không xác định" if record.phi_after is None else _number(record.phi_after)
        phi_change = (
            "không xác định"
            if record.phi_before is None or record.phi_after is None
            else _number(record.phi_after - record.phi_before)
        )
        open_attr = " open" if record.k < 2 else ""
        blocks.append(fr"""
        <details class="iteration"{open_attr}>
          <summary>Vòng k={record.k} - {escape(status)} - mục tiêu trước {escape(_number(record.f_before or 0))}</summary>
          <div class="iteration-grid">
            <div><h4>Bước 1 - Điểm trước vòng lặp</h4><p>\(x^{{(k)}}={_latex_vector(record.x_before)}\)<br>
              Với vòng đầu: \(x^{{(0)}}=a_0=e/n\).</p></div>
            <div><h4>Bước 2 - Thay đổi tọa độ</h4><p>\(D_k=\operatorname{{diag}}(x^{{(k)}})\),
              \(B_k=\begin{{bmatrix}}AD_k\\e^{{\mathsf T}}\end{{bmatrix}}\), \(v_k=D_kc\)<br>
              \(\operatorname{{diag}}(D_k)={_latex_vector(np.diag(record.D))}\)<br>
              \(v_k={_latex_vector(record.v)}\)</p>{_matrix_table(record.B)}</div>
            <div><h4>Bước 3 - Chiếu và chọn hướng</h4><p>\(p_k={_latex_vector(record.p)}\)<br>\(d_k={direction}\)</p></div>
            <div><h4>Bước 4 - Đi trong quả cầu</h4><p>\(y={y}\)<br>
              \(\lVert y-e/n\rVert_2={escape(_number(record.diagnostics.get('step_length', float('nan'))))}\),
              \(r={escape(_number(record.diagnostics.get('inradius', float('nan'))))}\)</p></div>
            <div><h4>Bước 5 - Xạ ảnh ngược</h4><p>\(u^{{(k+1)}}={after}\)</p></div>
            <div><h4>Bước 6 - Kiểm tra</h4><p>Mục tiêu sau = {escape(_number(record.f_after if record.f_after is not None else float('nan')))}<br>
              \(\Phi(x^{{(k)}})\) = {escape(phi_before)}<br>
              \(\Phi(x^{{(k+1)}})\) = {escape(phi_after)}<br>
              Độ thay đổi hàm thế = {escape(phi_change)}<br>
              sai số hướng = {escape(_number(record.diagnostics.get('direction_residual', float('nan'))))}<br>
              sai số đẳng thức sau = {escape(_number(record.diagnostics.get('after_eq_residual', float('nan'))))}<br>
              tọa độ nhỏ nhất sau = {escape(_number(record.diagnostics.get('after_min_x', float('nan'))))}</p></div>
          </div>
        </details>
        """)
    return "".join(blocks)


def _output_section(result: GeneralKarmarkarResult, reference: ReferenceResult | None) -> str:
    reference_html = "<p>Không chạy bộ giải tham chiếu.</p>"
    if reference is not None:
        if reference.success and reference.x is not None and reference.objective is not None:
            gap = abs(result.objective - reference.objective)
            reference_html = (
                f"<p><b>Đối chứng HiGHS sau cùng:</b> \\(x={_latex_vector(reference.x)}\\), mục tiêu={escape(_number(reference.objective))}, "
                f"chênh lệch mục tiêu={escape(_number(gap))}.</p>"
                "<p class='muted'>Kết quả này chỉ được gọi sau khi Karmarkar kết thúc và không được dùng để tạo D, B, p, d, y hay điểm lặp.</p>"
            )
        else:
            reference_html = f"<p>Bộ giải tham chiếu không thành công: {escape(reference.message)}</p>"
    return f"""
    <section id="output">
      <h2>6. Kết quả đầu ra</h2>
      <div class="result-grid">
        <div class="metric"><span>Trạng thái</span><strong>{escape(_status_vietnamese(result.status))}</strong></div>
        <div class="metric"><span>Số vòng</span><strong>{result.iterations}</strong></div>
        <div class="metric"><span>Giá trị mục tiêu</span><strong>{escape(_number(result.objective))}</strong></div>
      </div>
      <p><b>Nghiệm gần đúng theo biến đã nhập:</b> \\(x={_latex_vector(result.x)}\\)</p>
      <div class="callout">{escape(result.message)}</div>
      <h3>Đối chứng độc lập sau khi chạy</h3>
      {reference_html}
      <div class="warning"><b>Giới hạn kết luận:</b> các điểm lặp hữu hạn vẫn nằm trong miền trong.
      Trạng thái đạt ngưỡng là nghiệm gần đúng, không phải chứng nhận tối ưu hữu tỉ chính xác.</div>
    </section>
    """


def build_solution_html(
    result: GeneralKarmarkarResult,
    reference: ReferenceResult | None = None,
    *,
    details: bool = True,
) -> str:
    """Return a complete standalone HTML document for one interactive run."""
    flow = _plot_flow()
    images: list[tuple[str, str]] = []
    images.append(("Phép xạ ảnh đưa điểm khả thi ban đầu về trọng tâm", _plot_projective_recenter(result.embedding)))
    simplex = _plot_simplex(result)
    if simplex:
        images.append(("Đơn giác chuẩn và đường đi của các điểm lặp", simplex))
    original = _plot_original_2d(result, reference)
    if original:
        images.append(("Miền khả thi hai biến và đường đi trong tọa độ ban đầu", original))
    images.append(("Mục tiêu và sai số qua từng vòng", _plot_convergence(result)))
    detail_html = _step_details(result) if details else "<p>Chi tiết từng ma trận đang được ẩn theo cấu hình.</p>"
    return f"""<!doctype html>
<html lang="vi">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Lời giải Karmarkar - {escape(result.embedding.general.name)}</title>
  <script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
  <style>
    :root{{--navy:#17324d;--blue:#2d6cdf;--pale:#eef5fc;--line:#cad7e2;--text:#1d2935}}
    *{{box-sizing:border-box}} body{{margin:0;font-family:Inter,Segoe UI,Arial,sans-serif;color:var(--text);background:#f5f7fa;line-height:1.55}}
    header{{background:linear-gradient(135deg,#17324d,#2d6cdf);color:white;padding:44px 24px}}
    header .inner,main{{max-width:1120px;margin:auto}} header h1{{margin:0 0 8px;font-size:2rem}} header p{{margin:0;opacity:.9}}
    main{{padding:26px 18px 60px}} section{{background:white;margin:18px 0;padding:26px;border:1px solid #e1e7ed;border-radius:14px;box-shadow:0 4px 16px rgba(28,54,78,.05)}}
    h2{{color:var(--navy);border-bottom:2px solid #e7eef5;padding-bottom:8px}} h3{{color:#294e70}} code{{background:#edf2f7;padding:2px 5px;border-radius:4px;word-break:break-word}}
    .callout,.ok,.warning{{padding:13px 15px;border-radius:8px;margin:12px 0}} .callout{{background:#edf5ff;border-left:4px solid #2d6cdf}} .ok{{background:#ecf8f1;border-left:4px solid #2f855a}} .warning{{background:#fff5e8;border-left:4px solid #e48632}}
    .muted{{color:#667887;font-size:.92rem}} .table-wrap{{overflow:auto;margin:12px 0}} table{{border-collapse:collapse;width:100%;font-size:.91rem}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left;white-space:nowrap}} th{{background:#edf3f8;color:#17324d;position:sticky;top:0}} table.matrix{{width:auto;font-family:Consolas,monospace}} table.matrix td{{text-align:right}}
    .figure{{display:block;max-width:100%;height:auto;margin:14px auto;border:1px solid #e2e8ee;border-radius:9px}} figure{{margin:22px 0}} figcaption{{text-align:center;color:#607384;font-size:.9rem}}
    .algorithm-card{{border:1.5px solid #647789;border-radius:3px;padding:18px 24px;margin:18px 0;background:#fff}}
    .algorithm-card h3{{margin:0 0 14px;color:#182b3d;font-size:1.2rem}}
    .algorithm-step{{margin:13px 0;padding-left:18px}}
    .steps li{{margin:7px 0}} details.iteration{{border:1px solid #d9e2ea;border-radius:9px;margin:10px 0;background:#fbfcfd}} details.iteration summary{{cursor:pointer;padding:12px 14px;font-weight:650;color:#234b6d}} .iteration-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:12px;padding:0 14px 15px}} .iteration-grid>div{{background:white;border:1px solid #e5ebf0;border-radius:7px;padding:10px;overflow:auto}} .iteration-grid h4{{margin:0 0 8px;color:#305d82}}
    .result-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}} .metric{{background:#f0f5fa;border-radius:9px;padding:14px}} .metric span{{display:block;color:#647789;font-size:.85rem}} .metric strong{{font-size:1.15rem;color:#17324d}}
    nav{{max-width:1120px;margin:14px auto 0;padding:0 18px}} nav a{{color:#2d6cdf;text-decoration:none;margin-right:14px;font-size:.9rem}}
    @media(max-width:620px){{header h1{{font-size:1.5rem}}section{{padding:18px}}}}
  </style>
</head>
<body>
<header><div class="inner"><h1>Lời giải quy hoạch tuyến tính bằng Karmarkar</h1><p>{escape(result.embedding.general.name)} - báo cáo được tạo trực tiếp từ lần chạy hiện tại</p></div></header>
<nav><a href="#input">Dữ liệu vào</a><a href="#normalize">Chuẩn hóa</a><a href="#algorithm">Thuật toán</a><a href="#visuals">Hình minh họa</a><a href="#iterations">Các vòng lặp</a><a href="#output">Kết quả</a></nav>
<main>
  {_input_section(result.embedding)}
  {_normalization_section(result.embedding)}
  {_algorithm_section(flow)}
  {_visual_section(images)}
  <section id="iterations"><h2>5. Bảng bước lặp và phép tính chi tiết</h2>
    <p>Bảng đầu giúp nhìn nhanh. Mở từng vòng bên dưới để xem đúng thứ tự \\(D_k,B_k,v_k,p_k,d_k,y\\) và phép xạ ảnh ngược.</p>
    {_history_table(result)}
    <h3>Chi tiết từng vòng</h3>{detail_html}
  </section>
  {_output_section(result, reference)}
</main>
</body></html>"""


def _extended_value_latex(value: float | None) -> str:
    if value is None:
        return r"\text{chưa xác định}"
    if np.isposinf(value):
        return r"+\infty"
    if np.isneginf(value):
        return r"-\infty"
    return _number(value)


def build_classification_html(
    problem: GeneralLP,
    classification: ProblemClassification,
) -> str:
    """Build an HTML result for infeasible, unbounded or undetermined inputs."""
    labels = {
        "INFEASIBLE": "Bài toán vô nghiệm",
        "UNBOUNDED": "Bài toán không giới nội",
        "MULTIPLE_OPTIMA": "Bài toán có vô số nghiệm tối ưu",
        "KARMARKAR_PRECONDITION_FAILED": "Không thể khởi tạo phép lặp Karmarkar",
        "UNDETERMINED": "Chưa phân loại được",
    }
    label = labels.get(classification.status, classification.status)
    value = _extended_value_latex(classification.objective_value)
    if classification.status == "INFEASIBLE":
        explanation = (
            "Không tồn tại điểm nào đồng thời thỏa tất cả ràng buộc và điều kiện biến. "
            "Vì miền chấp nhận được rỗng, chương trình không thể tạo điểm trong để bắt đầu lặp."
        )
        convention = r"\min z=+\infty,\qquad \max z=-\infty"
    elif classification.status == "UNBOUNDED":
        explanation = (
            "Miền chấp nhận được có điểm, nhưng có một hướng đi khả thi làm giá trị mục tiêu "
            "tiếp tục tốt hơn mà không bị chặn. Vì vậy không tồn tại nghiệm tối ưu hữu hạn."
        )
        convention = r"\min z=-\infty,\qquad \max z=+\infty"
    elif classification.status == "MULTIPLE_OPTIMA":
        explanation = (
            "Tồn tại ít nhất hai nghiệm tối ưu khác nhau. Do miền chấp nhận được của bài toán "
            "quy hoạch tuyến tính là miền lồi, toàn bộ đoạn thẳng nối hai nghiệm này cũng gồm "
            "các nghiệm tối ưu."
        )
        convention = rf"z^\star={value}"
    elif classification.status == "KARMARKAR_PRECONDITION_FAILED":
        explanation = (
            "Bài toán vẫn có nghiệm tối ưu hữu hạn, nhưng miền chuẩn hóa không có điểm trong "
            "dương thích hợp hoặc không tạo được tổng tọa độ cố định. Đây là điều kiện khởi tạo "
            "của phiên bản Karmarkar xạ ảnh, không phải kết luận rằng bài toán vô nghiệm."
        )
        convention = rf"z^\star\approx {value}"
    else:
        explanation = "Kiểm tra số chưa đủ chắc chắn nên chương trình dừng, không tự kết luận sai."
        convention = r"z^\star\;\text{chưa xác định}"
    solution_family = ""
    if (
        classification.status == "MULTIPLE_OPTIMA"
        and classification.x is not None
        and classification.alternative_x is not None
    ):
        solution_family = fr"""
        <h3>Hai nghiệm tối ưu đại diện</h3>
        <p>\(x^{{(A)}}={_latex_vector(classification.x)}\)</p>
        <p>\(x^{{(B)}}={_latex_vector(classification.alternative_x)}\)</p>
        <p><b>Họ vô số nghiệm tối ưu:</b>
        \(x(\lambda)=\lambda x^{{(A)}}+(1-\lambda)x^{{(B)}},\quad 0\le\lambda\le1\).</p>
        """
    elif (
        classification.status == "KARMARKAR_PRECONDITION_FAILED"
        and classification.x is not None
    ):
        solution_family = fr"""
        <h3>Nghiệm hữu hạn đại diện từ bước phân loại</h3>
        <p>\(x^\star\approx {_latex_vector(classification.x)}\)</p>
        <p class="muted">Điểm này chỉ dùng để báo kết quả phân loại; nó không được giả làm
        một điểm lặp Karmarkar.</p>
        """
    if classification.status == "MULTIPLE_OPTIMA":
        value_heading = "Giá trị tối ưu"
        stopping_reason = (
            "Bước phân loại đã chứng nhận được cả giá trị tối ưu và nhiều nghiệm tối ưu, "
            "nên không cần thực hiện vòng lặp Karmarkar."
        )
    elif classification.status == "KARMARKAR_PRECONDITION_FAILED":
        value_heading = "Giá trị tối ưu hữu hạn"
        stopping_reason = (
            "Chương trình dừng có kiểm soát vì điều kiện khởi tạo của phép lặp xạ ảnh không đạt."
        )
    else:
        value_heading = "Quy ước giá trị mở rộng"
        stopping_reason = (
            "Do bài toán không có nghiệm tối ưu hữu hạn, chương trình không thực hiện vòng lặp Karmarkar."
        )
    return f"""<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Phân loại bài toán quy hoạch tuyến tính</title>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>
<style>
:root{{--navy:#17324d;--blue:#2d6cdf;--line:#cad7e2;--text:#1d2935}}
*{{box-sizing:border-box}} body{{margin:0;font-family:Inter,Segoe UI,Arial,sans-serif;color:var(--text);background:#f5f7fa;line-height:1.55}}
header{{background:linear-gradient(135deg,#17324d,#2d6cdf);color:white;padding:44px 24px}} header div,main{{max-width:1120px;margin:auto}}
main{{padding:26px 18px 60px}} section{{background:white;margin:18px 0;padding:26px;border:1px solid #e1e7ed;border-radius:14px}}
h2{{color:var(--navy);border-bottom:2px solid #e7eef5;padding-bottom:8px}}
.callout,.warning{{padding:13px 15px;border-radius:8px;margin:12px 0}} .callout{{background:#edf5ff;border-left:4px solid var(--blue)}} .warning{{background:#fff5e8;border-left:4px solid #e48632}}
.muted{{color:#667887;font-size:.92rem}}
.table-wrap{{overflow:auto}} table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid var(--line);padding:8px 10px;text-align:left}} th{{background:#edf3f8}}
.result{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:12px}} .metric{{background:#f0f5fa;border-radius:9px;padding:14px}} .metric span{{display:block;color:#647789}} .metric strong{{font-size:1.2rem;color:#17324d}}
</style></head><body>
<header><div><h1>Phân loại bài toán quy hoạch tuyến tính</h1><p>{escape(problem.name)}</p></div></header>
<main>
{_problem_input_section(problem)}
<section><h2>2. Kiểm tra trước khi chạy thuật toán</h2>
<div class="warning"><b>{escape(label)}:</b> {escape(classification.message)}</div>
<p>{escape(explanation)}</p>
<p><b>{value_heading}:</b> \\({convention}\\).</p>
{solution_family}
<p>{escape(stopping_reason)} Số vòng lặp Karmarkar được thực hiện là <b>0</b>.</p>
</section>
<section><h2>3. Kết quả đầu ra</h2><div class="result">
<div class="metric"><span>Trạng thái</span><strong>{escape(label)}</strong></div>
<div class="metric"><span>Số vòng lặp</span><strong>0</strong></div>
<div class="metric"><span>Giá trị bài toán đã nhập</span><strong>\\({value}\\)</strong></div>
</div></section>
</main></body></html>"""


def write_classification_html(
    problem: GeneralLP,
    classification: ProblemClassification,
    destination: str | Path,
) -> Path:
    """Write the terminal classification report and return its resolved path."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        build_classification_html(problem, classification), encoding="utf-8"
    )
    return destination.resolve()


def write_solution_html(
    result: GeneralKarmarkarResult,
    reference: ReferenceResult | None,
    destination: str | Path,
    *,
    details: bool = True,
) -> Path:
    """Write one self-contained UTF-8 HTML report and return its resolved path."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build_solution_html(result, reference, details=details), encoding="utf-8")
    return destination.resolve()

