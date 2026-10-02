import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../api";
import SeatMap from "../components/SeatMap";
import { Loading, ErrorState } from "../components/StateViews";
import { fullDateTime, money } from "../utils/format";
import { MAX_SEATS_PER_BOOKING, sortSeats, totalPrice } from "../utils/seats";

export default function SeatSelection() {
  const { showtimeId } = useParams();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [selected, setSelected] = useState([]);
  const [hint, setHint] = useState("");

  const load = () => {
    setError("");
    api.showtimes.get(showtimeId).then(setData).catch((e) => setError(e.message));
  };
  useEffect(load, [showtimeId]);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!data) return <Loading />;
  const { movie, showtime, booked_seats } = data;

  const toggle = (code) => {
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

  const total = totalPrice(selected, showtime.price);

  return (
    <div className="container booking">
      <div className="booking__head">
        <Link to={`/phim/${movie.id}#lich-chieu`} className="back">Đổi suất chiếu</Link>
        <h1 className="booking__title">{movie.title}</h1>
        <p className="muted">{fullDateTime(showtime.start_time)}, {showtime.room}</p>
      </div>

      <SeatMap booked={booked_seats} selected={selected} onToggle={toggle} />

      <div className="summary-bar">
        <div className="container summary-bar__inner">
          <div>
            <p className="summary-bar__seats">
              {selected.length ? `Ghế ${sortSeats(selected).join(", ")}` : "Chọn ghế trên sơ đồ"}
            </p>
            {hint && <p className="summary-bar__hint" role="status">{hint}</p>}
          </div>
          <p className="summary-bar__total">{money(total)}</p>
          <button className="btn btn--primary btn--lg" disabled={!selected.length}
            onClick={() => navigate("/xac-nhan", { state: { showtimeId: showtime.id, seats: selected } })}>
            Tiếp tục
          </button>
        </div>
      </div>
    </div>
  );
}
