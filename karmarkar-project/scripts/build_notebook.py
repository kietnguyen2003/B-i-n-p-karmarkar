"""[MasterSpec C12, section 5; BC 4.1-4.5] Generate all 68 annotated teaching cells.

The generated notebook imports the package, never duplicates the solver. This
generator is retained so its Vietnamese explanations and references are editable.
"""
from pathlib import Path
import nbformat as nbf


def build(root: Path):
    """[MS NB01-NB68] Build a beginner-first notebook with auditable source references."""
    cells=[nbf.v4.new_markdown_cell(r"""# Thuật toán xạ ảnh Karmarkar

**Notebook thuyết minh và kiểm chứng theo BC 4.1–4.5.**

Nguồn [BC]: `BC - Mục 4 - Karmarkar.pdf`, 27 trang PDF, trang in 33–59.
Đặc tả: `Karmarkar_Codex_MasterSpec.pdf`, phiên bản 3.0, 33 trang.
Tên nguồn có hậu tố `(1)` trong MasterSpec chỉ bản 27 trang; dự án dùng file cùng nội dung/phân trang hiện có trong thư mục cha.

Nhãn **[BC]** chỉ nội dung báo cáo; **[GD]** là hợp đồng tính toán; **[DX]** là phần kỹ thuật/thực nghiệm bổ sung.
Mỗi block NBxx ghi mục BC, công thức/hình liên quan và block Cxx trong MasterSpec.

Chạy từ kernel của môi trường đã `pip install -e '.[dev]'`, rồi **Restart Kernel → Run All**.
Không cần nhập tương tác hoặc cài thư viện trong cell. Các phép lặp là kết quả của solver tự cài;
nghiệm đóng chỉ làm đối chiếu, HiGHS chỉ nằm ở phần thực nghiệm độc lập.

Mạch đọc: **hình học → cơ sở toán học → thuật toán → ví dụ → nhận xét → thực nghiệm [DX]**.
Hai tệp Markdown trong `docs/` giải thích giả thiết và ánh xạ từng mục.
""")]

    cells.append(nbf.v4.new_markdown_cell(r"""# Cách đọc notebook nếu bạn chưa biết code

Bạn **không cần đọc hiểu từng dòng Python**. Mỗi mục được sắp theo thứ tự sau:

1. **Mục đích:** mục này giúp trả lời câu hỏi gì.
2. **Cách hiểu đơn giản:** ý tưởng được diễn đạt bằng lời thường.
3. **Loại nội dung:** cho biết đây là lý thuyết, cài đặt, vẽ hình, kiểm tra hay thực nghiệm.
4. **Input:** dữ liệu được đưa vào chương trình.
5. **Máy sẽ làm gì:** việc đoạn code thực hiện.
6. **Output:** bảng, con số hoặc hình nhận được.
7. **Bạn chỉ cần nhìn:** điểm quan trọng nhất trong kết quả.

Ô nền xám chứa code là phần dành cho người muốn xem cách cài đặt. Nếu chỉ muốn học ý tưởng,
bạn có thể **đọc phần ghi chú trước code, xem kết quả bên dưới rồi đọc “Kết luận dễ hiểu”**.

## Một số từ thường gặp

| Từ trong notebook | Hiểu đơn giản |
|---|---|
| Điểm khả thi | Một phương án không vi phạm điều kiện của bài toán |
| Hàm mục tiêu | Con số ta muốn làm nhỏ nhất |
| Vòng lặp | Một lần thuật toán tính từ điểm hiện tại sang điểm mới |
| Tọa độ | Các con số dùng để mô tả vị trí của một điểm |
| Xạ ảnh | Đổi cách nhìn để điểm hiện tại nằm ở vị trí dễ tính hơn |
| Phép chiếu | Loại bỏ phần chuyển động có thể làm sai các điều kiện |
| Residual / sai số ràng buộc | Mức lệch nhỏ do máy tính làm tròn số |
| Benchmark | Chạy thử nhiều bài để xem chương trình hoạt động ra sao |
| Solver | Chương trình thực hiện các vòng lặp để tìm phương án tốt dần |

Các ký hiệu như `D`, `B`, `p`, `d`, `Phi` chỉ là tên trung gian. Khi gặp chúng lần đầu,
hãy tập trung vào phần **“Cách hiểu đơn giản”**; phần công thức có thể đọc sau.
"""))

    def heading(title,text):
        """[MS 5.1] Open each section with a plain-language reading goal."""
        cells.append(nbf.v4.new_markdown_cell(
            f"## {title}\n\n**Phần này giúp bạn hiểu:** {text}\n\n"
            "Nếu gặp công thức khó, hãy đọc phần diễn giải bằng lời và nhìn hình/kết quả trước."
        ))

    simple_explanations = {
        1: "Ghi lại phiên bản Python và thư viện, giống như ghi tên máy móc đã dùng để người khác chạy lại đúng môi trường.",
        2: "Đọc các nút điều chỉnh của chương trình: bước đi lớn bao nhiêu, dừng ở mức nào và cho phép chạy tối đa bao nhiêu vòng.",
        3: "Chuẩn bị các ngăn để chương trình cất hình, bảng và lịch sử tính toán; mục này chưa giải bài toán.",
        4: "Quy định màu sắc và cách hiện hình để các hình sau dùng cùng một ngôn ngữ thị giác.",
        5: "Cho biết notebook đi theo phần nào của báo cáo và phần nào là thử nghiệm do chương trình bổ sung.",
        6: "Tô tất cả điểm thỏa ba điều kiện; vùng còn lại chính là các phương án được phép chọn.",
        7: "Vẽ vùng được phép và cho thấy muốn giảm giá trị mục tiêu thì phải đi dần sang bên phải.",
        8: "Thử ba góc của tam giác để thấy góc A cho giá trị nhỏ nhất bằng 0.",
        9: "Thêm một con số biểu diễn phần còn dư để biến tam giác hai chiều thành ba trọng số có tổng bằng 1.",
        10: "Đặt hai hình cạnh nhau để thấy đây vẫn là cùng một miền, chỉ thay cách ghi tọa độ.",
        11: "Tóm tắt toàn bộ một vòng Karmarkar bằng năm hành động dễ nhớ trước khi đi vào chi tiết.",
        12: "Đóng gói bài toán theo đúng định dạng chương trình cần: ma trận điều kiện và các hệ số mục tiêu.",
        13: "Kiểm tra bài toán có đủ điều kiện để áp dụng thuật toán hay chưa, giống bước kiểm tra đầu vào trước khi khởi động máy.",
        14: "Cố tình đưa dữ liệu sai để chắc chắn chương trình báo lỗi rõ ràng thay vì âm thầm cho kết quả sai.",
        15: "Tính tâm và hai khoảng cách an toàn của tam giác chuẩn; chúng giúp giới hạn bước đi để không ra ngoài miền.",
        16: "Vẽ tam giác cùng hai đường tròn để nhìn trực tiếp vùng bước đi an toàn quanh tâm.",
        17: "Cho thấy hướng giảm tự nhiên có thể làm hỏng điều kiện, nên chưa thể dùng ngay hướng đó.",
        18: "Giữ lại phần của hướng giảm vẫn tôn trọng điều kiện; có thể hình dung như chiếu một mũi tên xuống đường được phép đi.",
        19: "Thử trường hợp có điều kiện trùng nhau để chắc chắn phép chiếu vẫn chạy ổn định.",
        20: "Dùng cùng một phép đổi tọa độ cho hai điểm để thấy chỉ điểm làm mốc được đưa về tâm, không phải mọi điểm.",
        21: "Đổi tọa độ rồi đổi ngược lại; nếu kết quả trở về đúng điểm ban đầu thì phép biến đổi được cài đúng.",
        22: "Vẽ trước và sau khi đổi cách nhìn để thấy các điểm đổi vị trí trên hình nhưng vẫn đại diện cho cùng bài toán.",
        23: "Kiểm tra giá trị mục tiêu gốc vẫn được tính đúng sau khi đổi tọa độ; công thức phụ chỉ dùng để chọn hướng đi.",
        24: "Từ điểm ở tâm, chương trình tìm hướng hợp lệ rồi đi một đoạn ngắn trong vùng an toàn.",
        25: "Vẽ riêng bước đi vừa tính để thấy điểm mới chưa chạm biên và vẫn nằm trong vùng an toàn.",
        26: "Tính thước đo tiến triển ở hai hệ tọa độ; hai con số có thể lệch nhau một hằng số nhưng mức thay đổi phải giống nhau.",
        27: "So mức thay đổi trước và sau đổi tọa độ để xác nhận thước đo tiến triển không bị bóp méo.",
        28: "Kiểm tra trong ví dụ này mỗi vòng làm thước đo tiến triển giảm đủ nhiều so với mốc lý thuyết.",
        29: "Minh họa ý tưởng rằng số vòng có thể được ước lượng trong lý thuyết; hình này không phải kết quả đo thời gian chạy.",
        30: "Khóa bài toán, điểm xuất phát và các nút điều chỉnh trước khi bắt đầu vòng lặp đầu tiên.",
        31: "Tạo ba đối tượng trung gian từ điểm hiện tại: cách co giãn tọa độ, điều kiện được phép và hướng muốn giảm.",
        32: "Biến hướng muốn giảm thành hướng vừa giảm được mục tiêu vừa không phá điều kiện.",
        33: "Đi một bước trong hệ tọa độ dễ tính rồi đổi kết quả về hệ tọa độ ban đầu.",
        34: "Kiểm tra điểm mới vẫn dương, tổng vẫn bằng 1 và các điều kiện vẫn được giữ trong sai số máy tính.",
        35: "Lặp lại quy trình 20 lần và lưu toàn bộ lịch sử để xem điểm thay đổi dần như thế nào.",
        36: "Vẽ sơ đồ luồng của một vòng lặp để bạn theo dõi thứ tự các bước mà không cần đọc code.",
        37: "Cho xem các lý do chương trình có thể dừng và nhấn mạnh rằng dừng gần đúng không đồng nghĩa với chứng minh tối ưu tuyệt đối.",
        38: "Nhắc lại đề bài gốc bằng lời và bảng trước khi thực hiện các phép đổi biến.",
        39: "Vẽ tam giác nghiệm để thấy trực quan các phương án được phép và đỉnh tốt nhất.",
        40: "Lưu bảng giá trị ở ba đỉnh; đây là lời giải hình học đơn giản dùng để đối chiếu với thuật toán.",
        41: "Chuyển một điểm cụ thể sang ba trọng số và kiểm tra ba trọng số cộng lại bằng 1.",
        42: "Xác nhận mục tiêu trong bài toán mới chỉ khác mục tiêu gốc bởi hệ số 2, nên nghiệm tốt nhất không thay đổi.",
        43: "Tạo công cụ chiếu riêng cho ví dụ ba tọa độ và kiểm tra nó thật sự giữ hướng trong mặt phẳng được phép.",
        44: "Chạy vòng đầu tiên từ tâm và in đầy đủ các bước trung gian để đối chiếu với phép tính trong PDF.",
        45: "Đổi kết quả vòng đầu về hai biến gốc để thấy giá trị mục tiêu đã giảm.",
        46: "Chạy vòng thứ hai từ điểm mới; lần này điểm làm mốc không còn ở tâm nên phép đổi ngược bắt đầu có tác dụng rõ.",
        47: "So điểm trong hệ phụ với điểm sau khi đổi về hệ gốc để thấy chúng không còn là cùng một dãy số.",
        48: "Chạy vòng thứ ba và kiểm tra kết quả tiếp tục tiến gần đỉnh tốt nhất.",
        49: "Dùng công thức riêng của ví dụ để tính nhanh vị trí ở bất kỳ vòng nào; công thức này chỉ dùng để kiểm tra solver.",
        50: "So từng điểm do solver thật tạo ra với công thức kiểm tra độc lập; sai số rất nhỏ nghĩa là hai cách khớp nhau.",
        51: "Lấy sáu vòng tiêu biểu từ lịch sử thật và xuất thành bảng giống Bảng 4.2 trong báo cáo.",
        52: "Vẽ đường đi của các điểm lặp để thấy chúng ở trong tam giác và tiến dần về đỉnh A.",
        53: "Vẽ riêng giá trị mục tiêu và thước đo tiến triển để không nhầm hai khái niệm này với nhau.",
        54: "Kiểm tra mức giảm của thước đo ở mỗi vòng có đúng bằng con số được suy ra trong báo cáo.",
        55: "Tìm vòng đầu tiên mà sai số mục tiêu nhỏ hơn 0.1 và kiểm tra cả vòng ngay trước đó.",
        56: "So sánh lời giải bằng hình học với Karmarkar theo cách làm, kết quả và phạm vi sử dụng.",
        57: "Kiểm tra mọi điểm hữu hạn vẫn nằm trong miền; chỉ giới hạn của dãy mới tiến sát biên.",
        58: "Tách rõ ba vai trò: đổi điểm về tâm, giữ đúng điều kiện và giới hạn độ dài bước đi.",
        59: "Liệt kê điều dự án đã chứng minh bằng chạy máy và điều chưa được phép khẳng định.",
        60: "Tạo nhiều bài thử có chủ đích: bài bình thường, bài có điều kiện phụ, bài sai và bài khó về số học.",
        61: "Chạy thuật toán nhiều lần trên toàn bộ bộ bài thử và giữ lại cả các lần thất bại.",
        62: "Dùng một bộ giải độc lập làm thước tham khảo sau khi Karmarkar đã chạy xong; bộ giải này không tham gia tạo các bước Karmarkar.",
        63: "Tổng hợp thời gian và số vòng từ các lần chạy thật để người đọc biết kết quả đến từ môi trường nào.",
        64: "Vẽ xu hướng thời gian và số vòng khi kích thước bài tăng; đây chỉ là quan sát thực nghiệm.",
        65: "Đếm các kiểu kết thúc và xem sai số ràng buộc, kể cả các bài bị từ chối hoặc chưa hội tụ.",
        66: "Sinh lại toàn bộ hình, bảng và lịch sử bằng một lệnh để bảo đảm kết quả không được chép tay.",
        67: "Tự kiểm tra notebook có đủ mục, đủ hình, đủ bảng và đủ 68 mã NB hay chưa.",
        68: "Tóm tắt kết quả cuối cùng cùng những giới hạn cần nhớ để không diễn giải quá mức.",
    }

    def content_kind(i, bc, action):
        """Assign a human-readable role so beginners know what may be skimmed."""
        lower = action.lower()
        if "vẽ" in lower or "hình" in bc.lower():
            return "🎨 VẼ HÌNH", "Phần này dùng code để tạo hình minh họa. Bạn có thể bỏ qua code và xem hình."
        if i in {1, 2, 3, 4, 5, 66, 67, 68} or "xuất" in lower or "thiết lập" in lower or "tạo thư mục" in lower:
            return "🛠️ CÀI ĐẶT / TỔ CHỨC", "Phần này phục vụ chương trình và việc lưu kết quả, không phải bước toán học của Karmarkar."
        if i >= 60 or "[dx]" in bc.lower() or "benchmark" in lower:
            return "🧪 THỰC NGHIỆM", "Phần này chạy thử bằng máy để kiểm tra chương trình; không thay thế chứng minh toán học."
        if any(word in lower for word in ("kiểm", "thử", "đối chiếu", "so ", "tổng hợp")):
            return "✅ KIỂM TRA", "Phần này xác nhận kết quả đã tính đúng hoặc phát hiện dữ liệu sai."
        return "📘 Ý TƯỞNG / THUẬT TOÁN", "Phần này giúp hiểu thuật toán làm gì. Code chỉ là cách máy thực hiện ý tưởng đó."

    def split_io(io, check):
        """Separate the old compact Input/Output phrase into explicit beginner fields."""
        parts = [part.strip().rstrip(".") for part in io.split("→")]
        if len(parts) == 1:
            return parts[0], check.rstrip(".")
        return parts[0], parts[-1]

    def beginner_io_hints(kind):
        """Explain technical input/output names without asking readers to know Python."""
        if "VẼ HÌNH" in kind:
            return (
                "Các điểm hoặc số liệu đã được tính ở bước trước; chúng được đưa vào để đặt lên hình.",
                "Một hình minh họa. Bạn chỉ cần quan sát hình và đọc chú thích, không cần đọc lệnh vẽ.",
            )
        if "CÀI ĐẶT" in kind:
            return (
                "File, thư viện hoặc tùy chọn chương trình cần có sẵn trước khi tính toán.",
                "Một bảng, thư mục hoặc thông báo xác nhận rằng phần chuẩn bị đã hoàn tất.",
            )
        if "THỰC NGHIỆM" in kind:
            return (
                "Danh sách bài thử cùng các tùy chọn chạy; đây không phải dữ liệu bạn phải nhập bằng tay.",
                "Bảng hoặc hình thống kê được tạo từ các lần chạy thật trên máy.",
            )
        if "KIỂM TRA" in kind:
            return (
                "Kết quả vừa tính cùng điều kiện đúng dùng làm mốc so sánh.",
                "Sai số, bảng so sánh hoặc thông báo đạt/không đạt để biết bước trước có chạy đúng không.",
            )
        return (
            "Bài toán, điểm hiện tại và các nút điều chỉnh mà bước thuật toán này cần.",
            "Một hướng đi, điểm mới hoặc các con số trung gian để tiếp tục vòng Karmarkar.",
        )

    def beginner_purpose(kind):
        """Give every block a non-mathematical purpose before showing its specific story."""
        if "VẼ HÌNH" in kind:
            return "Biến các con số thành hình để người đọc nhìn ra ý chính mà không phải đọc công thức."
        if "CÀI ĐẶT" in kind:
            return "Chuẩn bị môi trường, dữ liệu hoặc nơi lưu kết quả để các phần sau chạy ổn định và có thể kiểm tra lại."
        if "THỰC NGHIỆM" in kind:
            return "Chạy thử trên nhiều tình huống để quan sát chương trình hoạt động ra sao trong thực tế."
        if "KIỂM TRA" in kind:
            return "Phát hiện sớm kết quả sai bằng cách so với một điều kiện hoặc kết quả đã biết."
        return "Giải thích hoặc thực hiện một bước giúp Karmarkar tìm phương án tốt dần mà vẫn tuân thủ các điều kiện."

    def block(i,bc,ms,action,why,io,check,code,after):
        """[MS 5.1,5.2] Explain every code block for a reader with no coding background."""
        ident=f"NB{i:02}"
        kind, kind_note = content_kind(i, bc, action)
        input_note, output_note = split_io(io, check)
        input_hint, output_hint = beginner_io_hints(kind)
        purpose_hint = beginner_purpose(kind)
        simple = simple_explanations[i]
        cells.append(nbf.v4.new_markdown_cell(
            f"### {ident} · {kind} · {bc}\n\n"
            f"> **Vị trí trong tài liệu:** BC {bc}; MasterSpec {ms}, §5.2 ({ident}).\n\n"
            f"**Mục đích / Vì sao cần (nói ngắn gọn):** {purpose_hint}\n\n"
            f"**Cách hiểu đơn giản:** {simple}\n\n"
            f"**Loại nội dung:** {kind_note}\n\n"
            f"**Input — dữ liệu đưa vào (tên dùng trong code/PDF):** {input_note}.  \n"
            f"*Hiểu đơn giản:* {input_hint}\n\n"
            f"**Đang làm gì — máy sẽ xử lý:** {action}\n\n"
            f"**Output — kết quả nhận được (tên dùng trong code/PDF):** {output_note}.  \n"
            f"*Hiểu đơn giản:* {output_hint}\n\n"
            f"**Input/Output:** đã được tách riêng ở hai dòng trên để dễ theo dõi.\n\n"
            f"**Nếu chỉ nhớ một ý:** {simple}\n\n"
            "<details><summary>Dấu hiệu kỹ thuật để kiểm tra — có thể bỏ qua ở lần đọc đầu</summary>\n\n"
            f"**Lý do kỹ thuật của bước này:** {why}\n\n"
            f"**Cần nhìn kết quả nào:** {check}\n\n</details>\n\n"
            "🧑‍💻 **Nếu bạn không học code:** có thể bỏ qua ô code ngay bên dưới, xem kết quả rồi đọc phần kết luận."
        ))
        cell=nbf.v4.new_code_cell(f"# {ident} | BC {bc} | MasterSpec {ms}, section 5.2\n{code.strip()}\n")
        cell.metadata["tags"]=[ident,"BC:"+bc.split()[0]]
        cells.append(cell)
        cells.append(nbf.v4.new_markdown_cell(
            f"#### Kết luận dễ hiểu sau {ident}\n\n"
            f"**Điều cần nhớ:** {simple}\n\n"
            "<details><summary>Ghi chú kỹ thuật — chỉ cần mở khi muốn xem sâu hơn</summary>\n\n"
            f"**Dấu hiệu kiểm tra:** {check}\n\n{after}\n\n</details>"
        ))

    heading("A. Chuẩn bị chương trình — chưa phải phần thuật toán","Biết máy đang dùng thư viện nào, các nút điều chỉnh được đặt ra sao và kết quả sẽ được lưu ở đâu.")
    block(1,"Dẫn nhập, trang 33–34","C01/C12","Đọc phiên bản thư viện thực tế.","Để người khác tái lập môi trường.","Python và các thư viện → bảng phiên bản.","Phiên bản được lấy từ môi trường đang chạy, không nhập tay.",'''
from pathlib import Path
from dataclasses import replace
from io import BytesIO
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from IPython.display import display, Image
from karmarkar import *
from karmarkar import plotting as plots
from karmarkar.io import load_config, environment_manifest, write_json, plain
from karmarkar.reporting import show_step_table, example_history, methods_table, export_example_artifacts, audit_project
from karmarkar.experiments import dataset_cases, run_benchmark, solve_reference_with_highs
ROOT = Path.cwd()
if ROOT.name == 'notebooks':
    ROOT = ROOT.parent
assert (ROOT / 'pyproject.toml').is_file(), 'Run from project root or notebooks/'
display(pd.DataFrame(environment_manifest()['versions'].items(), columns=['Thư viện','Phiên bản']))
''',"Phiên bản là một phần của bằng chứng thực thi; kết quả thời gian phụ thuộc máy và thư viện.")
    block(2,"4.3.1","C01/C12","Đọc cấu hình YAML.","Không đổi alpha hoặc tolerance ngầm giữa các bước.","configs/default.yaml → SolverConfig và seed.","alpha=0.25; epsilon là ngưỡng của w=cᵀu, khác z=2w.",'''
config, raw_config = load_config(ROOT / 'configs/default.yaml')
display(pd.DataFrame(plain(config).items(), columns=['Tùy chọn','Giá trị']))
print('seed =', raw_config['seed'], '; epsilon áp dụng cho w=z/2')
''',"Các lần chạy thay cấu hình sẽ dùng `replace(config, ...)` để cấu hình gốc giữ nguyên và thay đổi hiển thị rõ.")
    block(3,"4.5.3 [DX]","C12","Tạo thư mục đầu ra.","Lưu hình/bảng vào đường dẫn tương đối, tái lập được.","ROOT → OUT/figures, OUT/tables, OUT/traces.","Ba thư mục tồn tại.",'''
OUT = ROOT / 'outputs'
for folder in ['figures','tables','traces']:
    (OUT / folder).mkdir(parents=True, exist_ok=True)
display(pd.DataFrame({'Thư mục': ['outputs/'+s for s in ['figures','tables','traces']], 'Tồn tại':[True]*3}))
''',"Thư mục được tạo bởi chương trình; không phụ thuộc đường dẫn cá nhân trên máy người viết.")
    block(4,"Cách đọc hình; 4.1","C10/C12","Thiết lập màu và hàm hiển thị hình.","Miền, hướng và điểm dùng một quy ước xuyên suốt.","Palette và Matplotlib Figure → PNG/SVG cùng hình hiển thị.","Chú giải màu, không lẫn tọa độ gốc với hệ xạ ảnh.",'''
display(pd.DataFrame(plots.set_style().items(), columns=['Vai trò','Màu']))
def show(fig, stem=None):
    # [BC Figures 4.1-4.8 | MasterSpec C10] Display exact saved figure.
    if stem:
        plots.save_figure(fig, OUT / 'figures', stem)
    buffer = BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    display(Image(data=buffer.getvalue()))
    plt.close(fig)
''',"Xanh nhạt là miền khả thi; xanh đậm là điểm hiện tại; đỏ là điểm tiếp; xanh lục là hướng.")
    block(5,"Dẫn nhập; 4.1–4.5","C12","Hiển thị bản đồ nguồn.","Phần thực nghiệm là bổ sung, không đổi cấu trúc báo cáo.","Năm mục BC → bảng nguồn và phạm vi.","4.4 là ví dụ; 4.5 là nhận xét, không phải benchmark có sẵn.",'''
display(pd.DataFrame({'Mục':['4.1','4.2','4.3','4.4','4.5','[DX]'], 'Nội dung':['Quan sát hình học','Cơ sở toán học','Thuật toán','Ví dụ hình học/Karmarkar','Nhận xét và giới hạn','Mã máy/thực nghiệm bổ sung']}))
''',"Báo cáo nguồn chưa có số liệu chạy máy. Các bảng thực nghiệm cuối notebook phải do chương trình thực sự chạy.")

    heading("B. Nhìn bài toán bằng hình vẽ — BC 4.1","Nhận ra vùng nào được phép chọn và vì sao đỉnh A là phương án tốt nhất, chưa cần dùng thuật toán Karmarkar.")
    block(6,"4.1.1; (4.1)","C03/C10","Xác định miền bằng lưới và ràng buộc.","Hiểu miền trước khi tính hướng đi.","Lưới (x1,x2) → mặt nạ khả thi.","Chỉ các điểm x1,x2≥0, x1+x2≤2 được chọn.",'''
grid = np.linspace(-.25,2.25,101)
X1,X2 = np.meshgrid(grid,grid)
mask = (X1>=0)&(X2>=0)&(X1+X2<=2)
display(pd.DataFrame({'Tổng điểm':[mask.size], 'Điểm khả thi':[int(mask.sum())]}))
''',"Mặt nạ là phép giao các nửa mặt phẳng; hình ở cell tiếp theo biểu diễn chính miền liên tục đó.")
    block(7,"4.1.1; Hình 4.1","C10","Vẽ miền, hai đường mức và −∇z.","Xác định đúng dấu hướng giảm.","z=0.6,1.4 → figure_4_1.","Đường mức x1=1.4 và 0.6; hướng giảm sang phải.","show(plots.plot_figure_4_1(), 'figure_4_1')","Đường mức cuối còn tiếp xúc miền đi qua A. Mũi tên biểu diễn giảm z, không phải phép lặp Karmarkar trong hệ mới.")
    block(8,"4.1.1; 4.4.2; Bảng 4.1","C09","Tính mục tiêu tại ba đỉnh.","Tạo mốc kiểm tra độc lập với solver.","O,A,B → bảng x1,x2,z.","z(O),z(A),z(B)=2,0,2.",'''
vertices = pd.DataFrame({'vertex':['O','A','B'],'x1':[0.,2.,0.],'x2':[0.,0.,2.]})
vertices['z'] = 2-vertices.x1
display(vertices)
assert vertices.z.tolist()==[2,0,2]
''',"Nghiệm hình học duy nhất là A=(2,0), z*=0. Đây là kết quả của bài toán hai biến cụ thể.")
    block(9,"4.1.2; (4.44)","C09","Thêm biến bù và thử đổi tọa độ hai chiều.","Hiểu nguồn gốc tọa độ thứ ba.","Ba điểm gốc → u → điểm gốc.","Round-trip đúng và sum(u)=1.",'''
points = [(0.,0.),(2.,0.),(.5,.5)]
display(pd.DataFrame([{'x':x,'u':original_to_u(*x),'đổi_ngược':u_to_original(original_to_u(*x))} for x in points]))
for x in points:
    np.testing.assert_allclose(u_to_original(original_to_u(*x)),x)
''',"u3=s/2 biểu diễn phần dư. Đây là chuẩn hóa tuyến tính kèm biến bù, khác phép xạ ảnh lặp lại mỗi vòng.")
    block(10,"4.1.2; Hình 4.2","C10","Vẽ hai cách biểu diễn cùng miền.","Theo dõi tương ứng O↔e3, A↔e1, B↔e2.","Tam giác gốc và Δ3 → figure_4_2.","Điểm tâm trong hệ chuẩn là e/3.","show(plots.plot_figure_4_2(), 'figure_4_2')","Tam giác trên giấy có thể khác hướng, nhưng sự tương ứng giữa đỉnh và tọa độ phải giữ đúng.")
    block(11,"4.1.3","C10","Hiển thị năm nhịp hình học.","Nối trực giác với sáu bước điều phối của Thuật toán 4.1.","Điểm → tâm → chiếu → quả cầu → đổi ngược.","Phân biệt thao tác hình học với bước kiểm tra/dừng.",'''
fig,ax=plt.subplots(figsize=(12,2.3))
labels=['Điểm khả thi x','Xạ ảnh về tâm','Chiếu hướng Dc','Bước trong cầu','Xạ ảnh ngược']
for j,label in enumerate(labels):
    ax.text(j,.5,label,ha='center',va='center',bbox=dict(boxstyle='round,pad=.5',fc='#dceef7',ec='#174a73'))
    if j<4:
        ax.annotate('',(j+.65,.5),(j+.35,.5),arrowprops={'arrowstyle':'->'})
ax.set(xlim=(-.6,4.6),ylim=(0,1));ax.axis('off')
show(fig,'overview_4_1_3')
''',"Năm thao tác này là lõi hình học; phần điều phối bổ sung đánh giá hàm thế, mục tiêu và trạng thái dừng.")

    heading("C. Các công cụ Karmarkar cần dùng — BC 4.2","Hiểu bằng hình dung ba việc: đổi cách nhìn, giữ hướng đi không phá điều kiện và giới hạn bước để điểm mới vẫn an toàn. Không cần thuộc công thức ở lần đọc đầu.")
    block(12,"4.2.1; (4.2)–(4.6)","C01/C02","Tạo dữ liệu chuẩn của ví dụ.","Không nhầm A rỗng với mảng một chiều.","A shape (0,3), c → CanonicalLP.","m=0 hợp lệ; u có ba tọa độ.",'''
problem = report_example_lp()
center,r,R = simplex_geometry(3)
display(pd.DataFrame({'A.shape':[problem.A.shape],'c':[problem.c], 'n':[3],'m':[0],'a0':[center]}))
''',"Điều kiện tổng bằng 1 được thêm riêng vào B; A không chứa lại hàng eᵀ.")
    block(13,"4.2.1; (4.7)–(4.8)","C02","Kiểm tra giả thiết dạng chuẩn.","Không dùng định lý khi chưa kiểm tra tiền điều kiện.","problem, config → ValidationReport.","Nonnegativity PROVEN và zero witness (1,0,0) khả thi.","validation = validate_canonical(problem,config)\ndisplay(pd.DataFrame(plain(validation).items(),columns=['Kiểm tra','Giá trị']))","c≥0 chứng minh cᵀu≥0 trên đơn giác; một nghiệm khả thi với mục tiêu 0 xác lập ngữ cảnh tối ưu 0 trong sai số kiểm tra đã công bố.")
    block(14,"4.2.1; 4.3.1","C02","Thử ba dữ liệu sai.","Lỗi phải được trả rõ thay vì tiếp tục tính log hoặc nghịch đảo.","Sai shape, Ae≠0, NaN → báo lỗi.","Cả ba đều INVALID_INPUT.",'''
bad_cases = [CanonicalLP(np.zeros(3),np.ones(3),'shape'), CanonicalLP(np.array([[1.,0.,0.]]),np.ones(3),'Ae'), CanonicalLP(np.empty((0,3)),np.array([0.,np.nan,1.]),'NaN')]
display(pd.DataFrame([{'case':p.name,'status':solve_karmarkar(p).status.value,'issues':validate_canonical(p,config).errors} for p in bad_cases]))
''',"Từ chối dữ liệu sai là một phần của thuật toán phần mềm; không tự chuẩn hóa LP tổng quát chưa được hỗ trợ.")
    block(15,"4.2.2; (4.9)–(4.12)","C03","Tính trọng tâm và hai bán kính.","n là số tọa độ của đơn giác, không phải số chiều hình vẽ.","n=2,3,4 → a0,r,R,R/r.","R/r=n−1.",'''
display(pd.DataFrame([{'n':n,'a0':simplex_geometry(n)[0],'r':simplex_geometry(n)[1],'R':simplex_geometry(n)[2],'R/r':simplex_geometry(n)[2]/simplex_geometry(n)[1]} for n in [2,3,4]]))
''',"Bán kính được đo theo metric Euclid trong siêu phẳng tổng tọa độ bằng 1; quả cầu nhỏ bảo đảm không chạm mặt xi=0.")
    block(16,"4.2.2; Hình 4.3","C03/C10","Vẽ hai đường tròn theo embedding trực chuẩn.","Giữ đúng tỷ lệ khoảng cách r và R.","Δ3, r=1/√6, R=√(2/3) → figure_4_3.","R/r=2; vòng trong tiếp xúc cả ba cạnh.","show(plots.plot_figure_4_3(), 'figure_4_3')","Một mặt của đơn giác cách tâm r; mọi đỉnh cách tâm R. Hình dùng đẳng cự nên tỷ lệ có ý nghĩa toán học.")
    block(17,"4.2.3; (4.13)–(4.14)","C05","Tạo B,v và kiểm tra Bv.","Vectơ mục tiêu thường không bảo toàn đẳng thức.","B=eᵀ, v=(0,1,2) → Bv.","Bv khác 0, nên cần phép chiếu.","B_demo=np.ones((1,3)); v_demo=np.array([0.,1.,2.])\ndisplay({'B':B_demo,'v':v_demo,'B@v':B_demo@v_demo})","Hướng d phải nằm trong Ker B để eᵀd=0 và Ad=0; lấy ngay −v có thể phá vỡ ràng buộc.")
    block(18,"4.2.3; (4.15)–(4.17); Hình 4.4","C05/C10","Chiếu v và minh họa trực giao.","Loại thành phần vuông góc với không gian hướng.","B,v → p và residuals.","Bp≈0; v−p trực giao không gian kernel.",'''
p_demo, projection_info=project_to_kernel(B_demo,v_demo)
display({'p':p_demo,'B@p':B_demo@p_demo,**projection_info})
show(plots.plot_figure_4_4(),'figure_4_4')
''',"Hình 4.4 là sơ đồ 2D; số v,p vừa in là ví dụ 3D. Hướng đơn vị giảm hàm tuyến tính phụ là −p/‖p‖ khi p khác 0.")
    block(19,"4.2.3; trang in 41","C05","Thử SVD với hàng ràng buộc phụ thuộc.","Nghịch đảo BBᵀ có thể không tồn tại.","B có hàng lặp → rank,nullity,residual.","Chiếu thành công mà không dùng inv(BBᵀ).",'''
B_dep=np.array([[1.,-1.,0.],[2.,-2.,0.],[1.,1.,1.]])
p_dep,dep_info=project_to_kernel(B_dep,v_demo)
display({'p':p_dep,**dep_info})
''',"Hạng được xác định bằng cutoff SVD có co giãn theo singular value lớn nhất; các trường hợp gần suy biến cần đọc cả residual và cutoff.")
    block(20,"4.2.4; (4.19)–(4.21)","C04","Thử hai điểm với cùng mốc a.","Không biến mỗi điểm bằng chính nó làm mốc.","a=(1/2,1/4,1/4), b=(2/3,1/6,1/6) → Tₐ(a),Tₐ(b).", "Tₐ(a)=e/3; Tₐ(b)=a khác e/3.",'''
a=np.array([.5,.25,.25]); b=np.array([2/3,1/6,1/6])
display({'a':a,'b':b,'T_a(a)':to_projective(a,a),'T_a(b)':to_projective(a,b)})
''',"Phép đổi hệ tọa độ giữ đỉnh và từng mặt; điểm mốc về trọng tâm nhưng các điểm khác thay đổi theo cùng một ánh xạ.")
    block(21,"4.2.4; (4.20)","C04","Đổi ngược điểm b.","Kiểm tra ánh xạ nghịch đảo độc lập.","a,Tₐ(b) → b phục hồi.","Sai số round-trip gần 0.","b_back=from_projective(a,to_projective(a,b))\ndisplay({'b_back':b_back,'error_norm':np.linalg.norm(b_back-b)})","Mốc a phải cố định trong cả phép thuận và nghịch; sang vòng mới, a sẽ đổi theo nghiệm hiện tại.")
    block(22,"4.2.4; Hình 4.5","C04/C10","Vẽ hai hệ xạ ảnh.","Theo dõi đồng thời a,b và một lưới điểm.","Mốc cố định a → figure_4_5.","Chỉ a về tâm; b vẫn ở vị trí riêng.","show(plots.plot_figure_4_5(a), 'figure_4_5')","Đây là cách biểu diễn mới của các điểm trong đơn giác; không phải phép quay, tịnh tiến hay phép đồng dạng.")
    block(23,"4.2.4; (4.22)–(4.23)","C04/C06","Đối chiếu mục tiêu phân tuyến tính.","Không nhầm hệ số phụ Dc với mục tiêu gốc sau đổi tọa độ.","x=b; y=Tₐ(b); c → hai giá trị mục tiêu.","cᵀx=(Dc)ᵀy/(eᵀDy), thường khác (Dc)ᵀy.",'''
y_b=to_projective(a,b)
display({'original':problem.c@b, 'fractional':(a*problem.c)@y_b/(a@y_b), 'linear_surrogate':(a*problem.c)@y_b})
''',"Hàm tuyến tính phụ được tối thiểu trên quả cầu để chọn bước. Sự tiến triển của thuật toán được phân tích bằng hàm thế, không suy ra chỉ từ việc giảm tử số.")
    block(24,"4.2.5; (4.24)–(4.28)","C05/C07","Tính bước mẫu trên quả cầu.","Dùng Cauchy–Schwarz để chọn hướng tối thiểu tuyến tính phụ.","problem, center, alpha → B,p,d,y.","Bd≈0; ‖d‖≈1; (Dc)ᵀh≥−αr‖p‖.",'''
demo_step=karmarkar_step(problem,center,config)
display(show_step_table(demo_step))
assert np.linalg.norm(demo_step.B@demo_step.d)<1e-12
''',"Với h thuộc Ker B, (Dc)ᵀh=pᵀh≥−‖p‖‖h‖. Chọn h=−αrp/‖p‖ đạt dấu bằng và vẫn nằm trong đơn giác.")
    block(25,"4.2.5; Hình 4.6","C07/C10","Vẽ bước thật trong quả cầu.","Thấy αr<r giữ tọa độ dương.","demo_step → figure_4_6.","Điểm y nằm trên đường tròn αr, bên trong đường tròn r.","show(plots.plot_figure_4_6(demo_step), 'figure_4_6')","Quả cầu giữ tính dương; phép chiếu giữ ràng buộc đẳng thức. Hai điều kiện đều cần thiết.")
    block(26,"4.2.6; (4.29)–(4.31)","C06","Tính hai hàm thế với D cố định.","Bất biến hiệu không có nghĩa giá trị tuyệt đối bằng nhau.","a,y,c → Phi(x), Phi_tilde(y), hằng số.","Phi(x)−Phi_tilde(y)=−Σln(ai).",'''
y0=center.copy(); y1=np.array([.4,.3,.3]); x0=from_projective(a,y0); x1=from_projective(a,y1)
display({'Phi(x1)':potential(x1,problem.c),'Phi_tilde(y1)':transformed_potential(a,y1,problem.c),
         'offset':-np.log(a).sum()})
''',"Khi thay x=Dy/(eᵀDy), các số hạng chứa n ln(eᵀDy) triệt tiêu. Chỉ còn hằng số phụ thuộc mốc a.")
    block(27,"4.2.6; Mệnh đề 4.2.5","C06","Kiểm tra hiệu hàm thế.","Theo dõi tiến triển qua hai hệ tọa độ.","Hai điểm tương ứng cùng D → delta_old,delta_new.","Sai số chênh lệch dưới tolerance.",'''
delta_old=potential(x1,problem.c)-potential(x0,problem.c)
delta_new=transformed_potential(a,y1,problem.c)-transformed_potential(a,y0,problem.c)
display({'delta_original':delta_old,'delta_transformed':delta_new,'error':abs(delta_old-delta_new)})
assert abs(delta_old-delta_new)<1e-12
''',"Hằng số −Σln(ai) bị khử khi lấy hiệu trong cùng vòng. Không so các hệ có D khác nhau mà bỏ qua mốc.")
    block(28,"4.2.7; (4.32)","C06/C08","So mức giảm mẫu với 1/8.","Đánh dấu rõ phạm vi áp dụng định lý.","demo_step → mức giảm và thông tin giả thiết.","Giảm ln(10/7)≈0.356675>1/8 trong ví dụ.",'''
decrease=demo_step.phi_before-demo_step.phi_after
display({'decrease':decrease,'threshold':1/8,'alpha':config.alpha,'nonnegative':validation.nonnegative.value,'zero_optimum_witness_checked':validation.zero_optimum_known})
''',"Định lý nguồn phát biểu mức giảm hoặc nhận diện cực tiểu dương dưới các giả thiết/thủ tục gốc. Trong float64, một lần kiểm tra thất bại chỉ là diagnostic, không phải chứng nhận cực tiểu dương.")
    block(29,"4.2.8; (4.33)–(4.36)","C06/C10","Vẽ cận ký hiệu của log tỷ số mục tiêu.","Phân biệt cận số vòng với thời gian chạy mã.","n=3, δ=1/8, k → ln(n)−kδ/n.","Hình chỉ minh họa cận lý thuyết có giả thiết.",'''
kk=np.arange(121)
fig,ax=plt.subplots(figsize=(7,3.5))
ax.plot(kk,np.log(3)-kk/(8*3),label='Cận ln(n)−kδ/n, n=3, δ=1/8')
ax.set(xlabel='k',ylabel='Cận log tỷ số mục tiêu',title='BC (4.34) • Minh họa có giả thiết')
ax.legend();show(fig,'theoretical_iteration_bound')
''',r"Từ $\ln(c^Tx^k/c^Ta_0)\le\ln n-k\delta/n$, đạt tỷ số $2^{-q}$ sau $O(n(q+\ln n))$ vòng trong mô hình nguồn. Cận $O(n^{3.5}L)$ phép toán được dẫn cho phiên bản cải tiến, không phải chứng minh runtime của mã SVD này. Nghiệm hữu tỉ chính xác còn cần thủ tục cực biên/chứng nhận riêng.")

    heading("D. Một vòng Karmarkar diễn ra thế nào — BC 4.3","Ghép các công cụ ở phần trước thành một quy trình: chuẩn bị dữ liệu, tìm hướng hợp lệ, đi một bước, đổi về tọa độ gốc rồi kiểm tra kết quả.")
    block(30,"4.3.1","C01/C02","Khóa dữ liệu và giả thiết.","Xác định rõ điều kiện trước khi chạy solver.","problem, config → input/validation.","Ae=0; a0>0; cᵀa0>0; alpha=1/4.","display({'A':problem.A,'c':problem.c,'center':center,'alpha':config.alpha,'validation':plain(validation)})","Chọn e/n làm điểm đầu chỉ hợp lệ cho dữ liệu đã chuẩn hóa và có Ae=0.")
    block(31,"4.3.2; (4.37)","C07","In D,B,v từ bước thực.","Theo dõi AD thay vì A trong hệ mới.","demo_step → ba ma trận/vectơ.","B=[AD;eᵀ], v=Dc.","display({'x':demo_step.x_before,'D':demo_step.D,'B':demo_step.B,'v':demo_step.v})","Ma trận D được lập lại từ điểm hiện tại mỗi vòng; với ví dụ ban đầu D0=I/3.")
    block(32,"4.3.2; (4.38)–(4.39)","C05/C07","Kiểm p,d và các chuẩn.","Không chuẩn hóa khi p bằng 0 hoặc quá nhỏ.","demo_step → p,d,Bp,Bd,‖d‖.","‖d‖=1; Bp,Bd≈0.","display({'p':demo_step.p,'d':demo_step.d,'Bp':demo_step.B@demo_step.p,'Bd':demo_step.B@demo_step.d,'norm(d)':np.linalg.norm(demo_step.d)})","SVD xử lý hàng phụ thuộc; nullspace rỗng và p quá nhỏ được đưa về trạng thái riêng, không tự gọi là tối ưu.")
    block(33,"4.3.2; (4.40)–(4.41)","C04/C07","Theo dõi y và x_next.","Không dùng tọa độ mới làm nghiệm gốc cho mọi vòng.","D,y → mẫu số, x_next.","Mẫu số dương, x_next=Dy/sum(Dy).", "display({'y':demo_step.y,'D@y':demo_step.D@demo_step.y,'denominator':demo_step.diagnostics['denominator'],'x_next':demo_step.x_after})","Ở vòng đầu D0 có các phần tử bằng nhau nên phép đổi ngược triệt tiêu hệ số chung. Sự trùng số giữa y và x_next không đúng cho mọi vòng.")
    block(34,"4.3.2; Mệnh đề 4.3.1","C07","In bảng bất biến và hàm thế.","Kiểm cả tính dương, tổng tọa độ và đẳng thức.","StepRecord → bảng diagnostics.","Residual nhỏ; bước αr; mục tiêu và Phi được ghi riêng.","display(show_step_table(demo_step,include_matrices=False))","Đây là kiểm chứng số trong tolerance; chứng minh toán học dùng ADa0=0, Bd=0 và αr<r, rồi dùng mẫu số dương của phép đổi ngược.")
    block(35,"4.3.3; Thuật toán 4.1","C08","Chạy solver 20 vòng thực.","Tạo trace để đối chiếu công thức và hình.","max_iter=20 → source_run20.","20 bước và MAX_ITERATIONS vì chưa đạt epsilon.",'''
source_run20=solve_karmarkar(problem,replace(config,max_iter=20))
display({'iterations':source_run20.iterations,'status':source_run20.status.value,'w':source_run20.objective,'z':2*source_run20.objective})
history20=example_history(source_run20)
display(history20.tail())
''',"MAX_ITERATIONS không phải lỗi toán học hay thành công gần tối ưu; nó nói đúng rằng ngân sách này chưa đạt ngưỡng đã đặt.")
    block(36,"4.3.4; Hình 4.7","C10","Vẽ sơ đồ sáu bước điều phối.","Đối chiếu code với Thuật toán 4.1.","Thứ tự thực thi → figure_4_7.","Đánh giá xong mới quay lại vòng tiếp.","show(plots.plot_figure_4_7(),'figure_4_7')","Năm thao tác hình học và sáu bước điều phối là hai cách mô tả cùng thuật toán; bước đánh giá/dừng thuộc bộ điều phối.")
    block(37,"4.3.5","C02/C08","Thử các trạng thái kết thúc.","Tách không có hướng, không đủ ngân sách và dừng gần đúng.","Ba bài/cấu hình → bảng status.","Không có trạng thái OPTIMAL trong core.",'''
no_move=CanonicalLP(np.array([[1.,-1.]]),np.array([0.,1.]),'singleton')
status_runs=[solve_karmarkar(no_move,config), source_run20, solve_karmarkar(problem,replace(config,epsilon=.05))]
display(pd.DataFrame([{'status':r0.status.value,'iterations':r0.iterations,'objective':r0.objective,'message':r0.message} for r0 in status_runs]))
''',"p=0, kernel rỗng hoặc p gần 0 không cho phép tự kết luận optimum 0. Đạt epsilon cũng chỉ là ngưỡng gần đúng trong ngữ cảnh đã xác minh.")

    heading("E. Theo dõi một ví dụ từ đầu đến cuối — BC 4.4","Xem một điểm được cải thiện qua từng vòng cho tới khi tiến gần đỉnh tốt nhất. Phần này luôn đổi kết quả về hai biến gốc để bạn dễ nhìn trên hình.")
    block(38,"4.4.1; (4.42)","C09","Hiển thị đề bài gốc.","Đọc bài trước khi xem kết quả chuẩn hóa.","Mô hình → mục tiêu và ràng buộc.","min z=2−x1, x1+x2≤2, x1,x2≥0.","display(pd.DataFrame({'Thành phần':['Mục tiêu','Ràng buộc 1','Ràng buộc 2,3'],'Biểu thức':['min z=2−x1','x1+x2≤2','x1≥0; x2≥0']}))","Miền compact nên có nghiệm tối ưu. Hình học cho nghiệm tại A, làm mốc kiểm tra thuật toán.")
    block(39,"4.4.2; hình không đánh số","C10","Vẽ ba đường biên và chiều nửa mặt phẳng.","Tái hiện cả hình không mang số 4.x.","Miền OAB → geometry_4_4_2.","A=(2,0) là đỉnh tối ưu.","show(plots.plot_original_geometry(),'geometry_4_4_2')","Ba mũi tên chọn phía thỏa từng ràng buộc; giao ba phía cho miền tam giác.")
    block(40,"4.4.2; Bảng 4.1; (4.43)","C09/C12","Xuất bảng đỉnh.","Giữ bảng gốc tách khỏi dữ liệu thực nghiệm.","vertices → table_4_1_vertices.csv.","Giá trị z=2,0,2.","display(vertices)\nvertices.to_csv(OUT/'tables/table_4_1_vertices.csv',index=False,encoding='utf-8-sig')","Chỉ A có giá trị 0; hàm tuyến tính đạt cực tiểu trên một mặt, ở đây mặt tối ưu chỉ có một đỉnh.")
    block(41,"4.4.3; (4.44)","C09","Tính biến bù và tọa độ u.","Bảo toàn miền qua chuẩn hóa.","(x1,x2)=(2/3,2/3) → s,u.","s=2/3, u=e/3.","s=2-2/3-2/3\nu_demo=original_to_u(2/3,2/3)\ndisplay({'s':s,'u':u_demo,'sum(u)':u_demo.sum()})","Mỗi tọa độ u là trọng số của một đỉnh đơn giác; u3 ứng với đỉnh O của miền gốc.")
    block(42,"4.4.3; (4.45)–(4.46)","C09","Đối chiếu z=2w tại ba điểm.","Không bỏ mất hệ số 2 khi so báo cáo.","Ba điểm gốc → z,w,2w.","z và 2w trùng nhau.",'''
display(pd.DataFrame([{'x':x,'z':2-x[0],'w':problem.c@original_to_u(*x),'2w':2*problem.c@original_to_u(*x)} for x in points]))
''',"Nhân mục tiêu với hằng số dương giữ tập nghiệm tối ưu. Ngưỡng epsilon của solver áp dụng cho w; công thức (4.57) trong báo cáo áp dụng cho z.")
    block(43,"4.4.4; (4.47)–(4.48)","C03/C05","Lập ma trận chiếu cụ thể 3×3.","Đối chiếu phép chiếu tổng quát với công thức của ví dụ.","e → P3=I−eeᵀ/3.","P3²=P3, P3e=0.",'''
P3=np.eye(3)-np.ones((3,3))/3
display({'a0':center,'alpha':config.alpha,'r':r,'P3':P3,'idempotence_error':np.linalg.norm(P3@P3-P3)})
''',"Đây là trường hợp riêng B=eᵀ. Không dùng riêng P3 thay cho SVD khi A có ràng buộc bổ sung.")
    block(44,"4.4.5; (4.49)–(4.51)","C07/C09","Chạy vòng k=0 với đầy đủ ma trận.","Tái lập p0,d0,y0,u1 bằng code thực.","u0=e/3 → StepRecord.","p0=(−2,1,1)/9; u1=(10,7,7)/24.",'''
step0=karmarkar_step(problem,center,config,k=0)
display(show_step_table(step0))
np.testing.assert_allclose(step0.x_after,np.array([10,7,7])/24,atol=1e-12)
''',"u1 tăng, u2 và u3 giảm; cả ba vẫn dương. D0=I/3 khiến xạ ảnh ngược không thay các con số của y0.")
    block(45,"4.4.5; sau (4.51)","C09","Đổi lại tọa độ gốc sau vòng 1.","Kiểm kết quả z và vị trí trên miền OAB.","u1 → (x1,x2),z.","(5/6,7/12), z=7/6.","display({'x_original':u_to_original(step0.x_after),'z':2*problem.c@step0.x_after})","z ban đầu 4/3 giảm thành 7/6; không nhầm w=7/12 với mục tiêu gốc z.")
    block(46,"4.4.6; (4.52)","C07/C09","Tính vòng k=1 từ u1 thực.","Mốc xạ ảnh mới đã lệch trọng tâm.","step0.x_after → step1.","p1=(7/72)(−2,1,1).",'''
step1=karmarkar_step(problem,step0.x_after,config,k=1)
display(show_step_table(step1))
np.testing.assert_allclose(step1.p,7*np.array([-2,1,1])/72,atol=1e-12)
''',"D1 không còn là bội của ma trận đơn vị; bỏ phép đổi ngược từ vòng này sẽ cho kết quả sai.")
    block(47,"4.4.6; (4.52)","C04/C07/C09","In y1,D1y1 và u2 sau chuẩn hóa nghịch đảo.","Thấy cùng số y nhưng khác hệ tọa độ.","Mốc u1 và y1 → u2.","u2=(100,49,49)/198, khác y1.",'''
display({'y1':step1.y,'D1@y1':step1.D@step1.y,'u2':step1.x_after,'z2':2*problem.c@step1.x_after})
np.testing.assert_allclose(step1.x_after,np.array([100,49,49])/198,atol=1e-12)
''',"Nhân theo mốc rồi chia tổng cho u2; y1 trùng số với y0 chỉ vì tính đối xứng của ví dụ, không phải nghiệm gốc đứng yên.")
    block(48,"4.4.7; (4.53)","C07/C09","Chạy vòng k=2.","Hoàn tất ba bước tính tay của nguồn.","u2 thực → step2,u3,z3.","u3=(1000,343,343)/1686; z3=686/843.",'''
step2=karmarkar_step(problem,step1.x_after,config,k=2)
display(show_step_table(step2))
np.testing.assert_allclose(step2.x_after,np.array([1000,343,343])/1686,atol=1e-12)
''',"Hướng chuẩn hóa vẫn (2,−1,−1)/√6 trong ví dụ đối xứng. Không suy ra hướng bất biến cho LP bất kỳ.")
    block(49,"4.4.8; (4.54)–(4.55)","C09","Tính nghiệm đóng theo k bằng dạng ổn định.","Tránh tràn số 10^k khi k lớn.","t=(0.7)^k → u=(1,t,t)/(1+2t).", "Các k=0,1,2,3,10,20.","display(pd.DataFrame([{'k':k,'u_closed':analytic_u(k),'z_closed':analytic_objective(k)} for k in [0,1,2,3,10,20]]))","Khi k tăng, t→0 nên u→(1,0,0) và tọa độ gốc→(2,0). Dạng đóng là oracle độc lập, không được dùng để sinh trace solver.")
    block(50,"4.4.8; Bảng 4.2","C08/C09","So toàn bộ 20 vòng thực với oracle.","Phát hiện mã lặp sai dù vài số đầu trông hợp lý.","source_run20.trace và analytic_u → sai số.","max_error<1e−9.",'''
_,actual_points=plots.trace_arrays(source_run20)
max_error=max(np.max(np.abs(u-analytic_u(k))) for k,u in enumerate(actual_points))
display({'max_error':max_error,'tolerance':1e-9})
assert max_error<1e-9
''',"Lịch sử được tạo bởi solver trước, sau đó mới đối chiếu công thức. Đối chiếu không can thiệp quá trình lặp.")
    block(51,"4.4.8; Bảng 4.2","C09/C12","Xuất bảng sáu mốc từ lịch sử thực.","Tái lập Bảng 4.2 cùng residuals bổ sung [DX].", "history20 → CSV.","k=0,1,2,3,10,20 khớp số in sáu chữ số.",'''
table42=history20[history20.k.isin([0,1,2,3,10,20])]
display(table42)
table42.to_csv(OUT/'tables/table_4_2_iterations.csv',index=False,encoding='utf-8-sig')
''',"Các cột w,Phi,min_u và residual là thông tin triển khai bổ sung; ba cột x1,x2,z là số đối chiếu của báo cáo.")
    block(52,"4.4.9; Hình 4.8","C10","Vẽ các điểm lặp thực trong miền gốc.","Giữ nguồn gốc dữ liệu từ SolverResult.trace.","source_run20 → figure_4_8.","Các điểm hữu hạn nằm trong miền và tiến về A.","show(plots.plot_figure_4_8(source_run20),'figure_4_8')","Đường nối chỉ mô tả thứ tự các điểm lặp; không có bước hữu hạn nào được đặt sẵn tại nghiệm đỉnh.")
    block(53,"4.4.10; (4.56)","C06/C10","Vẽ mục tiêu và hàm thế trên hai hình riêng.","Hai đại lượng có ý nghĩa và thang đo khác nhau.","Lịch sử thực → objective_vs_iteration, potential_vs_iteration.","z→0; Phi giảm tuyến tính theo k trong ví dụ.",'''
hist_figures=plots.plot_histories(source_run20)
show(hist_figures['objective_vs_iteration'],'objective_vs_iteration')
show(hist_figures['potential_vs_iteration'],'potential_vs_iteration')
show(hist_figures['feasibility_residuals'],'feasibility_residuals')
''',"Phi có thể âm và không phải sai số mục tiêu; trong ví dụ nó giảm đều dù z giảm theo dạng phân thức của lũy thừa.")
    block(54,"4.4.10; (4.56)","C06/C09","Kiểm tra delta Phi thực.","Đối chiếu ln(7/10) và mức giảm 1/8.","history20.phi.diff() → bảng delta.","Delta≈−0.3566749439; mức giảm là đối dấu.",'''
delta_table=pd.DataFrame({'k':history20.k.iloc[1:],'delta_phi':history20.phi.diff().iloc[1:]})
delta_table['error']=delta_table.delta_phi-np.log(.7)
display(delta_table.head())
assert np.max(abs(delta_table.error))<1e-9
''',"Ở đây ΔPhi=Phi(k+1)−Phi(k)<0; lượng giảm dương là ln(10/7)>1/8. Hai cách ghi dấu phải nhất quán.")
    block(55,"4.4.10; (4.57)","C09","Tính số vòng nhỏ nhất với epsilon của z.","Kiểm cả k−1 và k thay vì chỉ thay công thức.","epsilon_z=0.1 → k_min,z(k−1),z(k).", "k=11; z10>0.1; z11≤0.1.",'''
epsilon_z=.1
k_min=minimum_example_iterations(epsilon_z)
display({'epsilon_z':epsilon_z,'k_min':k_min,'z(k-1)':analytic_objective(k_min-1),'z(k)':analytic_objective(k_min)})
assert k_min==11 and analytic_objective(10)>.1 and analytic_objective(11)<=.1
''',"Công thức chỉ dùng cho ví dụ có dạng đóng (4.54). Không dùng số vòng này để dự đoán LP khác.")
    block(56,"4.4.11; Bảng 4.3","C09/C12","Tái lập bảng so sánh hai cách giải.","So phạm vi và kết quả, không bịa thời gian chạy hình học.","Nội dung nguồn → table_4_3_methods.csv.","Hai phương pháp cùng nghiệm giới hạn; cách tiếp cận khác nhau.","display(methods_table())\nmethods_table().to_csv(OUT/'tables/table_4_3_methods.csv',index=False,encoding='utf-8-sig')","Hình học tiện cho hai biến; Karmarkar có công thức n biến ở dạng chuẩn. Bảng này không khẳng định thuật toán nào nhanh hơn.")

    heading("F. Giới hạn, kiểm tra và chạy thử — BC 4.5 và [DX]","Phân biệt điều đã thấy từ kết quả chạy máy với điều có thể khẳng định bằng lý thuyết; các bài thất bại cũng được giữ lại để báo cáo trung thực.")
    block(57,"4.5.1","C07/C09","Kiểm tọa độ nhỏ nhất ở các vòng hữu hạn.","Phân biệt điểm trong với giới hạn nằm trên biên.","Lịch sử thực → min(u).","Mọi giá trị đã chạy đều dương.","display(history20[['k','min_u']].iloc[[0,1,2,3,10,20]])\nassert np.all(actual_points>0)","u2,u3 tiến về 0 trong giới hạn; điều đó không đồng nghĩa đã bằng 0 ở một bước hữu hạn trong mô hình toán học.")
    block(58,"4.5.2","C04/C05","Đối chiếu vai trò xạ ảnh và chiếu.","Hai phép giải quyết hai khó khăn khác nhau.","Tₐ(a), Bp → bảng vai trò.","Xạ ảnh đưa về tâm; chiếu giữ đẳng thức.","display(pd.DataFrame({'Phép':['Xạ ảnh','Chiếu trực giao','Giới hạn bước'],'Vai trò':['Đưa điểm mốc về tâm để dùng cùng bán kính','Giữ hướng trong Ker[AD;eᵀ]','Giữ điểm mới trong đơn giác'],'Kiểm tra':[str(to_projective(a,a)),str(demo_step.B@demo_step.p),'alpha*r<r']}))","Cần ghép cả ba cơ chế để bảo toàn tính chấp nhận được; không thay cơ chế này bằng cơ chế kia.")
    block(59,"4.5.3","C08/C12","Hiển thị giới hạn các kết luận.","Ngăn diễn giải quá mức dữ liệu mẫu.","Bằng chứng hiện có → claims checklist.","Không chứng nhận exact optimality, complexity hay hỗ trợ LP tổng quát.","claims=pd.DataFrame({'Kết luận':['Khớp ví dụ 4.4','Chứng nhận tối ưu chính xác','Chứng minh runtime đa thức cho NumPy','Tiền xử lý LP tổng quát'],'Đã cung cấp':[True,False,False,False]})\ndisplay(claims)","Ví dụ kiểm chứng công thức, tính khả thi, hàm thế và giới hạn; phần còn lại chỉ được tuyên bố khi có thủ tục/chứng minh riêng.")
    block(60,"4.5.3 [DX]; MasterSpec 8.2","C11","Sinh các nhóm bài F1–F8 có kiểm soát.","Ví dụ A rỗng không kiểm hết nhánh AD.","Seed cố định → danh sách bài và chứng cứ giả thiết.","Có bài ràng buộc phụ, hàng phụ thuộc, cực tiểu dương, sai dữ liệu và stress.",'''
cases=dataset_cases(raw_config['seed'])
display(pd.DataFrame([{'case':p.name,'A.shape':p.A.shape,'c.shape':p.c.shape,
                      'valid':validate_canonical(p,config).valid,'zero_known':validate_canonical(p,config).zero_optimum_known} for p in cases]))
write_json(OUT/'dataset_manifest.json',{'seed':raw_config['seed'],'cases':cases})
''',"F2 có c≥0 và tọa độ chi phí 0; F3 có nghiệm biên (1/2,1/2,0,0). F7 là dữ liệu sai được giữ trong kết quả.")
    block(61,"4.5.3 [DX]; MasterSpec 8.4","C11","Chạy batch thật với trace.","Sinh số liệu thực thay vì chép bảng expected.","16 bài, 5 lần/bài → benchmark_results, traces, manifest.","Giữ nguyên mọi status, không lọc ca lỗi.",'''
benchmark_data,benchmark_summary=run_benchmark(cases,config,raw_config['repetitions'],raw_config['seed'],OUT)
display(benchmark_summary)
''',"Timer của Karmarkar chỉ bao phần gọi solver; reference chạy sau với timer riêng. Import, xuất file và vẽ hình nằm ngoài timer.")
    block(62,"4.5.3 [DX]; MasterSpec 8.3","C11","Xem đối chứng HiGHS và gọi độc lập một bài.","So cùng mục tiêu/ràng buộc, không dùng nghiệm tham chiếu sinh bước.","CanonicalLP → reference objective/status.","Source reference w*=0; Aeq=[A;eᵀ], beq=[0;1].",'''
reference=solve_reference_with_highs(problem)
display(plain(reference))
display(benchmark_data[['case','status','objective','z_ref','reference_gap','reference_status']].drop_duplicates('case'))
''',"reference_gap là khoảng cách tới kết quả HiGHS thành công, không phải chứng nhận do Karmarkar tự cung cấp. Nghiệm đỉnh và điểm trong có thể khác tọa độ dù mục tiêu gần nhau.")
    block(63,"4.5.3 [DX]; MasterSpec 8.4","C11","Tổng hợp thời gian thực và môi trường.","Một lần đo không đủ để khẳng định ưu thế tốc độ.","5 lần/bài → median/min/max/std.","Ghi rõ memory chưa đo; tolerance reference khác stopping rule của core.","display(benchmark_summary[['case','status','repetitions','median_ms','min_ms','max_ms','std_ms','reference_median_ms']])\ndisplay(environment_manifest(config,raw_config['seed']))","Thời gian chỉ là quan sát trên máy này. Hai backend và tiêu chí dừng khác nhau nên bảng không phải so sánh công bằng tuyệt đối về thuật toán.")
    block(64,"4.5.3 [DX]; MasterSpec 8.5","C10/C11","Vẽ runtime và số vòng theo n riêng.","Không trộn số vòng với chi phí mỗi vòng.","Nhóm F2 → hai hình so sánh.","Điểm dữ liệu từ benchmark thực, không diễn giải thành cận đa thức.",'''
benchmark_figs=plots.plot_benchmark(benchmark_data,benchmark_summary)
show(benchmark_figs['runtime_vs_n'],'runtime_vs_n')
show(benchmark_figs['iterations_vs_n'],'iterations_vs_n')
''',"Các đồ thị phụ thuộc SVD, kích thước, tolerance và phần ghi trace. Không suy ra O(n^3.5 L) cho mã từ bốn điểm thực nghiệm.")
    block(65,"4.5.3 [DX]; MasterSpec 8.5","C08/C11","Tổng hợp thất bại và residual.","Không chỉ báo các run hội tụ.","Toàn bộ benchmark → status histogram, residual table.","F7 bị từ chối, ca không hướng/cực tiểu dương vẫn có dòng.",'''
show(benchmark_figs['termination_statuses'],'termination_statuses')
display(benchmark_data.groupby('case')[['feas','sum_residual','min_x']].max())
''',"INVALID_INPUT là kết quả mong đợi của dữ liệu sai; MAX_ITERATIONS và uncertainty phải được đọc theo từng bài, không đổi thành thành công.")
    block(66,"4.1–4.5 [GD/DX]; MasterSpec 7.2","C12","Tái sinh toàn bộ bộ hình/bảng nguồn.","Bảo đảm output có thể được tạo lại từ một lệnh.","config → 8 hình, 3 bảng, JSON trace, history.","Các file có dữ liệu thực và tên ổn định.",'''
source_final,history_final=export_example_artifacts(OUT,config)
write_json(OUT/'source_run_summary.json',{'status':source_final.status,'iterations':source_final.iterations,'w':source_final.objective,'z':2*source_final.objective})
display(pd.DataFrame({'file':[str(p.relative_to(OUT)) for p in sorted(OUT.rglob('*')) if p.is_file() and 'pytest' not in str(p) and 'jupyter' not in str(p)]}).head(40))
''',"Các hình 4.8 và bảng bước lặp được lấy từ solver thực. Mọi ma trận nằm trong JSON; hình nguồn được ghi là tái dựng.")
    block(67,"4.1–4.5; MasterSpec 11.1","C12","Tự kiểm coverage và notebook IDs.","Không bỏ mục khó hoặc thiếu diễn giải từng block.","Source notebook + artifacts → audit.","68 ID, 30 tiểu mục, hình/bảng tồn tại.","coverage=audit_project(ROOT)\ndisplay(coverage)\nwrite_json(OUT/'coverage_audit.json',coverage)","Cell hiện tại kiểm cấu trúc và artifact. Sau khi lưu notebook executed, script run_notebook còn kiểm đủ execution_count và không có output lỗi.")
    block(68,"4.5.3; MasterSpec 11.2–11.3","C12","In kết luận có giới hạn và thông tin lần chạy.","Tách kết quả máy với chứng minh toán học.","source_final,benchmark_summary,manifest → kết luận.","Đã chạy, đạt ngưỡng gần đúng; không có chứng nhận exact optimality.",'''
display({'source_status':source_final.status.value,'source_iterations':source_final.iterations,
         'w_final':source_final.objective,'z_final':2*source_final.objective,
         'benchmark_rows':len(benchmark_data),'coverage':coverage,
         'timestamp':environment_manifest()['timestamp'],'config_hash':environment_manifest(config)['config_hash']})
display(claims)
''',"Hoàn tất notebook nghĩa là các phép tính và file được tạo lại; không mở rộng kết luận sang LP chưa chuẩn hóa, chứng nhận tối ưu chính xác hoặc cận runtime tổng quát.")

    nb=nbf.v4.new_notebook(cells=cells,metadata={"kernelspec":{"name":"python3","display_name":"Python (karmarkar-project)","language":"python"},
                    "language_info":{"name":"python","version":"3.10+"},
                    "source":{"BC":"27 pages, printed 33-59","MasterSpec":"v3.0, 33 pages"}})
    target=root/"notebooks/01_karmarkar_full_report.ipynb"
    target.parent.mkdir(parents=True,exist_ok=True)
    nbf.write(nb,target)
    assert len([c for c in cells if c.cell_type=="code"])==68
    print(f"Created {target.name}: 68 code cells, annotated before and after")


if __name__=="__main__":
    build(Path(__file__).resolve().parents[1])

