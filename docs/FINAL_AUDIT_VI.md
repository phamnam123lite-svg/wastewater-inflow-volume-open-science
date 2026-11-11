# Kiểm định và sửa chữa bản nộp 0.2.1

Ngày 11 tháng 11 năm 2026. Phạm vi gồm GitHub tại commit dc375bd7e3081fc784b8fe9b4bbb851d0cd3f3b9, bản v0.2.0 địa phương và bộ nộp mới. Đây là kiểm tra tính nhất quán có hỗ trợ AI; không phải năm phản biện độc lập hoặc chứng nhận chấp nhận tạp chí.

| Vị trí | Vấn đề và hậu quả | Sửa chữa |
| --- | --- | --- |
| README và CI cũ | Chạy ghi đè `results`, rồi so sánh với chính nó; không chứng minh tái lập | Tách đầu ra, chặn tự so sánh và ghi đè kết quả chuẩn; runner đầy đủ hai địa điểm |
| README và CI cũ | Thiếu configuration_sensitivity và bootstrap_diagnostic nhưng tuyên bố 34 bảng | Chạy đủ các bước, đối chiếu toàn bộ danh mục 34 + 12 bảng |
| README cũ | Tuyên bố byte-level và ngưỡng chính xác 0 khác comparator thực tế | Ghi rõ so sánh nội dung, rtol 1e-10 và atol 1e-8; báo sai khác thực đo riêng |
| Kho dữ liệu | Không có dữ liệu gốc trong clone, cần mạng; supplement lặp toàn dự án | Kèm ba tệp quan sát đã kiểm tra hash, giữ metadata/license, bỏ supplement lặp khỏi bản hiện hành |
| verification cũ | Báo cáo và comparator v0.1 gây nhầm với v0.2 | Sao lưu lịch sử, thay bằng kiểm tra thực của bộ nộp hiện hành |
| Paper và README | Cụm “near-nominal” quá rộng cho 83.7% ở mức danh nghĩa 90% | Mô tả chính xác chênh lệch coverage tổng thể và phân nhóm |
| Paper | Chưa có Word; một số đường dẫn phụ thuộc cấu trúc cũ | Tạo Word từ nguồn duy nhất, phương trình OMML, bảng có tiêu đề lặp, ảnh có caption |
| Bảng trong paper | Tên mô hình khác nhãn trong hình; không ghi rõ tập biến đầu vào; Bảng 3 thiếu điểm interval score dù văn bản dùng nó; n thiếu dấu phân cách; chú thích lẫn vào tiêu đề; bảng có thể bị ngắt trang | Sinh lại cả 4 bảng từ CSV chuẩn, thêm cột Inputs, cột Score (Bảng 3) và Bias (Bảng 4), tiêu đề trên và chú thích dưới bảng, kiểu ba đường; `audit_project.py` kiểm tra mọi ô kể cả nhãn hàng |
| Toàn dự án | Trùng lock file, PDF/HTML cũ và archive lặp | Giữ một requirements phân tích và một requirements soạn thảo, log dọn dẹp và backup riêng |

## ĐÃ XÁC MINH bằng kiểm tra có thể chạy lại

Các báo cáo JSON ở `verification/` là bằng chứng tính toán cụ thể; không dùng lời khẳng định CI thành công thay cho báo cáo. `audit_project.py` đối chiếu mọi ô số của bốn bảng với CSV. Các script kiểm tra hai địa điểm dựng lại nhãn từ dữ liệu gốc, tính lại chỉ số, khoảng dự báo và kiểm tra tính nhân quả theo thời gian. `test_integrity.py` thử các tình huống sai có thể dẫn đến báo cáo tái lập giả. Thư mục đầu ra mới khác hoàn toàn thư mục kết quả chuẩn.

## CÓ DẤU HIỆU VẤN ĐỀ còn phải diễn giải thận trọng

Chỉ năm cụm vượt ngưỡng ở Đan Mạch; các cửa sổ chồng lấn không độc lập. Các thí nghiệm bổ sung và cấu hình được mở rộng sau khi xem kết quả cũ, nên không diễn giải kiểm định xác nhận. Giá trị mưa quá khứ và calibration thích ứng không đồng nhất giữa địa điểm. Chênh lệch chỉ số không chứng minh nguyên nhân vật lý.

## CHƯA THỂ XÁC MINH từ dữ liệu hiện có

Không xác nhận được ngữ nghĩa lấy trung bình theo giờ của cảm biến Đan Mạch, múi giờ/độ trễ thực của nguồn Đức, chất lượng cảm biến, cơ chế missing-not-at-random, dự báo khí tượng đúng vintage đủ 12 giờ, dung tích bể và ràng buộc điều khiển, lợi ích xử lý/tiết kiệm năng lượng, tính đại diện quần thể, tính mới tuyệt đối hoặc khả năng được tạp chí chấp nhận. Email và phê duyệt tác giả chưa có. Không điền hoặc mô phỏng các thông tin này.

## Khôi phục

Trước dọn dẹp, đã lưu Git bundle toàn lịch sử và ZIP các tệp nghiên cứu địa phương ngoài bộ nộp. `verification/cleanup_register.json` nêu từng tệp loại khỏi bản hiện hành và hash trước sửa. Không xóa dữ liệu gốc, không force-push, không xóa release lịch sử. Môi trường Python và bản chạy lại đầy đủ lưu ngoài bộ nộp để tránh trùng lặp.
