import { useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function StarRating({ value, onChange, disabled = false }) {
  const [preview, setPreview] = useState(null);
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const choose = (stars) => {
    if (!user) return navigate("/dang-nhap", { state: { from: location } });
    onChange(value === stars ? null : stars);
  };
  return <div className="star-rating" role="group" aria-label="Chấm sao cho phim" onMouseLeave={() => setPreview(null)}>
    {[1, 2, 3, 4, 5].map((stars) => <button key={stars} type="button"
      aria-label={`Chấm ${stars} sao`} aria-pressed={value === stars} disabled={disabled}
      className={`star-rating__button${stars <= (preview ?? value ?? 0) ? " star-rating__button--active" : ""}`}
      onMouseEnter={() => setPreview(stars)} onFocus={() => setPreview(stars)} onBlur={() => setPreview(null)}
      onClick={() => choose(stars)}>★</button>)}
  </div>;
}
