import { useState } from "react";
import { API_URL } from "../config";
import { youtubeId } from "../utils/youtube";
import Poster from "./Poster";

const mediaUrl = (url) => url.startsWith("/uploads/") ? `${API_URL.replace(/\/$/, "")}${url}` : url;

export default function TrailerBanner({ movie }) {
  const [playing, setPlaying] = useState(false);
  const [failed, setFailed] = useState(false);
  const id = youtubeId(movie.trailer_url);
  return (
    <div className="trailer">
      <div className="trailer__banner">
        {playing ? failed ? <p role="alert">Không phát được video trailer.</p>
          : id ? <iframe src={`https://www.youtube-nocookie.com/embed/${id}?autoplay=1&rel=0`}
            title={`Trailer phim ${movie.title}`} allow="autoplay; encrypted-media; picture-in-picture; fullscreen" allowFullScreen />
          : <video controls autoPlay playsInline preload="metadata" src={mediaUrl(movie.trailer_url)} onError={() => setFailed(true)} />
          : <>
            <Poster movie={movie} size="lg" />
            <div className="trailer__shade" />
            {movie.trailer_url && <button type="button" className="trailer__play" aria-label={`Xem trailer phim ${movie.title}`} onClick={() => setPlaying(true)}>▶</button>}
          </>}
      </div>
      {id && <a className="trailer__external" href={`https://www.youtube.com/watch?v=${id}`} target="_blank" rel="noopener noreferrer">Mở trên YouTube</a>}
    </div>
  );
}
