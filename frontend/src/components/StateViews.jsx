import { Link } from "react-router-dom";

export function Loading({ label = "Đang tải..." }) {
  return <div className="state" role="status"><span className="loading-firefly" aria-hidden="true" />{label}</div>;
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="state state--error" role="alert">
      <p>{message}</p>
      <div className="state__actions">
        {onRetry && <button className="btn btn--ghost" onClick={onRetry}>Thử lại</button>}
        <Link className="btn btn--ghost" to="/">Về trang chủ</Link>
      </div>
    </div>
  );
}

export function Empty({ children }) {
  return <div className="state state--empty">{children}</div>;
}

// Khung thẻ phim mờ khi danh sách đang tải
export function MovieGridSkeleton({ count = 8 }) {
  return (
    <div className="movie-grid" role="status" aria-label="Đang tải danh sách phim">
      {Array.from({ length: count }, (_, i) => (
        <div key={i} className="skeleton-card" aria-hidden="true">
          <div className="skeleton skeleton--poster" />
          <div className="skeleton skeleton--line" />
          <div className="skeleton skeleton--line skeleton--short" />
        </div>
      ))}
    </div>
  );
}
