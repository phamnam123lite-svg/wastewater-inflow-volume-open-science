# Giới hạn khoa học: đã xử lý đến đâu?

Ngày 10/11/2026. Không thể biến thiếu bằng chứng thành bằng chứng bằng cách sửa câu chữ. Bản final xử lý các giới hạn bằng phân tích mới hoặc thu hẹp phát biểu có căn cứ.

| Giới hạn | Hành động đã thực hiện | Trạng thái sau sửa |
|---|---|---|
| Một nhà máy | Thêm Köln-Weiden, Đức, DOI 10.5281/zenodo.6992694; mô hình refit trên 2017-2018, calibration quý 1/2019, test phần còn lại 2019 | ĐÃ GIẢM: hai site; chưa đại diện mọi công nghệ/catchment |
| Chỉ 5 episode high-volume | Thêm 700 cửa sổ trong 41 episode tại Đức; không gộp thành sự kiện độc lập | ĐÃ GIẢM: nhiều episode hơn; vẫn có phụ thuộc |
| Kết luận model ranking do loss/calendar | Grid trong development, matched 2×2, 3 origins; thử ở site thứ hai | ĐÃ SỬA: annual feature bất lợi mạnh tại Danish không lặp lại tại German; không đưa quy tắc phổ quát |
| Mưa quá khứ “không hữu ích” | Matched information tests hai site | ĐÃ SỬA: mưa có ích rõ ở German, không nhất quán ở Danish; kết luận phụ thuộc site |
| Adaptive intervals luôn tốt hơn | So pooled/wet-dry/rolling theo maturity ở cả hai site | ĐÃ BÁC BỎ TỔNG QUÁT HÓA: rolling cải thiện Danish nhưng giảm German coverage |
| Đơn vị, target, giờ tổng hợp | German header L/s, mm/min; quy đổi và tích phân trực tiếp 48 mẫu; right-closed aggregation; không gắn UTC khi chưa biết | ĐÃ KIỂM TRA tính toán; semantics cảm biến và timezone vật lý còn CHƯA XÁC MINH |
| Latency lịch sử | Refit delay 1/2 giờ tại primary Danish | ĐÃ ĐỊNH LƯỢNG độ nhạy; actual telemetry latency chưa biết |
| Dữ liệu thiếu/QC | Không nội suy target; complete windows; no-QC refit; báo counts; German chỉ loại nonfinite/negative | ĐÃ ĐÁNH GIÁ; không chứng minh missing-at-random |
| Bootstrap và calibration rank | Sửa rank, edge cases; fixed circular blocks uniform inclusion; dependence sensitivity và synthetic diagnostic | ĐÃ SỬA code; tính stationarity/coverage thực vẫn không bảo đảm |
| Khả năng tái lập | Môi trường sạch; 34+12 CSV khớp; 2 bộ reference; full predictions và audit logs | ĐÃ XÁC MINH reproduction; không thay thế independent human review |
| Forecast mưa thực 12h | Kiểm tra archive 6992869 và checksum; chỉ có numbered columns chưa xác minh horizon/issue semantics phù hợp | CHƯA ĐỦ BẰNG CHỨNG; không tráo future observations thành operational forecasts |
| Hiệu quả xử lý, storage, energy | Bỏ mọi suy luận forecast error=storage saving; xác định cần geometry, controls, initial state, constraints, effluent/energy endpoints | CHƯA THỂ KIỂM ĐỊNH bằng nguồn hiện có; không phải kết quả paper |
| Tính mới | Bổ sung prior art gần; công khai reuse datasets và targeted review | Đóng góp là audit hai site có tái lập, không phải thuật toán mới hay “đầu tiên” |

Các phần không giải quyết được bằng dữ liệu hiện có cần nhà cung cấp xác nhận hoặc chiến dịch đánh giá mới. Không gửi liên hệ, cam kết hợp tác hoặc hồ sơ tạp chí thay tác giả. Trước khi nộp: email correspondence, xác nhận đóng góp tác giả, phê duyệt khoa học của tác giả/giảng viên, và kiểm tra yêu cầu của tạp chí đã chọn.
