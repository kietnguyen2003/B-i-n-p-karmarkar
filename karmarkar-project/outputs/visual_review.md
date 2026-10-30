# Kiểm tra hình ảnh trực quan

Ngày kiểm tra: 28/10/2026. Đối chiếu MasterSpec C10, §§7.1,8.5,11.1; BC Hình 4.1-4.8 và hình không đánh số ở 4.4.2.

- Đã mở và xem đủ 8 PNG `figure_4_1` đến `figure_4_8`: chữ tiếng Việt đọc được, ký hiệu toán không mất, nhãn đỉnh và hướng giảm đúng.
- Hình 4.2 phân biệt biến bù/chuẩn hóa với xạ ảnh; Hình 4.3 dùng embedding trực chuẩn, tỷ lệ R/r=2.
- Hình 4.4 ghi rõ minh họa 2D; Hình 4.5 dùng chung mốc a cho tất cả điểm và T_a(b) khác tâm.
- Hình 4.6 biểu diễn đúng bước nằm trong cầu; Hình 4.7 đủ sáu bước và vòng quay lại; Hình 4.8 dùng trace thực, mốc k=0,1,2,3,10 đọc được.
- Đã xem thêm hình miền 4.4.2, sơ đồ năm nhịp, cận lý thuyết minh họa, mục tiêu, hàm thế, residuals, runtime, số vòng theo n và biểu đồ trạng thái: tổng 17 PNG.
- Đã điều chỉnh khoảng cách chú thích và nhãn trục ở hai biểu đồ benchmark; đã xem lại sau điều chỉnh.
- PNG và SVG sinh từ cùng Matplotlib Figure; mỗi hình bắt buộc có cả hai định dạng.

Kết quả kiểm tra trực quan: PASS. Đây là kiểm tra khả năng đọc/diễn giải hình; tính đúng số học được kiểm riêng bằng pytest và notebook run-all.

