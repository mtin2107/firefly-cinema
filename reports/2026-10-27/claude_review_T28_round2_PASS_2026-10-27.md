# Claude review T28 round 2 — PASS (27/10/2026)

- Nhánh: `task/T28-giao-dien-tai-khoan` @ `7aba78b`, so với `e9650fa` (sau review round 1).
- Phạm vi: chỉ TODO-01 (PO quyết FIX_NOW ngày 27/10). Report Codex: `reports/2026-10-27/codex_fix_T28_round1_2026-10-27.md`.
- **Đổi schema: Không.**

## 1. Kết luận
**PASS.** TODO-01 CLOSED. RF 0. OBS-01..06 của round 1 giữ nguyên để PO quyết.

## 2. Diff
`git diff e9650fa..7aba78b`: 3 file — `frontend/src/pages/AdminMovies.jsx` (1 dòng), report Codex, file điều phối. Không có file production nào khác, không đụng backend, mock, test, dữ liệu.

```diff
-      status: movie.stored_status || movie.status,
+      status: movie.status,
```

Mock không cần sửa: `movieById` trả `status` hiệu lực và `stored_status`, danh sách admin mock dùng `movieById`.

## 3. Kiểm chứng độc lập (backend 8005 + frontend 5179, SQLite tạm)
| Bước | Kết quả |
|---|---|
| Danh sách admin, phim 6 (lưu `coming_soon`, ngày 24/10) | Có ghi chú "tự chuyển từ Sắp chiếu" |
| Bấm Sửa phim 6 | Ô trạng thái = `now_showing` ("Đang chiếu") |
| Bấm "Lưu thay đổi" không đổi gì | Thông báo "Đã cập nhật phim."; `GET /api/movies/6` → `status` và `stored_status` đều `now_showing`, ngày giữ 24/10 |
| `PUT /api/admin/movies/6` với `coming_soon` + ngày 27/10 (hôm nay) | 422 "Phim sắp chiếu phải có ngày khởi chiếu sau hôm nay." — quy tắc chặn vẫn còn |

Bước mock: dựa vào report Codex và đọc code, Claude không chạy lại.

## 4. Gate
| Gate | Kết quả |
|---|---|
| `compileall -q backend\app` | exit 0 |
| Backend + `/api/health` | `phobert_b` |
| `npm run build` real / mock | đạt / đạt |
| pytest toàn bộ (chạy 00:30 ngày 27/10) | **208 passed, 1 failed** — lỗi duy nhất `test_sentiment_uses_effective_label_group_by_and_complete_daily`, đúng OBS-01 T27 (fail 0h–7h); fix chỉ đổi frontend nên không ảnh hưởng pytest |

## 5. Việc PO cần làm
1. Quyết OBS-01..03 của round 1 (poster không bắt buộc, menu gọn ở ≤1360px, line-height tiêu đề) — chấp nhận hoặc ghi hạn chế ở T13.
2. Merge `task/T28-giao-dien-tai-khoan` vào master. **Không cần reset DB.** Sau merge, phim "Nửa Vầng Trăng Hà Tiên" trên DB thật tự hiện Đang chiếu; admin sửa và lưu được bình thường.
3. Xóa nhánh rỗng `task/T13-ten-task`, tạo `task/T13-v1` từ master mới, gửi prompt T13 ở mục 8 report round 1 (`claude_review_T28_PASS_WITH_TODO_2026-10-27.md`); dòng T28 TODO-01 ghi "đã sửa".
