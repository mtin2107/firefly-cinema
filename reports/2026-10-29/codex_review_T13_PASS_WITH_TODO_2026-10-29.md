# Codex independent review T13 — PASS_WITH_TODO

Ngày: 29/10/2026. Reviewer: Codex; implementation: Claude; approver: Tín.
Reviewed HEAD `915bd679b124cf5d259ebb04157ffa694dba675e`; diff `git diff master...task/T13-v1` (master db4b452). Không merge/tag; không sửa sản phẩm.

## Kết luận
PASS_WITH_TODO. Required Fix: 0. T13 → PO_REVIEW. AC-01 và AC-03 đạt độc lập; AC-02 phần tải lại Drive và AC-04 tag là PO action, không tính FAIL.

## Phạm vi và tài liệu
23 file: tài liệu, 14 ảnh, điều phối, report Claude (đổi vai theo lệnh PO), cùng ngoại lệ duy nhất requirements: thêm đúng `tzdata==2026.5`. Không có code app/frontend, model, DB hoặc .env trong diff.
Đã đọc T13, điều phối, report implementation và T31 mục 13. Bảng F1 README khớp làm tròn 4 chữ số từ comparison_B.csv/model_card_B; A research và checkpoint backend được phân biệt trong model_card_A/SAO_LUU. T15 khớp word_segment.csv và model_card_A: movie 0.864865/0.885417, phone 0.919540/0.923316, thêm 1.712811 ms/câu. Mốc hằng và chênh lệch miền khớp. Hạn chế bao phủ T12 TODO-01, audit OBS-01..04/07/08 và T28 OBS-01..03 theo PO T31.

## AC-01 độc lập
Clone mới `C:\Temp\firefly-review-20261029`, nhánh task/T13-v1, Python 3.13 venv mới; chép backend/models và ml/artifacts/baselines từ backup/v1.0. Không chép DB thật. .env tạo từ .env.example với SECRET_KEY và ADMIN_PASSWORD thử; không đọc backend/.env thật. DB và uploads nằm trong clone.
- Trước cài: `ZoneInfo('Asia/Ho_Chi_Minh')` tái hiện ModuleNotFoundError tzdata → ZoneInfoNotFoundError.
- Cài torch CPU 2.11.0 và requirements-ml/dev; sau cài tzdata 2026.5, ZoneInfo thành công; pip check: No broken requirements found.
- Ghi chú thao tác reviewer: hai lệnh pip ban đầu bị chạy chồng thời gian; cả hai hoàn tất exit 0, kết quả cuối torch 2.11.0+cpu và pip check đạt. Một lần pytest gọi sớm khi pip chưa xong lỗi thiếu fastapi, không tính gate; lần đầy đủ sau đó đạt như dưới.
- compileall -q app: exit 0.
- pytest -q: **286 passed, 1 warning, 195.40s**, exit 0. Warning Starlette/AnyIO deprecation.
- uvicorn thật port 18013: startup complete; GET /api/health status ok, classifier/active_model phobert_b, active_version phobert-B-2026-10-09, classifier_error null. phobert, phobert_b, svm, lr, nb, keyword đều available=true/error=null; A lazy loaded=false là bình thường.
- npm install đạt; build VITE_USE_MOCK=false: exit 0, index-CuKoJ6_Y.js 457.21 KB / gzip 156.31 KB. Build VITE_USE_MOCK=true: exit 0, index-CCO_Q3RT.js 485.35 KB / gzip 165.32 KB. CSS 71.38 KB / gzip 14.78 KB.
- Không thực hiện hồi quy browser đầy đủ trong review này; AC-01 kiểm theo các lệnh và health PO yêu cầu.

## Sao lưu và ảnh
Đối chiếu từng 9 dòng hash trong SAO_LUU với sha256.csv và Get-FileHash file thật cả repo lẫn backup: **9/9 khớp cả ba nguồn**, gồm 4 safetensors, 3 joblib, DB và sidecar. Không đọc nội dung DB thật, không thay đổi file backup. Không xác nhận lại toàn bộ 72 hash ngoài bảng.
Xem contact sheet đủ 14 ảnh, phóng riêng ảnh tài khoản và soát vé: tên rõ nghĩa, đúng trang, có Thống kê cảm xúc và So sánh mô hình. Dữ liệu tài khoản/vé là demo; không thấy password/API key/token. Footer có thông tin liên hệ tác giả (TODO-02).

## TODO không chặn
- TODO-01 Low: CONG_NGHE ghi mock 485.24 KB / gzip 165.27 KB, lần build độc lập ra 485.35 / 165.32. Cập nhật mốc hoặc ghi rõ commit/cấu hình đo; real/CSS tái lập đúng. Không sửa tài liệu sản phẩm trong review.
- TODO-02 Low: ảnh 10 và 13 có email/số điện thoại tác giả ở footer. Đây là nội dung liên hệ công khai của giao diện, chưa có bằng chứng là bí mật; PO xác nhận giữ khi công bố hoặc yêu cầu che/cắt. Không lặp lại thông tin cá nhân trong báo cáo.

## PO action
Drive upload/download + AC-02, T00 zip, video, bản ngoài máy và tag AC-04 giữ theo SAO_LUU. Không tự đóng hay thay disposition các TODO cũ. Không mở task mới.
