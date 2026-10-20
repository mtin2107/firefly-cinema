import { usePageTitle } from "../utils/pageTitle";
import { byRating } from "../utils/ratings";
import { useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../api";
import MovieCard from "../components/MovieCard";
import { useGridReveal } from "../utils/motion";
import { ErrorState, Empty, MovieGridSkeleton } from "../components/StateViews";
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
  usePageTitle("Khám phá");
  const [params, setParams] = useSearchParams();
  const [movies, setMovies] = useState(null);
  const gridRef = useRef(null);
  const [error, setError] = useState("");
  const { active, query, q } = readFilters(params);
  const sort = params.get("sap-xep") ?? "moi-nhat";
  const sorted = movies && [...movies].sort(sort === "danh-gia-cao" ? byRating
    : sort === "ten-a-z" ? (a, b) => a.title.localeCompare(b.title, "vi")
    : (a, b) => b.release_date.localeCompare(a.release_date) || a.id - b.id);
  const queryKey = JSON.stringify(query);

  const load = () => {
    setError(""); setMovies(null);
    api.movies.list(query).then(setMovies).catch((e) => setError(e.message));
  };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(load, [queryKey]);
  useGridReveal(gridRef, [movies]);

  const change = (key, slug) => {
    const next = new URLSearchParams(params);
    if (slug) next.set(key, slug); else next.delete(key);
    setParams(next);
  };

  return (
    <div className="container">
      <h1 className="page-title">{titleFor(active, q)}</h1>

      <div className="filters">
        <label className="filter"><span>Sắp xếp</span>
          <select aria-label="Sắp xếp" value={sort} onChange={(e) => change("sap-xep", e.target.value)}>
            <option value="moi-nhat">Mới nhất</option><option value="danh-gia-cao">Đánh giá cao</option><option value="ten-a-z">Tên A–Z</option>
          </select>
        </label>
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
        : !movies ? <MovieGridSkeleton />
        : movies.length === 0 ? (
          <Empty>
            <p>{q ? `Không tìm thấy phim nào có tên chứa "${q}". Thử gõ ngắn hơn hoặc kiểm tra chính tả.` : "Chưa có phim nào khớp với bộ lọc này."}</p>
            <button type="button" className="btn btn--primary" onClick={() => setParams({})}>Xem tất cả phim</button>
          </Empty>
        ) : (
          <>
            <p className="muted result-count">{movies.length} phim</p>
            <div className="movie-grid" ref={gridRef}>{sorted.map((m) => <MovieCard key={m.id} movie={m} />)}</div>
          </>
        )}
    </div>
  );
}
