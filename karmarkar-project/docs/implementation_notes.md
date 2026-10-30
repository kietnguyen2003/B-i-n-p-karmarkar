# Ghi chú triển khai

MasterSpec C01-C12 được tách theo module trong `src/karmarkar/`; từng module/hàm có tham chiếu `[MS ...; BC ...]`. Trong notebook, mỗi block có ID NB01-NB68 và chú giải trước/sau; có thể tìm theo `NB47`, `(4.52)` hoặc `4.4.6`.

- `types.py`: C01, dataclass và trạng thái; `canonical.py`: C02, chứng cứ tiền điều kiện.
- `geometry.py`: C03; `projective.py`: C04; `projection.py`: C05; `potential.py`: C06.
- `iteration.py`: C07; `solver.py`: C08; `examples.py`: C09.
- `plotting.py`: C10; `experiments.py`: C11; scripts/notebook/tests: C12.
- `io.py`, `reporting.py` là helper [DX] cho cấu hình, xuất kết quả và trình bày. Core không thực hiện I/O.
- `general_lp.py` là adapter [DX] cho LP tổng quát: phân loại, Giai đoạn I, biến tự do, chuẩn hóa trực
  tiếp hoặc nhúng primal-dual. `html_report.py` xuất báo cáo tiếng Việt tự chứa và tách rõ kết quả
  Karmarkar khỏi kết luận tiền xử lý.

`SolverConfig.store_trajectory=False` giảm bộ nhớ lịch sử; các tác vụ tái dựng báo cáo yêu cầu True. Với n lớn, cấu trúc StepRecord đầy đủ có chi phí O(n²) mỗi bước do lưu D/B. Dùng `display_detail=False`/`show_step_table(..., include_matrices=False)` để ẩn ma trận khi trình bày; hàm chỉ preview 5×5 nếu n>8. Đây là bản dạy học có trace, không tối ưu bộ nhớ cho LP rất lớn.

SVD được chọn thay nghịch đảo trực tiếp để xử lý hàng phụ thuộc. Có thêm kiểm thử điểm khả thi bất đối xứng với A≠0: chỉ dùng ví dụ F3 đối xứng chưa chắc bắt được lỗi bỏ D.

Các hàm `analytic_*` ở examples.py là oracle kiểm tra độc lập. `iteration.py` và `solver.py` không import chúng, không import scipy.optimize hoặc module experiments. Hình 4.8 lấy dữ liệu từ trace thật.

`run_manifest.json` ghi phiên bản, seed, cấu hình/hash, máy, thời gian, hash hai PDF nếu tìm thấy ở thư mục cha. Git commit để null khi không có git hoặc không ở repository. Khi thiếu PDF trên một checkout khác, mã vẫn chạy và trường hash nguồn có thể rỗng.

Thời gian benchmark dùng perf_counter, mặc định 5 lần/bài, có warm-up riêng; không trộn thời gian import/plot/serialize. Không đo bộ nhớ, ghi rõ trong manifest. Cả raw rows và thống kê median/min/max/std được lưu. Các ca F7 INVALID_INPUT được giữ, không gọi reference cho canonical sai.

Notebook được sinh lại bằng `scripts/build_notebook.py`. Mỗi code cell có đủ bốn nhãn Markdown bắt buộc ngay trước và diễn giải ngay sau. `scripts/run_notebook.py` dùng kernel mới với chính sys.executable để tránh dùng nhầm môi trường toàn cục.

