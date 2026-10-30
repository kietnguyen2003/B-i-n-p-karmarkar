"""Tests for the interactive general-LP adapter and HTML output."""

import numpy as np
import pytest

from karmarkar.general_lp import (
    GeneralSolverConfig,
    classify_general_lp,
    classify_preparation_failure,
    make_problem,
    prepare_simplex_embedding,
    solve_general_karmarkar,
    solve_reference,
)
from karmarkar.html_report import build_classification_html, build_solution_html


def source_problem():
    """BC 4.4 entered exactly as min z=2-x1 with x1+x2<=2."""
    return make_problem(
        [-1, 0], [[1, 1]], [2], ["<="], [">=0", ">=0"],
        objective_constant=2,
        name="BC 4.4 interactive",
    )


def test_entered_source_problem_normalizes_and_solves():
    config = GeneralSolverConfig(max_iter=120, objective_tolerance=1e-8)
    embedding = prepare_simplex_embedding(source_problem(), config)
    assert embedding.dimension == 3
    assert np.allclose(
        embedding.canonical.A @ np.ones(embedding.dimension), 0, atol=1e-10
    )
    assert embedding.embedding_mode == "direct_canonical"
    np.testing.assert_allclose(embedding.canonical.c, [0, 1, 1], atol=1e-12)
    result = solve_general_karmarkar(embedding, config)
    assert result.status == "APPROX_TOL_REACHED"
    assert result.iterations > 0
    assert result.objective <= 1e-8
    assert np.allclose(result.x, [2, 0], atol=2e-8)
    assert all(record.x_after is not None for record in result.trace)


def test_entered_source_problem_matches_every_printed_table_row():
    """The interactive input path must reproduce the report, not another embedding."""
    config = GeneralSolverConfig(max_iter=120, objective_tolerance=1e-8)
    result = solve_general_karmarkar(
        prepare_simplex_embedding(source_problem(), config), config
    )
    printed = {
        0: ([0.666667, 0.666667], 1.333333),
        1: ([0.833333, 0.583333], 1.166667),
        2: ([1.010101, 0.494949], 0.989899),
        3: ([1.186240, 0.406880], 0.813760),
        10: ([1.893052, 0.053474], 0.106948),
        20: ([1.996813, 0.001593], 0.003187),
    }
    for k, (expected_x, expected_objective) in printed.items():
        np.testing.assert_allclose(result.history[k].original_x, expected_x, atol=5e-7)
        assert result.history[k].objective == pytest.approx(expected_objective, abs=5e-7)


def test_max_problem_and_reference_are_kept_separate():
    problem = make_problem(
        [1], [[1]], [2], ["<="], [">=0"], sense="max",
    )
    config = GeneralSolverConfig(max_iter=120, objective_tolerance=1e-8)
    result = solve_general_karmarkar(prepare_simplex_embedding(problem, config), config)
    reference = solve_reference(problem)
    assert result.status == "APPROX_TOL_REACHED"
    assert result.objective == pytest.approx(2.0, abs=2e-8)
    assert reference.success and reference.objective == pytest.approx(2.0)


def test_bounded_free_variable_is_shifted_then_recovered():
    problem = make_problem(
        [1], [[1], [1]], [1, -1], ["<=", ">="], ["free"],
        objective_constant=1,
    )
    config = GeneralSolverConfig(max_iter=120, objective_tolerance=1e-8)
    embedding = prepare_simplex_embedding(problem, config)
    assert embedding.input_standard.original_offset[0] == pytest.approx(-1)
    result = solve_general_karmarkar(embedding, config)
    assert result.x[0] == pytest.approx(-1, abs=2e-8)
    assert result.objective <= 1e-8


def test_positive_optimum_is_converted_to_zero_duality_gap():
    problem = make_problem(
        [1], [[1], [1]], [2, 1], ["<=", ">="], [">=0"],
    )
    config = GeneralSolverConfig(max_iter=160, objective_tolerance=1e-8)
    result = solve_general_karmarkar(prepare_simplex_embedding(problem, config), config)
    assert result.status == "APPROX_TOL_REACHED"
    assert result.x[0] == pytest.approx(1.0, abs=5e-8)
    assert result.objective == pytest.approx(1.0, abs=5e-8)
    assert result.history[-1].internal_min_objective <= 1e-8


@pytest.mark.parametrize(
    ("sense", "coefficient", "expected"),
    [("min", -1, -np.inf), ("max", 1, np.inf)],
)
def test_unbounded_problem_uses_the_requested_extended_value(sense, coefficient, expected):
    problem = make_problem(
        [coefficient], [], [], [], [">=0"], sense=sense,
    )
    classification = classify_general_lp(problem)
    assert classification.status == "UNBOUNDED"
    assert classification.terminal
    assert classification.objective_value == expected
    html = build_classification_html(problem, classification)
    assert "Bài toán không giới nội" in html
    assert "Số vòng lặp</span><strong>0" in html
    assert (r"+\infty" if expected > 0 else r"-\infty") in html


@pytest.mark.parametrize(
    ("sense", "expected"),
    [("min", np.inf), ("max", -np.inf)],
)
def test_infeasible_problem_uses_the_requested_empty_set_value(sense, expected):
    problem = make_problem(
        [1], [[1], [1]], [0, 1], ["<=", ">="], [">=0"], sense=sense,
    )
    classification = classify_general_lp(problem)
    assert classification.status == "INFEASIBLE"
    assert classification.terminal
    assert classification.objective_value == expected
    html = build_classification_html(problem, classification)
    assert "Bài toán vô nghiệm" in html
    assert "Miền chấp nhận được rỗng" in html
    assert (r"+\infty" if expected > 0 else r"-\infty") in html


@pytest.mark.parametrize("sense", ["min", "max"])
def test_multiple_optima_returns_two_witnesses_and_the_infinite_family(sense):
    problem = make_problem(
        [1, 1], [[1, 1]], [1], ["="], [">=0", ">=0"], sense=sense,
    )
    classification = classify_general_lp(problem)
    assert classification.status == "MULTIPLE_OPTIMA"
    assert classification.terminal
    assert classification.objective_value == pytest.approx(1.0)
    assert classification.x is not None and classification.alternative_x is not None
    assert not np.allclose(classification.x, classification.alternative_x)
    assert np.sum(classification.x) == pytest.approx(1.0)
    assert np.sum(classification.alternative_x) == pytest.approx(1.0)
    html = build_classification_html(problem, classification)
    assert "Bài toán có vô số nghiệm tối ưu" in html
    assert "Họ vô số nghiệm tối ưu" in html
    assert r"x(\lambda)=\lambda x^{(A)}+(1-\lambda)x^{(B)}" in html
    assert "Số vòng lặp</span><strong>0" in html


def test_finite_degenerate_problem_becomes_a_report_instead_of_crashing():
    problem = make_problem([1], [[1]], [0], ["="], [">=0"])
    classification = classify_general_lp(problem)
    assert classification.status == "FINITE_OPTIMUM"
    with pytest.raises(ValueError) as caught:
        prepare_simplex_embedding(problem)
    terminal = classify_preparation_failure(classification, caught.value)
    assert terminal.status == "KARMARKAR_PRECONDITION_FAILED"
    assert terminal.terminal
    assert terminal.objective_value == pytest.approx(0.0)
    html = build_classification_html(problem, terminal)
    assert "Không thể khởi tạo phép lặp Karmarkar" in html
    assert "Nghiệm hữu hạn đại diện" in html


def test_unbounded_phase_one_margin_still_produces_a_valid_karmarkar_start():
    """A feasible ray may unbound Phase I's old margin without unbounding the LP."""
    problem = make_problem(
        [-1, -3, -1],
        [[2, -5, 1], [2, -1, 2]],
        [-5, 4],
        ["<=", "<="],
        [">=0", ">=0", ">=0"],
        sense="max",
    )
    classification = classify_general_lp(problem)
    assert classification.status == "FINITE_OPTIMUM"
    assert classification.objective_value == pytest.approx(-3.0)
    np.testing.assert_allclose(classification.x, [0, 1, 0], atol=1e-10)

    config = GeneralSolverConfig(max_iter=240, objective_tolerance=1e-8)
    embedding = prepare_simplex_embedding(problem, config)
    assert embedding.interior_margin > 0
    assert np.min(embedding.interior) > 0
    result = solve_general_karmarkar(embedding, config)
    assert result.status == "APPROX_TOL_REACHED"
    assert result.objective == pytest.approx(-3.0, abs=1e-7)
    np.testing.assert_allclose(result.x, [0, 1, 0], atol=1e-7)


def test_html_contains_inputs_six_steps_images_and_all_iterations():
    config = GeneralSolverConfig(max_iter=120, objective_tolerance=1e-8)
    problem = source_problem()
    result = solve_general_karmarkar(prepare_simplex_embedding(problem, config), config)
    html = build_solution_html(result, solve_reference(problem), details=True)
    assert "Dữ liệu đầu vào" in html
    assert "Chuẩn hóa dữ liệu" in html
    assert "Tìm điểm hợp lệ để bắt đầu" in html
    assert "Thuật toán Karmarkar dưới dạng các bước toán học" in html
    assert "Bước 1. Xuất phát." in html
    assert "Bước 6. Đánh giá." in html
    assert r"D_k=\operatorname{diag}" in html
    assert r"B_k=\begin{bmatrix}" in html
    assert r"\Phi(x^{(k+1)})-\Phi(x^{(k)})" in html
    assert "Xạ ảnh ngược" in html
    assert "data:image/png;base64," in html
    assert "tex-mml-chtml.js" in html
    assert html.count("class=\"iteration\"") == result.iterations
    assert "Đối chứng HiGHS" in html
    assert "duality gap" not in html.lower()
    assert "trong PDF" not in html

