# Thuật toán Karmarkar — Mã nguồn và báo cáo thực nghiệm

Dự án triển khai thuật toán điểm trong Karmarkar bằng Python, phục vụ việc trình bày và kiểm chứng **Phần 4 — Karmarkar** trong [báo cáo gốc](<tai_lieu/BC - Mục 4 - Karmarkar.pdf>). Nội dung kết hợp lý thuyết, phép lặp xạ ảnh, ví dụ tính toán từng bước và các hình minh họa.

Chương trình hiện sử dụng **Jupyter Notebook để nhập bài toán và xuất lời giải HTML**. Dự án chưa tích hợp Streamlit.

## Nội dung theo báo cáo

| Phần | Nội dung triển khai |
|---|---|
| 4.1 | Giới thiệu bài toán và trực quan hóa ý tưởng phương pháp điểm trong |
| 4.2 | Dạng chuẩn, hình học đơn giác, quả cầu nội tiếp, phép chiếu, phép xạ ảnh và hàm thế |
| 4.3 | Các bước của thuật toán, điều kiện dừng và xử lý trạng thái tính toán |
| 4.4 | Ví dụ minh họa, ba bước lặp đầu, công thức nghiệm theo vòng lặp, bảng và hình kết quả |
| 4.5 | Nhận xét, phạm vi áp dụng và thực nghiệm bổ sung |

Notebook báo cáo đối chiếu 30 tiểu mục, 57 công thức, 8 hình và 3 bảng của tài liệu nguồn. Xem [bảng ánh xạ báo cáo → notebook → mã nguồn → kiểm thử](karmarkar-project/docs/mapping_report_sections.md).

## Chức năng

- Nhập bài toán quy hoạch tuyến tính `min` hoặc `max`, hệ số hàm mục tiêu, hằng số và các ràng buộc `<=`, `>=`, `=`.
- Hỗ trợ biến không âm, không dương và biến tự do; nhận số nguyên, số thập phân hoặc phân số như `1/3`.
- Tiền xử lý và chuẩn hóa bài toán trước khi chạy lõi Karmarkar.
- Xuất báo cáo HTML gồm đề bài, bước chuẩn hóa, ma trận và vectơ trung gian, lịch sử vòng lặp, hình minh họa phù hợp và kết quả đối chứng.
- Phân loại bài toán vô nghiệm, không giới nội hoặc có vô số nghiệm tối ưu trước khi lặp; thông báo riêng khi không đủ điều kiện khởi tạo.
- Chạy ví dụ trong báo cáo, thực nghiệm theo cấu hình và bộ kiểm thử tự động.

## Cấu trúc thư mục

```text
.
├── README.md
├── tai_lieu/
│   └── BC - Mục 4 - Karmarkar.pdf       # Báo cáo gốc
├── Karmarkar_HTML.ipynb                # Nhập bài toán và xuất lời giải
├── output/
│   └── Loi_giai_Karmarkar.html         # Báo cáo HTML được tạo
└── karmarkar-project/
    ├── src/karmarkar/                  # Thuật toán, chuẩn hóa, vẽ hình, xuất báo cáo
    ├── notebooks/                     # Notebook đối chiếu báo cáo và bản đã chạy
    ├── scripts/                       # Chạy ví dụ, thực nghiệm và kiểm chứng
    ├── tests/                         # Kiểm thử các thành phần thuật toán
    ├── configs/default.yaml           # Cấu hình thực nghiệm
    ├── docs/                          # Giả thiết, ánh xạ và kết quả nghiệm thu
    ├── outputs/                       # Hình, bảng, trace và bằng chứng kiểm chứng
    └── pyproject.toml                 # Khai báo package và thư viện
```

## Cài đặt

Yêu cầu **Python 3.10 trở lên**. Các thư viện tính toán chính gồm NumPy, SciPy, Matplotlib, pandas và PyYAML. Mở terminal tại thư mục gốc của repository.

**macOS / Linux:**

```bash
python3 -m venv karmarkar-project/.venv
source karmarkar-project/.venv/bin/activate
python -m pip install -e "./karmarkar-project[dev]"
```

**Windows PowerShell:**

```powershell
python -m venv karmarkar-project/.venv
.\karmarkar-project\.venv\Scripts\python.exe -m pip install -e "./karmarkar-project[dev]"
```

Mở notebook bằng VS Code có hỗ trợ Jupyter và chọn kernel Python trong `karmarkar-project/.venv`. Nếu muốn dùng JupyterLab trên trình duyệt, cài thêm `jupyterlab` vào môi trường này rồi chạy `python -m jupyterlab`.

## Nhập bài toán và xem lời giải

1. Mở [Karmarkar_HTML.ipynb](Karmarkar_HTML.ipynb), chọn kernel đã cài ở trên.
2. Chọn **Run All / Chạy tất cả các ô**.
3. Nhập lần lượt loại bài toán, số biến, số ràng buộc, hàm mục tiêu, từng ràng buộc và điều kiện dấu của biến. Các hệ số trên một dòng cách nhau bằng khoảng trắng.
4. Mở [output/Loi_giai_Karmarkar.html](output/Loi_giai_Karmarkar.html) bằng trình duyệt để xem lời giải. Chạy lại sẽ ghi kết quả vào cùng đường dẫn mặc định.

Gõ `thoat` tại câu hỏi nhập liệu để hủy lần chạy, sau đó chạy lại notebook nếu muốn nhập lại từ đầu.

Ví dụ ở mục 4.4 của báo cáo:

```text
min z = 2 - x1
với x1 + x2 <= 2
    x1, x2 >= 0
```

Nhập theo thứ tự câu hỏi: `min` → `2` biến → `1` ràng buộc → hệ số mục tiêu `-1 0` → hằng số `2` → hệ số ràng buộc `1 1` → dấu `<=` → vế phải `2` → dấu `>=0` cho mỗi biến.

Notebook tương tác mặc định dùng `alpha = 0.25`, tối đa `300` vòng, sai số mục tiêu `1e-8` và sai số khả thi `1e-9`. Có thể sửa trong khối cài đặt trước khi chạy.

## Đọc báo cáo tính toán và chạy kiểm chứng

- [Notebook đã thực thi](karmarkar-project/notebooks/01_karmarkar_full_report_executed.ipynb): đọc ngay bảng, hình và kết quả đã lưu.
- [Notebook nguồn](karmarkar-project/notebooks/01_karmarkar_full_report.ipynb): tự chạy lại các nội dung đối chiếu báo cáo.
- [Hướng dẫn kỹ thuật chi tiết](karmarkar-project/README.md): cấu hình, đầu ra và các lệnh tái tạo tài liệu.

Các lệnh sau chạy trong thư mục `karmarkar-project`, với môi trường Python đã kích hoạt. Trên Windows, có thể thay `python` bằng `.\.venv\Scripts\python.exe`.

```bash
cd karmarkar-project
python scripts/run_example.py --alpha 0.25 --epsilon 1e-6
python scripts/run_experiments.py --config configs/default.yaml
python -m pytest -q
python scripts/verify_all.py
```

Các script có thể cập nhật hình, bảng, lịch sử tính toán và kết quả kiểm chứng trong `karmarkar-project/outputs/`.

Theo [kết quả nghiệm thu đã lưu ngày 30/10/2026](karmarkar-project/docs/verification_results.md):

| Hạng mục | Kết quả đã ghi nhận |
|---|---|
| Kiểm thử | 72 bài kiểm thử đạt, không lỗi hoặc bỏ qua |
| Notebook báo cáo | 68/68 ô mã đã thực thi, không có output lỗi |
| Thực nghiệm | 16 bài toán × 5 lần = 80 lượt chạy, giữ cả trạng thái thất bại |
| Ví dụ nguồn | 41 vòng để đạt mục tiêu chuẩn `w ≤ 1e-6` |

Đây là kết quả của lần chạy được lưu trong repository, không phải xác nhận cho mọi môi trường cài đặt. Trong ví dụ nguồn, `z = 2w`, nên ngưỡng sai số của `w` và `z` cần được phân biệt.

## Phạm vi toán học và giới hạn

Lõi Karmarkar giải bài toán đã chuẩn hóa `min cᵀu`, với `Au = 0`, `eᵀu = 1`, `u ≥ 0`. Việc khởi tạo và kết luận đạt ngưỡng yêu cầu các giả thiết về điểm trong, mục tiêu không âm và ngữ cảnh tối ưu bằng 0 được kiểm tra.

Mỗi vòng lặp dựng `D = diag(u)`, `B = [AD; eᵀ]`, chiếu `Dc` lên không gian nghiệm của `B`, bước theo hướng giảm trong quả cầu nội tiếp rồi xạ ảnh ngược. Các phép tính này được triển khai trong mã nguồn của dự án.

Adapter `general_lp.py` sử dụng HiGHS của SciPy để phân loại bài toán, tìm điểm khởi tạo và hỗ trợ chứng chỉ số. Với bài toán cần thiết, adapter ghép primal-dual để đưa mục tiêu về độ chênh lệch có cực tiểu 0. HiGHS không thay thế các bước lặp xạ ảnh Karmarkar.

Kết quả đạt tolerance là nghiệm gần đúng bằng số thực `float64`, không phải chứng nhận tối ưu hữu tỉ chính xác. Benchmark không chứng minh cận thời gian đa thức cho bản cài đặt Python. Xem thêm [giả thiết và giới hạn](karmarkar-project/docs/math_assumptions.md) cùng [ghi chú triển khai](karmarkar-project/docs/implementation_notes.md).
