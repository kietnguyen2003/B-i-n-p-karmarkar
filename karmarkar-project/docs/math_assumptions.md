# Giả thiết và phạm vi toán học

Đối chiếu MasterSpec §§0.2,2.2-2.8,3.3,9; BC §§4.2.1-4.2.8,4.3.5,4.5.3.

- Dữ liệu đã ở dạng min cᵀx, Ax=0, eᵀx=1, x≥0; n≥2; A.shape=(m,n), kể cả (0,n).
- Khởi đầu a0=e/n đòi Ae≈0 và cᵀa0>0. Không tự nhận hỗ trợ chuẩn hóa LP tổng quát Ax=b.
- Trên toàn miền P cần cᵀx≥0. `PROVEN` nhận từ c≥0 hoặc chứng chỉ đối ngẫu đã kiểm tra; `DISPROVEN` từ nghiệm khả thi có mục tiêu âm; còn lại `UNKNOWN`. Tâm có mục tiêu dương không đủ chứng minh.
- Chứng chỉ đối ngẫu dùng λ, β≥0 sao cho c−Aᵀλ−βe≥0. Khi Ax=0 và eᵀx=1 suy ra cᵀx≥β≥0. Việc kiểm bằng float64 có tolerance, không là chứng nhận số hữu tỉ chính xác.
- Ngữ cảnh tối ưu 0 chỉ được bật khi đã có chặn dưới không âm và một `zero_witness` khả thi đạt mục tiêu 0 trong tolerance. Ngưỡng epsilon là mục tiêu chuẩn cᵀx; trong ví dụ w=z/2, không đồng nhất hai ngưỡng.
- Core không dùng nghiệm từ solver tham chiếu. Reference HiGHS chỉ nằm ở `experiments.py`, chạy sau Karmarkar và có timer riêng.

## Adapter LP tổng quát dùng trong notebook tương tác

- Các giả thiết phía trên là hợp đồng của lõi `iteration.py`/`solver.py`. Notebook tương tác gọi
  `general_lp.py` để nhận min/max, dấu bất đẳng thức, biến không âm/không dương/tự do và cận nhập
  dưới dạng ràng buộc.
- HiGHS được dùng ở tiền xử lý để phân loại hữu hạn, vô nghiệm, không giới nội, nhiều nghiệm tối ưu;
  tìm điểm Giai đoạn I; và dựng các chứng chỉ số. Không nghiệm nào từ HiGHS được đưa vào để thay thế
  các phép tính D, B, p, d, y hoặc xạ ảnh ngược.
- Giai đoạn I giải bài toán biên `0 <= t <= 1`, `z_i >= t`. Bất kỳ `t>0` nào cũng là chứng cứ điểm
  trong; chặn `t<=1` tránh nhầm một tia khả thi với thất bại khởi tạo.
- Bài vô nghiệm, không giới nội hoặc có vô số nghiệm tối ưu được kết luận ở bước phân loại và có 0
  vòng Karmarkar. Bài hữu hạn nhưng không thỏa giả thiết điểm trong được báo riêng, không gắn nhãn sai.

## Công thức và lý do

BC (4.37)-(4.41): D=diag(x), B=[AD;eᵀ], v=Dc, p=projection_KerB(v), d=−p/‖p‖, y=e/n+αrd, x_next=Dy/(eᵀDy).

ADa0=Ax/n=0. Vì Bd=0, y thỏa ADy=0 và eᵀy=1. Với 0<α<1, ‖y−a0‖=αr<r nên y>0. Mẫu số đổi ngược dương; suy ra Ax_next=0, eᵀx_next=1 và x_next>0 trong số học chính xác. Phần mềm kiểm tra các tính chất này bằng tolerance co giãn.

SVD dùng cutoff max(svd_atol,svd_rtol*s_max) và full right singular vectors. Kernel rỗng có trạng thái riêng. Chuẩn p nhỏ được so với projection_abs_tol+projection_rel_tol*‖v‖. Không clip tọa độ hoặc chuẩn hóa lại để che bước sai. Phép chia tổng trong inverse map là thành phần công thức, không phải biện pháp sửa lỗi.

Hàm mục tiêu trong hệ y là (Dc)ᵀy/(eᵀDy), còn (Dc)ᵀy là hàm tuyến tính phụ. Không tự suy giảm mục tiêu gốc từ giảm hàm tuyến tính phụ.

Phi(x)=n ln(cᵀx)−Σln xi chỉ xác định khi x>0,cᵀx>0. Với mốc a cố định, Phi(x)=Phi_tilde_D(y)−Σln ai; hiệu được bảo toàn trong cùng một bước.

## Điều kiện kết thúc

| Trạng thái | Ý nghĩa |
|---|---|
| APPROX_TOL_REACHED | Ngữ cảnh tối ưu 0 đã kiểm, 0≤cᵀx≤epsilon; chỉ gần tối ưu |
| MAX_ITERATIONS | Hết ngân sách, chưa đạt tiêu chí |
| NO_PROJECTED_DIRECTION | Kernel rỗng hoặc hướng chiếu bằng 0/nhận diện cấu trúc hằng tại tâm |
| NUMERICALLY_UNDETERMINED | p nhỏ so với scale và precision |
| INVALID_INPUT | Sai dữ liệu/cấu hình/giả thiết đã bị bác bỏ |
| NUMERICAL_FAILURE | Không hữu hạn, mất tính dương, sai đẳng thức hoặc inverse lỗi |
| POTENTIAL_TEST_FAILED | Monitor mức giảm không đạt; không chứng nhận cực tiểu dương |
| PRECONDITION_UNVERIFIED | Thiếu chứng cứ để chạy chế độ yêu cầu hoặc bật monitor |

`monitor_potential=True` chỉ được bật khi α=1/4 và ngữ cảnh tối ưu 0 đã kiểm. Nếu không đủ điều kiện, trả PRECONDITION_UNVERIFIED. Khi bật, mức giảm kiểm là 1/8 với potential_tol. Monitor không cung cấp thủ tục nhận diện cực tiểu dương chính xác của bài báo gốc.

## Giới hạn cần giữ rõ

- Không có trạng thái OPTIMAL hay chứng nhận nghiệm tối ưu chính xác; không có bước cực biên/số hữu tỉ của thuật toán gốc.
- Không chứng minh cận runtime đa thức cho bản NumPy/SVD. Cận bước O(n(q+ln n)) và O(n^3.5 L) phép toán được dẫn theo giả thiết/mô hình trong nguồn.
- Các điểm hữu hạn của ví dụ nằm trong miền, giới hạn có thể trên biên. Float64 có underflow với k rất lớn; nghiệm đóng ở số máy có thể có 0 do underflow, không phải bằng chứng đạt đỉnh hữu hạn.
- Benchmark giữ ca thất bại, ghi reference gap riêng và không tuyên bố so sánh tốc độ công bằng tuyệt đối: backend và tiêu chí dừng khác nhau.
- Hình 4.4 là sơ đồ 2D; các hình hình học đơn giác dùng embedding trực chuẩn khi thể hiện khoảng cách.

