# Claude Review — T27 Thang điểm 10 và khung đánh giá có hiệu ứng

| Trường | Giá trị |
|---|---|
| Task | T27 |
| Nhánh / commit review | `task/T27-thang-diem-10` @ `73a57f6` (base `master` `ea79fe6`) |
| Ngày | 25/10/2026 (00:40–01:10) |
| Reviewer | Claude (độc lập) |
| Kết luận | **PASS_WITH_TODO** |
| Required Fix | 0 |
| TODO | 1 (Low) · OBS 1 (test có sẵn từ T21) |

## 1. Scope
`git diff --stat master...task/T27-thang-diem-10`: 19 file, +382/−65. **19/19 trong allowlist** mục 6. Không đụng `:root`, `.env`, `*.db`, `requirements.txt`, `package.json`. `CommentSection.jsx` chỉ đổi dòng hiển thị điểm.

## 2. Gate độc lập
| Gate | Kết quả |
|---|---|
| `compileall -q backend\app` | exit 0 |
| `pytest -q` | **200 passed, 1 failed** — test fail là `test_sentiment.py::test_sentiment_uses_effective_label_group_by_and_complete_daily` (T21), **fail y hệt trên `master`** khi chạy lúc 00:42; xem OBS-01. Toàn bộ test rating/T27 đạt. |
| `npm run build` real / mock | đạt / đạt |
| Backend tạm + health (SQLite tạm, cổng 8005) | `ok`, `phobert_b` |

## 3. Probe API (HTTP thật, DB tạm)
| Trường hợp | Kết quả |
|---|---|
| `PUT /rating` 1 / 10 | 200 |
| `PUT /rating` 0, 11, 5.5, `"8"`, `true`, `null` | 422 "Điểm phải từ 1 đến 10." |
| `distribution` | đủ khóa `"1"`…`"10"`, tổng = `rating_count`; `rating_avg` 8.3 khớp tính tay |
| `GET /my-rating` | khóa `stars`, `rating_avg`, `rating_count`, `distribution` |
| Seed | điểm khán giả mẫu nằm trong 6–10; có test seed hai DB rỗng (`test_t27_seed_two_fresh_databases`) |
| Constraint DB | DDL `CHECK (stars BETWEEN 1 AND 10)`; `UPDATE … stars=11` trực tiếp → `CHECK constraint failed: ck_rating_stars` |
| Bình luận kèm điểm 9 / 11 / không điểm | 201 (`author_stars=9`) / 422 / 201 |
| `DELETE /rating` | 200, `stars=null`, phân bố cập nhật |

## 4. Trình duyệt (khung Browser hiển thị thật, ~144 khung hình/giây)
| AC | Kết quả |
|---|---|
| AC-05 bố cục | Đầu khung poster + "ĐÁNH GIÁ PHIM" + tên + nhãn tuổi/thể loại/thời lượng + nút ✕; vòng điểm 8.3 tô 298.8° (= 8.3/10); 5 thanh 9–10:3, 7–8:2, 5–6:1, 3–4:0, 1–2:0 khớp API; 10 sao; nhãn "9 điểm · Xuất sắc". |
| AC-07 hiệu ứng | Mở: khung mờ dần vào (opacity 0.42 → 1), số điểm đếm 1.7 → 6.9 → 8.0 → 8.3. Chọn 9: sao nảy, **18** hạt đom đóm; sau 1,5 s còn **0** hạt. Lưu: số 8.3 → 8.4, 18 hạt bay từ vòng điểm, "Đã lưu 9 điểm · cảm ơn bạn!", tự đóng, không sót hạt. |
| AC-07 giảm chuyển động | Giả lập `prefers-reduced-motion: reduce` (thay `matchMedia` trong trang trước khi dựng lại component): mở khung opacity 1, transform none, số hiện ngay 6.5; chọn 9 → 0 hạt, không nảy; lưu → 7.3 ngay, 0 hạt, khung vẫn tự đóng. |
| AC-06 hành vi T26 | Lưu → `★ 8.4/10 (7 lượt)`, "Bạn đã chấm 9/10", focus về nút điểm. |
| AC-08 | Mở khung: focus ở nút ✕ "Đóng", **0** sao sáng (T26 TODO-01 đóng). |
| AC-04 hiển thị | Trang chủ `★ 8.6/10 (5 lượt)`; chọn ghế `★ 8.4/10 (7 lượt)`; bình luận `★ 9/10` (`aria-label` "Chấm 9 trên 10 điểm"); dashboard "Điểm 8.0 / 10 · 70 lượt", bảng phim "8.3 / 10"; không còn chuỗi "/ 5"; form bình luận có 10 sao. |
| AC-09 | 375px: dialog 337px, `scrollWidth` trang 375, dialog không cuộn ngang; 10 sao một hàng, mỗi sao 28px, sao 10 kết thúc ở x=334; lúc đom đóm bay vẫn không tràn. 1280px: không tràn. |
| AC-10 mock | `my-rating` 4 khóa, `distribution` 10 khóa; `set(11)` → 422 "Điểm phải từ 1 đến 10."; dialog hiện phân bố, chọn 6 → 8 hạt, lưu `8.1 → 8.0`, "Bạn đã chấm 6/10". |

## 5. TODO (Low, không chặn)
**TODO-01 — Validator điểm phân biệt lớp bằng tên lớp.**
- File: `backend/app/schemas.py`, `ScoreInput.valid_score`.
- Problem: `if value is None and cls.__name__ == "CommentIn"` — đổi tên lớp hoặc thêm lớp con mới sẽ làm sai luật `None` mà không có lỗi rõ ràng.
- Evidence: đọc code; hành vi hiện tại đúng (probe mục 3).
- Expected Fix: để `CommentIn` tự cho phép `None` (ví dụ validator riêng hoặc tham số lớp), không dựa vào `__name__`. Có thể để sau v1.0.

## 6. Quan sát
**OBS-01 — `test_sentiment` (T21) fail khi chạy trong khoảng 0h–7h sáng giờ Việt Nam.**
- Fail giống hệt trên `master` (worktree tạm, 00:42 ngày 25/10), nên không do T27. Test lấy ngày bằng `datetime.now().date()` (giờ máy) trong khi dữ liệu tính theo UTC, nên trước 7h sáng hai bên lệch một ngày. Codex chạy lúc ban ngày nên được 201/201.
- Khuyến nghị: ghi vào "Hạn chế" ở T13 hoặc sửa test trong một task nhỏ; nhớ chạy gate cuối T13 vào ban ngày.

## 7. Lưu ý cho PO
- **Đổi schema:** sau merge phải dừng backend, sao lưu `firefly.db` + sidecar (+ `backend\uploads\` nếu đã có trailer), kiểm SHA-256/integrity, xóa `firefly.db`, khởi động lại (`HUONG_DAN.md` mục T27). Không chạy code mới trên DB cũ: bảng `ratings` cũ vẫn giữ constraint 1–5, nên chấm 6–10 sẽ lỗi.
- Trailer đã thêm sau lần reset T25 sẽ còn file trong `backend\uploads\trailers\`, nhưng đường dẫn trong DB mất → phải gắn lại cho phim.
- Khóa luận/slide: đổi "thang 5 sao" thành "thang 10 điểm".

## 8. Bàn giao task kế tiếp — prompt Codex T13
T27 PASS_WITH_TODO, nên T13 chuyển sang `READY_FOR_HANDOFF` sau khi PO merge T27 và reset DB. Tín điền quyết định trước khi gửi.

```text
Bạn là Codex, dự án Firefly Cinema (C:\Projects\firefly-cinema, Windows + PowerShell).
Đọc theo thứ tự: docs/PROJECT_SOURCE_OF_TRUTH.md, docs/AGENT_RULES.md, docs/TASK_COORDINATION_ACTIVE.md, docs/tasks/T13.md. T13.md là bản PO đã duyệt.
T24, T25, T26, T27 đã merge vào master; DB thật đã reset sau T27 (bản sao trước đó ở backup\db-truoc-T25 và bản PO tạo trước T27). Làm trên nhánh task/T13-v1 (tạo từ master mới). Đầu tiên ghi closure T24–T27 (merge hash) và đặt T13 → IN_PROGRESS.

Quyết định PO trước T13 (Tín điền trước khi gửi):
- T12 TODO-01 (model B che câu khen phim 1): <giữ nguyên + ghi hạn chế | admin duyệt sẵn | đổi phim mở đầu>
- T14 TODO-02 (mã vé dùng lại sau khi hủy): <ghi hạn chế | ...>
- T25 TODO-01/02 (ô chọn video báo trống; ô YouTube hiện đường dẫn nội bộ): <ghi hạn chế | ...>
- T27 TODO-01 (validator điểm dựa vào tên lớp) và OBS-01 (test_sentiment fail 0h–7h): <ghi hạn chế | ...>

Nhiệm vụ: T13 "Chốt v1.0 và sao lưu" — chỉ tài liệu và sao lưu, không viết tính năng.
- README.md (giới thiệu, ảnh, tính năng gồm T16–T27: banner trailer, Nội dung phim, khung đánh giá thang 10 có hiệu ứng; kết quả F1 A/B/SVM/NB/LR và T15; cách chạy nhanh), HUONG_DAN.md (cài từ số 0, gắn model A/B/SVM, cấu hình .env gồm BANK_* cho QR và CHAT_* cho chatbot — chỉ tên khóa, không giá trị; chạy test; reset demo; định dạng video trailer).
- Mục "Hạn chế" gom: các quyết định PO ở trên, T14 TODO-04 (đổi mật khẩu không vô hiệu token cũ), T22 (ai đăng nhập cũng chấm điểm; OBS-01 model B nhầm câu khen), T23 OBS-01 (soát vé không chặn theo giờ chiếu), T24 OBS-01, T25 (file video mồ côi khi thay/gỡ; YouTube cần mạng và quyền nhúng; video mock mất khi tải lại).
- docs/SAO_LUU.md phải gồm cả backend\uploads\ (poster và trailers); docs/images/*, CHANGELOG.md [1.0.0], cập nhật cuối CONG_NGHE.md/ARCHITECTURE.md; xử lý T18 TODO-03 và T00 TODO-03 theo T13.md.
Ràng buộc: chỉ file trong mục 6 của T13.md; không sửa code; không commit model/DB/.env/video/dữ liệu lớn; không đọc hay in giá trị khóa trong .env.
Gate: compileall, pytest (chạy ban ngày, sau 7h sáng), npm run build (real + mock) để xác nhận không hồi quy.
Commit "[T13] mô tả". Viết reports/YYYY-MM-DD/codex_implementation_T13_YYYY-MM-DD.md, đặt T13 sang CLAUDE_REVIEW. Không merge, không gắn tag v1.0 (Tín gắn).
```

**Việc Tín cần làm:** merge `task/T27-thang-diem-10` → sao lưu và reset DB (mục 7) → gắn lại trailer nếu cần → `git checkout -b task/T13-v1` → gửi prompt trên.
