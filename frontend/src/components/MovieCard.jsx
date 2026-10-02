import { Link } from "react-router-dom";
import Poster from "./Poster";
import AgeBadge from "./AgeBadge";
import { duration } from "../utils/format";

export default function MovieCard({ movie }) {
  const showing = movie.status === "now_showing";
  return (
    <article className="movie-card">
      <Link to={`/phim/${movie.id}`} state={{ intro: movie }} className="movie-card__poster">
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
