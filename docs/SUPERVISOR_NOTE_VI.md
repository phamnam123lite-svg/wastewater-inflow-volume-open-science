# Bản final gửi giảng viên - hướng dẫn đọc

Tác giả: **Viet Nam Tran**, Faculty of Environment, Van Lang University, Ho Chi Minh City, Vietnam. Phiên bản v0.2.0, ngày 10/11/2026.

## Hồ sơ nên gửi

1. manuscript_FINAL.pdf: bản thảo tiếng Anh 16 trang, 218 từ Abstract, 4 bảng và 5 hình.
2. RESPONSE_TO_AUDIT_VI.md: đối chiếu từng phát hiện và giới hạn chưa khắc phục được bằng dữ liệu hiện có.
3. supplementary_v0.2.0.zip và link GitHub https://github.com/phamnam123lite-svg/wastewater-inflow-volume-open-science/releases/tag/v0.2.0: dữ liệu nguồn, code, numerical references, figure assets và kiểm tra tái lập.

## Điểm sửa làm thay đổi nội dung khoa học

Mô hình historical HGB mới có MAE 2.280,1 m³ so với 3.406,6 của baseline 24-hour mean; cấu hình legacy là 7.607,1. Vì vậy paper không còn dùng thất bại của cấu hình legacy để suy ra giới hạn của historical information. Flow/calendar HGB tốt hơn baseline ở cả 3 temporal origins, nhưng thêm thời tiết quá khứ không cải thiện nhất quán; kết quả 24 giờ vẫn không tốt hơn baseline. Oracle tương lai chỉ để chẩn đoán.

Khoảng dự báo historical HGB có coverage 83,7% toàn tập nhưng 21,0% high-volume; rolling calibration tăng lên 88,8% và 46,9%. Chỉ có 81 cửa sổ chồng lấn trong 5 episode. Kết luận được giới hạn theo đúng số sự kiện đó.

Đã chạy lại trong Python 3.11.9 mới cài thư viện theo lock. **34 CSV trùng số học, maximum absolute difference 0.0.** Đây là reproduction bằng cùng code/data, không phải xác nhận độc lập của một nhóm nghiên cứu khác. Ngoài 34 CSV chính, đã chạy lại 12 CSV kiểm định nhà máy Đức, cũng khớp tuyệt đối; tổng cộng 46 bảng. Kiểm định Đức là refit tại site thứ hai, không phải zero-shot transfer. Tất cả phân tích revision là hồi cứu vì kết quả cũ đã được xem.

## Những việc cần người thật quyết định trước khi nộp tạp chí

- Bổ sung email của corresponding author. Không tự suy đoán email.
- Tác giả và giảng viên đọc, xác nhận đóng góp tác giả, thông tin affiliation, phát biểu khoa học và việc khai báo AI. Không đưa tên giảng viên vào đồng tác giả nếu chưa có đóng góp/đồng ý phù hợp.
- Chọn tạp chí và chỉnh theo hướng dẫn riêng. Không có khẳng định đã xác minh đủ tất cả yêu cầu submission hoặc quartile hiện hành.
- Cân nhắc yêu cầu DHI giải thích hourly rate là mean hay sample, timestamp và latency; đã bổ sung site Đức, nhưng vẫn cần thêm nhà máy và một thử nghiệm vận hành tương lai nếu muốn nâng mức bằng chứng.
- Nếu cần DOI cho code/paper, archive release sau khi tác giả duyệt. DOI nguồn dữ liệu không được dùng như DOI của nghiên cứu này.

Tác giả đã trả lời không có funding/COI/đồng tác giả thêm. Các khai báo tương ứng đã đưa vào manuscript. Việc không có funding không thay cho thông tin correspondence và xác nhận author contributions.

## Định hướng tạp chí để thảo luận, không phải cam kết chấp nhận

- **Journal of Hydroinformatics:** phù hợp chủ đề dự báo, dữ liệu, uncertainty và hệ thống nước; ưu tiên cân nhắc nếu giảng viên đồng ý định vị đây là benchmark/audit. [Aims & Scope](https://iwaponline.com/jh/pages/Aims_and_Scope) đã truy xuất qua nguồn IWA ngày 10/11/2026. Đóng góp hiện tại vẫn cần bảo vệ trước phản biện về tính mới và khả năng khái quát từ hai site.
- **Water Science & Technology:** lĩnh vực wastewater phù hợp, nhưng paper cần liên hệ kỹ thuật vận hành đủ rõ. [Trang tạp chí](https://iwaponline.com/wst); trang hướng dẫn chi tiết trả 403 trong lần kiểm tra này.
- **Environmental Modelling & Software:** chỉ nên cân nhắc nếu tiếp tục mở rộng từ hai site hiện có thành đánh giá phương pháp và ứng dụng vận hành mạnh hơn. [Trang chính thức](https://www.sciencedirect.com/journal/environmental-modelling-and-software); trang scope chi tiết trả 403 trong lần kiểm tra này. Không dùng website mạo danh/nguồn trung gian để khẳng định yêu cầu tạp chí.

Phân hạng Q1/Q2 phụ thuộc năm, ngành và hệ JCR/SJR; chưa xác minh độc lập phân hạng hiện hành trong lần sửa này. Không đưa quartile chưa kiểm chứng vào cover letter. Hồ sơ chưa được gửi cho giảng viên/tạp chí bằng công cụ; chỉ được chuẩn bị và cập nhật kho công khai theo yêu cầu.

## Giới hạn khoa học đã được xử lý thêm theo yêu cầu

Đã bổ sung dữ liệu độc lập về nguồn và địa điểm: Köln-Weiden, Đức, DOI 10.5281/zenodo.6992694, CC BY 4.0. Có 17.484 train, 2.124 calibration và 6.588 test; high-volume gồm 700 cửa sổ/41 episode. Kiểm tra trực tiếp 8.712 target từ 48 mẫu 15 phút, dùng hệ số đổi đơn vị 900/1000. Không khẳng định múi giờ chưa được nguồn xác nhận.

Kết quả mới không chỉ củng cố paper mà còn buộc thu hẹp kết luận: mưa quá khứ có ích tại Đức; annual predictors không gây suy giảm mạnh giống Đan Mạch; rolling calibration giảm coverage tại Đức. Paper final đã phản ánh đầy đủ các khác biệt này. Chi tiết và trạng thái từng giới hạn nằm trong LIMITATIONS_RESOLVED_VI.md.
