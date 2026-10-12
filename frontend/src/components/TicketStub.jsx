import AgeBadge from "./AgeBadge";
import { fullDateTime, money } from "../utils/format";
import { sortSeats } from "../utils/seats";

const STATUS_LABELS = {
  held: "Giữ chỗ – chưa thanh toán",
  pending_verify: "Chờ xác nhận chuyển khoản",
  paid: "Đã thanh toán",
  expired: "Đã hủy – quá hạn thanh toán",
  rejected: "Đã hủy – không nhận được thanh toán",
};

export default function TicketStub({ movie, showtime, seats, total, code, status, holdExpiresAt,
  qrUrl, highlight = false, onClaim, claiming = false }) {
  const holdText = holdExpiresAt ? fullDateTime(holdExpiresAt) : "—";
  return (
    <article className={`ticket${highlight ? " ticket--new" : ""}`}>
      <div className="ticket__main">
        <h3 className="ticket__title">{movie.title}</h3>
        <p className="ticket__line"><AgeBadge rating={movie.age_rating} /> {showtime.room}</p>
        <dl className="ticket__facts">
          <div><dt>Suất chiếu</dt><dd>{fullDateTime(showtime.start_time)}</dd></div>
          <div><dt>Ghế</dt><dd>{sortSeats(seats).join(", ")}</dd></div>
          <div><dt>Tổng tiền</dt><dd>{money(total)}</dd></div>
          {status && <div><dt>Trạng thái</dt><dd><span className={`ticket-status ticket-status--${status}`}>{STATUS_LABELS[status]}</span></dd></div>}
          {status === "held" && <div><dt>Tự hủy lúc</dt><dd>{holdText}</dd></div>}
        </dl>
        {status === "held" && <div className="ticket-payment">
          {qrUrl ? <img className="ticket-payment__qr" src={qrUrl} alt={`Mã QR thanh toán vé ${code}`} />
            : <p className="muted">Chưa cấu hình thanh toán QR. Vui lòng thanh toán tại quầy trước giờ tự hủy.</p>}
          {qrUrl && <div><p>Quét QR để chuyển khoản.</p><p><strong>Nội dung chuyển khoản: {code}</strong></p></div>}
          <button type="button" className="btn btn--primary btn--sm" onClick={onClaim} disabled={claiming}>
            {claiming ? "Đang gửi..." : "Tôi đã chuyển khoản"}
          </button>
        </div>}
      </div>
      <div className="ticket__stub">
        <span className="ticket__stub-label">Mã vé</span>
        <span className="ticket__code">{code ?? "—"}</span>
      </div>
    </article>
  );
}
