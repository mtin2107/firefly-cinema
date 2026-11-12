import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api } from "../api";
import MovieCard from "../components/MovieCard";
import { Empty, ErrorState, MovieGridSkeleton } from "../components/StateViews";
import { MEMBERSHIP } from "../config";
import { useAuth } from "../context/AuthContext";
import { money } from "../utils/format";
import { useGridReveal } from "../utils/motion";
import { usePageTitle } from "../utils/pageTitle";

export default function Offers() {
  usePageTitle("Ưu đãi");
  const { user } = useAuth();
  const [movies, setMovies] = useState(null);
  const [error, setError] = useState("");
  const gridRef = useRef(null);
  const { hash } = useLocation();
  // Link "Hạng thành viên" trên menu trỏ tới #hang-thanh-vien
  useEffect(() => { if (hash) document.getElementById(hash.slice(1))?.scrollIntoView(); }, [hash]);

  const load = () => {
    setError(""); setMovies(null);
    api.movies.list({ status: "coming_soon" }).then(setMovies).catch((e) => setError(e.message));
  };
  useEffect(load, []);
  useGridReveal(gridRef, [movies]);

  return (
    <div className="container offers">
      <h1 className="page-title">Tin tức và ưu đãi</h1>

      <section className="section" id="hang-thanh-vien" aria-labelledby="tier-title">
        <h2 id="tier-title" className="section-title">Hạng thành viên</h2>
        <p className="muted">Hạng được tính theo tổng tiền vé đã thanh toán trong năm.</p>
        <ul className="tier-list">
          {MEMBERSHIP.map((t, i) => (
            <li key={t.name} className={`tier tier--${i}`}>
              <strong>{t.name}</strong>
              <span>{t.threshold === 0 ? "Khi đăng ký tài khoản" : `Từ ${money(t.threshold)}`}</span>
            </li>
          ))}
        </ul>
        <Link className="btn btn--ghost btn--sm" to={user ? "/tai-khoan" : "/dang-ky"}>
          {user ? "Xem hạng của tôi" : "Đăng ký thành viên"}
        </Link>
      </section>

      <section className="section" aria-labelledby="soon-title">
        <h2 id="soon-title" className="section-title">Phim sắp ra mắt</h2>
        {error ? <ErrorState message={error} onRetry={load} />
          : !movies ? <MovieGridSkeleton count={4} />
          : movies.length === 0 ? <Empty><p>Chưa có phim sắp chiếu nào.</p></Empty>
          : <div className="movie-grid" ref={gridRef}>{movies.map((m) => <MovieCard key={m.id} movie={m} />)}</div>}
      </section>
    </div>
  );
}
