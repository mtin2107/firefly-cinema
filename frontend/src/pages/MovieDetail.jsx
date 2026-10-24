import { usePageTitle } from "../utils/pageTitle";
import TrailerBanner from "../components/TrailerBanner";
import RatingDialog from "../components/RatingDialog";
import { useAuth } from "../context/AuthContext";
import { ratingText } from "../utils/ratings";
import { useEffect, useMemo, useRef, useState } from "react";
import { Link, useLocation, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import Poster from "../components/Poster";
import AgeBadge from "../components/AgeBadge";
import CommentSection from "../components/CommentSection";
import PosterIntro from "../components/PosterIntro";
import { Loading, ErrorState } from "../components/StateViews";
import { dayKey, dayLabel, duration, money, timeOf } from "../utils/format";
import { exploreLink, slugify } from "../utils/taxonomy";
import { gsap, useGSAP, EASE, DUR, useReducedMotion } from "../utils/motion";

// "Hài, Tâm lý" -> các link tới trang lọc
const TagLinks = ({ value, filterKey }) => value.split(",").map((x) => x.trim()).filter(Boolean)
  .map((x, i) => <span key={x}>{i > 0 && ", "}<Link to={exploreLink(filterKey, slugify(x))}>{x}</Link></span>);

export default function MovieDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [stars, setStars] = useState(null);
  const [commentBusy, setCommentBusy] = useState(false);
  const [ratingBusy, setRatingBusy] = useState(false);
  const [ratingNotice, setRatingNotice] = useState("");
  const [ratingOpen, setRatingOpen] = useState(false);
  const ratingButtonRef = useRef(null);
  const [commentVersion, setCommentVersion] = useState(0);
  useEffect(() => {
    let active = true;
    setStars(null); setRatingNotice("");
    if (user) api.ratings.mine(id).then((r) => { if (active) setStars(r.stars); })
      .catch((e) => { if (active) setRatingNotice(e.message); });
    return () => { active = false; };
  }, [id, user]);
  const refreshRating = (created) => {
    setStars(created.author_stars);
    setRatingNotice("");
    // The comment is already committed; a refresh error must not look like a
    // failed submission and invite a duplicate POST.
    api.movies.get(id).then(setMovie).catch((e) => setRatingNotice(e.message));
    setCommentVersion((v) => v + 1);
  };
  const changeRating = async (value) => {
    setRatingBusy(true);
    try {
      const result = value == null ? await api.ratings.remove(id) : await api.ratings.set(id, value);
      setStars(result.stars);
      setMovie((m) => ({ ...m, rating_avg: result.rating_avg, rating_count: result.rating_count }));
      setCommentVersion((v) => v + 1);
      setRatingNotice(value == null ? "Đã hủy đánh giá." : "Đã lưu đánh giá.");
      return true;
    } catch (e) { setRatingNotice(e.message); return false; }
    finally { setRatingBusy(false); }
  };
  const location = useLocation();
  const [movie, setMovie] = useState(null);
  const [showtimes, setShowtimes] = useState([]);
  const [error, setError] = useState("");
  const [day, setDay] = useState(null);
  const navigate = useNavigate();
  // Phim được truyền từ trang trước khi bấm vào -> hiện khung bong bóng poster
  const [intro, setIntro] = useState(location.state?.intro ?? null);
  const posterRef = useRef(null);
  const pageRef = useRef(null);
  const introFor = useRef(null);    // phim đã chạy hiệu ứng vào trang (không chạy lại khi bật/tắt giảm chuyển động)
  const reduced = useReducedMotion();

  usePageTitle(movie?.title ?? "Chi tiết phim");

  // Xóa state để tải lại trang (F5) không hiện lại hiệu ứng
  useEffect(() => {
    if (location.state?.intro) navigate(`${location.pathname}${location.search}${location.hash}`, { replace: true, state: null });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const load = () => {
    setError(""); setMovie(null);
    Promise.all([api.movies.get(id), api.movies.showtimes(id)])
      .then(([m, s]) => { setMovie(m); setShowtimes(s); })
      .catch(setError);
  };
  useEffect(load, [id]);

  const days = useMemo(() => [...new Set(showtimes.map((s) => dayKey(s.start_time)))].sort(), [showtimes]);
  const activeDay = day && days.includes(day) ? day : days[0];
  const todays = showtimes.filter((s) => dayKey(s.start_time) === activeDay)
    .sort((a, b) => a.start_time.localeCompare(b.start_time));

  useEffect(() => {
    if (movie && location.hash === "#lich-chieu") document.getElementById("lich-chieu")?.scrollIntoView();
  }, [movie, location.hash]);

  // Chữ trượt vào lần lượt, poster trôi chậm hơn khi cuộn (parallax).
  // Bật giảm chuyển động giữa chừng: revertOnUpdate dọn timeline + parallax, nội dung về trạng thái cuối.
  useGSAP(() => {
    if (!movie) return;
    const poster = posterRef.current;
    gsap.set(poster, { clearProps: "transform" }); // revert của parallax/scrub không luôn trả transform về trống
    if (reduced) return;
    gsap.to(poster, { yPercent: -10, ease: "none",
      scrollTrigger: { trigger: pageRef.current.querySelector(".detail"), start: "top top", end: "bottom top", scrub: true } });
    if (introFor.current === movie.id) return;
    introFor.current = movie.id;
    gsap.timeline()
      .from(poster, { autoAlpha: 0, scale: 0.96, duration: DUR.base, ease: EASE.out })
      .from(pageRef.current.querySelectorAll(".detail__info > *"), { autoAlpha: 0, y: 16, stagger: 0.05, duration: DUR.slow, ease: EASE.out }, 0);
  }, { dependencies: [movie, reduced], revertOnUpdate: true });

  // Khung bong bóng đứng cùng một vị trí ở mọi nhánh để không bị chạy lại khi dữ liệu tải xong
  const introLayer = intro && <PosterIntro movie={intro} onDone={() => setIntro(null)} />;

  if (error) return <>{introLayer}<ErrorState message={error.message} onRetry={error.status === 404 ? undefined : load} /></>;
  if (!movie) return <>{introLayer}<Loading /></>;

  return (
    <>{introLayer}
    <div className="container" ref={pageRef}>
      <TrailerBanner key={`${movie.id}:${movie.trailer_url}`} movie={movie} />
      <section className="detail" style={{ "--p-bg": movie.poster_bg }}>
        <div className="detail__poster" ref={posterRef}><Poster movie={movie} size="lg" /></div>
        <div className="detail__info">
          <h1 className="detail__title">{movie.title}</h1>
          <p className="detail__meta">
            <AgeBadge rating={movie.age_rating} />
            <span>{duration(movie.duration_min)}</span>
            {movie.status === "coming_soon" ? <span className="score">{ratingText(movie)}</span> : <>
              <button type="button" className="score rating-trigger" ref={ratingButtonRef}
                aria-haspopup="dialog" disabled={ratingBusy || commentBusy}
                onClick={() => {
                  if (!user) return navigate("/dang-nhap", { state: { from: location } });
                  setRatingNotice(""); setRatingOpen(true);
                }}>{movie.rating_count ? ratingText(movie) : "Chưa có đánh giá — chấm ngay"}</button>
              {stars != null && <small className="rating-personal">Bạn đã chấm {stars}★</small>}
            </>}
          </p>
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

      <section className="section movie-synopsis" aria-labelledby="synopsis-title">
        <h2 id="synopsis-title" className="section-title">Nội dung phim</h2>
        {(movie.synopsis || movie.description).split(/\n\s*\n/).filter(Boolean).map((paragraph, index) => <p key={index}>{paragraph}</p>)}
      </section>

      <section className="section" id="lich-chieu" aria-labelledby="showtime-title">
        <h2 id="showtime-title" className="section-title">Lịch chiếu</h2>
        <p className="score">{ratingText(movie)}</p>
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

      <CommentSection movieId={movie.id} allowed={movie.status !== "coming_soon"}
        stars={stars} ratingBusy={ratingBusy || commentBusy}
        onSendingChange={setCommentBusy}
        version={commentVersion} onCreated={refreshRating} />
    </div>
    {movie.status !== "coming_soon" && <RatingDialog key={`${movie.id}:${user?.id}`} open={ratingOpen}
      movie={movie} stars={stars} busy={ratingBusy || commentBusy} notice={ratingNotice}
      onSave={changeRating} onClose={() => { setRatingOpen(false); ratingButtonRef.current?.focus(); }} />}
    </>
  );
}
