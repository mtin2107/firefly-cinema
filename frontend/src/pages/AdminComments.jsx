import { useEffect, useState } from "react";
import { api } from "../api";
import { Loading, ErrorState } from "../components/StateViews";
import { relativeTime } from "../utils/format";

const LABEL_FILTERS = [
  { key: "", label: "Tất cả nhãn model" },
  { key: "negative", label: "Model: Tiêu cực" },
  { key: "normal", label: "Model: Bình thường" },
];
const PAGE_SIZE = 20;

function Label({ negative }) {
  return <span className={`label ${negative ? "label--neg" : "label--ok"}`}>
    {negative ? "Tiêu cực" : "Bình thường"}
  </span>;
}

export default function AdminComments() {
  const [label, setLabel] = useState("");
  const [reviewed, setReviewed] = useState("");
  const [page, setPage] = useState(1);
  const [result, setResult] = useState(null);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);
  const [notice, setNotice] = useState("");

  const load = () => {
    setError("");
    setResult(null);
    Promise.all([
      api.admin.comments.list({ label, reviewed, page, page_size: PAGE_SIZE }),
      api.admin.comments.stats(),
    ]).then(([rows, nextStats]) => {
      setStats(nextStats);
      const lastPage = Math.max(1, Math.ceil(rows.total / PAGE_SIZE));
      if (page > lastPage) setPage(lastPage);
      else setResult(rows);
    }).catch((err) => setError(err.message));
  };
  useEffect(load, [label, reviewed, page]);

  const changeFilters = (nextLabel, nextReviewed) => {
    setPage(1);
    setLabel(nextLabel);
    setReviewed(nextReviewed);
  };

  const act = async (comment, action, actionLabel) => {
    setBusyId(comment.id); setNotice("");
    try {
      await api.admin.comments.update(comment.id, {
        action,
        ...(action === "relabel" ? { label: actionLabel } : {}),
      });
      setNotice("Đã cập nhật bình luận.");
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusyId(null);
    }
  };

  const exportCsv = async () => {
    setNotice(""); setError("");
    try {
      const blob = await api.admin.comments.exportCsv();
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "firefly_comments_reviewed.csv";
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(url);
      setNotice("Đã tải CSV bình luận được duyệt.");
    } catch (err) {
      setError(err.message);
    }
  };

  const pages = Math.max(1, Math.ceil((result?.total ?? 0) / PAGE_SIZE));

  return (
    <div className="container">
      <div className="admin-comments__heading">
        <div>
          <h1 className="page-title">Kiểm duyệt bình luận</h1>
          <p className="muted admin__intro">Nhãn người duyệt được ưu tiên khi hiển thị; kết quả và điểm gốc của model luôn được giữ nguyên.</p>
        </div>
        <button className="btn btn--ghost" onClick={exportCsv}>Tải CSV</button>
      </div>

      {stats && <section className="moderation-stats" aria-label="Thống kê độ chính xác model">
        <div><span>Đã duyệt</span><strong>{stats.reviewed}</strong></div>
        <div><span>Model đúng</span><strong>{stats.agree}</strong></div>
        <div><span>Model sai</span><strong>{stats.disagree}</strong></div>
        <div><span>Độ chính xác</span><strong>{(stats.accuracy * 100).toFixed(1)}%</strong></div>
        <div><span>TP / FP / TN / FN</span><strong>{stats.tp} / {stats.fp} / {stats.tn} / {stats.fn}</strong></div>
      </section>}

      <div className="admin-comments__filters">
        <div className="tabs" role="tablist" aria-label="Lọc theo nhãn model">
          {LABEL_FILTERS.map((filter) => <button key={filter.key} role="tab" aria-selected={label === filter.key}
            className={`tab${label === filter.key ? " tab--active" : ""}`}
            onClick={() => changeFilters(filter.key, reviewed)}>{filter.label}</button>)}
        </div>
        <label className="field moderation-review-filter">Trạng thái duyệt
          <select value={reviewed} onChange={(event) => changeFilters(label, event.target.value)}>
            <option value="">Tất cả</option>
            <option value="false">Chưa duyệt</option>
            <option value="true">Đã duyệt</option>
          </select>
        </label>
      </div>

      {notice && <p className="notice notice--ok" role="status">{notice}</p>}
      {error ? <ErrorState message={error} onRetry={load} />
        : !result ? <Loading />
        : result.items.length === 0 ? <p className="state">Không có bình luận phù hợp.</p>
        : <>
          <div className="table-wrap">
            <table className="admin-table moderation-table">
              <thead><tr><th>Phim / người viết</th><th>Nội dung</th><th>Model</th><th>Nhãn duyệt</th><th>Hiển thị</th><th>Thao tác</th></tr></thead>
              <tbody>{result.items.map((comment) => {
                const nextLabel = comment.effective_negative ? 0 : 1;
                return <tr key={comment.id}>
                  <td><strong>{comment.movie_title}</strong><br /><span className="muted">{comment.user_name} · {relativeTime(comment.created_at)}</span></td>
                  <td className="admin-table__content">{comment.content}</td>
                  <td><Label negative={comment.is_negative} /><div className="meter"><span className="meter__fill" style={{ width: `${comment.negative_score * 100}%` }} /></div><span className="meter__num">{comment.negative_score.toFixed(2)} · {comment.model_name}</span></td>
                  <td>{comment.reviewed ? <><Label negative={comment.human_label === 1} /><small className="moderation-meta">{comment.reviewed_by_name ?? "Không rõ người duyệt"}<br />{comment.reviewed_at ? relativeTime(comment.reviewed_at) : "Chưa có thời gian duyệt"}</small></> : <span className="muted">Chưa duyệt</span>}</td>
                  <td><span className={`label ${comment.hidden ? "label--neg" : "label--ok"}`}>{comment.hidden ? "Đã ẩn" : "Đang hiện"}</span></td>
                  <td><div className="moderation-actions">
                    {!comment.reviewed && <button className="btn btn--sm btn--primary" disabled={busyId === comment.id} onClick={() => act(comment, "confirm")}>Xác nhận nhãn</button>}
                    <button className="btn btn--sm btn--ghost" disabled={busyId === comment.id} onClick={() => act(comment, "relabel", nextLabel)}>Đổi sang {nextLabel ? "tiêu cực" : "bình thường"}</button>
                    <button className={`btn btn--sm ${comment.hidden ? "btn--ghost" : "btn--danger"}`} disabled={busyId === comment.id} onClick={() => act(comment, comment.hidden ? "unhide" : "hide")}>{comment.hidden ? "Hiện lại" : "Ẩn"}</button>
                  </div></td>
                </tr>;
              })}</tbody>
            </table>
          </div>
          <nav className="pagination" aria-label="Phân trang bình luận">
            <button className="btn btn--sm btn--ghost" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>Trang trước</button>
            <span>Trang {page} / {pages} · {result.total} bình luận</span>
            <button className="btn btn--sm btn--ghost" disabled={page >= pages} onClick={() => setPage((value) => value + 1)}>Trang sau</button>
          </nav>
        </>}
    </div>
  );
}
