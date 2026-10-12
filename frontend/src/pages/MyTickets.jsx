import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api } from "../api";
import TicketStub from "../components/TicketStub";
import { Loading, ErrorState, Empty } from "../components/StateViews";

export default function MyTickets() {
  const { state } = useLocation();
  const [bookings, setBookings] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [claimingId, setClaimingId] = useState(null);

  const load = () => {
    setError("");
    api.bookings.mine().then(setBookings).catch((e) => setError(e.message));
  };
  useEffect(load, []);

  const claim = async (booking) => {
    setClaimingId(booking.id); setError(""); setNotice("");
    try {
      await api.bookings.claimTransfer(booking.id);
      setNotice(`Đã gửi báo chuyển khoản cho vé ${booking.code}. Quản trị viên sẽ kiểm tra.`);
      load();
    } catch (err) {
      setError(err.message);
    } finally {
      setClaimingId(null);
    }
  };

  if (error) return <ErrorState message={error} onRetry={load} />;
  if (!bookings) return <Loading />;

  return (
    <div className="container narrow">
      <h1 className="page-title">Vé của tôi</h1>
      {state?.newBookingId && (
        <p className="notice notice--ok" role="status">
          Đã giữ chỗ thành công. Hãy thanh toán vé bên dưới trước giờ tự hủy.
        </p>
      )}
      {bookings.some((booking) => booking.status === "expired") && (
        <p className="notice notice--warn" role="status">Có vé đã tự hủy vì quá hạn thanh toán; ghế đã được trả lại.</p>
      )}
      {notice && <p className="notice notice--ok" role="status">{notice}</p>}
      {bookings.length === 0 ? (
        <Empty>
          <p>Bạn chưa đặt vé nào.</p>
          <Link className="btn btn--primary" to="/">Chọn phim</Link>
        </Empty>
      ) : (
        <div className="ticket-list">
          {bookings.map((b) => (
            <TicketStub key={b.id} movie={b.movie} showtime={b.showtime} seats={b.seats}
              total={b.total} code={b.code} status={b.status} holdExpiresAt={b.hold_expires_at}
              qrUrl={b.qr_url} onClaim={() => claim(b)} claiming={claimingId === b.id}
              highlight={b.id === state?.newBookingId} />
          ))}
        </div>
      )}
    </div>
  );
}
