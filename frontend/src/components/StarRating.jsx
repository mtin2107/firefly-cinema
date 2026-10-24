import { ratingLabels } from "../utils/ratings";
import { gsap, MOTION_OK, useReducedMotion } from "../utils/motion";
import { useEffect, useRef, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function StarRating({ value, onChange, disabled = false, max = 10, onSelect }) {
  const rootRef = useRef(null);
  const reduced = useReducedMotion();
  useEffect(() => {
    const buttons = rootRef.current?.querySelectorAll("button");
    if (buttons) { gsap.killTweensOf(buttons); gsap.set(buttons, { clearProps: "transform" }); }
    return () => { if (buttons) gsap.killTweensOf(buttons); };
  }, [reduced]);
  const [preview, setPreview] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const choose = (stars, event) => {
    if (!user) return navigate("/dang-nhap", { state: { from: location } });
    onChange(value === stars ? null : stars);
    onSelect?.(stars, event.currentTarget);
  };
  return <div ref={rootRef}><div className="star-rating" role="group" aria-label="Chấm điểm cho phim" onMouseLeave={() => setPreview(null)}>
    {Array.from({ length: max }, (_, i) => i + 1).map((stars) => <button key={stars} type="button"
      aria-label={`Chấm ${stars} điểm`} aria-pressed={value === stars} disabled={disabled}
      className={`star-rating__button${stars <= (preview ?? value ?? 0) ? " star-rating__button--active" : ""}`}
      onMouseEnter={(event) => { setPreview(stars); if (window.matchMedia(MOTION_OK).matches) gsap.to(event.currentTarget, { scale: 1.2, duration: 0.15 }); }} onMouseLeave={(event) => gsap.set(event.currentTarget, { scale: 1 })}
      onClick={(event) => choose(stars, event)}>★</button>)}
  </div><p className="rating-label">{(preview ?? value) ? `${preview ?? value} điểm · ${ratingLabels[(preview ?? value) - 1]}` : "Chọn điểm của bạn"}</p></div>;
}
