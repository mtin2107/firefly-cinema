# Claude Independent Review — T04 — Quản lý phim (admin) — 08/10/2026

| Trường | Giá trị |
|---|---|
| Task | T04 — Quản lý phim (admin) |
| Branch | `task/T04-quan-ly-phim` |
| Baseline | `b6cc3d677a5e748ed4818ce111967bfa234e9edb` (= `master`) |
| Implementation commit | `d8e67e0484afa4e6fe3e085c365c3de1ae2d33ed` |
| Handoff commit | `7df775d` (chỉ report Codex + file điều phối) |
| Reviewer | Claude (Independent Reviewer) |
| **Kết luận** | **PASS_WITH_TODO** — AC 7/7 có bằng chứng độc lập; RF 0; Blocker 0; **2 scope deviation cần PO quyết định trước khi APPROVE** |
| Đề xuất trạng thái | T04 `CLAUDE_REVIEW` → `PO_REVIEW` |

Review dựa trên diff thật `git diff b6cc3d6 d8e67e0` và probe chạy lại độc lập; report Codex chỉ dùng làm bằng chứng phụ. Không sửa production code, không merge, không PO approve, không mở T05.

---

## 1. Scope Review

### 1.1. File thay đổi (`git diff --name-only b6cc3d6 7df775d`)

| File | Trong allowlist T04 mục 6? |
|---|---|
| `backend/app/routers/admin_movies.py` (mới) | Có |
| `backend/app/taxonomy.py` (mới) | Có |
| `backend/app/schemas.py` | Có |
| `backend/app/main.py` | Có |
| `frontend/src/pages/AdminMovies.jsx` (mới) | Có |
| `frontend/src/App.jsx` | Có |
| `frontend/src/components/Header.jsx` | Có |
| `frontend/src/api/real.js`, `frontend/src/api/mock.js` | Có |
| `frontend/src/styles/global.css` | Có, **kèm điều kiện** "thêm class, không đổi biến `:root`" → xem SD-02 |
| `docs/ARCHITECTURE.md`, `HUONG_DAN.md` | Có |
| `docs/TASK_COORDINATION_ACTIVE.md`, `reports/2026-10-08/codex_implementation_T04_2026-10-08.md` | Có |
| **`frontend/src/utils/taxonomy.js`** | **Không** → SD-01 |

- Forbidden Files (`classifier.py`, `seats.py`, `models.py`, `backend/app/data/movies.json`, `frontend/src/api/movies.json`): `git diff b6cc3d6 d8e67e0 -- <5 file>` rỗng (0 dòng). **Không bị sửa.**
- Hai file `movies.json` vẫn giống hệt nhau (parity `True`, 21 phim).
- Không có `.env`, `*.db`, model, CSV trong diff. `frontend/dist` bị ignore. `git diff --check`: sạch.
- Không thêm thư viện (không đổi `package.json`, `requirements*.txt`). Không đổi schema (`models.py` không đổi).

### 1.2. SD-01 — `frontend/src/utils/taxonomy.js` ngoài allowlist

- **Sự thật:** file bị sửa nhưng không có trong T04 mục 6. Report Codex mục 4 có liệt kê file này, nhưng mục 11 và 12 ghi "Tất cả file thay đổi nằm trong Allowed Files T04" / "14 file, đúng allowlist" → **khẳng định sai**.
- **Nội dung sửa:** tách mảng nhãn thành export mới `GENRE_LABELS` (22), `COUNTRY_LABELS` (9), `FORMAT_LABELS` (2), `AGE_RATINGS` (4); `GENRES`/`COUNTRIES` dựng lại từ các mảng đó.
- **Ảnh hưởng hành vi:** Claude import bản baseline và bản mới bằng Node rồi so `GENRES`, `COUNTRIES`, `STATUSES`, `YEARS`, `FILTERS` (key + options): **giống hệt nhau** (`identical exports: true`). Menu vẫn 23 mục, thứ tự và slug không đổi. Chỉ thêm export, không bỏ export nào.
- **Có cần thiết không:** không bắt buộc. T04 mục 4 chỉ yêu cầu `taxonomy.py` "khớp `frontend/src/utils/taxonomy.js`", và mock/trang admin có thể lấy nhãn bằng cách lọc `GENRES` hiện có. Tuy vậy, cách làm của Codex là refactor nhỏ, không đổi hành vi, giúp frontend có một nguồn nhãn duy nhất.
- **Kết luận:** **Cần PO scope approval.** Theo `AGENT_RULES.md` mục 3.1, gate Scope là bắt buộc; Claude không có quyền tự chấp nhận file ngoài allowlist. Claude không xếp vào RF vì không có lỗi chức năng và sửa lại chỉ làm thay đổi cách tổ chức mã. PO chọn một trong hai:
  - (a) chấp nhận hồi tố SD-01 (Claude đề xuất phương án này), ghi vào `po_review_T04_*`;
  - (b) đưa T04 về `FIX_LOOP`: Codex hoàn nguyên `taxonomy.js` về baseline, lấy nhãn trong `mock.js`/`AdminMovies.jsx` từ `GENRES.filter((g) => !g.query).map((g) => g.label)` và `COUNTRIES.map((c) => c.label)`. Cách kiểm tra lại: `git diff master...HEAD -- frontend/src/utils/taxonomy.js` rỗng, build đạt, mock CRUD đạt.

### 1.3. SD-02 — `global.css` sửa rule có sẵn, không chỉ thêm class

Allowlist chỉ cho phép `global.css` "thêm class, không đổi biến `:root`". `:root` không bị đổi, nhưng diff sửa rule có sẵn áp dụng cho **mọi trang**:
- `@media (max-width: 600px)`: `.container` padding ngang 20px → 14px; `.page-title` 2.5rem → 2rem (toàn site trên điện thoại).
- `.field input` mở rộng thành `.field input, .field select, .field textarea` và thêm `.field [aria-invalid="true"]`. Ở trang Đăng nhập/Đăng ký, ô input trông y như cũ (cùng thuộc tính; các trang này không dùng `aria-invalid`).

Ảnh hưởng nhỏ và hợp lý cho màn 375px, nhưng đây là thay đổi giao diện toàn cục ngoài mô tả allowlist, nên **cần PO xác nhận** (chấp nhận, hoặc yêu cầu giới hạn trong `.admin-movies`).

### 1.4. Vấn đề 22/23 thể loại — nguồn canonical

- `BOI_CANH_DU_AN.md` dòng 205: "Thể loại ▾ (23 mục, 3 cột)" nói về **menu**.
- Baseline `taxonomy.js`: `GENRES` = 21 thể loại + "Phim 18+" (`query: {age_rating: "T18"}`, ghi rõ "lọc theo độ tuổi, không phải thể loại") + "Anime & Hoạt hình" = **23 mục menu**, trong đó **22 thể loại thật**.
- Task T04 mục 13 ("ngoài 23 mục") dùng con số của menu. Danh mục thể loại hợp lệ cho validation đúng là 22; "Phim 18+" không được là giá trị `genre`.
- Đối chiếu: backend `taxonomy.GENRES` == frontend `GENRE_LABELS` (22, cùng thứ tự); quốc gia 9/9, định dạng 2/2, độ tuổi 4/4 đều khớp (script so sánh, `True` cả 4). Mọi thể loại và quốc gia trong `movies.json` đều thuộc taxonomy (tập ngoài danh mục = rỗng).
- **Kết luận:** con số 22 của Codex đúng, không có lỗi. Đề xuất PO sửa chữ "23 mục" trong T04 mục 13 thành "22 thể loại (menu 23 mục gồm cả Phim 18+)" ở lần chỉnh tài liệu sau (không chặn).

---

## 2. Backend Review

Probe tạm `probe_t04.py`, `probe_t04_del.py`, `probe_reg.py` đặt ở scratchpad ngoài repo, chạy `fastapi.testclient` với SQLite tạm (`DATABASE_URL` trỏ thư mục temp), không đụng `backend/firefly.db`. Đã chạy trước gate cuối; repo không chứa probe (`git status` sạch).

### 2.1. Xác thực (AC-01)
| Endpoint | Không token | User `demo@` | Token rác |
|---|---|---|---|
| `GET /api/admin/movies` | 401 | 403 | 401 "Phiên đăng nhập không hợp lệ." |
| `POST /api/admin/movies` | 401 | 403 | — |
| `PUT /api/admin/movies/1` | 401 | 403 | — |
| `DELETE /api/admin/movies/1` | 401 | 403 | — |

Cả 4 route đều có `Depends(require_admin)`; câu 403 tiếng Việt "Chỉ quản trị viên mới xem được trang này.".

### 2.2. Validation 422 (AC-02)
Năm trường hợp của AC đều trả 422 với `detail` là **một chuỗi** tiếng Việt nêu đúng ô:
- tên `"   "` → `Trường 'title' không hợp lệ: Tên phim không được để trống.`
- thời lượng 0 → `Trường 'duration_min' …: Thời lượng phải từ 1 đến 400 phút.`
- `2026-02-30` → `Trường 'release_date' …: Ngày phát hành phải là ngày hợp lệ theo dạng YYYY-MM-DD.`
- `T21` → `Trường 'age_rating' …: Phân loại độ tuổi phải là P, T13, T16 hoặc T18.`
- thể loại `Lạ` → `Trường 'genre' …: Thể loại không hợp lệ: Lạ.`

Kiểm tra thêm, đều 422 tiếng Việt: quốc gia `Đức`, định dạng `IMAX`, màu `red`, URL `ftp://`, status `draft`, thời lượng 401, ngày `2026-1-5`, thể loại rỗng.
Edge (xem TODO-03): thiếu trường / sai kiểu / trường thừa vẫn trả 422 một câu, nhưng phần sau là thông điệp Pydantic tiếng Anh (`Field required`, `Input should be a valid integer…`, `Extra inputs are not permitted`).

### 2.3. CRUD và nhất quán dữ liệu
- POST 201, trả `MovieOut`; `genre` lưu dạng `"Phiêu lưu, Gia đình"`, màu chuẩn hóa chữ thường, `score=0`.
- PUT 200; đổi status `now_showing` → `coming_soon` làm phim chuyển tab đúng. PUT/DELETE id không tồn tại → 404 "Không tìm thấy phim.".
- **Lưu lại không đổi gì cho cả 21 phim seed qua PUT → 21/21 trả 200** (gồm 11 phim có `formats=""` và màu viết hoa). Admin sửa được mọi phim có sẵn.
- DELETE phim chưa có vé (id 6, có thêm 1 suất chiếu và 1 bình luận) → 200; `GET /api/movies/6` → 404; không còn suất chiếu hay bình luận mồ côi; `/api/admin/comments` và trang chủ vẫn 200.
- Seed chỉ chạy khi bảng `movies` rỗng → phim seed đã xóa không bị thêm lại khi khởi động lại.

### 2.4. 409 khi phim đã có vé (AC-03)
- Seed có sẵn vé cho phim 1, 2, 3, 4, 5, 8, 9, 10, 18. Đặt thêm 2 ghế phim 1 → 201.
- `DELETE /api/admin/movies/1` → **409**, `detail` khớp **từng ký tự** "Phim đã có vé, không xóa được. Hãy chuyển trạng thái sang Đã chiếu xong.".
- `PUT` phim 1 với `status=ended` → 200; vé vẫn còn trong `/api/bookings/me`.

### 2.5. Schema và PhoBERT
- `models.py` không đổi; dùng cột sẵn có. Không cần xóa `firefly.db`.
- `classifier.py` không đổi, `normalize()` không đổi.
- Backend thật (`preview_start backend`, `.env` thật): `/api/health` → `{"status":"ok","classifier":"phobert","classifier_error":null}`.
- PhoBERT thật trên DB tạm: "Ko hay như quảng cáo, hơi thất vọng" → `is_negative=True, 0.9937`; "Phim rất hay, diễn viên đóng xuất sắc" → `False, 0.0034`.

---

## 3. Frontend Review

| Hạng mục | Kết quả | Bằng chứng |
|---|---|---|
| Route protection | PASS | `/quan-tri/phim` nằm trong `<ProtectedRoute adminOnly>`. Chưa đăng nhập → chuyển `/dang-nhap`; user `demo@` → "Trang này chỉ dành cho quản trị viên." |
| Menu | PASS | Dropdown admin: "Vé của tôi → Quản lý phim → Kiểm duyệt bình luận → Đăng xuất"; chỉ hiện khi `role === "admin"` |
| Form thêm | PASS | Submit rỗng hiện lỗi theo từng ô (tên, thời lượng, ngày, thể loại). Tạo phim qua UI → "Đã thêm phim mới.", bảng 21 → 22 |
| Form sửa | PASS | "Sửa" nạp đúng dữ liệu, tiêu đề đổi "Sửa phim"; đổi trạng thái → "Đã cập nhật phim." |
| Xóa | PASS | Xóa phim mới → "Đã xóa phim."; xóa phim có vé → hiện đúng câu 409 trong `notice--error` |
| Poster preview | PASS | Nhập tên + chọn thể loại → khung xem trước hiện ngay "ĐOM ĐÓM PHIÊU LƯU REVIEW / Phiêu lưu, Anime & Hoạt hình"; có `poster_url` thì `Poster` dùng `<img>` |
| Loading / rỗng / lỗi | PASS | Thay tạm hàm `list` của mock trong bộ nhớ trình duyệt (không sửa file): "Đang tải danh sách phim...", "Chưa có phim nào. Hãy thêm bộ phim đầu tiên.", lỗi "Không kết nối được máy chủ." kèm nút "Thử lại" |
| 375px | PASS | Viewport 375×812: `scrollWidth = 375 = innerWidth`; form và lưới một cột (317px); bảng nằm trong `.table-wrap` `overflow-x: auto` (bảng 760px cuộn trong khung 347px); không phần tử nào tràn ngoài khung bảng. Có ảnh chụp màn hình |
| Lọc + tìm không dấu | PASS | Phim mới hiện ở `/`, `/kham-pha?trang-thai=dang-chieu` (không ở `sap-chieu`), `?the-loai=phieu-luu`, `?the-loai=anime-hoat-hinh`, `?q=dom dom phieu luu review`; trang chi tiết `/phim/22` mở được, ghi "Hiện chưa có suất chiếu nào sắp tới." |
| Real mode (5173 + backend thật) | PASS | Admin tạo "ZZ Claude Probe T04" qua UI → 201, có ở `/api/movies?q=zz claude probe`; xóa qua UI → hết; xóa phim đang chiếu có vé → 409. Sau probe DB thật còn đúng 21 phim |
| Payload | PASS | `EMPTY_FORM` có đúng 14 khóa của `MovieIn` (`extra="forbid"` không chặn nhầm) |
| Giao diện chỉ import `api` | PASS | `AdminMovies.jsx` import từ `../api` (index.js) |

---

## 4. Mock Review

Chạy Vite với `VITE_USE_MOCK=true` ở cổng 5174 qua cấu hình launch tạm, đã gỡ sau review.

| Hạng mục | Kết quả | Bằng chứng |
|---|---|---|
| Phân quyền mock | PASS | 4 hàm: không token → 401 "Bạn cần đăng nhập để tiếp tục."; user → 403 |
| Validation mock | PASS | 5 trường hợp AC-02 → `ApiError` 422 cùng câu tiếng Việt (không có tiền tố `Trường '…'` → TODO-06) |
| CRUD | PASS | create / update / delete qua UI; 409 đúng câu khi phim có vé (đặt vé mock trên phim 1); PUT phim 1 sang `ended` đạt |
| F5 | PASS | Sau reload vẫn 22 dòng và còn phim mới; sau xóa + reload vẫn 21 dòng |
| Dữ liệu mock khác | PASS | Sau CRUD: users 2, comments 12 (không đổi), bookings giữ nguyên; tìm "meo muop" → "Mèo Mướp Đi Lạc"; đặt vé mock và "Vé của tôi" đạt; bình luận "Phim chán, thất vọng" → negative 0.87 |
| Tương thích DB mock cũ | PASS | Ghi một `firefly_mockdb_v2` không có `movies`/`seq.movie` (giống DB trước T04) → reload: tự nạp lại 21 phim, tạo/xóa phim đạt |
| Parity real/mock | PASS | Cùng 4 hàm `api.admin.movies.{list,create,update,remove}`, cùng cấu trúc `MovieOut` (genre/formats dạng chuỗi), cùng `{detail}` khi xóa, cùng mã 401/403/404/409/422 |

---

## 5. Regression Review (BOI_CANH mục 7)

| # | Kiểm tra | Kết quả | Bằng chứng Claude |
|---|---|---|---|
| 1 | Trang chủ hiện phim, poster | PASS | Mock `/` có phim mới; real 21 phim; trang chi tiết render đủ |
| 2 | Menu thể loại / tìm "meo muop" | PASS | Real và mock đều ra "Mèo Mướp Đi Lạc"; `GENRES` không đổi (so bằng Node) |
| 3 | Đăng ký; đặt vé yêu cầu login | PASS | Register 201; `POST /api/bookings` không token → 401; route admin chưa login → `/dang-nhap` |
| 4 | Đặt 2 ghế, ghế bị đánh dấu, Vé của tôi | PASS | Booking 201; `H11`,`H12` có trong `booked_seats`; `/bookings/me` có 1 vé (real); mock 2 vé |
| 5 | Bình luận tiêu cực bị ẩn / admin thấy điểm | PASS | PhoBERT 0.9937 negative; `/api/admin/comments?label=negative` 200 |
| 6 | `/api/health` báo PhoBERT | PASS | `classifier: phobert`, `classifier_error: null` |
| 7 | `VITE_USE_MOCK=true` dùng được | PASS | Mục 4 |

### Gate (AGENT_RULES 3.1)
| Gate | Kết quả |
|---|---|
| `python -m compileall -q backend\app` | PASS (exit 0) |
| Backend khởi động + health | PASS (phobert) |
| `npm run build` | PASS (Vite, built in 698ms) |
| pytest | N/A (bắt đầu từ T11) |
| Mock mode | PASS |
| Hồi quy 7 mục | PASS |
| Scope | **DEVIATION** — SD-01, SD-02, chờ PO |
| Bí mật | PASS |

---

## 6. Acceptance Criteria

| AC | Kết quả | Ghi chú |
|---|---|---|
| AC-01 | PASS | 4/4 endpoint: 401 / 403 (real và mock) |
| AC-02 | PASS | 5/5 trường hợp → 422, một câu tiếng Việt, nêu đúng ô |
| AC-03 | PASS | 409 đúng từng ký tự; PUT `ended` 200 (real, mock, UI) |
| AC-04 | PASS | Đúng tab theo status, lọc thể loại, tìm không dấu (API và UI) |
| AC-05 | PASS | Mock thêm/sửa/xóa và F5 |
| AC-06 | PASS | Loading/rỗng/lỗi + 375px không tràn ngang |
| AC-07 | PASS | Checklist 7/7 |

**AC 7/7 PASS.**

## 7. Definition of Done

| Mục | Trạng thái |
|---|---|
| Code đúng thiết kế T04 mục 4 | MET |
| Endpoint có ở cả `real.js` và `mock.js` | MET |
| `require_admin`, lỗi `HTTPException` tiếng Việt | MET |
| Không đổi schema / Forbidden Files | MET |
| Gate web | MET (trừ Scope) |
| Tài liệu (`HUONG_DAN.md`, `ARCHITECTURE.md`) | MET (bảng endpoint, khóa mock `v2`, cây thư mục) |
| Chỉ file trong allowlist | **NOT MET — SD-01, SD-02, chờ PO quyết** |
| Report Codex chính xác | **PARTIAL** — mục 11/12 khẳng định sai về allowlist |

---

## 8. Phân loại kết quả

### Required Fixes
**0.** (Nếu PO chọn phương án (b) ở SD-01 thì chuyển thành RF-01 trong `po_review_T04_*`.)

### Blockers
**0** về kỹ thuật. Trước khi APPROVE, PO cần ra quyết định về SD-01/SD-02.

### Scope deviations
| ID | Mức | Nội dung | Đề xuất |
|---|---|---|---|
| SD-01 | Medium (quy trình) | `frontend/src/utils/taxonomy.js` ngoài allowlist; refactor không đổi hành vi; report Codex ghi sai là "đúng allowlist" | PO chấp nhận hồi tố, hoặc FIX_LOOP hoàn nguyên (mục 1.2) |
| SD-02 | Low | `global.css` sửa `.container`, `.page-title` (≤600px, toàn site) và mở rộng `.field input` | PO xác nhận chấp nhận, hoặc yêu cầu giới hạn trong `.admin-movies` |

### Non-blocking TODOs
| ID | Mức | Nội dung | Đề xuất disposition |
|---|---|---|---|
| TODO-01 | Low | Report Codex mục 11/12 ghi "tất cả file nằm trong allowlist" dù có `taxonomy.js` | Ghi nhận; từ T05, Codex phải tự so `git diff --name-only` với mục 6 của task và nêu mọi file ngoài allowlist |
| TODO-02 | Low | T04 mục 13 ghi "ngoài 23 mục", thực tế là 22 thể loại (23 mục menu gồm "Phim 18+") | PO sửa câu chữ khi tiện; không đổi code |
| TODO-03 | Low | Lỗi 422 do sai kiểu, thiếu trường hay thừa trường vẫn kèm thông điệp Pydantic tiếng Anh (handler toàn cục có từ trước T04). UI chặn trước nên người dùng không gặp | ACCEPT_LATER → T11 |
| TODO-04 | Low | Cột `genre` là `String(100)`; chọn ≥ 10 thể loại tạo chuỗi 101 ký tự, SQLite vẫn nhận nên chưa lỗi. Chưa có giới hạn tổng độ dài | ACCEPT_LATER; nếu đổi DB thì thêm kiểm tra độ dài |
| TODO-05 | Info | DELETE phim chưa có vé còn xóa **bình luận** của phim (T04 chỉ nói suất chiếu). Cần làm vậy để giữ khóa ngoại, nhưng mất dữ liệu kiểm duyệt của phim đó | PO xác nhận chấp nhận |
| TODO-06 | Info | Câu 422 của mock không có tiền tố `Trường 'x' không hợp lệ:` như real; cấu trúc lỗi vẫn giống nhau | ACCEPT / WONT_FIX |
| TODO-07 | Info → T05 | Phim mới `now_showing` chưa có suất chiếu (backend chỉ sinh suất cho ngày chưa có suất; mock sinh vào ngày hôm sau). Phim chuyển `ended` vẫn giữ suất tương lai và vẫn đặt vé được (booking không kiểm `status`) | Đưa vào phạm vi T05 |
| TODO-08 | Info | Mock xóa `bookings` mỗi ngày (có từ trước T04), nên 409 ở mock chỉ tái hiện được trong ngày đặt vé | WONT_FIX |

---

## 9. Kết luận

**PASS_WITH_TODO.** Chức năng T04 đúng thiết kế, AC 7/7 có bằng chứng độc lập trên backend thật (PhoBERT), DB tạm, UI real mode và UI mock mode. Không có lỗi chức năng hay bảo mật, không đổi schema, không đụng Forbidden Files.

Điểm chưa đạt duy nhất thuộc về quy trình: gate Scope có hai sai lệch (SD-01, SD-02) mà Claude không có quyền tự chấp nhận. **Đề xuất chuyển T04 sang `PO_REVIEW`**, kèm điều kiện PO ghi rõ quyết định về SD-01 và SD-02 trong `po_review_T04_*` trước khi APPROVE.

## 10. Task kế tiếp

Theo `AGENT_RULES.md` mục 1.1, T05 (dependency T04) đủ điều kiện `READY_FOR_HANDOFF`. Tuy nhiên prompt review của PO yêu cầu rõ **"Không mở T05"**, nên Claude **giữ T05 ở `PLANNED`** và không soạn prompt bàn giao. Khi PO approve, merge T04 và quyết định mở T05, Tín (hoặc Claude theo yêu cầu) sẽ cập nhật trạng thái này.

## 11. Ghi chú môi trường review

- Probe đặt ở scratchpad ngoài repo, chạy với SQLite tạm. Cấu hình launch `frontend-mock-probe` đã gỡ, `.claude/launch.json` khôi phục từ bản sao lưu. localStorage của origin mock 5174 đã xóa. Mọi dev server đã dừng.
- Real mode có ghi vào `backend/firefly.db` (ngoài Git): tạo rồi xóa phim "ZZ Claude Probe T04" (id 22) và một lần DELETE phim đang chiếu bị chặn 409. Sau review, DB còn đúng 21 phim như ban đầu.
- `git status` sạch trước khi viết report.
