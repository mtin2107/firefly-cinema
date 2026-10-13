import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import Poster from "./Poster";

// Thời gian (ms): giữ poster bao lâu, và hiệu ứng mờ dần bao lâu
const HOLD_MS = 1800;
const FADE_MS = 600;

// Khung bong bóng hiện poster khi vừa bấm vào phim, rồi mờ dần.
// Bấm bất kỳ đâu hoặc phím Esc để bỏ qua.
export default function PosterIntro({ movie, onDone }) {
  const [leaving, setLeaving] = useState(false);
  const timers = useRef([]);

  const leave = () => {
    if (leaving) return;
    setLeaving(true);
    timers.current.push(setTimeout(onDone, FADE_MS));
  };

  useEffect(() => {
    // Người dùng tắt hiệu ứng chuyển động trên máy -> bỏ qua luôn
    if (window.matchMedia?.("(prefers-reduced-motion: reduce)").matches) { onDone(); return; }
    timers.current.push(setTimeout(() => {
      setLeaving(true);
      timers.current.push(setTimeout(onDone, FADE_MS));
    }, HOLD_MS));
    const onKey = (e) => { if (e.key === "Escape") leave(); };
    window.addEventListener("keydown", onKey);
    return () => {
      timers.current.forEach(clearTimeout);
      window.removeEventListener("keydown", onKey);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return createPortal(
    <div className={`intro${leaving ? " intro--leaving" : ""}`} onClick={leave}
      style={{ "--fade": `${FADE_MS}ms` }} aria-hidden="true">
      <div className="intro__bubble">
        <Poster movie={movie} size="xl" />
      </div>
      <p className="intro__title">{movie.title}</p>
    </div>,
    document.body,
  );
}
