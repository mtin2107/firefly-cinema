# Bộ tài liệu Firefly Cinema — mục lục và cách tải lên nguồn

> Lập ngày 03/10/2026. File này cho biết mỗi tài liệu dùng để làm gì, ai được sửa, và tải file nào lên nguồn (project knowledge) của ChatGPT/Codex.

## 1. Danh sách tài liệu

| File | Vai trò | Ai sửa | Tải lên nguồn |
|---|---|---|---|
| `docs/PROJECT_SOURCE_OF_TRUTH.md` | Cổng vào: vai trò, thứ tự ưu tiên nguồn, quyết định đã chốt | Tín | **Có** |
| `docs/BOI_CANH_DU_AN.md` | Bối cảnh chi tiết: kiến trúc, quy ước, model A, kế hoạch T00–T15 | Tín | **Có** |
| `docs/REQUIREMENTS.md` | Yêu cầu chức năng / phi chức năng, gắn với task | Codex đề xuất, Tín duyệt | **Có** |
| `docs/ARCHITECTURE.md` | Hợp đồng kỹ thuật bất biến (API, DB, model, luật đồng bộ) | Codex khi task đổi kiến trúc, Tín duyệt | **Có** |
| `docs/CONG_NGHE.md` | Công nghệ và lý do lựa chọn | Codex khi thêm thư viện | **Có** |
| `docs/AGENT_RULES.md` | Áp dụng workflow vào dự án này: gate, nhánh Git, prompt mẫu | Tín | **Có** |
| `docs/CODEX_CLAUDE_REVIEW_WORKFLOW_POLICY.md` | Chính sách workflow chung (bản gốc) | Không sửa | **Có** |
| `docs/TASK_COORDINATION_ACTIVE.md` | Trạng thái task đang chạy (single active source of truth) | Codex, Claude, Tín theo vai | Có, **tải lại mỗi khi đổi trạng thái** |
| `docs/tasks/_TEMPLATE.md` | Mẫu Task Record | Không sửa | Có |
| `docs/tasks/Txx.md` | Task Record từng task (Codex viết, Tín chốt) | Codex soạn, Tín duyệt | Chỉ task đang làm |
| `reports/YYYY-MM-DD/*.md` | Báo cáo Codex / Claude / PO | Theo vai | Không (chỉ dán report mới nhất khi cần) |

## 2. Thứ tự tải lên nguồn ChatGPT/Codex

1. `PROJECT_SOURCE_OF_TRUTH.md`
2. `AGENT_RULES.md`
3. `TASK_COORDINATION_ACTIVE.md`
4. `BOI_CANH_DU_AN.md`
5. `ARCHITECTURE.md`, `REQUIREMENTS.md`, `CONG_NGHE.md`
6. `CODEX_CLAUDE_REVIEW_WORKFLOW_POLICY.md`, `tasks/_TEMPLATE.md`

Mỗi khi `TASK_COORDINATION_ACTIVE.md` hoặc một `Txx.md` thay đổi trong repo, xóa bản cũ trong nguồn rồi tải bản mới. Bản trong repo luôn thắng bản trong nguồn.

## 3. Cây thư mục

```
firefly-cinema/
├── docs/
│   ├── README.md                          ← file này
│   ├── PROJECT_SOURCE_OF_TRUTH.md
│   ├── BOI_CANH_DU_AN.md
│   ├── REQUIREMENTS.md
│   ├── ARCHITECTURE.md
│   ├── CONG_NGHE.md
│   ├── AGENT_RULES.md
│   ├── CODEX_CLAUDE_REVIEW_WORKFLOW_POLICY.md
│   ├── TASK_COORDINATION_ACTIVE.md
│   ├── tasks/
│   │   ├── _TEMPLATE.md
│   │   └── T00.md … T15.md                ← Codex soạn ở bước PLANNING
│   └── images/
└── reports/
    ├── README.md
    └── YYYY-MM-DD/                        ← tạo khi có report đầu tiên trong ngày
```
