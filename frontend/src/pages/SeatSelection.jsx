import { useAuth } from "../context/AuthContext";
import { ageAllowed, ageNotice } from "../utils/account";
import { usePageTitle } from "../utils/pageTitle";
import { ratingText } from "../utils/ratings";
import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import SeatMap from "../components/SeatMap";
import { Loading, ErrorState } from "../components/StateViews";
import { fullDateTime, money } from "../utils/format";
import { MAX_SEATS_PER_BOOKING, sortSeats, totalPrice } from "../utils/seats";

export default function SeatSelection() {
  const { user } = useAuth();
  const { showtimeId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState([]);
  const [hint, setHint] = useState("");

  usePageTitle(data?.movie?.title ? `Chọn ghế – ${data.movie.title}` : "Chọn ghế");

  const load = () => {
    setError("");
    setData(null); setSelected([]);
    api.showtimes.get(showtimeId).then(setData).catch(setError);
  };
  useEffect(load, [showtimeId]);

  if (error) return <ErrorState message={error.message} onRetry={error.status === 404 ? undefined : load} />;
  if (!data) return <Loading />;
  const { movie, showtime, booked_seats, bookable } = data;

  const toggle = (code) => {
    if (!bookable) return;
    setHint("");
    setSelected((cur) => {
      if (cur.includes(code)) return cur.filter((c) => c !== code);
      if (cur.length >= MAX_SEATS_PER_BOOKING) {
        setHint(`Mỗi lần đặt tối đa ${MAX_SEATS_PER_BOOKING} ghế.`);
        return cur;
      }
      return [...cur, code];
    });
  };

  const eligible = user?.role === "admin" || ageAllowed(user?.birth_date, movie.age_rating, showtime.start_time);
  const notice = ageNotice(user, movie, showtime.start_time);
  const total = totalPrice(selected, showtime.price);

  return (
    <div className="container booking">
      <div className="booking__head">
        <Link to={`/phim/${movie.id}#lich-chieu`} className="back">Đổi suất chiếu</Link>
        <h1 className="booking__title">{movie.title}</h1>
        <p className="score">{ratingText(movie)}</p>
        <p className="muted">{fullDateTime(showtime.start_time)}, {showtime.room}</p>
      </div>

      {notice && <p role="status" className="notice notice--warn">{notice}</p>}
      {!bookable && <p className="notice notice--warn" role="status">
        {new Date(showtime.start_time).getTime() <= Date.now()
          ? "Suất chiếu đã bắt đầu, không thể đặt vé."
          : "Suất chiếu sắp bắt đầu, vui lòng mua vé tại quầy."}
        {" "}<Link to={`/phim/${movie.id}#lich-chieu`}>Về lịch chiếu</Link>
      </p>}
      <fieldset className="booking-seat-fieldset" disabled={!eligible || !bookable} aria-label="Chọn ghế">
        <SeatMap booked={booked_seats} selected={selected} onToggle={toggle} />
      </fieldset>

      <div className="summary-bar">
        <div className="container summary-bar__inner">
          <div>
            <p className="summary-bar__seats">
              {selected.length ? `Ghế ${sortSeats(selected).join(", ")}` : "Chọn ghế trên sơ đồ"}
            </p>
            {hint && <p className="summary-bar__hint" role="status">{hint}</p>}
          </div>
          <p className="summary-bar__total">{money(total)}</p>
          <button className="btn btn--primary btn--lg" disabled={!eligible || !bookable || !selected.length}
            onClick={() => navigate("/xac-nhan", { state: { showtimeId: showtime.id, seats: selected } })}>
            Tiếp tục
          </button>
        </div>
      </div>
    </div>
  );
}
