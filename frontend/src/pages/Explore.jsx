import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import MovieCard from "../components/MovieCard";
import { Loading, ErrorState, Empty } from "../components/StateViews";
import { FILTERS, readFilters } from "../utils/taxonomy";

// Tiêu đề trang theo bộ lọc đang chọn
function titleFor(active, q) {
  if (q) return `Kết quả tìm "${q}"`;
  if (active.length === 0) return "Tất cả phim";
  if (active.length > 1) return "Kết quả lọc phim";
  const { filter, option } = active[0];
  if (filter.key === "trang-thai") return `Phim ${option.label.toLowerCase()}`;
  if (filter.key === "the-loai") return option.label.startsWith("Phim") ? option.label : `Phim ${option.label.toLowerCase()}`;
  if (filter.key === "quoc-gia") return `Phim ${option.label}`;
  if (filter.key === "nam") return option.slug.startsWith("truoc") ? `Phim phát hành ${option.label.toLowerCase()}` : `Phim năm ${option.label}`;
  return option.label;
}

export default function Explore() {
  const [params, setParams] = useSearchParams();
  const [movies, setMovies] = useState(null);
  const [error, setError] = useState("");
  const { active, query, q } = readFilters(params);
  const queryKey = JSON.stringify(query);

  const load = () => {
    setError(""); setMovies(null);
    api.movies.list(query).then(setMovies).catch((e) => setError(e.message));
  };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(load, [queryKey]);

  const change = (key, slug) => {
    const next = new URLSearchParams(params);
    if (slug) next.set(key, slug); else next.delete(key);
    setParams(next);
  };

  return (
    <div className="container">
      <h1 className="page-title">{titleFor(active, q)}</h1>

      <div className="filters">
        {FILTERS.map((f) => (
          <label key={f.key} className="filter">
            <span>{f.label}</span>
            <select value={params.get(f.key) ?? ""} onChange={(e) => change(f.key, e.target.value)}>
              <option value="">Tất cả</option>
              {f.options.map((o) => <option key={o.slug} value={o.slug}>{o.label}</option>)}
            </select>
          </label>
        ))}
        {(active.length > 0 || q) && (
          <button type="button" className="btn btn--ghost btn--sm filters__clear" onClick={() => setParams({})}>
            Xóa bộ lọc
          </button>
        )}
      </div>

      {error ? <ErrorState message={error} onRetry={load} />
        : !movies ? <Loading />
        : movies.length === 0 ? (
          <Empty>
            <p>{q ? `Không tìm thấy phim nào có tên chứa "${q}". Thử gõ ngắn hơn hoặc kiểm tra chính tả.` : "Chưa có phim nào khớp với bộ lọc này."}</p>
            <button type="button" className="btn btn--primary" onClick={() => setParams({})}>Xem tất cả phim</button>
          </Empty>
        ) : (
          <>
            <p className="muted result-count">{movies.length} phim</p>
            <div className="movie-grid">{movies.map((m) => <MovieCard key={m.id} movie={m} />)}</div>
          </>
        )}
    </div>
  );
}
