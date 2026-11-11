# Trạng thái bộ nộp

Ngày 11 tháng 11 năm 2026. Thư mục này là bộ nộp hoàn chỉnh, phiên bản 0.2.1.

## Nộp cho giảng viên

- Nộp nguyên thư mục. Bản để đọc và nhận xét: `paper/manuscript.docx`; bản PDF cùng nội dung: `paper/manuscript.pdf`.
- Hướng dẫn thẩm định: `HUONG_DAN_THAM_DINH_VI.md`. Kết quả kiểm định: `docs/FINAL_AUDIT_VI.md`, `docs/SECTION_AUDIT.md`.
- Bản công khai: https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science, nhánh `main`, thẻ `v0.2.1`.

## Đã kiểm tra

- Lần chạy lại đầy đủ từ môi trường Python 3.11.9 mới: PASS, 46 bảng CSV, sai khác số học lớn nhất 0.0 (`verification/final_run_summary.json`).
- Cả 4 bảng trong paper được sinh lại trực tiếp từ CSV chuẩn. `verification/paper_code_audit.json` xác nhận 27 hàng bảng, 129 ô số, cùng nhãn hàng và mã biến đầu vào, khớp với `results/` và `external_results/`. Các số liệu trong phần văn bản cũng đã được đối chiếu lại thủ công; không có sai lệch.
- 10 tài liệu tham khảo đã đối chiếu với trang nhà xuất bản, Zenodo và arXiv.
- Bố cục Word đã kiểm tra bằng bản dựng LibreOffice (15 trang, mỗi bảng nằm trọn một trang). Word hoặc WPS có thể ngắt trang hơi khác.
- Phép so sánh từng điểm ảnh của 5 hình chỉ chạy trong `reproduce.py` (trên kết quả chạy lại), nên tệp kiểm tra bảng ở đây ghi 0 hình; điều này không phải lỗi.

## Thay đổi ở bản cuối (không đổi số liệu hay kết luận)

- Bảng: tên mô hình khớp nhãn trong hình; thêm cột Inputs; Bảng 3 thêm interval score; Bảng 4 thêm Bias; tiêu đề trên, chú thích dưới bảng; kiểu bảng ba đường, số căn phải, dấu trừ chuẩn.
- Văn bản: làm rõ một câu ở mục 3.4 và một câu ở Kết luận; bổ sung lời cảm ơn nguồn dữ liệu Đức và công khai công cụ AI; sửa tên tác giả Sølve Eidnes trong BibTeX.
- Thêm `.gitattributes` để giữ nguyên byte của dữ liệu trên mọi hệ điều hành (mã hash không đổi khi tải từ GitHub).

## Chưa có, cần tác giả bổ sung

- Email liên hệ và xác nhận phê duyệt nội dung của tác giả.
- Đây là bộ gửi giảng viên thẩm định, chưa phải tuyên bố được tạp chí chấp nhận.

Các giới hạn khoa học được nêu trong paper và `docs/FINAL_AUDIT_VI.md`. Không có kết quả vận hành hoặc thí nghiệm mới được giả lập.
