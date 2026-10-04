# AGENT RULES — áp dụng workflow Codex + Claude cho Firefly Cinema

> Chính sách chung: `CODEX_CLAUDE_REVIEW_WORKFLOW_POLICY.md`. File này chỉ ghi phần **riêng của dự án**: ai làm gì, gate nào, Git thế nào, prompt dán vào đâu.
> Khi file này khác `BOI_CANH_DU_AN.md` mục 11, **file này thắng** (nó thay quy trình cũ).

## 1. Luồng một task

```
PLANNING            Task Record docs/tasks/Txx.md đã có sẵn (bản nháp T00–T15)
   │                Tín gửi Txx.md cho ChatGPT/Codex = PO DUYỆT Task Record như bản đang có
   ▼                (không cần bước duyệt riêng; muốn sửa thì Tín sửa Txx.md TRƯỚC khi gửi)
READY_FOR_HANDOFF   Tín tạo nhánh: git checkout -b task/Txx-ten-ngan
   ▼
IN_PROGRESS         Codex code + test trong allowlist, chạy gate
   ▼                Report: reports/YYYY-MM-DD/codex_implementation_Txx_YYYY-MM-DD.md
CLAUDE_REVIEW       Claude đọc code thật, chạy gate độc lập
   ├─ FAIL ────────► FIX_LOOP → Codex sửa đúng RF-xx → codex_fix_Txx_roundN → CLAUDE_REVIEW
   └─ PASS / PASS_WITH_TODO
   ▼
PO_REVIEW           Tín chạy thử, xử lý từng TODO, ra quyết định
   ▼
PO_APPROVED → DONE  Tín merge vào master, gắn tag nếu là mốc
   ▼
CLOSED              File điều phối về "Current Active Task: NONE"
```

**Mỗi lần chỉ một task ở trạng thái IN_PROGRESS.** Task ML (Colab) và task dữ liệu T03 được phép chạy song song với một task web, nhưng phải ghi rõ trong file điều phối.

### 1.1. Ủy quyền: Claude chuẩn bị task kế tiếp (Tín chốt 04/10/2026)

Ngoại lệ có chủ đích so với chính sách mục 2.2 ("Claude không tự tạo task tiếp theo"). Task Record T00–T15 đã có sẵn, nên Claude **chỉ chuyển trạng thái, không soạn task mới**.

Khi Claude review task hiện tại ra **PASS** hoặc **PASS_WITH_TODO** (mọi TODO đều không chặn task sau), Claude làm thêm:
1. Chọn task kế tiếp theo **thứ tự bàn giao** bên dưới: lấy task đầu tiên chưa xong mà đạt cả 3 điều kiện:
   - mọi dependency đã `CLOSED`, hoặc chính là task vừa PASS;
   - không bị chặn bởi câu hỏi mở (Q1–Q4) hay blocker;
   - không phải task tùy chọn (T14, T15 chỉ mở khi Tín yêu cầu).
2. Ghi task đó là `READY_FOR_HANDOFF` trong file điều phối, cùng commit với review report.
3. Ở cuối review report, thêm mục **"Bàn giao task kế tiếp"** gồm prompt ChatGPT soạn sẵn cho task đó, theo mẫu prompt T00.

Claude **không** được: chuyển task vừa review sang `PO_APPROVED` / `CLOSED`, merge, gắn tag, hay sửa nội dung `Txx.md`.
FAIL thì không mở task kế tiếp.

**Thứ tự bàn giao:** T00 → T01 → T02 → T04 → T05 → T06 → T07 → T08 → T09 → T10 → T11 → T12 → T13.
T03 chạy song song: Claude đánh dấu T03 `READY_FOR_HANDOFF` ngay khi Q1 được chốt.

**Việc Tín vẫn phải làm trước khi gửi task kế tiếp cho ChatGPT:**
1. PO review task vừa PASS, rồi `git checkout master` → `git merge task/Txx-...` (gắn tag nếu là mốc).
2. `git checkout -b task/Tyy-...` **từ master đã merge**, để Codex làm trên code mới nhất.
3. Gửi prompt trong mục "Bàn giao task kế tiếp" kèm `Tyy.md` và file điều phối.

## 2. Ai được sửa gì

| File | Codex | Claude | Tín |
|---|---|---|---|
| Production code (`frontend/`, `backend/`, `ml/src/`) | Có, trong allowlist | **Không** | Có |
| Test (`backend/tests/`) | Có | Chỉ probe tạm, xóa trước gate cuối | Có |
| `docs/tasks/Txx.md` | Soạn ở PLANNING; sau khi duyệt chỉ sửa khi Tín yêu cầu | Không | Có |
| `docs/TASK_COORDINATION_ACTIVE.md` | Cập nhật trạng thái mình chuyển được | Cập nhật kết quả review; đặt task kế tiếp `READY_FOR_HANDOFF` khi PASS (mục 1.1) | Cập nhật duyệt PO |
| `docs/ARCHITECTURE.md`, `CONG_NGHE.md`, `HUONG_DAN.md` | Khi task đổi kiến trúc / thư viện / cách chạy | Không | Có |
| `docs/PROJECT_SOURCE_OF_TRUTH.md`, `AGENT_RULES.md`, `BOI_CANH_DU_AN.md` | Không | Không | Có |
| `reports/` | Report của mình | Report của mình | Report PO |

## 3. Quality gate theo loại task

Dự án chưa có linter. Dùng các gate sau (lệnh PowerShell, chạy ở `C:\Projects\firefly-cinema`).

### 3.1. Task web

| Gate | Lệnh / cách làm | Bắt buộc |
|---|---|---|
| Backend biên dịch | `backend\venv\Scripts\python -m compileall -q backend\app` | Có |
| Backend khởi động | `cd backend; venv\Scripts\Activate.ps1; uvicorn app.main:app --port 8000` rồi mở `/api/health` | Có |
| Frontend build | `cd frontend; npm run build` | Có |
| pytest | `cd backend; venv\Scripts\python -m pytest -q` | Từ T11 trở đi |
| Mock mode | Đặt `VITE_USE_MOCK=true`, chạy `npm run dev`, đi hết luồng của task | Khi task đụng lớp API |
| Hồi quy | Checklist `BOI_CANH_DU_AN.md` mục 7 (7 mục) | Có |
| Scope | `git diff --stat master...HEAD` chỉ chứa file trong allowlist | Có |
| Bí mật | `git diff master...HEAD --name-only` không có `.env`, `*.db`, model, CSV lớn | Có |

### 3.2. Task ML / dữ liệu (Colab)

| Gate | Cách làm |
|---|---|
| Tái lập | Seed cố định; chạy lại notebook từ runtime mới ra cùng số (sai lệch ≤ 0,001) |
| Đúng cách chia | Dùng đúng `train/dev/test.csv` trên Drive; không dùng test để chọn siêu tham số |
| Đúng tiền xử lý | Notebook import hoặc chép nguyên văn `normalize()` của backend, có ô so sánh trên 20 câu mẫu |
| Kết quả nhỏ vào Git | `ml/results/*.csv`, `*.md`, hình PNG; model và dữ liệu lớn chỉ ghi đường dẫn Drive / ổ D |
| Bằng chứng | Report đính kèm bảng số liệu và đường dẫn notebook trên Drive |

Claude không chạy được Colab: với task ML, Claude kiểm tra notebook, file kết quả, tính nhất quán số liệu và tái lập phần chạy được trên CPU (ví dụ mô hình truyền thống). Phần cần GPU do Tín chạy lại khi PO_REVIEW nếu cần.

## 4. Git

- Nhánh: `task/Txx-ten-ngan` tách từ `master`. Commit dạng `[Txx] mô tả`.
- Report và cập nhật file điều phối được commit trong cùng nhánh task.
- Chỉ Tín merge vào `master`, sau `PO_APPROVED`.
- Tag mốc: T02 → `ml-baselines`, T07 → `admin-v1`, T09/T10 → `phobert-B`, T13 → `v1.0`.

## 5. Quy ước đặt tên report

Dùng đúng chính sách mục 8, Task ID là `T00` … `T15`:

```
reports/2026-10-05/codex_implementation_T00_2026-10-05.md
reports/2026-10-05/claude_review_T00_FAIL_2026-10-05.md
reports/2026-10-06/codex_fix_T00_round1_2026-10-06.md
reports/2026-10-06/claude_review_T00_round2_PASS_2026-10-06.md
reports/2026-10-06/po_review_T00_APPROVED_2026-10-06.md
```

## 6. Prompt mẫu

### 6.1. Codex — PLANNING (soạn Task Record, chạy một lần đầu)

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Đọc theo thứ tự: PROJECT_SOURCE_OF_TRUTH.md, AGENT_RULES.md, TASK_COORDINATION_ACTIVE.md,
BOI_CANH_DU_AN.md (mục 6, 9, 10), ARCHITECTURE.md, REQUIREMENTS.md, tasks/_TEMPLATE.md.

Việc: soạn Task Record cho <T00 | T00–T15> theo đúng tasks/_TEMPLATE.md.
- Mỗi task một file docs/tasks/Txx.md.
- Allowed Files phải là danh sách file cụ thể, không ghi chung chung "frontend/".
- Acceptance Criteria đánh số AC-01, AC-02... và kiểm được bằng lệnh hoặc thao tác cụ thể.
- Gắn mã yêu cầu FR-/NFR- từ REQUIREMENTS.md.
- Câu hỏi chưa rõ ghi vào mục "Câu hỏi mở cho PO", không tự quyết.
- Current Status: PLANNED.
Không viết code. Trả lời bằng tiếng Việt.
```

### 6.2. Codex — Implementation

```text
Bạn là Codex, Primary Implementer của dự án Firefly Cinema.
Chỉ đọc: PROJECT_SOURCE_OF_TRUTH.md, AGENT_RULES.md, TASK_COORDINATION_ACTIVE.md (Snapshot, Status, Next Step),
docs/tasks/<Txx>.md, và source/test liên quan trực tiếp. Không đọc task CLOSED trừ khi là dependency.

Thực hiện <Txx> trên nhánh task/<Txx>-<ten-ngan>, chỉ sửa file trong Allowed Files.
Chạy gate theo AGENT_RULES.md mục 3 (focused trước, full sau).
Tạo reports/<YYYY-MM-DD>/codex_implementation_<Txx>_<YYYY-MM-DD>.md theo mẫu ở chính sách mục 11,
thêm dòng "Đổi schema: Có/Không" và kết quả checklist hồi quy.
Cập nhật TASK_COORDINATION_ACTIVE.md: IN_PROGRESS -> CLAUDE_REVIEW.
Không tự review, không tự PASS, không mở task kế tiếp. Trả lời bằng tiếng Việt.
```

### 6.3. Claude — Review (chạy trong Claude Code tại repo)

```text
Bạn là Claude, Independent Reviewer của Firefly Cinema.
Đọc: PROJECT_SOURCE_OF_TRUTH.md, AGENT_RULES.md, TASK_COORDINATION_ACTIVE.md, docs/tasks/<Txx>.md,
report Codex mới nhất của <Txx>, rồi `git diff master...task/<Txx>-...` và source/test liên quan.
Review theo chính sách mục 12, chạy gate độc lập theo AGENT_RULES.md mục 3.
Không sửa production code. Probe tạm phải xóa trước gate cuối.
Tạo reports/<YYYY-MM-DD>/claude_review_<Txx>_<RESULT>_<YYYY-MM-DD>.md và cập nhật file điều phối.
```

### 6.4. Codex — Fix

```text
Bạn là Codex, Fix Implementer cho <Txx>.
Chỉ đọc: docs/tasks/<Txx>.md, TASK_COORDINATION_ACTIVE.md, report Claude FAIL mới nhất, source/test liên quan RF.
Chỉ sửa các RF-xx được nêu. Không thêm feature, không xóa test.
Chạy lại gate, tạo reports/<YYYY-MM-DD>/codex_fix_<Txx>_round<N>_<YYYY-MM-DD>.md,
cập nhật file điều phối FIX_LOOP -> CLAUDE_REVIEW.
```

### 6.5. Tín — PO Review (tự làm hoặc nhờ trợ lý soạn nháp)

Dùng mẫu chính sách mục 18. Mỗi TODO trong review Claude phải có disposition: `ACCEPT_LATER (task nào)`, `FIX_NOW`, hoặc `WONT_FIX (lý do)`.

## 7. Escalation

- FAIL 2 vòng liên tiếp cùng một RF: dừng, Codex viết phân tích nguyên nhân gốc vào report, Tín quyết.
- Task cần thư viện mới, đổi giao diện đã chốt, đổi `normalize()`, đổi schema ngoài kế hoạch: `BLOCKED` cho tới khi Tín trả lời.
