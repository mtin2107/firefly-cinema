# Txx — <Tên task>

| Trường | Giá trị |
|---|---|
| Task ID | Txx |
| Module | Web / ML / Dữ liệu / Tất cả |
| Assignee | Codex |
| Reviewer | Claude |
| Approver | Tín (PO) |
| Nhánh | `task/Txx-ten-ngan` |
| Dependencies | Txx (phải CLOSED) |
| Yêu cầu liên quan | FR-…, NFR-… (REQUIREMENTS.md) |
| Ước lượng | … ngày |
| Current Status | PLANNED |

## 1. Objective
<Một đến ba câu: xong task thì sản phẩm có thêm gì.>

## 2. Context
<Vì sao cần, liên quan mục nào trong BOI_CANH_DU_AN.md / ARCHITECTURE.md.>

## 3. Scope
### Allowed Scope
- …

### Out of Scope
- …

## 4. Thiết kế
- **Backend:** model / schema / endpoint (phương thức, đường dẫn, request, response, mã lỗi, quyền).
- **Frontend:** trang / component mới; hàm thêm vào `real.js` **và** `mock.js`.
- **Dữ liệu / ML:** notebook, file vào / ra, đường dẫn Drive, seed.

## 5. Đổi schema?
Có / Không. Nếu có: các bước người dùng phải làm (xóa `backend\firefly.db`…), đã ghi vào `HUONG_DAN.md` chưa.

## 6. Allowed Files to Modify
- `đường/dẫn/cụ/thể`
- `reports/YYYY-MM-DD/codex_*_Txx_*.md`
- `docs/TASK_COORDINATION_ACTIVE.md`

## 7. Forbidden Files to Modify
- `docs/PROJECT_SOURCE_OF_TRUTH.md`, `docs/AGENT_RULES.md`, `docs/BOI_CANH_DU_AN.md`
- `.env`, `firefly.db`, `backend/models/`
- `frontend/src/styles/global.css` phần biến màu `:root` (trừ khi task ghi rõ)
- …

## 8. Acceptance Criteria
- [ ] AC-01 …
- [ ] AC-02 …
- [ ] AC-xx Qua checklist hồi quy `BOI_CANH_DU_AN.md` mục 7 (task web)

## 9. Definition of Done
- [ ] Toàn bộ AC đạt, có bằng chứng trong report
- [ ] Gate theo `AGENT_RULES.md` mục 3 đạt
- [ ] Không có file ngoài allowlist trong diff
- [ ] Tài liệu liên quan đã cập nhật (`ARCHITECTURE.md` / `CONG_NGHE.md` / `HUONG_DAN.md` nếu có đổi)
- [ ] Claude PASS hoặc PASS_WITH_TODO, Tín APPROVED

## 10. How to Test
```powershell
# lệnh PowerShell hoặc mô tả ô Colab
```

## 11. Required Gates
Web: compileall · backend khởi động + `/api/health` · `npm run build` · mock mode (nếu đụng API) · hồi quy · pytest (từ T11).
ML: tái lập seed · đúng cách chia · đúng `normalize()` · kết quả nhỏ vào `ml/results/`.

## 12. Expected Reports
- `reports/YYYY-MM-DD/codex_implementation_Txx_YYYY-MM-DD.md`
- `reports/YYYY-MM-DD/claude_review_Txx_<RESULT>_YYYY-MM-DD.md`
- `reports/YYYY-MM-DD/po_review_Txx_<DECISION>_YYYY-MM-DD.md`

## 13. Rủi ro / câu hỏi mở cho PO
- …
