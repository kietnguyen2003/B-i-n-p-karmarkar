"""Execute the interactive notebook for cancel, terminal and finite scenarios."""

from __future__ import annotations

import builtins
from pathlib import Path

import nbformat


BOUNDED_ANSWERS = [
    "min",      # sense
    "2",        # n
    "1",        # m
    "-1 0",     # objective coefficients
    "2",        # objective constant
    "1 1",      # constraint coefficients
    "<=",       # constraint sign
    "2",        # rhs
    ">=0",      # x1 sign
    ">=0",      # x2 sign
]


def execute_notebook(notebook_path: Path, answers: list[str]) -> dict:
    notebook = nbformat.read(notebook_path, as_version=4)
    namespace = {"__name__": "__notebook_verification__"}
    answer_iterator = iter(answers)
    original_input = builtins.input

    def supplied_input(prompt: str = "") -> str:
        value = next(answer_iterator)
        print(f"{prompt}{value}")
        return value

    builtins.input = supplied_input
    try:
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type != "code":
                continue
            exec(compile(cell.source, f"{notebook_path.name}:cell-{index}", "exec"), namespace)
    finally:
        builtins.input = original_input
    return namespace


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    workspace = project.parent
    notebook_path = workspace / "Karmarkar_HTML.ipynb"
    cancelled = execute_notebook(notebook_path, ["min", "2", "thoat"])
    assert cancelled["problem"] is None
    assert cancelled["report_path"] is None

    unbounded = execute_notebook(
        notebook_path, ["max", "1", "0", "1", "0", ">=0"]
    )
    assert unbounded["problem_classification"].status == "UNBOUNDED"
    assert unbounded["problem_classification"].objective_value == float("inf")
    unbounded_html = Path(unbounded["report_path"]).read_text(encoding="utf-8")
    assert "Bài toán không giới nội" in unbounded_html
    assert r"+\infty" in unbounded_html

    infeasible = execute_notebook(
        notebook_path,
        ["min", "1", "2", "1", "0", "1", "<=", "0", "1", ">=", "1", ">=0"],
    )
    assert infeasible["problem_classification"].status == "INFEASIBLE"
    assert infeasible["problem_classification"].objective_value == float("inf")
    infeasible_html = Path(infeasible["report_path"]).read_text(encoding="utf-8")
    assert "Bài toán vô nghiệm" in infeasible_html
    assert r"+\infty" in infeasible_html

    degenerate = execute_notebook(
        notebook_path, ["min", "1", "1", "1", "0", "1", "=", "0", ">=0"]
    )
    assert degenerate["problem_classification"].status == "KARMARKAR_PRECONDITION_FAILED"
    degenerate_html = Path(degenerate["report_path"]).read_text(encoding="utf-8")
    assert "Không thể khởi tạo phép lặp Karmarkar" in degenerate_html
    assert "Nghiệm hữu hạn đại diện" in degenerate_html

    phase_one_ray = execute_notebook(
        notebook_path,
        [
            "max", "3", "2", "-1 -3 -1", "0",
            "2 -5 1", "<=", "-5",
            "2 -1 2", "<=", "4",
            ">=0", ">=0", ">=0",
        ],
    )
    assert phase_one_ray["problem_classification"].status == "FINITE_OPTIMUM"
    phase_one_result = phase_one_ray["karmarkar_result"]
    assert phase_one_result.status == "APPROX_TOL_REACHED"
    assert abs(phase_one_result.objective + 3.0) <= 1e-7
    assert max(abs(a - b) for a, b in zip(phase_one_result.x, [0, 1, 0])) <= 1e-7

    multiple = execute_notebook(
        notebook_path,
        ["min", "2", "1", "1 1", "0", "1 1", "=", "1", ">=0", ">=0"],
    )
    assert multiple["problem_classification"].status == "MULTIPLE_OPTIMA"
    assert multiple["problem_classification"].objective_value == 1.0
    multiple_html = Path(multiple["report_path"]).read_text(encoding="utf-8")
    assert "Bài toán có vô số nghiệm tối ưu" in multiple_html
    assert "Họ vô số nghiệm tối ưu" in multiple_html

    # Run the bounded source example last so the user's main HTML remains useful.
    namespace = execute_notebook(notebook_path, BOUNDED_ANSWERS)

    result = namespace["karmarkar_result"]
    embedding = namespace["embedding"]
    report_path = Path(namespace["report_path"])
    assert result.status == "APPROX_TOL_REACHED"
    assert result.objective <= 1e-8
    assert embedding.embedding_mode == "direct_canonical"
    assert embedding.dimension == 3
    expected_rows = {
        0: ([0.666667, 0.666667], 1.333333),
        1: ([0.833333, 0.583333], 1.166667),
        2: ([1.010101, 0.494949], 0.989899),
        3: ([1.186240, 0.406880], 0.813760),
        10: ([1.893052, 0.053474], 0.106948),
        20: ([1.996813, 0.001593], 0.003187),
    }
    for k, (expected_x, expected_objective) in expected_rows.items():
        assert max(abs(a - b) for a, b in zip(result.history[k].original_x, expected_x)) <= 5e-7
        assert abs(result.history[k].objective - expected_objective) <= 5e-7
    assert report_path.is_file() and report_path.stat().st_size > 100_000
    html = report_path.read_text(encoding="utf-8")
    for required in (
        "Dữ liệu đầu vào",
        "Tìm điểm hợp lệ để bắt đầu",
        "Chuẩn hóa dữ liệu",
        "Thuật toán Karmarkar dưới dạng các bước toán học",
        "Bước 1. Xuất phát.",
        "Bước 6. Đánh giá.",
        "data:image/png;base64",
        "Kết quả đầu ra",
    ):
        assert required in html
    for forbidden in ("duality gap", "trong PDF", "Cách hiểu:", "Input -", "Output -"):
        assert forbidden.lower() not in html.lower()
    print({
        "status": result.status,
        "iterations": result.iterations,
        "objective": result.objective,
        "x": result.x.tolist(),
        "html": str(report_path),
        "bytes": report_path.stat().st_size,
    })


if __name__ == "__main__":
    main()

