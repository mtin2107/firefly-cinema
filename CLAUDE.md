# Firefly Cinema — hướng dẫn cho Claude Code

Khóa luận tốt nghiệp (NTTU, ngành Khoa học dữ liệu): website đặt vé xem phim tích hợp PhoBERT phân loại bình luận tiêu cực, so sánh với mô hình truyền thống.

## Đọc trước khi làm bất cứ việc gì
- `docs/BOI_CANH_DU_AN.md`: nguồn sự thật về kiến trúc, quy ước bắt buộc (mục 6), checklist hồi quy (mục 7), kế hoạch T00–T15 (mục 9), quy trình task (mục 11).
- `docs/CONG_NGHE.md`: công nghệ và phiên bản đang dùng.
- `docs/tasks/Txx.md`: đặc tả của task đang làm (nếu đã có).

## Thư mục
- Thư mục gốc duy nhất: `C:\Projects\firefly-cinema` (Git, nhánh `master`).
- `D:\KhoaLuan_PhimVe` chỉ là kho file lớn (model, dữ liệu, sao lưu). Được ĐỌC để gom mã train cũ vào `ml/` (task T00), KHÔNG sửa code ở đó.

## Môi trường
- Windows + PowerShell. Python 3.13 (venv ở `backend\venv`), Node 24.
- Backend: `cd backend; venv\Scripts\Activate.ps1; uvicorn app.main:app --reload --port 8000`
- Frontend: `cd frontend; npm run dev` (cổng 5173). Hoặc bấm đúp `chay-firefly.bat`.
- Kiểm tra: http://localhost:8000/api/health phải báo `"classifier":"phobert"`.

## Quy tắc làm việc
- Chỉ làm MỘT task mỗi lần, trên nhánh `task/Txx-ten-ngan`; commit dạng `[Txx] mô tả`. Không sửa file ngoài phạm vi task.
- Thêm endpoint thì phải thêm vào CẢ `frontend/src/api/real.js` và `frontend/src/api/mock.js`, cùng cấu trúc JSON.
- Luật ghế phải khớp giữa `frontend/src/utils/seats.js` và `backend/app/seats.py`; dữ liệu phim phải khớp giữa `backend/app/data/movies.json` và `frontend/src/api/movies.json`.
- Không đổi `normalize()` trong `backend/app/classifier.py` khi chưa đánh giá lại F1.
- Đổi schema database thì ghi rõ cần xóa `backend/firefly.db` (chưa có migration).
- Không thêm thư viện mới, không đổi thiết kế giao diện đã chốt, không commit `.env`, `*.db`, model hay dữ liệu lớn khi chưa hỏi Tín.
- Chữ trên giao diện và thông báo lỗi viết bằng tiếng Việt; tên biến, hàm, API viết bằng tiếng Anh. Trả lời Tín bằng tiếng Việt.
- Sau mỗi task web: chạy checklist hồi quy (mục 7 trong `docs/BOI_CANH_DU_AN.md`).
- Kết thúc task: viết báo cáo theo mẫu ở mục 11 để Tín gửi review độc lập.
