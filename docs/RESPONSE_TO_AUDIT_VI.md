# Đối chiếu xử lý toàn bộ 19 phát hiện - final v0.2.0

Đã sửa và bổ sung nghiên cứu trên hai nguồn/địa điểm: Đan Mạch và Köln-Weiden, Đức. Bản thảo final 16 trang, Abstract 218 từ, 4 bảng, 5 hình, 10 references chính. Chạy lại 34 CSV chính và 12 CSV external, tất cả sai số số học tối đa 0.0. Đây là computational reproduction, không phải phản biện độc lập của con người.

Các trạng thái dưới đây phân biệt thay đổi đã kiểm chứng với giới hạn chưa có nguồn xác nhận. Xem thêm LIMITATIONS_RESOLVED_VI.md.

## A01 - Major - ĐÃ SỬA

**Vị trí:** Methods 2.4; Results 3.2; configuration_sensitivity.csv.

**Xử lý và bằng chứng:** Mở grid loss/annual bằng development folds; giữ legacy và so sánh 2×2 cố định. Viết lại kết luận theo MAE 2.280,1 thay cho 7.607,1 m³.

**Giới hạn còn lại:** Nghiên cứu vẫn hồi cứu; cần kiểm định dữ liệu chưa xem.

## A02 - Major - ĐÃ BỔ SUNG TEMPORAL VÀ EXTERNAL SITE

**Vị trí:** Methods 2.4, 2.7; Tables 2, 4; external_results/.

**Xử lý và bằng chứng:** Thêm 3 Danish origins và site Đức (17.484 train/2.124 cal/6.588 test). Refit tại site thứ hai; 12 CSV tái lập đúng.

**Giới hạn còn lại:** Chưa có prospective trial; không phải zero-shot transfer.

## A03 - Moderate - ĐÃ SỬA

**Vị trí:** Results 3.2-3.3; bootstrap.csv.

**Xử lý và bằng chứng:** Thêm mean24-persistence, model-mean24, oracle-mean24 và matched information sets.

**Giới hạn còn lại:** Khoảng bootstrap chỉ là sensitivity; không tuyên bố ý nghĩa xác nhận.

## A04 - Moderate - ĐÃ SỬA THUẬT TOÁN; NÊU GIỚI HẠN

**Vị trí:** run_analysis.py:circular_blocks; Methods 2.6.

**Xử lý và bằng chứng:** Dùng block cố định circular trong contiguous runs; kiểm tra mọi điểm có inclusion bằng nhau; AR(1) diagnostic công khai.

**Giới hạn còn lại:** Wrapping tạo nối giả; stationary bootstrap assumptions không được bảo đảm ở dữ liệu thật.

## A05 - Major - ĐÃ MỞ RỘNG BẰNG CHỨNG SỰ KIỆN

**Vị trí:** Figure 5; Section 3.6; external_episodes.csv.

**Xử lý và bằng chứng:** Giữ 5 Danish episodes và thêm 41 German episodes/700 cửa sổ high; báo sự khác biệt coverage giữa site.

**Giới hạn còn lại:** Các episode vẫn có thể phụ thuộc; không phải 700 sự kiện độc lập.

## A06 - Moderate - ĐÃ SỬA DIỄN GIẢI

**Vị trí:** Methods 2.5-2.6; Discussion 4.3.

**Xử lý và bằng chứng:** Phân biệt subgroup Y tương lai và wet state từ X tại issue; bỏ ý bảo đảm conditional coverage.

**Giới hạn còn lại:** High-volume coverage là stress diagnostic hồi cứu.

## A07 - Moderate - ĐÃ SỬA VÀ KIỂM TRA

**Vị trí:** exact_quantile; Table 3; verification.json.

**Xử lý và bằng chứng:** Dùng đúng order statistic k, infinity khi k>n, từ chối rỗng/nonfinite; tính lại mọi khoảng.

**Giới hạn còn lại:** Mean24 pooled coverage hiện là 87,1296%, không còn 87,5%.

## A08 - Major - ĐÃ BỔ SUNG; THU HẸP TÍNH MỚI

**Vị trí:** Introduction; References 5-6; LITERATURE_MATRIX.md.

**Xử lý và bằng chứng:** Thêm Pearson 2025, Lee & Lee 2026; nói rõ không mới ở rainfall/uncertainty/adaptive calibration.

**Giới hạn còn lại:** Rà soát có mục tiêu, chưa phải systematic review đầy đủ.

## A09 - Major - ĐÃ KIỂM TRA ĐƠN VỊ VÀ NHÂN QUẢ; CÒN METADATA

**Vị trí:** Methods 2.3, 2.7; verify_external.py.

**Xử lý và bằng chứng:** Danish target được gọi approximation, có delay sensitivity. German CSV ghi L/s và mm/min; 8.712 target kiểm tra trực tiếp từ 48 mẫu quarter-hour.

**Giới hạn còn lại:** Chưa xác nhận DHI averaging/latency; German timezone không suy đoán.

## A10 - Moderate - ĐÃ BỔ SUNG

**Vị trí:** Methods 2.2; sensitivity.csv.

**Xử lý và bằng chứng:** Refit không QC; 4.656 train/2.126 cal; 2.160 test không đổi; MAE history 2.252,1 m³.

**Giới hạn còn lại:** Không chứng minh missingness không gây bias hay heuristic QC đúng.

## A11 - Major - ĐÃ KHẮC PHỤC TRUY CẬP

**Vị trí:** Repository/release v0.2.0; publication verification.

**Xử lý và bằng chứng:** Chủ repo đã chuyển public; cuối quy trình kiểm tra anonymous tải manuscript và supplement khớp hash.

**Giới hạn còn lại:** GitHub không phải DOI archive; cần duy trì public và cân nhắc archive DOI sau duyệt.

## A12 - Major - ĐÃ SỬA VÀ TÁI HIỆN

**Vị trí:** compare_reproduction.py; verify_results.py; reproduction.json.

**Xử lý và bằng chứng:** Bỏ đường dẫn máy cố định; manifest bắt buộc 34 CSV; fail rỗng/thiếu/schema/sai số; 6 negative tests.

**Giới hạn còn lại:** Tolerances có khai báo; khác platform có thể cho sai số nhỏ.

## A13 - Moderate - ĐÃ SỬA TUYÊN BỐ

**Vị trí:** Introduction; Methods; PROTOCOL_DEVIATIONS.md.

**Xử lý và bằng chứng:** Không gọi preregistered/prespecified confirmatory; nêu test cũ đã xem trước khi mở grid.

**Giới hạn còn lại:** Không thể khôi phục tính độc lập của dữ liệu đã xem.

## A14 - Moderate - ĐÃ MỞ RỘNG VÀ TÁI HIỆN HAI SITE

**Vị trí:** verification.json; external_verification.json; claim_evidence_map.csv.

**Xử lý và bằng chứng:** 34 CSV chính + 12 CSV external tái lập với chênh lệch tối đa 0.0; kiểm tra metric, interval, target, causality.

**Giới hạn còn lại:** Cùng code/workflow, chưa phải independent human review.

## A15 - Moderate - ĐÃ SỬA

**Vị trí:** build_paper.py; requirements-docs.txt; README.

**Xử lý và bằng chứng:** Font từ matplotlib; không hardcode Windows; tách reportlab; hướng dẫn chạy Python tương đối.

**Giới hạn còn lại:** PDF byte-for-byte không được hứa giữa platform; số liệu đã đối chiếu.

## A16 - Minor - ĐÃ SỬA TRÌNH BÀY

**Vị trí:** manuscript_FINAL.pdf; Figures 1-5; Tables 1-3.

**Xử lý và bằng chứng:** Mọi hình/bảng có gọi trong text; caption gắn bảng; kiểm tra ảnh render cả 15 trang.

**Giới hạn còn lại:** Giảng viên/tạp chí có thể yêu cầu format riêng.

## A17 - Minor - ĐÃ SỬA

**Vị trí:** Figure 1; Figures 2-5; Methods 2.3.

**Xử lý và bằng chứng:** Mưa ghi hourly precipitation mm; split ghi rõ; biểu đồ hạng mục dùng cột/điểm; phương trình và đơn vị thống nhất.

**Giới hạn còn lại:** Đơn vị volume vẫn có điều kiện về aggregation của nguồn.

## A18 - Minor - ĐÃ BỔ SUNG MỘT PHẦN

**Vị trí:** Funding; competing interests; AI disclosure; supervisor note.

**Xử lý và bằng chứng:** Theo thông tin tác giả: không funding/COI/đồng tác giả thêm; giữ đúng tên và affiliation.

**Giới hạn còn lại:** Chưa có email; author contributions và phê duyệt cuối phải được người thật xác nhận.

## A19 - Minor - ĐÃ SỬA

**Vị trí:** References; README; CHANGELOG.

**Xử lý và bằng chứng:** Ghi đầy đủ author list cho references; version cũ đánh dấu lịch sử; root dẫn bản mới.

**Giới hạn còn lại:** Không coi GitHub release là bài đã xuất bản hay DOI nghiên cứu.
