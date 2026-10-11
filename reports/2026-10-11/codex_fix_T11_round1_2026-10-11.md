# Codex Fix Report — T11 Round 1

- Ngày: 11/10/2026
- Branch: `task/T11-kiem-thu`
- Commit trước Round 1: `a5bedd90b14aa5269d9b1bfef408261ebd3852a9`
- Trạng thái: `IN_PROGRESS`
- Đổi schema: **Không**
- Backend/model thật: **Không khởi động**
- Database thật: **Không kết nối hoặc ghi**; SHA-256 read-only vẫn `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3`

## 1. Scope verification

`git diff master...a5bedd9 --name-status` cho thấy implementation ban đầu có 21 file. Mọi file nằm trong allowlist T11 ngoại trừ `docs/tasks/T11.md`.

Diff chính xác của file ngoài allowlist chỉ là:

```diff
-| Current Status | PLANNED |
+| Current Status | IN_PROGRESS / BLOCKED_PENDING_PO_RUNTIME_GATE |
```

Không có thay đổi nội dung Task Record nào khác. Vì `docs/TASK_COORDINATION_ACTIVE.md` là nguồn trạng thái hoạt động và hoàn nguyên an toàn, Round 1 đã trả `docs/tasks/T11.md` về đúng byte/nội dung của `master`. Không xin ngoại lệ và không tự hợp thức hóa scope.

Trước Round 1, working tree sạch và toàn bộ implementation đã commit tại `a5bedd90b14aa5269d9b1bfef408261ebd3852a9`. Các thay đổi Round 1 được commit riêng sau khi hoàn tất report/gates.

## 2. Regression F-02

### Phát hiện

Bản sửa F-02 ban đầu bỏ lời gọi `_ensure_showtimes()` khi database đã có phim. Test xóa suất PASS nhưng hợp đồng rolling 5 ngày bị phá: khi ngày giả lập dịch từ 11/10 sang 12/10, ngày 16/10 không được bổ sung.

Focused evidence trước sửa:

```text
1 failed, 2 passed
missing: 2026-10-16
```

### Nguyên nhân và sửa

Hai yêu cầu “không tái tạo suất đã xóa” và “tự bổ sung ngày mới” xung đột nếu lấp theo từng suất thiếu mà không có tombstone/schema. Giải pháp không đổi schema:

- `seed()` tiếp tục gọi `_ensure_showtimes()` trên mỗi startup để duy trì cửa sổ 5 ngày.
- Ngày đã có ít nhất một suất được coi là đã chuyển sang admin quản lý; seed không lấp các suất thiếu trong ngày đó.
- Ngày hoàn toàn mới trong cửa sổ rolling được seed đầy đủ cho mọi phim `now_showing`.
- Không update/delete bất kỳ suất, booking hoặc booking seat hiện hữu.

### Ba regression test bắt buộc

| Test | Kết quả |
|---|---|
| Xóa một suất seed rồi gọi `seed()` cùng ngày: identity `(movie_id,start_time,room)` không xuất hiện lại | PASS |
| Dịch ngày +1: đủ năm ngày tương lai mới, mỗi ngày có đủ cả hai phim đang chiếu | PASS |
| Suất admin tự tạo giữ nguyên toàn bộ field; booking và booking seat vẫn tồn tại | PASS |

Focused F-02: `3 passed`. Full pytest: `22 passed, 1 warning` trong 5,30 giây. Backend compileall và frontend build 70 modules đều PASS.

## 3. Chuẩn bị AC-06 — chưa thực thi

### 3.1. Read-only model/config preflight

- Effective config hiện tại nếu không override: `DATABASE_URL=sqlite:///./firefly.db`, `ACTIVE_MODEL=phobert_b`, `MODEL_DIR_B=models/phobert-binhluan-B`, `NEGATIVE_LABEL_ID=1`, `USE_WORD_SEGMENT=false`.
- Vì URL mặc định là database thật, AC-06 bắt buộc override `DATABASE_URL` trước mọi import/startup.
- Checkpoint B tồn tại, chưa nạp model:
  - `model.safetensors`: `0B80947CA8FECFFBFAA39373E92D1ED44D638DCB4981FF00DA2DD08921D22F4F` — khớp T10.
  - `config.json`: `3AF764B446752118AA33982D7983F52919318373FF3108ADD0128834F28005DA` — khớp T10.
  - `id2label`: `0=binh_thuong`, `1=tieu_cuc`.
  - `version.txt`: `phobert-B-2026-10-09`.

### 3.2. Runtime isolation đề xuất cho PO

Chỉ thực hiện sau quyết định runtime authorization riêng:

1. Dừng mọi backend cũ; xác minh không có listener ở cổng được chọn.
2. Tạo thư mục mới, không ghi đè: `backup/T11_2026-10-11/ac06_<timestamp>/`.
3. Chọn database mới trong thư mục này, ví dụ `firefly-t11-ac06.db`; hard fail nếu path resolve bằng hoặc nằm ngoài runtime root dự kiến.
4. Trước khi import `app.main`, đặt rõ:

   ```powershell
   $env:DATABASE_URL = "sqlite:///C:/Projects/firefly-cinema/backup/T11_2026-10-11/ac06_<timestamp>/firefly-t11-ac06.db"
   $env:ACTIVE_MODEL = "phobert_b"
   $env:MODEL_DIR_B = "C:/Projects/firefly-cinema/backend/models/phobert-binhluan-B"
   $env:MODEL_VERSION_B = "phobert-B-2026-10-09"
   $env:NEGATIVE_LABEL_ID = "1"
   $env:USE_WORD_SEGMENT = "false"
   $env:USE_TEXT_NORM = "true"
   ```

5. Chạy preflight chỉ dùng `pathlib`: xác minh URL là SQLite absolute, resolved DB nằm trong runtime root, khác tuyệt đối `backend/firefly.db`, và file chưa tồn tại. Ghi SHA-256 database thật làm guard nhưng không mở kết nối tới nó.
6. Xác minh lại hash model/config/version rồi mới startup. Health bắt buộc trả `active_model=phobert_b`, `active_version=phobert-B-2026-10-09`, `classifier_error=null`; nếu fallback thì dừng AC-06.

### 3.3. Checkpoint, kiểm tra và khôi phục

- Sau startup/seed đầu tiên trên DB tạm, dừng backend và tạo `checkpoint-pre-browser.db` bằng SQLite Online Backup API từ DB tạm.
- Trên source/checkpoint: `integrity_check=ok`, `foreign_key_check` rỗng; schema, row count và fingerprint bảng khớp.
- Restore checkpoint sang file mới `restore-probe.db`, không ghi đè source; lặp lại integrity/FK/count/fingerprint. Chỉ khi restore probe PASS mới chạy browser.
- Sau checklist: dừng backend, kiểm tra DB tạm, hash checkpoint/model trước-sau và xác nhận hash database thật vẫn nguyên.
- Rollback: dừng backend, quarantine DB tạm lỗi, restore checkpoint sang **một file mới**, verify đầy đủ rồi chỉ dùng file phục hồi nếu PO còn cho phép chạy tiếp. Không bao giờ restore vào `backend/firefly.db`.

## 4. Browser checklist BOI_CANH mục 7

Sau runtime authorization, chạy trên frontend real mode trỏ backend DB tạm:

1. Trang chủ hiện phim; PosterIntro chạy ở “Xem chi tiết” và “Đặt vé”.
2. Menu Thể loại/Chủ đề và tìm `meo muop` trả đúng phim.
3. Đăng ký mới; chưa đăng nhập chọn giờ bị chuyển login; login xong quay lại đúng trang.
4. Đặt hai ghế; mở lại thấy hai ghế xám; “Vé của tôi” có vé mới.
5. Bình luận `Ko hay như quảng cáo, hơi thất vọng` bị ẩn; admin thấy điểm khoảng 0,99, model `phobert_b`, version B.
6. `/api/health` báo `phobert_b` và version `phobert-B-2026-10-09`, không rò đường dẫn/lỗi thô.
7. Tắt backend real, chạy `VITE_USE_MOCK=true`; kiểm lại luồng mock phù hợp và xác nhận không request tới backend.

Ghi ảnh/log cho từng mục, ID user/booking/comment chỉ thuộc DB tạm, và xóa biến môi trường runtime sau khi dừng.

## 5. Trạng thái AC

- AC-01…AC-05: giữ DEV PASS; full suite hiện 22/22.
- AC-06: **PENDING PO RUNTIME AUTHORIZATION**.
- T11 giữ `IN_PROGRESS`; không chuyển `CLAUDE_REVIEW`, không merge/close và không mở T12.
