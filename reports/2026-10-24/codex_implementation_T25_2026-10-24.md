# Codex Implementation Report

Task: T25 — Banner trailer và mục Nội dung phim
Date: 2026-10-24
Result: IMPLEMENTATION_COMPLETED / PENDING_CLAUDE_REVIEW
Branch: `task/T25-trailer-phim`, tạo từ `master` `b8f6ef6`
Đổi schema: **Có** — `movies.trailer_url VARCHAR(500) NULL`, `movies.synopsis TEXT NULL`.

## Files Changed

- Backend: `models.py`, `schemas.py`, `main.py`, router mới `admin_trailers.py`, `app/data/movies.json`, `tests/test_trailers.py`.
- Frontend: `api/http.js`, `real.js`, `mock.js`, `movies.json`; component mới `TrailerBanner.jsx`, helper mới `utils/youtube.js`; `MovieDetail.jsx`, `AdminMovies.jsx`, `styles/global.css` (chỉ thêm CSS).
- Tài liệu: `ARCHITECTURE.md`, `HUONG_DAN.md`, `CHANGELOG.md`, coordination và report này.

## Implemented / Architecture / Contract

- Admin upload raw body qua request.stream(), giới hạn 100 MiB, từ chối Content-Length quá giới hạn trước khi đọc. Ghi dần file tạm, signature quyết định MP4/WebM và đuôi UUID; dọn file tạm cả khi quá hạn, sai chữ ký hoặc ngắt kết nối. Require_admin giữ 401/403.
- Route video đứng trước StaticFiles; nhận `{name:path}` để bắt cả slash mã hóa rồi kiểm tên bằng fullmatch. Streaming 64 KiB, 200/206/416, Range đóng/mở/suffix; không dùng hỗ trợ Range của Starlette.
- Validator nhận upload path hoặc các dạng YouTube đã duyệt, lưu canonical watch URL; synopsis strip, null khi rỗng, tối đa 5000 ký tự. Hai JSON giống byte, 21 synopsis hai đoạn, 21 trailer_url null. Seed hiện có dùng Movie(**m), không cần sửa seed.py.
- Banner chỉ tạo media sau bấm, iframe youtube-nocookie, link mở YouTube, lỗi video tiếng Việt; fallback Poster, không hiệu ứng. Mục Nội dung phim nhiều đoạn trước Lịch chiếu, fallback description; bỏ mô tả trùng, hero không đổi.
- Form có video/link/gỡ/synopsis, type/size client, trạng thái đang tải và khóa form; poster → video → movie, file ưu tiên link. Real raw File + token; mock signature + blob URL trong phiên, cùng JSON `{trailer_url}` và helper YouTube dùng chung với banner.
- CSS mới giữ nguyên :root; thu gọn chữ Poster trong banner mobile để nút không che chữ, chặn min-width của fieldset làm giãn form mock.

## Focused Tests / Final Gates

| Gate | Kết quả thực thi |
|---|---|
| Compileall | `backend\venv\Scripts\python -m compileall -q backend\app`: exit 0 |
| Full pytest | Trong backend: `venv\Scripts\python -m pytest -q`: **194 passed**, 121,33 giây; 148 cũ + 46 mới |
| Build real / mock | `VITE_USE_MOCK=false/true; npm run build`: cả hai exit 0, 91 modules |
| Startup / health | Uvicorn 8025: status ok, classifier phobert_b, version phobert-B-2026-10-09, loaded=true, không fallback |
| Range curl | 206, `bytes 0-1023/29703`, length 1024, Accept-Ranges bytes, MIME video/mp4; vượt file → 416 `bytes */29703` |
| Browser | Playwright runtime có sẵn + Chrome; real 5185/mock 5186, 375px/1280px, không pageerror và không tràn ngang |
| Format / scope | git diff --check sạch; không linter riêng; seed byte parity và :root byte-equivalent đạt |

46 test mới bao phủ upload MP4/WebM/MIME khai sai, khách/user, body rỗng/sai, dọn tạm, Content-Length không đọc body, stream không Content-Length quá hạn, đúng biên (thu nhỏ hằng số để tránh cấp phát 100 MiB), signature chia chunk và disconnect; Range đóng/mở/suffix/clamp/416, tên/path xấu; chuẩn hóa/link xấu, synopsis 5000/5001/null, create/update/public output và seed parity. Một DeprecationWarning Starlette/AnyIO có sẵn.

## Acceptance Evidence

- AC-01/03/09: Browser thêm/sửa phim có MP4 demo H.264 29.703 byte, phát và seek đến 2 giây trong real/mock ở cả hai cỡ; file + link đồng thời → upload path/blob được lưu. Gỡ → null, không nút play. Browser tạo phim xác nhận request POST lần lượt posters, trailers, movies trên real.
- AC-02: youtu.be/watch/shorts/embed được pytest kiểm canonical. Browser real/mock kiểm lazy iframe URL và link ngoài bằng fixture ID có kiểm soát. Kiểm mạng thật thêm với [trailer Elio chính thức](https://www.youtube.com/watch?v=ETVi5_cnnaE), chỉ lưu DB tạm: iframe video currentTime=2,507848, paused=false, readyState=4. Không thêm link này vào seed.
- AC-04/05: pytest có 401/403/413/422/404/416, nội dung tiếng Việt và cleanup. UI chọn text/plain hiện lỗi ngay dưới ô. Browser video URL không tồn tại hiện “Không phát được video trailer.” ở real/mock.
- AC-06: theo dõi request trước bấm: 0 request trailer/YouTube, 0 video/iframe. Bấm Enter trên nút được focus mới tạo video và phát.
- AC-07/08: hai đoạn synopsis render đúng; browser sửa synopsis null hiển thị description dự phòng. Không còn detail__desc; hero vẫn description ngắn. Seed parity được test tự động.
- AC-10: bốn cặp mode/kích thước đều phát/seek; screenshot trước bấm và khi phát; không tràn trang. Form admin cũng kiểm 375/1280, lỗi min-width mock đã sửa và kiểm lại.
- AC-11: gates và hồi quy dưới đây đạt DEV; chờ Claude kiểm độc lập, không tự kết luận review PASS.

## Checklist hồi quy BOI_CANH mục 7

1. Real/mock: có phim, hero tự đổi qua phim tiếp theo trong 15 giây; Xem chi tiết mở đúng phim với PosterIntro. Không đổi code hero/PosterIntro.
2. Tìm “meo muop” ra Mèo Mướp Đi Lạc; hover và click Thể loại → Kinh dị, Chủ đề → lựa chọn đầu điều hướng đúng ở real/mock.
3. Đăng ký qua public API thành công; browser khách chọn giờ → đăng nhập → quay lại đúng suất ở real/mock.
4. Browser đặt hai ghế, xác nhận, Vé của tôi có vé; quay lại suất thấy đúng hai ghế disabled, real/mock.
5. Bình luận mẫu bị ẩn; real negative_score=0,9992, admin thấy nhãn Tiêu cực và điểm làm tròn 1.00; mock=0,87 và admin thấy đúng comment.
6. Health model thật đạt; tên hiện hành phobert_b theo quyết định T10, checklist cũ ghi phobert.
7. Mock chạy được toàn bộ luồng bị ảnh hưởng, gồm upload blob/phát/tua trong phiên, YouTube, gỡ, thêm phim, đặt vé và bình luận.

## Evidence / Runtime

SQLite và UPLOAD_DIR duy nhất cho runtime: `%TEMP%\firefly-t25-b8ef2f0d-af8b-42e1-93ae-61b10e5077cd\t25.db` và `uploads\`. PRAGMA integrity_check=ok, foreign_key_check=0; hai cột mới đúng kiểu. Video được tạo bằng canvas/MediaRecorder ở thư mục tạm, không tải video bản quyền về và không commit video/DB.

Bằng chứng browser JSON trong cùng thư mục tạm: browser-trailers.json, browser-create.json, browser-regression.json, browser-extra.json, browser-layout-error.json, youtube-live.json. Ảnh được giữ ở thư mục visualization của phiên (ngoài Git để tuân allowlist):

- [Real 375 trước bấm](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16e1f-abac-7c22-ac0d-a642c75fba44/t25-real-375-before.png) · [Real 1280 đang phát](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16e1f-abac-7c22-ac0d-a642c75fba44/t25-real-1280-playing.png).
- [Mock 375 đang phát](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16e1f-abac-7c22-ac0d-a642c75fba44/t25-mock-375-playing.png) · [Mock 1280 trước bấm](C:/Users/lemin/.codex/visualizations/2026/10/24/01a16e1f-abac-7c22-ac0d-a642c75fba44/t25-mock-1280-before.png).

Đã xem trực tiếp ảnh real mobile và desktop. Probe đầu có lỗi selector/điều hướng lặp cùng route, và kiểm cleanup nhầm cả test.db; đã sửa probe/test, chạy lại đạt. Test traversal ban đầu phát hiện request rơi vào StaticFiles, đã sửa bằng route name:path rồi kiểm fullmatch.

## Security / Scope / Blockers / TODO

- Không kết nối, reset, migrate hoặc seed DB thật; không sửa .env, normalize(), model hay dependencies. Không sửa root variables, không ghi backend/uploads. Không thao tác process backend có sẵn của PO.
- Out-of-scope changes do Codex: **NO**. Coordination đã có chỉnh sửa PO từ trước, được giữ lại. `docs/tasks/T25.md` là file PO có sẵn ở trạng thái untracked: giữ nguyên, không stage/commit vì ngoài allowlist; không sửa Task Record đã duyệt.
- Blockers kỹ thuật: 0. Giới hạn đã duyệt: không xóa file mồ côi, không chuyển codec, blob mock mất sau reload; YouTube còn phụ thuộc mạng/quyền nhúng từng video.
- Required follow-up: Claude review độc lập; PO backup/checksum/integrity DB + sidecar + uploads rồi tự reset schema sau duyệt theo HUONG_DAN. Không tự thực hiện bước DB thật.

## Handoff

T25 → **CLAUDE_REVIEW**. Không tự PASS, không chuyển PO_REVIEW, không merge/tag, không mở T13.
