# Kết quả nghiệm thu thực chạy

Ngày 30/10/2026; MasterSpec G0-G7, C01-C12, §11. Đọc bằng chứng gốc tại `outputs/verification.json`, `outputs/pytest.xml`, `outputs/notebook_audit.json` và `outputs/run_manifest.json`.

| Hạng mục | Kết quả |
|---|---|
| Pytest | 72 passed; 0 failures, 0 errors, 0 skipped |
| Bộ T01-T35 | Có đủ, kèm kiểm thử bổ sung và parametrization |
| Notebook thực thi | 68/68 code cell; execution_count 1-68; không có output lỗi |
| Coverage nguồn | 30 tiểu mục 4.1.1-4.5.3, 57 công thức được ánh xạ |
| Hình nguồn | 8 PNG và 8 SVG; thêm hình không đánh số 4.4.2 |
| Bảng nguồn | Bảng 4.1-4.3, CSV sinh từ mô hình/lịch sử thực |
| Tổng hình | 17 PNG + SVG, gồm phần bổ sung [DX] |
| Benchmark | 16 bài × 5 lần = 80 lượt chạy, giữ toàn bộ trạng thái |
| Chạy lệnh toàn bộ | verify_all.py trả exit code 0, verification PASS |

Ví dụ nguồn đạt epsilon chuẩn w≤1e-6 sau 41 vòng: w≈8.91352012e-7, z=2w≈1.782704024e-6. Ba bước đầu và các mốc k=0,1,2,3,10,20 khớp báo cáo. Công thức hàm thế và epsilon_z=0.1 → k=11 đều được kiểm.

Benchmark có 45 dòng đạt ngưỡng, 20 dòng INVALID_INPUT của nhóm dữ liệu sai, 10 dòng NO_PROJECTED_DIRECTION và 5 dòng MAX_ITERATIONS của bài cực tiểu dương. Những trạng thái này được giữ, không loại để làm đẹp kết quả. Trong các bài hợp lệ đã chạy, residual đẳng thức tuyệt đối lớn nhất xấp xỉ 5.82e-11 và sai số tổng lớn nhất xấp xỉ 2.22e-16; tolerance còn co giãn theo scale dữ liệu.

Không có tiêu chí bắt buộc nào đang để INCOMPLETE trong quy trình đã chạy. Adapter tương tác đã bổ
sung chuẩn hóa LP tổng quát, phân loại vô nghiệm/không giới nội/vô số nghiệm, biến tự do và báo cáo
điều kiện khởi tạo suy biến. Phần không cung cấp theo ranh giới của đặc tả: chứng nhận tối ưu hữu tỉ
chính xác và chứng minh cận runtime của mã Python; bộ nhớ chưa đo và CI là tùy chọn. Các giới hạn
này đã được nêu trong README, notebook và docs/math_assumptions.md.

Trong môi trường Windows/Python 3.14 hiện tại, runner dùng một selector event loop được quản lý và đóng tường minh để tiến trình Jupyter kết thúc sạch. Bản notebook được chạy bằng kernel mới của chính môi trường dự án.

