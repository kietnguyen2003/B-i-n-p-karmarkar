# Karmarkar: mã nguồn và notebook theo báo cáo Phần 4

Dự án triển khai phép lặp xạ ảnh Karmarkar từ đầu theo `BC - Mục 4 - Karmarkar.pdf` (27 trang, trang in 33-59) và `Karmarkar_Codex_MasterSpec.pdf` v3.0 (33 trang).

## Chương trình nhập bài toán và xuất HTML

Notebook chính dành cho người sử dụng là **`../Karmarkar_HTML.ipynb`**. Mở notebook,
chọn **Run All**, rồi nhập `min/max`, số biến, số ràng buộc, hàm mục tiêu, từng ràng buộc
và điều kiện dấu biến. Báo cáo tự chứa được ghi tại **`../output/Loi_giai_Karmarkar.html`**;
trong đó có bước chuẩn hóa, xạ ảnh, quả cầu nội tiếp, toàn bộ vòng lặp và hình minh họa phù hợp.

Kiểm tra tự động đúng luồng nhập liệu của bài BC 4.4:

```powershell
.venv\Scripts\python.exe scripts\build_interactive_notebook.py
cd ..
./karmarkar-project/.venv/Scripts/python.exe ./karmarkar-project/scripts/verify_interactive_notebook.py
```

Phần nhập LP tổng quát là tiền xử lý `[DX]`. Chương trình dùng HiGHS trước vòng lặp để phân loại
bài toán hữu hạn, vô nghiệm, không giới nội hoặc có vô số nghiệm tối ưu. Các trường hợp kết thúc
được xuất thành HTML với quy ước giá trị mở rộng và không giả tạo vòng lặp Karmarkar. Với bài có
nghiệm hữu hạn duy nhất, chương trình ưu tiên chuẩn hóa trực tiếp; khi cần sẽ ghép primal-dual,
dùng **độ chênh lệch primal-dual** làm mục tiêu không âm có cực tiểu 0 rồi đưa điểm đầu về tâm.

Giai đoạn I tìm điểm dương dùng `0 <= t <= 1`: chỉ cần `t>0` để chứng minh có điểm trong, nhờ đó
một tia khả thi không còn làm bài toán phụ bị báo `Unbounded`. Phép lặp sau chuẩn hóa vẫn dùng đúng
`D`, `B=[AD;eᵀ]`, `Dc`, phép chiếu, bước `alpha*r` và xạ ảnh ngược của PDF. HiGHS có thể tạo dữ
liệu tiền xử lý/chứng chỉ nhưng không tạo bất kỳ bước `D`, `B`, `p`, `d`, `y` nào của Karmarkar.

## Mở và kiểm tra từng mục

- **Bắt đầu:** `notebooks/01_karmarkar_full_report_executed.ipynb` để xem bản đã chạy có hình/bảng. Bản `01_karmarkar_full_report.ipynb` để tự Restart & Run All.
- Mỗi cell ghi **NB01-NB68**, mục BC, công thức/hình và block **C01-C12** trong MasterSpec. Ngay trước code có bốn nhãn “Đang làm gì”, “Vì sao cần”, “Input/Output”, “Cần nhìn kết quả nào”; sau code có diễn giải.
- Mỗi hàm/module Python cũng có docstring dẫn mục BC và MasterSpec. Ví dụ: BC 4.4.6, (4.52) → notebook NB46-NB47 → `iteration.py` C07 → T27.
- Bảng đối chiếu đầy đủ: [docs/mapping_report_sections.md](docs/mapping_report_sections.md): 30 tiểu mục, 57 công thức, 8 hình, 3 bảng.
- [Giả thiết/phạm vi](docs/math_assumptions.md); [quyết định triển khai](docs/implementation_notes.md).
- [Kết quả nghiệm thu thực chạy](docs/verification_results.md): 72 kiểm thử qua, 68 cell đã thực thi, 80 lượt benchmark.

## Cài và chạy

Python >=3.10. Trên Windows PowerShell, mở terminal tại thư mục dự án:

```powershell
# MasterSpec C12/G1: tạo môi trường rồi cài package và công cụ kiểm thử.
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
```

```powershell
# MasterSpec C12/G4-G7; BC 4.1-4.5: tái sinh và kiểm chứng toàn bộ.
.venv\Scripts\python.exe scripts/build_mapping.py
.venv\Scripts\python.exe scripts/build_notebook.py
.venv\Scripts\python.exe scripts/verify_all.py
```

Hoặc chạy riêng từng phần:

```powershell
# BC 4.4; MasterSpec C09-C10: ví dụ, 8 hình, 3 bảng và trace thực.
.venv\Scripts\python.exe scripts/run_example.py --alpha 0.25 --epsilon 1e-6
# MasterSpec C11/G6: benchmark thật 5 lần/bài; reference HiGHS tách lõi.
.venv\Scripts\python.exe scripts/run_experiments.py --config configs/default.yaml
# MasterSpec C12/G7: T01-T35 và các kiểm thử bổ sung.
.venv\Scripts\python.exe -m pytest -q
# MasterSpec C12/G5/G7: kernel mới, chạy NB01-NB68 và audit bản executed.
.venv\Scripts\python.exe scripts/run_notebook.py
```

Trên Linux/macOS dùng `.venv/bin/python` thay cho `.venv\Scripts\python.exe`. Không có đường dẫn tuyệt đối cá nhân trong mã. Có thể xem notebook bằng VS Code/Jupyter với kernel của `.venv`.

## Đầu ra

- `outputs/figures/figure_4_1` đến `figure_4_8`: PNG + SVG; thêm hình mục 4.4.2 và các biểu đồ [DX].
- `outputs/tables/table_4_1_vertices.csv`, `table_4_2_iterations.csv`, `table_4_3_methods.csv`.
- `outputs/tables/source_full_history.csv`, `step_diagnostics.csv`, `potential_history.csv`.
- `outputs/tables/benchmark_results.csv`: mọi lần chạy; `comparison_table.csv`: thống kê, giữ cả ca lỗi.
- `outputs/traces/`: JSON chứa ma trận và diagnostics đầy đủ.
- `outputs/run_manifest.json`: môi trường, seed, timestamp, config hash, hash PDF nếu có, phương thức reference.
- `outputs/pytest.xml`, `pytest_summary.txt`, `notebook_audit.json`, `verification.json`: chứng cứ nghiệm thu.
- `notebooks/01_karmarkar_full_report_executed.ipynb`: 68 cell có kết quả thực.

## Cấu hình và giới hạn

`configs/default.yaml` cố định alpha=0.25, epsilon=1e-6, max_iter=1000, seed=20261028, repetitions=5. **epsilon của solver/CLI áp dụng cho mục tiêu chuẩn w=cᵀu; z=2w trong ví dụ.** Công thức k_epsilon ở BC (4.57) dùng epsilon của z và chỉ dành cho ví dụ; epsilon_z=0.1 cho k=11.

Các tolerance được tách theo mục đích: `feas_tol` cho đẳng thức/tổng; `positive_tol` là ngưỡng tọa độ nội tại; `projection_abs_tol`, `projection_rel_tol` phân loại hướng quá nhỏ; `svd_atol`, `svd_rtol` xác định hạng; `potential_tol` cho monitor hàm thế. `verbose` bật log; `store_trajectory` bật trace; `seed` chỉ ảnh hưởng phát sinh dataset, không ảnh hưởng solver xác định.

`require_nonnegative_certificate` mặc định True. Dữ liệu chưa chứng minh không âm được trả PRECONDITION_UNVERIFIED, trừ khi bật `allow_unverified_demo`. Tối ưu 0 cần `zero_witness` đã kiểm. Monitor mức giảm 1/8 mặc định tắt; nếu bật phải có alpha=1/4 và ngữ cảnh tối ưu 0 đã kiểm.

Lõi toán học `iteration.py`/`solver.py` không gọi `linprog` và chỉ nhận LP **đã chuẩn hóa**. Adapter
`general_lp.py` mới là phần nhận LP tổng quát, phân loại, chạy Giai đoạn I, dựng chứng chỉ và phép
nhúng; adapter dùng HiGHS nhưng giữ kết quả đó ngoài công thức bước lặp Karmarkar. Trạng thái đạt
tolerance là nghiệm gần đúng, không phải chứng nhận tối ưu hữu tỉ chính xác. Benchmark không chứng
minh cận thời gian đa thức của mã NumPy/SVD. Mọi chứng chỉ được kiểm bằng float64 với tolerance.

