# Claude review T29 round 3 — PASS (27/10/2026)

- Nhánh: `task/T29-tai-khoan` @ `da86372`, so với `51b4ddd` (PO quyết TODO-03 = FIX_NOW).
- Report Codex: `reports/2026-10-27/codex_fix_T29_round2_2026-10-27.md`.
- **Đổi schema:** vòng này không; T29 gốc vẫn cần reset DB sau merge.

## 1. Kết luận
**PASS.** TODO-03 CLOSED. RF 0. Không còn TODO mở của T29; OBS-02, OBS-03, OBS-05 giữ nguyên (ghi hạn chế ở T13 nếu PO muốn).

## 2. Diff
`git diff 51b4ddd..da86372`: `auth.py` (+9/−1), `test_t29_round1.py` (+61), report, file điều phối. `put_avatar` đọc body bằng `request.stream()`, cộng dồn số byte, vượt 3 MB thì trả 413 ngay; các bước sau (parse `PosterUploadIn`, `validate_image`, ghi file, xóa ảnh cũ) giữ nguyên. Test mới đưa từng chunk thẳng vào ASGI, kiểm 413, dừng đọc ở chunk thứ 4 và không tạo thư mục; ảnh hợp lệ dạng chunked vẫn 200. `git diff --check` exit 0.

## 3. Kiểm chứng độc lập (backend 8006, DB và UPLOAD_DIR tạm, đã khởi động lại để nạp bản sửa)
| Trường hợp | Kết quả |
|---|---|
| 4 MB có `Content-Length` | 413 "Ảnh đại diện tối đa 2 MB." |
| 4 MB `Transfer-Encoding: chunked`, không `Content-Length` | **413** "Ảnh đại diện tối đa 2 MB." (round 2: 422 sau khi đọc hết) |
| Ảnh PNG hợp lệ | 200, tạo đúng 1 file |
| Bình luận công khai | vẫn 12 khóa như trước T29 |

## 4. Gate
| Gate | Kết quả |
|---|---|
| `compileall -q backend\app` | exit 0 |
| Backend + `/api/health` | `phobert_b` |
| `npm run build` | đạt (frontend không đổi ở vòng này) |
| pytest toàn bộ (12:57 ngày 27/10) | **241 passed**, 0 failed (gồm 2 test chunked mới) |

## 5. Việc PO cần làm
1. Merge `task/T29-tai-khoan` vào master.
2. **Dừng backend → sao lưu `firefly.db` + sidecar + `backend\uploads\` → kiểm SHA-256 → xóa `firefly.db` → khởi động lại** theo `HUONG_DAN.md` mục T29.
3. Xóa nhánh rỗng `task/T13-ten-task`, tạo `task/T13-v1` từ master mới, gửi prompt T13 ở mục 8 của `claude_review_T29_PASS_WITH_TODO_2026-10-27.md`; dòng T29 ghi "TODO-01/02/03 đã sửa".
