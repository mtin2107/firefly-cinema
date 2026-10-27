# Claude — Review T30 (Sửa lỗi audit trước T13) — PASS_WITH_TODO

- Ngày: 27/10/2026 · Reviewer: Claude (Independent Reviewer)
- Nhánh: `task/T30-sua-loi-audit`, commit `9a2cc34`, base master `73eb3c7`
- Task Record: `docs/tasks/T30.md` (PO chốt Q1 = (a), Q2 = 8.0, Q3 = reset một lần sau merge T30)
- Report Codex: `reports/2026-10-27/codex_implementation_T30_2026-10-27.md`

## 1. Kết luận
**PASS_WITH_TODO.** Cả 6 lỗi và TEST-01 đều được sửa đúng chỗ gốc, có regression test, và cả real lẫn mock đều được sửa. RF: 0. Có 1 TODO Low và 1 điểm cần PO xác nhận về allowlist. **Đổi schema: Có** (bảng `bookings` dùng AUTOINCREMENT).

## 2. Diff và scope
- 18 file, +395/−90. Production chỉ gồm các file sau, đúng phạm vi cho phép ở mục 6:
  - `models.py` (1 dòng);
  - `admin_movies.py` (1 dòng);
  - `admin_posters.py` (+7);
  - `bookings.py` (bọc khóa, thân hàm chỉ thụt lề, logic giữ nguyên);
  - `movies.py`;
  - `mock.js`;
  - `MyTickets.jsx`.
- Không có `.env`, `*.db`, model, upload hay CSV trong diff.
- **Ngoài allowlist:** `backend/tests/test_booking_payment.py`. Đây là test cũ khẳng định "xóa phim có vé expired/rejected → 200", trái với BUG-01 mới, nên phải sửa. Codex ghi rằng PO đã cho phép trong chat. Claude không có bằng chứng về lần cho phép đó, nên **Tín cần xác nhận ở PO review** (xem OBS-01). Allowlist thiếu file này là sót của Task Record do Claude soạn, không phải lỗi của Codex.

## 3. Đối chiếu AC
| AC | Kết quả | Bằng chứng |
|---|---|---|
| AC-01 BUG-01 | PASS | `delete_movie` bỏ điều kiện trạng thái, mock cũng vậy. Câu 409 giữ nguyên. Test `bug01[expired/rejected]`: 409, các GET vé 200, không có vé mồ côi. Ca không có vé vẫn xóa được. |
| AC-02 BUG-02 | PASS | `sqlite_autoincrement` có hiệu lực. Test: A hủy, B nhận mã lớn hơn. `sqlite_master` có AUTOINCREMENT. Mock dùng `seq` tăng dần (đã kiểm). |
| AC-03 BUG-03 | PASS | `threading.Lock` cấp module bọc toàn bộ đoạn kiểm tra → ghi. Comment `shortcut:` đúng mẫu. Test chạy 4 thread thật với Barrier, Session riêng cho mỗi request, cố ý làm chậm câu đếm để mở rộng cửa sổ race. Cả 5 lượt đều ra 2×201 + 2×409, DB có đúng 2 vé held. Trên master cả 5 lượt fail. |
| AC-04 BUG-04 | PASS | `TOP_RATED_MIN = 8.0`. Backend lọc bằng `HAVING AVG >= 8` trên trung bình **chưa làm tròn**, nên 7.99 không bị làm tròn thành 8.0 rồi lọt vào. Mock tính từ ratings gốc. Biên 4.5/7.99 bị loại, 8.0/10 được nhận. |
| AC-05 BUG-05 | PASS (TODO-01) | Kiểm IHDR/IEND cho PNG, FFD9 cho JPEG, kích thước RIFF cho WebP. Trả 422 đúng câu trước khi ghi file, áp dụng cho cả poster và ảnh đại diện. Mock dùng cùng quy tắc. Claude kiểm thêm 12 PNG thật trong `reports/`: 12/12 đều được nhận. |
| AC-06 BUG-06 | PASS (đọc code) | `newBookingId` chỉ đọc một lần vào state, sau đó `navigate(..., { replace: true, state: null })`. Effect chạy lại khi state đã null thì không làm gì. Codex có bằng chứng trình duyệt cho real và mock. Claude không chạy lại trên trình duyệt. |
| AC-07 TEST-01 | PASS | Test được tham số hóa ở 00:30, 12:00 và 23:59, monkeypatch `admin_sentiment.datetime`. Full pytest không còn ngoại lệ chạy theo giờ. |
| AC-08 | PASS | Claude chạy độc lập `test_t30_regressions.py` trên worktree tạm của `73eb3c7`: **16 failed, 4 passed**, khớp report Codex. Trên nhánh: 20/20 đạt. |
| AC-09 | PASS | Gate ở mục 4. Hồi quy mục 7 theo report Codex (real + mock). Claude không chạy lại trên trình duyệt. |

## 4. Gate độc lập (Claude, 27/10/2026)
| Gate | Kết quả |
|---|---|
| compileall | exit 0 |
| pytest toàn bộ (DB và UPLOAD_DIR tạm) | **263 passed**, 20:50:37–20:52:21 (1 DeprecationWarning sẵn có) |
| Regression trên master `73eb3c7` | 16 failed, 4 passed, đúng các lỗi BUG-01..05 |
| `npm run build` real | exit 0 (456.77 kB) |
| `vite build` mock (outDir tạm) | exit 0 (484.59 kB) |
| Backend + health | Không chạy lại. Codex ghi `phobert_b` / `phobert-B-2026-10-09` trên DB tạm. T30 không đụng classifier. |

## 5. TODO / OBS
- **TODO-01 (Low): JPEG có dữ liệu sau `FFD9` bị từ chối.** Một số máy chụp (ví dụ điện thoại Samsung, ảnh chụp chuyển động) ghi thêm metadata sau marker EOI. Validator hiện bắt buộc file kết thúc bằng `FFD9`, nên ảnh đại diện chụp từ các máy đó có thể nhận 422 "Ảnh bị hỏng hoặc không đầy đủ.". Quy tắc này do Task Record (Claude soạn) quy định, Codex làm đúng spec. Claude chưa có ảnh điện thoại thật để thử. Đề xuất: PO thử 1–2 ảnh chụp từ điện thoại khi PO review. Nếu bị từ chối, chọn FIX_NOW (nhận khi tìm thấy `FFD9` sau SOS) hoặc ghi Hạn chế ở T13.
- **OBS-01:** `test_booking_payment.py` ngoài allowlist (mục 2). Cần Tín xác nhận đã cho phép.
- **OBS-02:** `mock.js` khai báo `const TOP_RATED_MIN` trước câu `import`. JS vẫn chạy được vì import được hoist, chỉ lệch thói quen viết. Không cần sửa.
- **OBS-03:** khóa BUG-03 chỉ đúng khi chạy 1 worker uvicorn. Đã ghi ở comment, `HUONG_DAN.md` và Task Record. Cần đưa vào Hạn chế ở T13.

## 6. Việc PO cần làm
1. PO review: xác nhận OBS-01; thử ảnh điện thoại cho TODO-01 và chọn disposition.
2. Merge `task/T30-sua-loi-audit` vào `master`.
3. **Reset DB một lần cho T29 + T30** theo `HUONG_DAN.md` mục T30: sao lưu DB, sidecar và `backend\uploads\`, kiểm SHA-256/integrity, xóa `firefly.db`, khởi động lại. Kiểm `users` có 3 cột mới, `bookings` có AUTOINCREMENT, health báo PhoBERT B. Thử đặt → hủy → đặt lại phải ra mã mới.
4. `git checkout -b task/T13-v1` từ master đã merge, điền quyết định rồi gửi prompt ở mục 7.
5. Báo cáo audit `reports/2026-10-27/claude_audit_full_system_pre_T13_2026-10-27.md` vẫn chưa commit, chờ Tín chỉ định.

## 7. Bàn giao task kế tiếp — prompt Codex T13
T30 PASS_WITH_TODO, TODO-01 không chặn T13. T13 chuyển `READY_FOR_HANDOFF` **sau khi PO merge T30 và reset DB**.

```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell).
Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T13.md. T13.md là bản PO đã duyệt.
T24–T30 đã merge vào master; DB thật đã reset một lần sau T30 (schema users mới + bookings AUTOINCREMENT). Làm trên nhánh task/T13-v1 (tạo từ master mới). Đầu tiên ghi closure T24–T30 (merge hash) và đặt T13 → IN_PROGRESS.

Quyết định PO trước T13 (Tín điền trước khi gửi):
- T12 TODO-01 (model B che câu khen phim 1): <giữ nguyên + ghi hạn chế | admin duyệt sẵn | đổi phim mở đầu>
- T14 TODO-02 (mã vé dùng lại sau khi hủy): ĐÃ SỬA ở T30 (BUG-02).
- T25 TODO-01/02 (ô chọn video báo trống; ô YouTube hiện đường dẫn nội bộ): <ghi hạn chế | ...>
- T27 TODO-01 (validator điểm dựa vào tên lớp): <ghi hạn chế | ...>; OBS-01 test_sentiment theo giờ: ĐÃ SỬA ở T30 (TEST-01).
- T28 OBS-01..03 (poster không bắt buộc, menu gọn ở ≤1360px, line-height tiêu đề): <chấp nhận | ghi hạn chế>
- T30 TODO-01 (JPEG có dữ liệu sau FFD9 bị từ chối): <đã sửa | ghi hạn chế>
- Audit 27/10 OBS-01..08 (claude_audit_full_system_pre_T13_2026-10-27.md mục 9): <ghi hạn chế | ...>

Nhiệm vụ: T13 "Chốt v1.0 và sao lưu" — chỉ tài liệu và sao lưu, không viết tính năng.
- README.md (giới thiệu, ảnh, tính năng gồm T16–T30; kết quả F1 A/B/SVM/NB/LR và T15; cách chạy nhanh), HUONG_DAN.md (cài từ số 0, gắn model A/B/SVM, cấu hình .env gồm BANK_* và CHAT_* — chỉ tên khóa, không giá trị; chạy test; reset demo; định dạng video trailer).
- Mục "Hạn chế" gom: các quyết định PO ở trên, T14 TODO-04 / audit OBS-04 (đổi mật khẩu/email không vô hiệu token cũ), T22 (ai đăng nhập cũng chấm điểm; model B nhầm câu khen), soát vé không chặn theo giờ chiếu, vé chờ xác nhận chuyển khoản không tự hết hạn, T25 (file video mồ côi; YouTube cần mạng; video mock mất khi tải lại), T29 (đổi email chưa xác minh qua thư; admin dùng chung; chưa khai ngày sinh vẫn đặt được, kiểm giấy tờ tại rạp), T30 (giới hạn 2 vé giữ chỉ đảm bảo khi chạy 1 worker uvicorn).
- docs/SAO_LUU.md phải gồm cả backend\uploads\ (poster, trailers, avatars); docs/images/*, CHANGELOG.md [1.0.0], cập nhật cuối CONG_NGHE.md/ARCHITECTURE.md; xử lý T18 TODO-03 và T00 TODO-03 theo T13.md.
Ràng buộc: chỉ file trong mục 6 của T13.md; không sửa code; không commit model/DB/.env/video/ảnh tải lên/dữ liệu lớn; không đọc hay in giá trị khóa trong .env.
Gate: compileall, pytest, npm run build (real + mock) để xác nhận không hồi quy.
Commit "[T13] mô tả". Viết reports/YYYY-MM-DD/codex_implementation_T13_YYYY-MM-DD.md, đặt T13 sang CLAUDE_REVIEW. Không merge, không gắn tag v1.0 (Tín gắn).
```

## 8. Dọn dẹp
Worktree tạm của master, các DB tạm, UPLOAD_DIR tạm và thư mục build mock tạm đều đã xóa. Script kiểm ảnh chỉ đọc nằm trong `%TEMP%`. Không đụng `backend/firefly.db`, `.env` hay model. Không sửa production code.
