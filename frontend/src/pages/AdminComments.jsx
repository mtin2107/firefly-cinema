import { useEffect, useState } from "react";
import { api } from "../api";
import { Loading, ErrorState } from "../components/StateViews";
import { relativeTime } from "../utils/format";

const FILTERS = [
  { key: "", label: "Tất cả" },
  { key: "negative", label: "Tiêu cực" },
  { key: "normal", label: "Bình thường" },
];

export default function AdminComments() {
  const [filter, setFilter] = useState("");
  const [rows, setRows] = useState(null);
  const [all, setAll] = useState([]);
  const [error, setError] = useState("");

  const load = () => {
    setError(""); setRows(null);
    Promise.all([api.admin.comments(filter), api.admin.comments("")])
      .then(([r, a]) => { setRows(r); setAll(a); })
      .catch((e) => setError(e.message));
  };
  useEffect(load, [filter]);

  const negCount = all.filter((c) => c.is_negative).length;

  return (
    <div className="container">
      <h1 className="page-title">Kiểm duyệt bình luận</h1>
      <p className="muted admin__intro">
        Mỗi bình luận mới được mô hình chấm điểm tiêu cực từ 0 đến 1. Điểm từ 0,5 trở lên bị ẩn mặc định trên trang phim.
      </p>
      <p className="admin__stats">
        <strong>{all.length}</strong> bình luận, trong đó <strong className="text-red">{negCount}</strong> bị đánh giá tiêu cực.
      </p>

      <div className="tabs" role="tablist" aria-label="Lọc bình luận">
        {FILTERS.map((f) => (
          <button key={f.key} role="tab" aria-selected={filter === f.key}
            className={`tab${filter === f.key ? " tab--active" : ""}`} onClick={() => setFilter(f.key)}>
            {f.label}
          </button>
        ))}
      </div>

      {error ? <ErrorState message={error} onRetry={load} />
        : !rows ? <Loading />
        : (
          <div className="table-wrap">
            <table className="admin-table">
              <thead>
                <tr><th>Phim</th><th>Người viết</th><th>Nội dung</th><th>Kết quả</th><th>Điểm tiêu cực</th><th>Thời gian</th></tr>
              </thead>
              <tbody>
                {rows.length === 0 && <tr><td colSpan={6} className="muted">Không có bình luận nào.</td></tr>}
                {rows.map((c) => (
                  <tr key={c.id}>
                    <td>{c.movie_title}</td>
                    <td>{c.user_name}</td>
                    <td className="admin-table__content">{c.content}</td>
                    <td><span className={`label ${c.is_negative ? "label--neg" : "label--ok"}`}>{c.is_negative ? "Tiêu cực" : "Bình thường"}</span></td>
                    <td>
                      <div className="meter" aria-label={`Điểm ${c.negative_score.toFixed(2)}`}>
                        <span className="meter__fill" style={{ width: `${c.negative_score * 100}%` }} />
                      </div>
                      <span className="meter__num">{c.negative_score.toFixed(2)}</span>
                    </td>
                    <td className="muted">{relativeTime(c.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
    </div>
  );
}
