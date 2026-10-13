import { useRef } from "react";
import { Link } from "react-router-dom";
import Poster from "./Poster";
import AgeBadge from "./AgeBadge";
import { duration } from "../utils/format";
import { gsap, useGSAP, MOTION_OK, FINE_POINTER } from "../utils/motion";

const TILT_DEG = 8;

export default function MovieCard({ movie }) {
  const showing = movie.status === "now_showing";
  const posterLink = useRef(null);

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
    <article className="movie-card">
      <Link to={`/phim/${movie.id}`} state={{ intro: movie }} className="movie-card__poster" ref={posterLink}>
        <Poster movie={movie} />
      </Link>
      <div className="movie-card__body">
        <h3 className="movie-card__title"><Link to={`/phim/${movie.id}`} state={{ intro: movie }}>{movie.title}</Link></h3>
        <p className="movie-card__meta">
          <AgeBadge rating={movie.age_rating} /> {duration(movie.duration_min)}
        </p>
        <p className="movie-card__meta muted">{movie.genre}</p>
        {showing
          ? <Link to={`/phim/${movie.id}#lich-chieu`} state={{ intro: movie }} className="btn btn--primary btn--sm btn--block">Đặt vé</Link>
          : movie.status === "coming_soon"
            ? <p className="movie-card__soon">Khởi chiếu {new Date(movie.release_date).toLocaleDateString("vi-VN")}</p>
            : <p className="movie-card__ended">Đã ngừng chiếu</p>}
      </div>
    </article>
  );
}
