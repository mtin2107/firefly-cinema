import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import Poster from "../components/Poster";
import AgeBadge from "../components/AgeBadge";
import CommentSection from "../components/CommentSection";
import PosterIntro from "../components/PosterIntro";
import { Loading, ErrorState } from "../components/StateViews";
import { dayKey, dayLabel, duration, money, timeOf } from "../utils/format";
import { exploreLink, slugify } from "../utils/taxonomy";

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
  // Phim được truyền từ trang trước khi bấm vào -> hiện khung bong bóng poster
  const [intro, setIntro] = useState(location.state?.intro ?? null);

  // Xóa state để tải lại trang (F5) không hiện lại hiệu ứng
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

  useEffect(() => {
    if (movie && location.hash === "#lich-chieu") document.getElementById("lich-chieu")?.scrollIntoView();
  }, [movie, location.hash]);

  const introLayer = intro && <PosterIntro movie={intro} onDone={() => setIntro(null)} />;

  // Đặt khung bong bóng ở cùng một vị trí để không bị chạy lại khi dữ liệu tải xong
  return <>{introLayer}{renderPage()}</>;

  function renderPage() {
    if (error) return <ErrorState message={error} onRetry={load} />;
    if (!movie) return <Loading />;

    return (
      <div className="container">
        <section className="detail">
          <Poster movie={movie} size="lg" />
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
}
