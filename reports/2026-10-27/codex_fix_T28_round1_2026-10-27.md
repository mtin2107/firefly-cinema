# T28 — Fix Round 1 — TODO-01

- Ngày: 27/10/2026, Asia/Saigon (UTC+07:00).
- Nhánh: `task/T28-giao-dien-tai-khoan`; baseline `e9650fa223c08d443220357ecf85ad14b91c2660`, working tree sạch trước sửa.
- PO quyết TODO-01 = FIX_NOW ngày 27/10/2026; phạm vi theo mục 5 review Claude.
- **Đổi schema: Không**.
- Trạng thái: TODO-01 đã sửa ở mức triển khai, **chờ Claude xác minh**; bàn giao `CLAUDE_REVIEW`. Không tự kết luận review/PASS, không merge, không mở T13.

## Thay đổi duy nhất trong production

`frontend/src/pages/AdminMovies.jsx:145`, trong `startEdit`:

```diff
-      status: movie.stored_status || movie.status,
+      status: movie.status,
```

Form sửa phim dùng trạng thái hiệu lực API trả về. Khi admin lưu phim tự chuyển sang Đang chiếu, thao tác lưu chủ động ghi `now_showing` vào DB theo quyết định PO. Quy tắc đọc trạng thái vẫn không tự ghi DB.

Ghi chú “tự chuyển từ Sắp chiếu” ở danh sách giữ nguyên. Không sửa backend, mock.js, dữ liệu JSON hoặc test. Đã kiểm source `movieById` của mock: trả `status: effectiveStatus(m)` và `stored_status: m.status`, nên cùng trang AdminMovies áp dụng đúng cho cả hai chế độ.

Ngoài một file production trên, chỉ cập nhật report này và TASK_COORDINATION_ACTIVE.md theo yêu cầu bàn giao. Không có ngoại lệ mở rộng production scope.

## Môi trường kiểm chứng

- Backend riêng tại `http://127.0.0.1:8029`; DATABASE_URL trỏ `sqlite:///C:/Users/lemin/AppData/Local/Temp/firefly-t28-todo01-20261027-0023.db`.
- UPLOAD_DIR ở Temp. Tài khoản admin kiểm chứng chỉ thêm vào DB tạm.
- Frontend real: port 5185, VITE_USE_MOCK=false, VITE_API_URL trỏ 8029.
- Frontend mock: port 5186, VITE_USE_MOCK=true; trình duyệt/context mới, dữ liệu seed mock trong localStorage riêng.
- Test: DATABASE_URL riêng `.../firefly-t28-todo01-pytest.db`; các fixture pytest tạo DB riêng trong thư mục tạm.
- Không mở/đọc/ghi/reset backend/firefly.db. Không thêm thư viện. Dùng Playwright có sẵn và Edge cho probe UI.

## Kết quả 3 bước kiểm chứng

| Bước | Real | Mock |
|---|---|---|
| 1. Mở sửa phim 6 tự chuyển, lưu không đổi gì | Trước lưu: status=now_showing, stored_status=coming_soon, release_date=2026-10-24. Danh sách có ghi chú tự chuyển. Mở form chọn **Đang chiếu**; bấm Lưu thay đổi hiện “Đã cập nhật phim.”. GET /api/movies/6 sau lưu: status và stored_status đều now_showing; ngày vẫn 24/10. Truy vấn trực tiếp SQLite tạm xác nhận status lưu now_showing. | `api.movies.get(6)` trước lưu trả cùng trạng thái hiệu lực/lưu và ngày 24/10. Ghi chú hiện, form chọn **Đang chiếu**, lưu không đổi gì thành công. `api.movies.get(6)` sau lưu trả status và stored_status đều now_showing, ngày giữ nguyên. |
| 2. Chủ động chọn Sắp chiếu với ngày hôm nay | Chọn coming_soon, ngày 2026-10-27 rồi lưu: form báo “Phim sắp chiếu phải có ngày khởi chiếu sau hôm nay.”; không gửi PUT. Gọi trực tiếp API PUT và POST với cùng trạng thái/ngày đều HTTP 422, đúng câu trên. Phim đã lưu không bị đổi ngày/trạng thái sau các lần bị từ chối. | Cùng thao tác form, cùng thông báo. Gọi trực tiếp `api.admin.movies.update` và `create` đều ném ApiError có status=422, đúng thông báo. Dữ liệu phim vẫn now_showing và ngày 24/10. |
| 3. Đối chiếu real/mock | Cùng trang AdminMovies và cùng kết quả thao tác; browser không có pageerror. | `movieById` trả trạng thái hiệu lực trước khi form đọc; không cần sửa mock.js. Browser không có pageerror. |

Probe được thực thi qua đăng nhập và form Quản lý phim thật; gọi API trực tiếp bổ sung nhằm chứng minh backend/mock vẫn chặn kể cả khi bỏ qua kiểm tra form.

## Gate

| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend/app` | exit 0 |
| Backend SQLite tạm + `/api/health` | status=ok; classifier/active_model=phobert_b |
| `npm run build`, real | exit 0, 92 modules, JS 437.24kB, CSS 54.08kB |
| `npm run build`, mock | exit 0, 92 modules, JS 462.29kB, CSS 54.08kB |
| `python -m pytest -q`, toàn bộ | Bắt đầu **00:24:05**, kết thúc **00:26:34**, ngày **27/10/2026 +07:00**. **208 passed, 1 failed, 1 warning**, 146.38s, exit 1. |
| Lỗi pytest duy nhất | `tests/test_sentiment.py::test_sentiment_uses_effective_label_group_by_and_complete_daily`, dòng 91: dữ liệu lùi 1–2 giờ rơi vào hôm trước, total/negative hôm nay actual=0/0 thay vì expected=2/1. Đúng **OBS-01 T27**, chạy trong 0h–7h, thuộc ngoại lệ PO cho phép. Không sửa/skip/xóa test; không có lỗi pytest khác. |
| Scope và whitespace | `git diff --check` exit 0; production chỉ thay một dòng AdminMovies.jsx. Metadata chỉ report + coordination theo yêu cầu. |

Warning hiện có là DeprecationWarning của Starlette/AnyIO.

## Bằng chứng probe

Artifact ngoài repo để giữ đúng phạm vi file được sửa:

- [JSON kết quả real/mock](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round1/results.json>).
- [Form real chọn trạng thái hiệu lực](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round1/real-edit-effective.png>).
- [Form mock chọn trạng thái hiệu lực](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round1/mock-edit-effective.png>).
- [Form real vẫn chặn ngày hôm nay](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round1/real-invalid-today.png>).
- [Form mock vẫn chặn ngày hôm nay](<C:/Users/lemin/.codex/visualizations/2026/10/26/01a17911-5822-7093-93a3-a8fdad30164a/T28-fix-round1/mock-invalid-today.png>).
