"""Build the small input -> Karmarkar -> HTML notebook requested by the user."""

from pathlib import Path
import nbformat as nbf


def markdown(text: str):
    return nbf.v4.new_markdown_cell(text.strip() + "\n")


def code(text: str):
    return nbf.v4.new_code_cell(text.strip() + "\n")


def build(workspace: Path) -> Path:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"] = {
        "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
        "language_info": {"name": "python", "version": "3.10"},
    }
    notebook["cells"] = [
        markdown(r"""
# Karmarkar - nhập bài toán và xuất lời giải HTML

Chọn **Chạy tất cả các ô**, sau đó nhập hàm mục tiêu và các ràng buộc theo câu hỏi trên màn hình.
Chương trình sẽ chuẩn hóa bài toán, chạy các bước Karmarkar và ghi toàn bộ
lời giải vào **`output/Loi_giai_Karmarkar.html`**.

Notebook chỉ hiển thị câu hỏi nhập liệu và đường dẫn kết quả. Trong file HTML có:

- đề bài đã nhập;
- cách đổi dấu biến, thêm biến dư và đưa về đơn giác chuẩn;
- phép xạ ảnh, quả cầu nội tiếp và phép chiếu;
- bảng mọi vòng lặp;
- các giá trị `D`, `B`, `v`, `p`, `d`, `y` và điểm mới;
- hình minh họa khi bài toán có 2 biến hoặc đơn giác có 3-4 tọa độ;
- nghiệm gần đúng và đối chứng độc lập sau cùng;
- kết luận riêng khi bài toán vô nghiệm, không giới nội hoặc có vô số nghiệm tối ưu.

**Phạm vi toán học:** dạng chuẩn cần một mục tiêu không âm có giá trị tối ưu bằng 0.
Nếu bài nhập đã đưa trực tiếp được về dạng này, chương trình giữ nguyên bài toán để các vòng lặp
đúng với cách tính trong báo cáo. Với bài tổng quát hơn, chương trình ghép bài toán primal-dual và
giảm **độ chênh lệch primal-dual** về 0. Miền vẫn cần có điểm trong ở các phía liên quan.
Trước khi lặp, chương trình phân loại và dừng đúng cách nếu miền chấp nhận được rỗng, mục tiêu
không giới nội hoặc tồn tại vô số nghiệm tối ưu. Trường hợp suy biến không khởi tạo được sẽ
được báo rõ thay vì xuất một nghiệm sai.
"""),
        markdown(r"""
## Khối 1 - Cài đặt môi trường tính toán

Nạp thư viện và mã nguồn Karmarkar. Khối này chỉ chuẩn bị chương trình, chưa giải bài toán.
"""),
        code(r"""
import importlib
import sys
from fractions import Fraction
from pathlib import Path
from IPython.display import display, HTML
from IPython.utils.capture import capture_output

RUN_DIR = Path.cwd().resolve()
if (RUN_DIR / 'karmarkar-project' / 'src').is_dir():
    WORKSPACE = RUN_DIR
    PROJECT_DIR = WORKSPACE / 'karmarkar-project'
elif (RUN_DIR / 'src' / 'karmarkar').is_dir():
    PROJECT_DIR = RUN_DIR
    WORKSPACE = PROJECT_DIR.parent
elif (RUN_DIR.parent / 'src' / 'karmarkar').is_dir():
    PROJECT_DIR = RUN_DIR.parent
    WORKSPACE = PROJECT_DIR.parent
else:
    raise FileNotFoundError('Không tìm thấy thư mục karmarkar-project/src.')

src_path = str(PROJECT_DIR / 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

with capture_output():
    general_lp = importlib.reload(importlib.import_module('karmarkar.general_lp'))
    html_report = importlib.reload(importlib.import_module('karmarkar.html_report'))
"""),
        markdown(r"""
## Khối 2 - Cài đặt cách chạy

Đặt số vòng tối đa, sai số mong muốn và tên file HTML. Đây là phần cài đặt; thông thường
chỉ cần giữ nguyên các giá trị bên dưới.
"""),
        code(r"""
ALPHA = 0.25
MAX_ITER = 300
OBJECTIVE_TOLERANCE = 1e-8
FEASIBILITY_TOLERANCE = 1e-9
COMPARE_WITH_REFERENCE = True
SHOW_EVERY_CALCULATION = True
HTML_REPORT_PATH = WORKSPACE / 'output' / 'Loi_giai_Karmarkar.html'

solver_config = general_lp.GeneralSolverConfig(
    alpha=ALPHA,
    max_iter=MAX_ITER,
    objective_tolerance=OBJECTIVE_TOLERANCE,
    feasibility_tolerance=FEASIBILITY_TOLERANCE,
)
"""),
        markdown(r"""
## Khối 3 - Nhập hàm mục tiêu và các ràng buộc

Nhập lần lượt:

1. bài toán `min` hay `max`;
2. số biến và số ràng buộc;
3. hệ số hàm mục tiêu và hằng số;
4. hệ số, dấu và vế phải của từng ràng buộc;
5. điều kiện dấu của từng biến.

Có thể nhập số nguyên, số thập phân hoặc phân số như `1/3`. Các hệ số trên cùng một dòng
được ngăn bằng khoảng trắng.

Nếu phát hiện đã nhập sai ở bước trước, gõ **`thoat`** tại bất kỳ câu hỏi nào. Lần chạy
hiện tại sẽ dừng an toàn; sau đó chọn **Chạy tất cả các ô** để nhập lại từ đầu.
"""),
        code(r"""
class InputCancelled(Exception):
    pass


def ask(prompt):
    raw = input(prompt)
    if raw.strip().lower() in {'thoat', 'thoát', 'exit', 'quit', 'q'}:
        raise InputCancelled
    return raw


def read_choice(prompt, allowed):
    message = ''
    while True:
        value = ask(message + prompt).strip().lower()
        if value in allowed:
            return value
        message = 'Chỉ chấp nhận: ' + ', '.join(allowed) + '. '


def read_integer(prompt, minimum=0):
    message = ''
    while True:
        try:
            value = int(ask(message + prompt).strip())
            if value >= minimum:
                return value
        except ValueError:
            pass
        message = f'Hãy nhập số nguyên >= {minimum}. '


def parse_number(text):
    try:
        return float(Fraction(text.strip()))
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError(f'Không đọc được số "{text}"') from error


def read_number(prompt):
    message = ''
    while True:
        raw = ask(message + prompt)
        try:
            return parse_number(raw)
        except ValueError as error:
            message = str(error) + '. '


def read_vector(name, length):
    message = ''
    while True:
        parts = ask(message + f'Nhập {length} hệ số của {name}, cách nhau bằng khoảng trắng: ').split()
        if len(parts) != length:
            message = f'Cần đúng {length} số. '
            continue
        try:
            return [parse_number(part) for part in parts]
        except ValueError as error:
            message = str(error) + '. '


problem = None
try:
    sense = read_choice('Bài toán min hay max? ', ['min', 'max'])
    n = read_integer('Nhập số biến n (>=1): ', 1)
    m = read_integer('Nhập số ràng buộc m (>=0): ', 0)
    objective = read_vector('hàm mục tiêu', n)
    objective_constant = read_number('Nhập hằng số của hàm mục tiêu (không có thì nhập 0): ')

    constraints = []
    constraint_signs = []
    rhs = []
    for i in range(m):
        print(f'--- Ràng buộc {i + 1} ---')
        constraints.append(read_vector(f'ràng buộc {i + 1}', n))
        constraint_signs.append(read_choice('Dấu (<=, >=, =): ', ['<=', '>=', '=']))
        rhs.append(read_number('Vế phải: '))

    variable_signs = [
        read_choice(f'Điều kiện của x{j + 1} (>=0, <=0, free): ', ['>=0', '<=0', 'free'])
        for j in range(n)
    ]

    problem = general_lp.make_problem(
        objective, constraints, rhs, constraint_signs, variable_signs,
        sense=sense, objective_constant=objective_constant,
        name='Bài toán nhập từ Karmarkar_HTML.ipynb',
    )
except InputCancelled:
    print('Đã thoát lần nhập hiện tại. Hãy chọn Chạy tất cả các ô để nhập lại từ đầu.')
"""),
        markdown(r"""
## Khối 4 - Kiểm tra và chuẩn hóa tọa độ

Trước tiên, chương trình phân loại bài toán. Nếu miền rỗng, hàm mục tiêu không giới nội hoặc
có vô số nghiệm tối ưu, chương trình dừng trước vòng lặp và xuất kết luận tương ứng. Với bài
toán có nghiệm tối ưu hữu hạn duy nhất,
chương trình đổi mọi biến về không âm, thêm biến dư hoặc biến thừa và đưa về đơn giác chuẩn.
Nếu bài toán đã có mục tiêu tối ưu bằng 0, chương trình dùng trực tiếp dạng chuẩn này để giữ đúng
đường đi của thuật toán. Chỉ khi cần thiết, chương trình mới ghép primal với dual và dùng
**độ chênh lệch primal-dual** làm mục tiêu không âm. Phép xạ ảnh ban đầu đưa điểm khả thi
đang có về đúng trọng tâm.

Khối này cũng kiểm tra có điểm trong dương và có thể tạo tổng tọa độ cố định hay không.
"""),
        code(r"""
with capture_output():
    problem_classification = general_lp.classify_general_lp(problem) if problem is not None else None
    embedding = None
    if problem_classification is not None and not problem_classification.terminal:
        try:
            embedding = general_lp.prepare_simplex_embedding(problem, solver_config)
        except ValueError as error:
            problem_classification = general_lp.classify_preparation_failure(
                problem_classification, error
            )
"""),
        markdown(r"""
## Khối 5 - Chạy thuật toán Karmarkar

Chương trình xuất phát tại trọng tâm, rồi mỗi vòng thực hiện đủ: tạo `D` và `B`, tính `Dc`,
chiếu để có `p`, chuẩn hóa hướng `d`, đi trong quả cầu nội tiếp để có `y`, xạ ảnh ngược
thành điểm mới, cuối cùng kiểm tra hàm thế, mục tiêu, tính khả thi và điều kiện dừng.
"""),
        code(r"""
with capture_output():
    karmarkar_result = (
        general_lp.solve_general_karmarkar(embedding, solver_config)
        if embedding is not None else None
    )
"""),
        markdown(r"""
## Khối 6 - Kiểm tra kết quả độc lập

HiGHS được dùng trước vòng lặp chỉ để phân loại bài toán hữu hạn, vô nghiệm hay không giới nội.
Với bài toán hữu hạn, nếu bật tùy chọn đối chứng, HiGHS còn được gọi sau khi Karmarkar kết thúc
để so sánh nghiệm. Không kết quả nào từ HiGHS được dùng để tạo các bước `D`, `B`, `p`, `d`, `y`.
"""),
        code(r"""
with capture_output():
    reference_result = (
        general_lp.solve_reference(problem)
        if problem is not None and karmarkar_result is not None and COMPARE_WITH_REFERENCE
        else None
    )
"""),
        markdown(r"""
## Khối 7 - Xuất kết quả thành file HTML

Tạo lại file HTML cho lần chạy hiện tại. Hình ảnh được nhúng trực tiếp nên chỉ cần mở một
file HTML là xem được toàn bộ đề bài, phép chuẩn hóa, bước lặp, hình và kết quả.
"""),
        code(r"""
with capture_output():
    if problem is None:
        report_path = None
    elif problem_classification.terminal:
        report_path = html_report.write_classification_html(
            problem, problem_classification, HTML_REPORT_PATH
        )
    else:
        report_path = html_report.write_solution_html(
            karmarkar_result,
            reference_result,
            HTML_REPORT_PATH,
            details=SHOW_EVERY_CALCULATION,
        )
"""),
        markdown(r"""
## Khối 8 - Mở kết quả

Nhấn đường dẫn được hiện bên dưới để mở file lời giải HTML vừa tạo.
"""),
        code(r"""
if report_path is None:
    display(HTML(
        '<div style="padding:14px;border-left:4px solid #e48632;background:#fff5e8">'
        '<b>Đã thoát lần nhập hiện tại.</b> Chọn <b>Chạy tất cả các ô</b> để nhập lại từ đầu.</div>'
    ))
else:
    relative_report = report_path.relative_to(WORKSPACE).as_posix()
    if problem_classification.terminal:
        summary = (
            f'Trạng thái: {problem_classification.status}; số vòng: 0; '
            f'giá trị mở rộng: {problem_classification.objective_value}'
        )
    else:
        summary = (
            f'Trạng thái: {karmarkar_result.status}; số vòng: {karmarkar_result.iterations}; '
            f'mục tiêu: {karmarkar_result.objective:.10g}'
        )
    display(HTML(
        f'<div style="padding:14px;border-left:4px solid #2f855a;background:#edf8f1">'
        f'<b>Đã tạo kết quả:</b> <a href="{relative_report}" target="_blank">{relative_report}</a><br>'
        f'{summary}</div>'
    ))
"""),
    ]
    output = workspace / "Karmarkar_HTML.ipynb"
    output.write_text(nbf.writes(notebook), encoding="utf-8")
    return output


if __name__ == "__main__":
    project = Path(__file__).resolve().parents[1]
    target = build(project.parent)
    print(f"Created {target}")

