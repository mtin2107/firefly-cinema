import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import Poster from "../components/Poster";
import AgeBadge from "../components/AgeBadge";
import CommentSection from "../components/CommentSection";
import { Loading, ErrorState } from "../components/StateViews";
import { dayKey, dayLabel, duration, money, timeOf } from "../utils/format";
import { exploreLink, slugify } from "../utils/taxonomy";
import { gsap, useGSAP, EASE, DUR, flipFrom, prefersReduced, useReducedMotion } from "../utils/motion";

// "Hài, Tâm lý" -> các link tới trang lọc
const TagLinks = ({ value, filterKey }) => value.split(",").map((x) => x.trim()).filter(Boolean)
  .map((x, i) => <span key={x}>{i > 0 && ", "}<Link to={exploreLink(filterKey, slugify(x))}>{x}</Link></span>);

export default function MovieDetail() {
  const { id } = useParams();
  const location = useLocation();
  const [movie, setMovie] = useState(null);
  const [showtimes, setShowtimes] = useState([]);
  const [error, setError] = useState("");
  const [day, setDay] = useState(null);
  const navigate = useNavigate();
  // Vị trí poster ở trang trước (thẻ phim/hero) -> poster bay từ đó sang
  const fromRef = useRef(location.state?.from ?? null);
  const posterRef = useRef(null);
  const pageRef = useRef(null);
  const introFor = useRef(null);    // phim đã chạy hiệu ứng vào trang (không chạy lại khi bật/tắt giảm chuyển động)
  const scrolledFor = useRef(null); // phim đã cuộn tới lịch chiếu
  const reduced = useReducedMotion();

  // Xóa state để tải lại trang (F5) không chạy lại hiệu ứng
  useEffect(() => {
    if (location.state?.intro) navigate(`${location.pathname}${location.hash}`, { replace: true, state: null });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const load = () => {
    setError(""); setMovie(null);
    Promise.all([api.movies.get(id), api.movies.showtimes(id)])
      .then(([m, s]) => { setMovie(m); setShowtimes(s); })
      .catch((e) => setError(e.message));
  };
  useEffect(load, [id]);

  const days = useMemo(() => [...new Set(showtimes.map((s) => dayKey(s.start_time)))].sort(), [showtimes]);
  const activeDay = day && days.includes(day) ? day : days[0];
  const todays = showtimes.filter((s) => dayKey(s.start_time) === activeDay)
    .sort((a, b) => a.start_time.localeCompare(b.start_time));

  const scrollToShowtimes = () => {
    if (scrolledFor.current === movie?.id || location.hash !== "#lich-chieu") return;
    scrolledFor.current = movie.id;
    document.getElementById("lich-chieu")?.scrollIntoView({ behavior: prefersReduced() ? "auto" : "smooth" });
  };

  // Poster bay từ chỗ cũ về chỗ mới (FLIP), chữ trượt vào sau; xong mới cuộn tới lịch chiếu nếu cần.
  // Bật giảm chuyển động giữa chừng: revertOnUpdate dọn timeline + parallax, nội dung về trạng thái cuối.
  useGSAP(() => {
    if (!movie) return;
    const from = fromRef.current;
    fromRef.current = null;
    const poster = posterRef.current;
    gsap.set(poster, { clearProps: "transform" }); // revert của parallax/scrub không luôn trả transform về trống
    if (reduced) { scrollToShowtimes(); return; }
    // Poster trôi chậm hơn chữ khi cuộn (parallax nhẹ)
    gsap.to(poster, { yPercent: -10, ease: "none",
      scrollTrigger: { trigger: pageRef.current.querySelector(".detail"), start: "top top", end: "bottom top", scrub: true } });
    if (introFor.current === movie.id) return;
    introFor.current = movie.id;
    const tl = gsap.timeline({ onComplete: scrollToShowtimes });
    if (from) {
      window.scrollTo(0, 0);
      const r = poster.getBoundingClientRect();
      tl.from(poster, { ...flipFrom(from, { x: r.left, y: r.top, w: r.width, h: r.height }),
        transformOrigin: "0 0", duration: DUR.slow, ease: EASE.out });
    } else {
      tl.from(poster, { autoAlpha: 0, scale: 0.96, duration: DUR.base, ease: EASE.out });
    }
    tl.from(pageRef.current.querySelectorAll(".detail__info > *"), { autoAlpha: 0, y: 16, stagger: 0.05, duration: DUR.slow, ease: EASE.out }, from ? "-=0.3" : 0);
  }, { dependencies: [movie, reduced], revertOnUpdate: true });

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!movie) return <Loading />;

  return (
    <div className="container" ref={pageRef}>
      <section className="detail" style={{ "--p-bg": movie.poster_bg }}>
        <div className="detail__poster" ref={posterRef}><Poster movie={movie} size="lg" /></div>
        <div className="detail__info">
          <h1 className="detail__title">{movie.title}</h1>
          <p className="detail__meta">
            <AgeBadge rating={movie.age_rating} />
            <span>{duration(movie.duration_min)}</span>
            {movie.score > 0 && <span className="score">★ {movie.score}</span>}
          </p>
          <p className="detail__desc">{movie.description}</p>
          <dl className="facts">
            <div><dt>Thể loại</dt><dd><TagLinks value={movie.genre} filterKey="the-loai" /></dd></div>
            <div><dt>Quốc gia</dt><dd><Link to={exploreLink("quoc-gia", slugify(movie.country))}>{movie.country}</Link></dd></div>
            {movie.formats && <div><dt>Định dạng</dt><dd><TagLinks value={movie.formats} filterKey="chu-de" /></dd></div>}
            <div><dt>Đạo diễn</dt><dd>{movie.director}</dd></div>
            <div><dt>Diễn viên</dt><dd>{movie.cast}</dd></div>
            <div><dt>Khởi chiếu</dt><dd>{new Date(movie.release_date).toLocaleDateString("vi-VN")}</dd></div>
          </dl>
        </div>
      </section>

      <section className="section" id="lich-chieu" aria-labelledby="showtime-title">
        <h2 id="showtime-title" className="section-title">Lịch chiếu</h2>
        {movie.status === "ended" ? (
          <p className="muted">Phim đã ngừng chiếu tại rạp.</p>
        ) : movie.status !== "now_showing" ? (
          <p className="muted">Phim chưa mở bán vé. Quay lại khi phim khởi chiếu nhé.</p>
        ) : days.length === 0 ? (
          <p className="muted">Hiện chưa có suất chiếu nào sắp tới.</p>
        ) : (
          <>
            <div className="days" role="tablist" aria-label="Chọn ngày">
              {days.map((d) => {
                const l = dayLabel(d);
                return (
                  <button key={d} role="tab" aria-selected={d === activeDay}
                    className={`day${d === activeDay ? " day--active" : ""}`} onClick={() => setDay(d)}>
                    <span className="day__weekday">{l.weekday}</span>
                    <span className="day__date">{l.date}</span>
                  </button>
                  );
              })}
            </div>
            <ul className="times">
              {todays.map((s) => (
                <li key={s.id}>
                  <Link className="time" to={`/dat-ve/${s.id}`}>
                    <span className="time__clock">{timeOf(s.start_time)}</span>
                    <span className="time__info">{s.room}, từ {money(s.price)}</span>
                  </Link>
                </li>
              ))}
            </ul>
          </>
        )}
      </section>

      <CommentSection movieId={movie.id} />
    </div>
  );
}
