# Claude Final Independent Review — T10 — Post-Gate-2 — 11/10/2026

**Kết luận: PASS_WITH_TODO** — AC 7/7, Required Fixes 0. TODO toàn bộ thuộc governance/vận hành, không chặn PO review.

## 1. Task, ngày, commit

| Trường | Giá trị |
|---|---|
| Task | T10 — Gắn PhoBERT B vào web |
| Ngày review | 11/10/2026 |
| Branch | `task/T10-gan-model-B` |
| Reviewed HEAD | `27701d19a150117919e0172f2386d819a7b9d369` |
| Baseline | `38f63eedf3682216c1256cc581811e5ae9e05406` |
| Production code cuối | `ed26454` (RF-01 fix). `git diff ed26454 27701d1 -- backend frontend ml` **rỗng** → `27701d1` chỉ đổi tài liệu |

**Safety gate trước khi test: PASS.**
- Đúng branch và HEAD; worktree sạch.
- SHA-256 DB thật `B3F7DF79BDA4478412200EA80B8EC15E6B73DA730068A52E11C40136EAC4CFE3` khớp giá trị kỳ vọng; không có sidecar `-wal/-shm/-journal`.
- Không có `python.exe` nào đang chạy; không có listener trên 8000/8001/8011/18110/5173/5174.
- Không thực hiện cleanup MOVE/DELETE nào trên evidence.

## 2. Source review

- Code không đổi kể từ Round 2 (đối chiếu diff ở trên), gồm:
  - registry PhoBERT B mặc định, A dự phòng;
  - `RLock` riêng cho mỗi model bao toàn bộ nạp → suy luận → giải phóng;
  - version lấy từ env, rồi `version.txt`, rồi fingerprint `config.json`;
  - `comments.model_version` nullable;
  - health có `active_model`/`active_version` và trạng thái từng model;
  - `AdminComments`/`AdminModelCompare` hiện version; `mock.js` cùng contract.
- `normalize()` / `_ABBR` / `_PUNCT` / `_REPEAT`: 0 hunk thay đổi so với baseline.
- `backend/scripts/check_model.py`: chỉ import `app.classifier` và `app.config`; không import `app.main`/`app.database`, không seed, không mở SQLite.

## 3. Acceptance Criteria

| AC | Kết quả | Bằng chứng (loại) |
|---|---|---|
| AC-01 | **PASS** | **Mới, độc lập:** `check_model.py --model phobert_b` (exit 0): `PARITY=10/10`, `MAX_ABS_DELTA=0.000048`. Probe Transformers trực tiếp trên `ml/artifacts/phobert_B_best` (không qua backend; normalize lấy từ `ml/src`): 10/10, **Δ 0** so với JSON; movie test 149 (SHA `5AF8F616…C660`, 48/101): F1_neg `0.917525773196`, Macro-F1 `0.881839809675`, lệch T09 ≈ 1e-13. Runtime dir `backend/models/phobert-binhluan-B` giống từng byte artifact (6/6); `version.txt` = `phobert-B-2026-10-09`; `ml/test_sentences.json` SHA `D5C8BAAA…4547`, không đổi kể từ khi khóa ở `0e80015`. Không có dấu hiệu leakage hay sửa baseline |
| AC-02 | **PASS** | Mới: reference `0.998829185963`, runtime `0.9988`, nhãn `tieu_cuc`. Clone Smoke (JSON): comment id 14 `is_negative=true`, `0.9988` |
| AC-03 | **PASS** | Clone Smoke JSON `b_active.health`: `active_model=phobert_b`, `active_version=phobert-B-2026-10-09`, `classifier_error=null`; A `available/loaded=false/active=false`, B `loaded/active`. Quét JSON: không có password/secret/token |
| AC-04 | **PASS** | Clone: id 14 lưu/trả `phobert_b` / `phobert-B-2026-10-09`. Postverify JSON: `comments_count=13`, `old_comments_model_version_null=13`, 6 bảng được bảo toàn, integrity `ok`, FK 0. Không POST vào DB thật |
| AC-05 | **PASS** (bằng chứng lịch sử, cùng code) | Chọn A **thủ công** (không phải fallback): Claude Round 2 chạy tiến trình uvicorn độc lập với `ACTIVE_MODEL=phobert`: health `phobert/A-backend`, comment lưu `('phobert','A-backend',0.9937)`, đồng thời 18/18 + stress 30/30. Production code tại HEAD giống hệt code đã test (diff rỗng). Lượt này không chạy lại vì cần runtime ngoài phạm vi; `config.py` đọc `ACTIVE_MODEL` từ env/`.env` (mặc định `phobert_b`) |
| AC-06 | **PASS** | Clone Smoke JSON `a_fallback`: B trỏ thư mục cố ý thiếu → health `phobert/A-backend`, B `available=false` kèm lỗi rõ; comment id 15 `phobert/A-backend` `0.9937` |
| AC-07 | **PASS** (mục 7) | Kết hợp E2E lịch sử trên code giống hệt + Clone Smoke mới + build mới |

**ACCEPTANCE CRITERIA: 7/7 PASS.**

## 4. Definition of Done

| Mục | Trạng thái |
|---|---|
| AC-01…07 có evidence | MET |
| Quality gates (compile, check_model, build real/mock, security, scope) | MET |
| Security | MET |
| Regression 7/7 | MET (xem phạm vi ở mục 7) |
| Scope integrity | MET (mục 8) |
| Required Fixes = 0 | MET |
| Blocker kỹ thuật | 0 |
| Kiến trúc/contract | MET |
| Traceability evidence | MET — hash các artifact ở mục 11 |
| TODO đã phân loại | MET (mục 13) |

**DEFINITION OF DONE: MET** (ở mức kỹ thuật; việc closure và đồng bộ governance thuộc PO).

## 5. Architecture

- Registry giữ được các model T07 (svm/lr/nb/keyword).
- B mặc định theo Q3; A dự phòng không phụ thuộc việc B có nạp được hay không.
- Model active không bao giờ bị giải phóng.
- Engine DB chỉ lấy từ `config.DATABASE_URL`.
- Gate 2 dùng phương án A1 (một ALTER), đúng ngoại lệ `PO-DECISION-T10-REALDB-A1-GATE1-20261010` ghi trong `PROJECT_SOURCE_OF_TRUTH.md`.

## 6. Security

- `admin_predict.py:14` và mọi route admin trong `comments.py` (dòng 70/92/120/135) dùng `Depends(require_admin)`. `security.py` không đổi (403 kèm câu tiếng Việt).
- Clone Smoke JSON: anonymous/user/admin = **401/403/200**. Round 2 (cùng code): 401/403/200 trên 5 cấu hình.
- Diff baseline→HEAD: không có `.env`, `*.db`, `.safetensors`, `.joblib`, CSV, ZIP; quét `secret_key|password=|api_key|token=` trên dòng thêm: 0.
- Danh sách bình luận công khai không lộ `model_version` (Round 2).

**SECURITY: PASS.**

## 7. Regression

| # | Mục | Bằng chứng | Loại |
|---|---|---|---|
| 1 | Trang chủ, poster intro, chi tiết, đặt vé | Round 1 browser E2E (trang chủ → "Xem chi tiết" → trang phim; poster intro không kiểm từng khung hình) | Lịch sử; frontend tại HEAD giống từng byte (`git diff 0e80015 27701d1 -- frontend` rỗng; bundle mới có cùng tên hash `index-C9_3fB4L.js` như Round 1) |
| 2 | Thể loại/chủ đề, tìm kiếm | Round 1 browser (Kinh dị, "meo muop"); Round 2 API | Lịch sử, cùng code |
| 3 | Đăng ký, đăng nhập, redirect | Round 1 + Round 2 browser (22:00 → đăng nhập → `/dat-ve/20`) | Lịch sử, cùng code |
| 4 | Đặt 2 ghế, trạng thái ghế, Vé của tôi | Round 1 (A1/A2) + Round 2 (C1/C2) browser | Lịch sử, cùng code |
| 5 | Bình luận tiêu cực + kiểm duyệt | Round 2 browser (admin thấy `1.00 · phobert_b · phobert-B-2026-10-09`); **Clone Smoke mới** lưu model/version, 401/403/200 | Lịch sử + mới |
| 6 | Health mặc định B | **Clone Smoke mới** `phobert_b/phobert-B-2026-10-09` | Mới |
| 7 | Mock mode | **Build mock mới** (exit 0, chứa chuỗi `phobert-B-2026-10-09-mock`); Round 1/2 browser mock (0 request tới backend, version null → "Chưa có phiên bản") | Mới (build) + lịch sử (runtime) |

**Không có browser E2E mới trong lượt này.** Không khởi động backend, theo đúng phạm vi. Bằng chứng lịch sử áp dụng được vì production code và frontend tại HEAD giống từng byte với code đã E2E.

**REGRESSION: 7/7 PASS.**

## 8. Scope integrity

24 file thay đổi (`git diff --name-status 38f63ee...HEAD`), `git diff --check` sạch:

- **Production (allowlist T10):** `backend/app/{classifier,config,main,models,schemas}.py`, `routers/{admin_predict,comments}.py`, `backend/scripts/check_model.py`, `backend/.env.example`, `ml/test_sentences.json`, `frontend/src/api/mock.js`, `frontend/src/pages/{AdminComments,AdminModelCompare}.jsx` — **đúng allowlist**.
- **Tài liệu:**
  - `HUONG_DAN.md`, `docs/ARCHITECTURE.md` (allowlist);
  - `docs/tasks/T10.md` (ngoại lệ AC-01 của PO);
  - `docs/TASK_COORDINATION_ACTIVE.md`;
  - `docs/PROJECT_SOURCE_OF_TRUTH.md` — ngoại lệ một lần, PO cấp cho Codex để ghi Gate 1 (`codex_authority_sync_T10_A1_gate1_2026-10-10.md` §3, commit `27701d1`).
- **Reports:** 4 report `codex_*_T10_*` + 2 report Claude.
- Không đổi dependency manifest. Không có feature hay refactor ngoài phạm vi.

**SCOPE: PASS.**

## 9. Independent tests (lượt này)

Output ghi vào `C:\Projects\firefly-cinema\backup\T10_2026-10-10\disposable\claude_final_review_20261011_103131\`. Log tổng hợp: `backup\T10_2026-10-10\reports\T10_CLAUDE_FINAL_REVIEW_TEST_LOG_20261011.md` (SHA-256 `E011CDE5…9400`).

| Gate | Lệnh | Kết quả |
|---|---|---|
| Backend compile | `python -B -m compileall -q backend/app backend/scripts` (bytecode chuyển sang disposable qua `PYTHONPYCACHEPREFIX`) | exit 0 |
| Parity | `python -B scripts\check_model.py --model phobert_b` | exit 0, 10/10, Δ 0,000048 |
| Reference độc lập + movie 149 | Probe Transformers trực tiếp (`-I -B`) | exit 0; 10/10 Δ 0; F1/Macro khớp T09 |
| Frontend real | `npm run build -- --outDir <disposable>\frontend-dist-real --emptyOutDir` | exit 0 |
| Frontend mock | `VITE_USE_MOCK=true` + outDir `frontend-dist-mock` | exit 0 |
| Security / scope / secret | Static (mục 6, 8) | PASS |

Không khởi động backend, không kết nối SQLite với DB thật hay clone, không chạy lại ALTER/Postverify/Clone Smoke. Sau test: worktree sạch, không có `.pyc` mới trong source, SHA DB thật không đổi.

## 10. Temporary probes

- Tạo: `claude_ref_probe.py` trong thư mục disposable. **Đã xóa sau khi chạy.**
- Còn lại trong disposable: log, build output, bytecode — là output test, không phải probe.

**TEMPORARY PROBES REMAINING: 0.**

## 11. Database / evidence integrity

Claude đối chiếu trực tiếp JSON và hash; chỉ băm file, không mở SQLite.

| Artifact | SHA-256 (Claude tính) | Nội dung xác minh |
|---|---|---|
| `…\gate2_20261010_202624_922925+0700\manifest.json` | `D2E46C35…E9B4` (= `manifest.sha256`) | Decision `PO-DECISION-T10-REALDB-A1-GATE2-20261010`; git `27701d1`; hash-set `ABDC6993…899A` (= package đã review); source trước = `ED3ABDBA…0D0A`; 6 bảng, count tổng **559** (282+141+13+21+99+3); integrity `ok`, FK rỗng; 12 cột cũ |
| `firefly_online_backup.db` / `restore_validation\firefly_restored.db` | `BADCE9E0…8782` cả hai | Khớp manifest |
| `postverify_evidence.json` | `DDE0E114…8071` | `result=PASS`; `post_alter_sha256=B3F7DF79…CFE3` (= DB thật hiện tại); gắn với manifest và hash-set `ABDC…`; integrity `ok`; FK 0; 6 bảng; 13/13 comment cũ có NULL |
| `clone_smoke\clone_smoke_evidence.json` | `ECC9C299…BC92` | `result=PASS`; B/A/security như AC-02/03/04/06; `real_database_sha256_unchanged=B3F7…`; `original_clone_rows_preserved=true` |
| `clone_smoke\firefly_t10_smoke.db`, `backend_b.log`, `backend_fallback_a.log` | `08710CB7…C45C`, `DC426AF0…E071`, `1D498CC1…3CE9` | Khớp cột "actual" của hash reconciliation. Hai log có marker `EFFECTIVE_DATABASE_VERIFIED=<clone>`, 0 Traceback/500 |
| Reconciliation report | `8733C428…BAD2` | 4 lỗi chép hash trong report lịch sử (`92C53BD1…`) là `REPORT_TRANSCRIPTION_ERROR`, không có file nào lệch. Report lịch sử được giữ nguyên, Claude không sửa |
| Final Candidate (6 file) | `56CAB1EE`, `F81496DB`, `6F812ECE`, `E957A2D2`, `3624F177`, `FDCDCCA4` | Không đổi so với bản đã review GC-RF-01 |

Cột `comments.model_version` = VARCHAR(100), nullable: `04_postverify.py` (đã review) chỉ ghi PASS khi định nghĩa cột đúng `[n,'model_version','VARCHAR(100)',0,None,0]`, và evidence ghi `result=PASS`.

**DATABASE EVIDENCE: PASS. REAL DB PRESERVED: YES.** SHA hiện tại = `post_alter_sha256`; 559 dòng gốc được bảo toàn theo postverify.

## 12. Required Fixes

**0.**

## 13. TODO

| ID | Severity | Nội dung | Đề xuất |
|---|---|---|---|
| F-TODO-01 | Medium (governance) | `TASK_COORDINATION_ACTIVE.md` còn ghi `PO_REVIEW / PENDING_PO_DB_ACTION`, "Gate 2 NOT AUTHORIZED", trong khi evidence cho thấy ALTER đã COMMIT dưới `PO-DECISION-T10-REALDB-A1-GATE2-20261010`. Trong Git chưa có bản ghi nào của quyết định thực thi Gate 2 (SoT/coordination) | PO đồng bộ coordination và ghi quyết định Gate 2 (`COORDINATION_SYNC_PENDING`) |
| F-TODO-02 | Medium (vận hành) | Lần đầu khởi động backend trên DB thật sau ALTER sẽ chạy `seed()`/`_ensure_showtimes()` (ghi suất chiếu). Gate 2 không cấp quyền khởi động | PO quyết định riêng trước demo (kèm backup) |
| F-TODO-03 | Low | `T10.md` vẫn `Current Status: IN_PROGRESS` | ACCEPT_WITH_NOTES (coordination là nguồn trạng thái) |
| F-TODO-04 | Low | `CLAUDE.md` và `BOI_CANH_DU_AN.md` mục 7 còn ghi health `classifier: phobert` | PO cập nhật tài liệu PO-owned |
| F-TODO-05 | Low | `C:\Projects\T10_GATE2_A1_FINAL_CANDIDATE_20261010\__pycache__\02_fresh_backup.cpython-313.pyc` sinh ra lúc chạy ALTER (21:33:18). Nằm ngoài hash-set 6 file; Codex đã ghi nhận trong cleanup audit | PO quyết định lưu giữ; lần sau chạy package với `-B` |
| F-TODO-06 | Low | Health trả nguyên văn `classifier_error`, kể cả đường dẫn đã cấu hình (trong smoke là đường dẫn tuyệt đối). Thuộc T07 TODO-03 | Giữ ACCEPT_LATER → T11 |
| F-TODO-07 | Info | TODO Round 2 (02 làm tròn 4 chữ số, 05 mock dùng `fakeClassify`, 06 T07 TODO-05, 07 lock tuần tự hóa) và G2-R4-01…04 | Giữ disposition hiện có |

**TODO: 7.**

## 14. Governance discrepancy

1. Coordination lỗi thời so với Gate 2 (F-TODO-01). Claude **không** tự sửa và không commit trong lượt này.
2. Prompt đề xuất "CLAUDE_REVIEW → PO_REVIEW", nhưng coordination đang ghi `PO_REVIEW / PENDING_PO_DB_ACTION` (đã ở PO_REVIEW từ Round 2). Vì vậy trạng thái đúng cần PO chốt là "PO_REVIEW — Gate 2 executed, Claude Final PASS_WITH_TODO".
3. `AGENT_RULES.md` mục 1.1: khi PASS thì task kế tiếp theo thứ tự là **T11** (dependency T04–T10). Nhưng PO đang giữ T11 `PLANNED / NOT AUTHORIZED`. Claude **không** chuyển T11 sang `READY_FOR_HANDOFF`; chỉ đề xuất ở mục 17.
4. Không có sai lệch giữa evidence JSON và kết quả Claude tái lập.

## 15. Final decision

**PASS_WITH_TODO.**

## 16. Transition recommendation

- Giữ T10 ở **PO_REVIEW** (cập nhật mô tả theo Gate 2 khi PO đồng bộ coordination).
- Không DONE/CLOSED, không merge/tag `phobert-B`, cho tới khi PO approve.

## 17. Remaining PO decisions

1. Approve hay không T10 dựa trên report này; disposition F-TODO-01…07.
2. Đồng bộ coordination và ghi quyết định Gate 2 vào nguồn authority.
3. Quyền khởi động backend trên DB thật (F-TODO-02).
4. Merge vào `master` + tag `phobert-B` (chỉ Tín).
5. Có authorize T11 hay không. Đề xuất (chưa được authorize): sau merge, tạo `task/T11-...` từ `master`; scope cần PO xác nhận các TODO đã đưa vào T11 (T04-TODO-03/04, T05-TODO-01/03/05, T06-TODO-01/02/03, T07-TODO-02/03/04, booking phim ended, `httpx` cho pytest).

---

TASK: T10
REVIEWED HEAD: 27701d19a150117919e0172f2386d819a7b9d369
CLAUDE FINAL REVIEW: PASS_WITH_TODO
ACCEPTANCE CRITERIA: 7 / 7 PASS
DEFINITION OF DONE: MET
BACKEND GATES: PASS
FRONTEND GATES: PASS
REGRESSION: 7 / 7 PASS
SECURITY: PASS
SCOPE: PASS
DATABASE EVIDENCE: PASS
REAL DB PRESERVED: YES
TEMPORARY PROBES REMAINING: 0
REQUIRED FIXES: 0
TODO: 7
COORDINATION SYNC: PENDING
GIT COMMIT: NOT CREATED
T10 PO APPROVAL: PENDING
T10 CLOSURE: NOT AUTHORIZED
T11: NOT AUTHORIZED
NEXT STEP: PO REVIEW CLAUDE FINAL REVIEW

**HARD STOP — báo cáo cho Product Owner.**
