import { Link } from "react-router-dom";

export function Loading({ label = "Đang tải..." }) {
  return <div className="state" role="status"><span className="spinner" aria-hidden="true" />{label}</div>;
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
