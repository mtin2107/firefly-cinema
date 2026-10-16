# Codex Fix Report — T12 Round 1 — 16/10/2026

## Phạm vi

- Nhánh: `task/T12-demo`.
- Sửa đúng RF-01 và RF-02 từ `claude_review_T12_FAIL_2026-10-16.md`.
- Đổi schema: Không.
- Không chạy reset hoặc backend trên `backend/firefly.db` thật; mọi probe dùng SQLite tạm dưới `backup/T12_fix_round1/`.
- TODO-01, TODO-02, TODO-03: không thực hiện trong Fix Round 1.

## RF-01 — fallback mật khẩu admin dev

- Khôi phục `seed.py` về quyết định T20: nếu thiếu `ADMIN_PASSWORD`, tài khoản admin dev dùng fallback `admin123` và ghi cảnh báo log.
- `reset_demo.py` vẫn bắt buộc `ADMIN_PASSWORD`; nếu biến rỗng, script exit `2` trước khi tạo/xóa database.
- Probe seed trực tiếp với `ADMIN_PASSWORD` rỗng và classifier keyword tạm:

```text
ADMIN_PASSWORD chưa được cấu hình; đang dùng mật khẩu admin mặc định cho máy dev.
FALLBACK_ADMIN_OK=True
```

`HUONG_DAN.md` đã khớp quyết định này nên không cần sửa.

## RF-02 — reset khi Backend đang giữ SQLite

- Thêm preflight `ensure_database_unlocked`: trước backup/import seed/xóa DB hoặc sidecar, script thử đổi tên DB sang file probe rồi đổi lại.
- Nếu Windows từ chối đổi tên vì uvicorn đang giữ file, script in một câu tiếng Việt và exit `2`; sidecar chưa bị đụng tới.
- Thứ tự xóa khi reset bình thường đổi thành DB trước, sidecar sau.
- Khối phục hồi seed lỗi chuyển thành best-effort: từng bước đóng engine, dọn DB, dọn sidecar, phục hồi DB, phục hồi sidecar được thử độc lập; lỗi phục hồi được gom thành cảnh báo và không che exception gốc.
- Kịch bản demo ghi rõ phải tắt cửa sổ Backend trước khi chạy lại `reset-demo.bat`.

### Probe database bị khóa

Thiết lập: uvicorn thật ở `127.0.0.1:8010`, `DATABASE_URL=sqlite:///../backup/T12_fix_round1/locked.db`, health `ok / phobert_b`. Sau đó gọi trực tiếp `reset_demo.py`:

```text
LỖI: Database đang được Backend sử dụng. Hãy tắt Backend trước khi đặt lại dữ liệu demo.
EXIT=2
DB_EXISTS=True
SIDECAR_EXISTS=True
```

Đối chiếu sau khi dừng uvicorn:

```text
DB_SHA256_BEFORE=5025C9F1D10585E65BEC8A883C621EABFB77F3BE3F2A9429FC3166ABF0D0F5E8
DB_SHA256_AFTER =5025C9F1D10585E65BEC8A883C621EABFB77F3BE3F2A9429FC3166ABF0D0F5E8
SIDECAR_SHA256_BEFORE=D998B571B8DC98C13897C256B7487F003433DA91370684D0B5C686CE008D330E
SIDECAR_SHA256_AFTER =D998B571B8DC98C13897C256B7487F003433DA91370684D0B5C686CE008D330E
PROBE_FILES=0
```

## Hai lần reset bình thường

| Chỉ số | Lần 1 | Lần 2 |
|---|---:|---:|
| Wall time gồm nạp model | 23,69 giây | 23,69 giây |
| Seed không tính nạp model | 3,83 giây | 3,85 giây |
| Phim / suất / vé / bình luận | 21 / 99 / 143 / 30 | 21 / 99 / 143 / 30 |
| Nhãn model tiêu cực / admin đã duyệt | 16 / 8 | 16 / 8 |
| Trạng thái vé | expired 1; paid 141; pending_verify 1 | expired 1; paid 141; pending_verify 1 |

## Gate Round 1

| Gate | Kết quả |
|---|---|
| `compileall -q backend/app backend/scripts` | exit 0 |
| Reset 2 lần trên SQLite tạm | cùng kết quả, dưới 1 phút |
| Backend + `/api/health` trên DB tạm | 200; `classifier=phobert_b`, không fallback |
| Full pytest với `--basetemp` trong backup | `81 passed`, 1 warning thư viện, 45,18 giây |
| `npm run build` real | đạt, 82 modules |
| `VITE_USE_MOCK=true; npm run build` | đạt, 82 modules |
| Mock flow | 9 phim; booking `held`; bình luận tiêu cực bị che; admin relabel `0`; A/B trả đúng contract; seed có paid/pending_verify/expired |

RF-01 và RF-02 đã được sửa ở mức DEV, chờ Claude xác minh độc lập. Không tự review, không tự kết luận PASS.
