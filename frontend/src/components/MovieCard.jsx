import { ratingText } from "../utils/ratings";
import { useRef } from "react";
import { Link } from "react-router-dom";
import Poster from "./Poster";
import AgeBadge from "./AgeBadge";
import { duration } from "../utils/format";
import { gsap, useGSAP, MOTION_OK, FINE_POINTER } from "../utils/motion";

const TILT_DEG = 8;
const TITLE_SPEED = 40;
const TITLE_PAUSE = 1.5;

export default function MovieCard({ movie }) {
  const showing = movie.status === "now_showing";
  const cardRef = useRef(null);
  const titleLink = useRef(null);
  const titleText = useRef(null);
  const posterLink = useRef(null);
  const detail = `/phim/${movie.id}`;

  // Đo theo khung thật; mọi MovieCard dùng cùng quy tắc, kể cả phim mới.
  useGSAP(() => {
    const mm = gsap.matchMedia();
    mm.add({ motion: MOTION_OK, hover: "(hover: hover)" }, ({ conditions }) => {
      if (!conditions.motion) return;
      const card = cardRef.current;
      const link = titleLink.current;
      const text = titleText.current;
      const canHover = conditions.hover;
      let timeline = null;
      let distance = 0;
      let active = true;
      let hovered = card.matches(":hover");
      let focused = card.contains(document.activeElement);

      const stop = () => {
        timeline?.kill();
        timeline = null;
        gsap.set(text, { clearProps: "transform" });
        card.classList.remove("movie-card--title-running");
      };
      const sync = () => {
        if (distance <= 0 || (canHover && !hovered && !focused)) {
          stop();
          return;
        }
        if (timeline) return;
        card.classList.add("movie-card--title-running");
        timeline = gsap.timeline({ repeat: -1, repeatDelay: TITLE_PAUSE,
          delay: canHover ? 0 : TITLE_PAUSE })
          .to(text, { x: -distance, duration: distance / TITLE_SPEED, ease: "none" })
          .to(text, { x: -distance, duration: TITLE_PAUSE })
          .set(text, { x: 0 });
      };
      const measure = () => {
        if (!active) return;
        stop();
        distance = Math.max(0, link.scrollWidth - link.clientWidth);
        sync();
      };
      const enter = () => { hovered = true; sync(); };
      const leave = () => { hovered = false; sync(); };
      const focus = () => { focused = true; sync(); };
      const blur = (event) => { focused = card.contains(event.relatedTarget); sync(); };
      card.addEventListener("pointerenter", enter);
      card.addEventListener("pointerleave", leave);
      card.addEventListener("focusin", focus);
      card.addEventListener("focusout", blur);
      const observer = new ResizeObserver(measure);
      observer.observe(link);
      document.fonts?.addEventListener("loadingdone", measure);
      document.fonts?.ready.then(measure);
      measure();
      return () => {
        active = false;
        observer.disconnect();
        document.fonts?.removeEventListener("loadingdone", measure);
        card.removeEventListener("pointerenter", enter);
        card.removeEventListener("pointerleave", leave);
        card.removeEventListener("focusin", focus);
        card.removeEventListener("focusout", blur);
        stop();
      };
    });
    return () => mm.revert();
  }, { dependencies: [movie.title], scope: cardRef, revertOnUpdate: true });

  // Poster nghiêng theo chuột, vệt sáng chạy theo góc nghiêng (chỉ máy có chuột)
  useGSAP(() => {
    const mm = gsap.matchMedia();
    mm.add(`${MOTION_OK} and ${FINE_POINTER}`, () => {
      const link = posterLink.current;
      const poster = link.querySelector(".poster");
      const rotY = gsap.quickTo(poster, "rotationY", { duration: 0.5, ease: "power3" });
      const rotX = gsap.quickTo(poster, "rotationX", { duration: 0.5, ease: "power3" });
      const move = (e) => {
        const r = link.getBoundingClientRect();
        const px = (e.clientX - r.left) / r.width - 0.5;
        const py = (e.clientY - r.top) / r.height - 0.5;
        rotY(px * TILT_DEG * 2);
        rotX(-py * TILT_DEG * 2);
        poster.style.setProperty("--glare-x", `${(px + 0.5) * 100}%`);
        poster.style.setProperty("--glare-y", `${(py + 0.5) * 100}%`);
      };
      const leave = () => { rotY(0); rotX(0); };
      link.addEventListener("pointermove", move);
      link.addEventListener("pointerleave", leave);
      return () => {
        link.removeEventListener("pointermove", move);
        link.removeEventListener("pointerleave", leave);
      };
    });
    return () => mm.revert();
  });

  return (
    <article className="movie-card" ref={cardRef}>
      <Link to={detail} state={{ intro: movie }} className="movie-card__poster" ref={posterLink}>
        <Poster movie={movie} />
      </Link>
      <div className="movie-card__body">
        <h3 className="movie-card__title" title={movie.title}><Link to={detail} state={{ intro: movie }} ref={titleLink}><span className="movie-card__title-text" ref={titleText}>{movie.title}</span></Link></h3>
        <p className="movie-card__meta">
          <AgeBadge rating={movie.age_rating} /> {duration(movie.duration_min)}
        </p>
        <p className="score">{ratingText(movie)}</p>
        <p className="movie-card__meta muted movie-card__genre" title={movie.genre}>{movie.genre}</p>
        {showing
          ? <Link to={`${detail}#lich-chieu`} state={{ intro: movie }} className="btn btn--primary btn--sm btn--block">Đặt vé</Link>
          : movie.status === "coming_soon"
            ? <p className="movie-card__soon">Khởi chiếu {new Date(movie.release_date).toLocaleDateString("vi-VN")}</p>
            : <p className="movie-card__ended">Đã ngừng chiếu</p>}
      </div>
    </article>
  );
}
