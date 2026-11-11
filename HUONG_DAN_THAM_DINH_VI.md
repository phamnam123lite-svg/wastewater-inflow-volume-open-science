# Hướng dẫn thẩm định bộ nộp chính thức

Tác giả: Viet Nam Tran, Faculty of Environment, Van Lang University, Ho Chi Minh City, Vietnam.

1. Đọc `paper/manuscript.docx` (hoặc `paper/manuscript.pdf` để xem nhanh trên mọi máy): đây là bản paper để giảng viên nhận xét. Bản Markdown là nguồn tạo Word, không phải bản nghiên cứu khác.
2. Đọc `docs/FINAL_AUDIT_VI.md` và `docs/SECTION_AUDIT.md` để biết nội dung đã kiểm tra và phạm vi chưa thể xác minh.
3. Đọc README, tạo môi trường Python mới và chạy `reproduce.py`. Không cần tài khoản hoặc tải dữ liệu riêng; ba tệp quan sát gốc đã kèm theo.
4. Đối chiếu `verification/` với báo cáo mới tại `reproduced/`. Hai thư mục kết quả chuẩn phải được giữ nguyên.
5. Các kết quả chính được đối chiếu tự động với 4 bảng trong paper; cả 5 hình được tái tạo từ kết quả. Mã kiểm tra không thể xác nhận chất lượng cảm biến hoặc lợi ích vận hành ngoài dữ liệu.

Phạm vi nghiên cứu là kiểm định tính nhạy cấu hình và độ tin cậy dự báo dòng vào hai nhà máy, không phải thí nghiệm loại bỏ chất ô nhiễm hoặc bằng chứng tiết kiệm năng lượng. Không suy diễn điều khiển trạm hay dung tích bể từ MAE.

Đây là bộ gửi giảng viên thẩm định, chưa phải tuyên bố được chấp nhận xuất bản. Người dùng đã khai báo không có tài trợ và xung đột lợi ích, chưa cung cấp email liên hệ. AI hỗ trợ tính toán và soạn thảo được công khai trong paper. Cần tác giả đọc, chịu trách nhiệm và quyết định bản nộp tạp chí.

Bản công khai tương ứng: https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science (thẻ `v0.2.1`). Thư mục này và thẻ `v0.2.1` có cùng nội dung; GitHub Actions chạy lại toàn bộ phân tích hai địa điểm sau mỗi lần cập nhật.
