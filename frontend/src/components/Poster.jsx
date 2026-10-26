import { API_URL } from "../config";

// Poster tự vẽ bằng CSS từ màu của phim — khỏi lo bản quyền ảnh.
// Khi có ảnh thật, thêm trường poster_url vào phim và component sẽ dùng ảnh.
export default function Poster({ movie, size = "md" }) {
  if (movie.poster_url) {
    return <img className={`poster poster--${size}`} src={movie.poster_url.startsWith("/uploads/") ? `${API_URL.replace(/\/$/, "")}${movie.poster_url}` : movie.poster_url} alt={`Poster phim ${movie.title}`} />;
  }
  return (
    <div className={`poster poster--${size}`} style={{ "--p-bg": movie.poster_bg, "--p-fg": movie.poster_fg }}
      role="img" aria-label={`Poster phim ${movie.title}`}>
      <span className="poster__rating">{movie.age_rating}</span>
      <span className="poster__title" title={movie.title}>{movie.title}</span>
      <span className="poster__genre">{movie.genre}</span>
    </div>
  );
}
