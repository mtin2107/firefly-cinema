import { useEffect, useState } from "react";
import { Navigate, useLocation, useNavigate } from "react-router-dom";
import { api } from "../api";
import TicketStub from "../components/TicketStub";
import { Loading, ErrorState } from "../components/StateViews";
import { money } from "../utils/format";
import { isVip, seatPrice, sortSeats, totalPrice } from "../utils/seats";

export default function Checkout() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");

  useEffect(() => {
    if (state?.showtimeId) api.showtimes.get(state.showtimeId).then(setData).catch((e) => setError(e.message));
  }, [state?.showtimeId]);

  // Vào thẳng trang này (không qua chọn ghế) thì quay về trang chủ
  if (!state?.showtimeId || !state?.seats?.length) return <Navigate to="/" replace />;
  if (error) return <ErrorState message={error} />;
  if (!data) return <Loading />;

  const { movie, showtime } = data;
  const seats = sortSeats(state.seats);
  const total = totalPrice(seats, showtime.price);

  const confirm = async () => {
    setSubmitting(true); setSubmitError("");
    try {
      const booking = await api.bookings.create({ showtime_id: showtime.id, seats });
      navigate("/ve-cua-toi", { replace: true, state: { newBookingId: booking.id } });
    } catch (e) {
      setSubmitError(e.message);
      setSubmitting(false);
    }
  };

  return (
    <div className="container narrow">
      <h1 className="page-title">Xác nhận đặt vé</h1>
      <TicketStub movie={movie} showtime={showtime} seats={seats} total={total} />

      <table className="price-table">
        <caption className="sr-only">Chi tiết giá vé</caption>
        <tbody>
          {seats.map((s) => (
            <tr key={s}><th scope="row">Ghế {s}{isVip(s) ? " (VIP)" : ""}</th><td>{money(seatPrice(s, showtime.price))}</td></tr>
          ))}
          <tr className="price-table__total"><th scope="row">Tổng cộng</th><td>{money(total)}</td></tr>
        </tbody>
      </table>

      <p className="muted">Thanh toán tại quầy khi nhận vé. Vé được giữ đến 15 phút trước giờ chiếu.</p>
      {submitError && <p className="notice notice--error" role="alert">{submitError}</p>}

      <div className="actions">
        <button className="btn btn--ghost" onClick={() => navigate(-1)} disabled={submitting}>Chọn lại ghế</button>
        <button className="btn btn--primary btn--lg" onClick={confirm} disabled={submitting}>
          {submitting ? "Đang đặt vé..." : "Đặt vé"}
        </button>
      </div>
    </div>
  );
}
