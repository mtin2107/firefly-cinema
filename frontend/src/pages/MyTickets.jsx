import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api } from "../api";
import TicketStub from "../components/TicketStub";
import { Loading, ErrorState, Empty } from "../components/StateViews";

const ticketCode = (id) => `FF${String(id).padStart(6, "0")}`;

export default function MyTickets() {
  const { state } = useLocation();
  const [bookings, setBookings] = useState(null);
  const [error, setError] = useState("");

  const load = () => {
    setError("");
    api.bookings.mine().then(setBookings).catch((e) => setError(e.message));
  };
  useEffect(load, []);

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!bookings) return <Loading />;

  return (
    <div className="container narrow">
      <h1 className="page-title">Vé của tôi</h1>
      {state?.newBookingId && (
        <p className="notice notice--ok" role="status">
          Đã đặt vé. Đưa mã {ticketCode(state.newBookingId)} cho nhân viên quầy để nhận vé.
        </p>
      )}
      {bookings.length === 0 ? (
        <Empty>
          <p>Bạn chưa đặt vé nào.</p>
          <Link className="btn btn--primary" to="/">Chọn phim</Link>
        </Empty>
      ) : (
        <div className="ticket-list">
          {bookings.map((b) => (
            <TicketStub key={b.id} movie={b.movie} showtime={b.showtime} seats={b.seats}
              total={b.total} code={ticketCode(b.id)} highlight={b.id === state?.newBookingId} />
          ))}
        </div>
      )}
    </div>
  );
}
