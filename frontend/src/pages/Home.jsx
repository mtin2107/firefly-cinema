import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import MovieCard from "../components/MovieCard";
import Poster from "../components/Poster";
import AgeBadge from "../components/AgeBadge";
import { Loading, ErrorState } from "../components/StateViews";
import { duration } from "../utils/format";

const TABS = [
  { key: "now_showing", label: "Đang chiếu" },
  { key: "coming_soon", label: "Sắp chiếu" },
];

export default function Home() {
  const [movies, setMovies] = useState(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("now_showing");
  const tabsRef = useRef(null);
  const [ink, setInk] = useState(null);

  const load = () => {
    setError("");
    api.movies.list().then(setMovies).catch((e) => setError(e.message));
  };
  useEffect(load, []);

  // Đo tab đang chọn để gạch vàng trượt tới đúng chỗ
  useLayoutEffect(() => {
    const measure = () => {
      const el = tabsRef.current?.querySelector(".tab--active");
      if (el) setInk({ "--ink-x": `${el.offsetLeft}px`, "--ink-w": `${el.offsetWidth}px` });
    };
    measure();
    document.fonts?.ready.then(measure); // font tiêu đề tải xong thì chữ tab rộng ra
    window.addEventListener("resize", measure);
    return () => window.removeEventListener("resize", measure);
  }, [tab, movies]);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!movies) return <Loading />;

  const showing = movies.filter((m) => m.status === "now_showing");
  const featured = [...showing].sort((a, b) => b.score - a.score)[0];
  const list = movies.filter((m) => m.status === tab);

  return (
    <>
      {featured && (
        <section className="container">
          <div className="marquee">
            <div className="marquee__text">
              <p className="marquee__kicker">Được khán giả chấm cao nhất tuần này</p>
              <h1 className="marquee__title">{featured.title}</h1>
              <p className="marquee__meta">
                <AgeBadge rating={featured.age_rating} />
                <span>{featured.genre}</span>
                <span>{duration(featured.duration_min)}</span>
                <span className="score">★ {featured.score}</span>
              </p>
              <p className="marquee__desc">{featured.description}</p>
              <div className="marquee__actions">
                <Link className="btn btn--primary btn--lg" to={`/phim/${featured.id}#lich-chieu`} state={{ intro: featured }}>Đặt vé</Link>
                <Link className="btn btn--ghost btn--lg" to={`/phim/${featured.id}`} state={{ intro: featured }}>Xem chi tiết</Link>
              </div>
            </div>
            <div className="marquee__poster"><Poster movie={featured} size="lg" /></div>
          </div>
        </section>
      )}

      <section className="container section">
        <div className="tabs tabs--ink" role="tablist" aria-label="Danh sách phim" ref={tabsRef}>
          {TABS.map((t) => (
            <button key={t.key} role="tab" aria-selected={tab === t.key}
              className={`tab${tab === t.key ? " tab--active" : ""}`} onClick={() => setTab(t.key)}>
              {t.label}
            </button>
          ))}
          {ink && <span className="tabs__ink" style={ink} aria-hidden="true" />}
        </div>
        <div className="movie-grid">
          {list.map((m) => <MovieCard key={m.id} movie={m} />)}
        </div>
      </section>
    </>
  );
}
