# Product Owner Review — T17 Chatbot AI tư vấn phim

- **Task:** T17 — Chatbot AI tư vấn phim, chỉ tư vấn/chỉ đọc
- **Ngày quyết định:** 13/10/2026
- **Approver:** Tín (Product Owner)
- **Decision:** **APPROVED_WITH_NOTES — MVP/LOCAL ONLY**
- **Giới hạn quyết định:** Không phê duyệt production deployment hoặc chạy/migrate `backend/firefly.db` thật; không cấp phép xử lý T16 TODO-01.
- **Task branch:** `task/T17-chatbot-tu-van`
- **Reviewed commits:** Implementation `8ab2f00`; Claude Round 1 `7e161b1`; FIX TODO-03 `447c941`; Claude Round 2 / coordination `2f3b844`.
- **Đổi schema:** **Không**.
- **Git disposition:** `PO_REVIEW -> PO_APPROVED / PENDING_MERGE`. `DONE / CLOSED` **chỉ sau khi PO merge và kiểm chứng trên master**.

## Claude Result

- Round 1: **PASS_WITH_TODO**; Required Fixes 0; TODO-01..08; AC-02 chờ PO kiểm key thật.
- Round 2: **PASS_WITH_TODO**; Required Fixes **0**; TODO-03 **FIXED / VERIFIED BY CLAUDE**; phát hiện thêm TODO-09/10 (Low, MOCK-only).
- Báo cáo nguồn:
  - `reports/2026-10-13/claude_review_T17_PASS_WITH_TODO_2026-10-13.md`
  - `reports/2026-10-13/claude_review_T17_round2_PASS_WITH_TODO_2026-10-13.md`
  - `reports/2026-10-13/codex_fix_T17_round1_2026-10-13.md`

## Acceptance Criteria

**11/11 PASS — theo quyết định PO**, gồm AC-01, AC-03..11 dựa trên bằng chứng DEV/Claude và AC-02 dựa trên kiểm thử thủ công bằng Gemini thật của PO. Việc AC-02 PASS **không** đồng nghĩa Claude đã tự thực hiện gọi API thật.

### AC-02 — PO_ATTESTED / PASS

- Gemini `gemini-3.8-flash` trả HTTP 503 cả trong chatbot và lệnh gọi trực tiếp tại thời điểm thử; không quy kết do code hoặc khóa.
- PO đổi `CHAT_MODEL=gemini-3.5-flash-lite` trong `backend/.env` **cục bộ** (không commit key và không sửa source code). Gọi trực tiếp: `DIRECT_LITE=PASS`, `HAS_RESPONSE=True`.
- Backend chạy với SQLite tạm `firefly-t17-ac02-*`, frontend REAL; PO hỏi “Tối nay có phim gì?” và nhận danh sách phim/giờ chiếu.
- PO hỏi “Phim Thứ Bảy Không Ngủ chiếu mấy giờ ngày mai, giá bao nhiêu?”; chatbot trả ngày **14/10/2026**, **09:30 và 13:15**, **Phòng 2**, giá ghế thường **75.000đ**; PO đối chiếu và xác nhận khớp trang phim.
- Nút dẫn phim hoạt động, điều hướng đúng trang chi tiết.
- PO hỏi “Gợi ý phim hài đang chiếu”; Gemini trả **Thứ Bảy Không Ngủ** và có nút dẫn phim.
- Evidence là ảnh/trình tự thử nghiệm do PO cung cấp; không có truy vấn đối soát độc lập bằng key thật từ Claude.

## Definition of Done

**MET / ACCEPTED_WITH_NOTES** cho phạm vi MVP/local: backend tests 14/14 focused, 50/50 full; Python compile; backend Uvicorn SQLite tạm health `ok` / `phobert_b`; frontend REAL/MOCK build PASS; bảo mật/scope PASS; hồi quy 7/7 do PO xác nhận thủ công. Claude Round 2 cũng độc lập kiểm thử regression phù hợp phạm vi thay đổi MOCK.

## Security

- **PASS trong phạm vi đánh giá T17.** Chỉ có 3 read-only tools; xác thực, rate limit, xử lý lỗi nhà cung cấp và bảo vệ thông tin cá nhân đã qua review.
- Không commit `.env`, khóa API, SQLite thật, model/dữ liệu lớn; `backend/.env` được `.gitignore` bỏ qua.
- **API key bị xuất hiện trong ảnh trước đây:** PO xác nhận đã **thu hồi khóa cũ và thay khóa mới**. Đây là xác nhận của PO, không phải kiểm toán độc lập tại Google AI Studio.
- Không đưa khóa hoặc giá trị bí mật vào report, log chia sẻ, mã nguồn hay Git.
- Free Tier có giới hạn riêng theo account/project; PO đã xem dashboard và sử dụng model Flash-Lite cho local. Số hạn mức có thể thay đổi và phải kiểm tra lại tại thời điểm demo/deploy.

## Scope

**PASS.** Implementation thuộc allowlist T17, dependency backend thêm đúng `openai==3.29.0`, không chỉnh sửa schema. Fix Round 1 chỉ sửa `frontend/src/api/mock.js` cùng report/coordination. Không phê duyệt deploy thật qua quyết định này.

## Required Fixes

**0 open.** Không có RF bắt buộc từ Claude Round 1 hoặc Round 2.

## TODO Disposition — T17 TODO-01..10

| TODO | PO disposition | Chủ sở hữu / Điều kiện theo dõi |
|---|---|---|
| **TODO-01** | **ACCEPT_LATER (backlog CHATBOT_QUALITY — chưa authorize) / RISK_ACKNOWLEDGED** | So khớp thể loại REAL còn phụ thuộc hoa thường/dấu; PO đã thử thành công “Gợi ý phim hài đang chiếu” nhưng chưa kiểm mọi cách viết. Backlog chất lượng chatbot, task sau **chưa chỉ định/chưa authorize**; sửa nếu thấy model trả sai. |
| **TODO-02** | **ACCEPT_LATER (backlog CHATBOT_QUALITY — chưa authorize) / RISK_ACKNOWLEDGED** | Link phim đã hiện khi PO thử; cách model viết tắt/khác dấu có thể làm mất nút. Backlog độ bền link, chưa authorize task; sửa nếu ca thực tế thiếu link. |
| **TODO-03** | **FIX_NOW → FIXED / VERIFIED BY CLAUDE (Round 2)** | Commit `447c941`; câu “Gợi ý phim hài đang chiếu” trong MOCK trả đúng phim hài; giữ toàn bộ bằng chứng 12 probe × 2 trạng thái dữ liệu của Claude. **CLOSED**. |
| **TODO-04** | **ACCEPT_LATER (backlog UX_CHAT — chưa authorize)** | Nút chat khi kéo xuống đáy có thể che mép phải nút “Tiếp tục”; mặc định không che tâm, có thể kéo nút đi. Xử lý trong task UX tiếp theo **nếu được PO authorize**. |
| **TODO-05** | **ACCEPT_LATER (backlog CHAT_CONFIG — chưa authorize) / LOCAL_CONFIG_REQUIRED** | Dùng `CHAT_MODEL=gemini-3.5-flash-lite` trong `.env` local (PO đã kiểm API thực tế). **Mặc định trong code/`.env.example` vẫn là `gemini-3.8-flash`** và đã có 503; trước mọi demo/deploy phải xác minh model chạy được và khai báo rõ `CHAT_MODEL` tại môi trường. Quota/cost kiểm lại trong AI Studio; không mặc định model 3.8 được phê duyệt vận hành. |
| **TODO-06** | **ACCEPT_LATER (backlog VALIDATION_UX — chưa authorize)** | 11 tin trả thông báo 422 chung chung nhưng vẫn tiếng Việt, đúng AC-04; backlog UX validation nếu cần. |
| **TODO-07** | **WONT_FIX (cố ý tính lượt lỗi để chống spam) / BEHAVIOR_DOCUMENTED** | Lượt gọi 503 vẫn bị tính rate limit; chấp nhận để chống spam. Counter in-memory reset khi restart và không chia sẻ nhiều worker, chỉ phù hợp MVP/local; đánh giá lại trước scale. |
| **TODO-08** | **ACCEPT_LATER (T16 TODO-01 / DB_GATE) / DEPLOYMENT_BLOCKED** | Schema của DB thật `backend/firefly.db` chưa qua xử lý T16 TODO-01. **Không khởi động triển khai, thay schema, reset hoặc migrate DB thật theo T17**; yêu cầu backup/checkpoint và PO authorization riêng ở gate T16. TODO T16 giữ nguyên. |
| **TODO-09** | **ACCEPT_LATER (backlog MOCK_CHAT — chưa authorize)** | Regex “phim hài?” hoặc dấu câu liền có thể không lọc hài; “hai người” có thể bị hiểu nhầm. Sửa khi cải thiện bộ phân loại từ khóa MOCK; trước demo tránh ca chưa hỗ trợ hoặc chạy test đã xác nhận. |
| **TODO-10** | **ACCEPT_LATER (backlog MOCK_CHAT — chưa authorize)** | “Gợi ý phim gia đình” hoặc chữ “thương” có thể rơi vào nhánh giá. Cần sửa **trước khi** dùng kịch bản demo MOCK theo thể loại Gia đình; chưa phải RF chặn bản MVP/local với demo đã thử. |

**Tình trạng TODO:** 10/10 đã có PO disposition; TODO-03 đã thực hiện `FIX_NOW` và CLOSED/VERIFIED, TODO-07 `WONT_FIX` có lý do. Các mục `ACCEPT_LATER` được đưa vào nhóm backlog ghi tên ở bảng nhưng **chưa tạo/ủy quyền task mới** và không được coi là đã sửa. TODO-08 giữ nguyên **deployment gate**; không tạo task mới hay tự quyết định thời hạn backlog.

## Product Value / Notes

- Bot tiếng Việt tư vấn phim, suất chiếu, giá vé, link phim; không tự đặt vé.
- Free Tier phù hợp thử nghiệm nhỏ; hạn mức không đảm bảo tải sản xuất. Dữ liệu đầu ra AI vẫn có nguy cơ sai, cần đối soát trước hành động của người dùng.
- Trước demo phải xác minh `CHAT_MODEL` ở môi trường chạy đúng Flash-Lite hoặc model đã được kiểm thực tế; đảm bảo key có hiệu lực và không bị lộ. Không lưu chat/PII trong source hoặc report.

## Final Transition

**Decision: APPROVED_WITH_NOTES — MVP/LOCAL ONLY**.

1. `PO_REVIEW -> PO_APPROVED / PENDING_MERGE` sau khi PO tạo/commit report và cập nhật coordination.
2. **Chỉ Tín (PO)** thực hiện merge nhánh `task/T17-chatbot-tu-van` vào `master` sau khi rà soát Git sạch và phạm vi thay đổi.
3. Sau khi xác minh merge, cập nhật `docs/TASK_COORDINATION_ACTIVE.md` trên `master` thành `T17 = DONE / CLOSED`, `Current Active Task: NONE`, kèm merge hash/report. Không tự tag nếu chưa có quyết định mốc.
4. **Task kế tiếp: NOT SELECTED / NOT AUTHORIZED.** T12/T13 còn mâu thuẫn lịch sử/commit và Q4 chưa chốt; không tự mở task tiếp theo.
5. **Production deployment: NOT APPROVED**, chờ T16 DB gate + xác minh cấu hình/model/quota ở môi trường triển khai.

## PO Authorization Record

PO xác nhận qua cuộc trò chuyện ngày 13/10/2026: khóa API bị lộ đã thu hồi/thay mới; yêu cầu chuẩn bị quyết định `APPROVED_WITH_NOTES` và disposition toàn bộ TODO T17. **Việc thực thi bước xác nhận áp dụng trên máy PO là hành động phê duyệt cuối cùng đối với nội dung báo cáo này.**
