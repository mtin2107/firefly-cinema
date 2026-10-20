import { usePageTitle } from "../utils/pageTitle";
import { byRating } from "../utils/ratings";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { api } from "../api";
import MovieCard from "../components/MovieCard";
import HeroCarousel from "../components/HeroCarousel";
import { useGridReveal } from "../utils/motion";
import { ErrorState, MovieGridSkeleton } from "../components/StateViews";

const HERO_SIZE = 5;
const TABS = [
  { key: "now_showing", label: "Đang chiếu" },
  { key: "coming_soon", label: "Sắp chiếu" },
];

export default function Home() {
  usePageTitle("Trang chủ");
  const [movies, setMovies] = useState(null);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("now_showing");
  const tabsRef = useRef(null);
  const gridRef = useRef(null);
  const [ink, setInk] = useState(null);

  const load = () => {
    setError("");
    api.movies.list().then(setMovies).catch((e) => setError(e.message));
  };
  useEffect(load, []);
  useGridReveal(gridRef, [tab, movies]);

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
  if (!movies) return (
    <>
      <section className="container"><div className="marquee marquee--skeleton skeleton" aria-hidden="true" /></section>
      <section className="container section"><MovieGridSkeleton /></section>
    </>
  );

  const showing = movies.filter((m) => m.status === "now_showing");
  const hero = [...showing].sort(byRating).slice(0, HERO_SIZE);
  const list = movies.filter((m) => m.status === tab);

  return (
    <>
      {hero.length > 0 && (
        <section className="container">
          <HeroCarousel movies={hero} />
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
        <div className="movie-grid" ref={gridRef}>
          {list.map((m) => <MovieCard key={m.id} movie={m} />)}
        </div>
      </section>
    </>
  );
}
