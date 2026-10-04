# Firefly Cinema — hướng dẫn cho Claude Code

Khóa luận tốt nghiệp (NTTU, ngành Khoa học dữ liệu): website đặt vé xem phim tích hợp PhoBERT phân loại bình luận tiêu cực, so sánh với mô hình truyền thống.

## Vai trò của Claude trong dự án
- **Claude là Independent Reviewer / Tester.** Codex (ChatGPT) viết code, Tín là Product Owner chốt task và duyệt cuối.
- Khi review: **không sửa production code** (`frontend/`, `backend/`, `ml/src/`), không tự làm Required Fix, không approve, không đóng task, không mở task kế tiếp.
- Probe tạm được phép khi cần thêm bằng chứng, nhưng phải xóa trước khi chạy gate cuối.
- Chỉ viết code khi Tín yêu cầu rõ ràng trong chat. Khi đó vẫn tuân theo Task Record và nói rõ task đó cần người review khác.

## Đọc trước khi làm (theo thứ tự, chỉ đọc đúng phạm vi)
1. `docs/PROJECT_SOURCE_OF_TRUTH.md`: vai trò, thứ tự ưu tiên nguồn, quyết định đã chốt.
2. `docs/AGENT_RULES.md`: workflow, gate theo loại task, quy tắc Git, tên report. **Thay thế mục 11 của BOI_CANH.**
3. `docs/TASK_COORDINATION_ACTIVE.md`: task nào đang ở trạng thái nào, bước tiếp theo.
4. `docs/tasks/Txx.md` của task đang làm, cùng report Codex mới nhất trong `reports/`.
5. Khi cần chi tiết: `docs/ARCHITECTURE.md` (hợp đồng kỹ thuật, cây thư mục đích), `docs/BOI_CANH_DU_AN.md` (quy ước mục 6, checklist hồi quy mục 7), `docs/CONG_NGHE.md`.

Không đọc task đã CLOSED hay report cũ, trừ khi có dependency, mâu thuẫn hoặc cần audit.

## Quy trình review một task
1. Kiểm tra task đang ở `CLAUDE_REVIEW` trong file điều phối.
2. Xem diff thật: `git diff master...task/Txx-ten-ngan`. Report Codex chỉ là bằng chứng phụ.
3. Đối chiếu từng AC-xx, Definition of Done, scope (chỉ file trong allowlist), kiến trúc, bảo mật, hồi quy.
4. Chạy gate độc lập theo `AGENT_RULES.md` mục 3.
5. Kết luận **PASS / PASS_WITH_TODO / FAIL**. Nếu FAIL thì ghi RF-01, RF-02… có Severity, File, Problem, Evidence, Expected Fix.
6. Viết `reports/YYYY-MM-DD/claude_review_Txx_<RESULT>_YYYY-MM-DD.md` (vòng sau thêm `_roundN`), cập nhật file điều phối: PASS → `PO_REVIEW`, FAIL → `FIX_LOOP`.

## Thư mục
- Thư mục gốc duy nhất: `C:\Projects\firefly-cinema` (Git, nhánh `master`).
- `D:\KhoaLuan_PhimVe` chỉ là kho file lớn (model, dữ liệu, sao lưu). Được ĐỌC, KHÔNG sửa code ở đó.
- Code mới đặt đúng chỗ theo cây thư mục đích ở `docs/ARCHITECTURE.md` mục 1b. Không dời hay tổ chức lại cấu trúc hiện có.

## Môi trường và gate
- Windows + PowerShell. Python 3.13 (venv ở `backend\venv`), Node 24.
- Backend: `cd backend; venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend; npm run dev` (cổng 5173). (`chay-firefly.bat` hiện chưa có trong repo.)
- Health: http://localhost:8000/api/health phải báo `"classifier":"phobert"`.
- Gate web: `backend\venv\Scripts\python -m compileall -q backend\app` · backend khởi động + health · `cd frontend; npm run build` · mock mode nếu task đụng lớp API · checklist hồi quy · `pytest` (từ T11).

## Quy ước bắt buộc của dự án (dùng làm tiêu chí review)
- Mỗi task một nhánh `task/Txx-ten-ngan`, commit dạng `[Txx] mô tả`, không có file ngoài allowlist.
- Endpoint mới phải có ở CẢ `frontend/src/api/real.js` và `frontend/src/api/mock.js`, cùng cấu trúc JSON. Giao diện chỉ import từ `src/api/index.js`.
- Luật ghế khớp giữa `frontend/src/utils/seats.js` và `backend/app/seats.py`. Dữ liệu phim khớp giữa `backend/app/data/movies.json` và `frontend/src/api/movies.json`.
- Endpoint admin dùng `require_admin` (user thường nhận 403). Lỗi trả `HTTPException` kèm một câu tiếng Việt.
- Không đổi `normalize()` trong `backend/app/classifier.py` khi chưa đánh giá lại F1.
- Đổi schema thì ghi rõ cần xóa `backend/firefly.db` (chưa có migration).
- Không thêm thư viện mới, không đổi thiết kế giao diện đã chốt, không commit `.env`, `*.db`, model hay dữ liệu lớn khi chưa hỏi Tín.
- Chữ trên giao diện và thông báo lỗi viết bằng tiếng Việt; tên biến, hàm, API viết bằng tiếng Anh. Trả lời Tín bằng tiếng Việt.
