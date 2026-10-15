import { useEffect, useRef, useState } from "react";
import AgeBadge from "./AgeBadge";
import FireflyField from "./FireflyField";
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
  // Vé giữ chỗ có QR không lật để thao tác thanh toán luôn thấy và bấm được
  const flippable = status === "paid" || status === "pending_verify";
  const [flipped, setFlipped] = useState(false);
  const [burst, setBurst] = useState(null);
  const front = useRef(null);
  const back = useRef(null);
  const userFlipped = useRef(false);

  // Mặt đang úp không nhận focus/đọc màn hình; sau khi lật thì đưa focus sang nút của mặt mới
  useEffect(() => {
    if (front.current) front.current.inert = flipped;
    if (back.current) back.current.inert = !flipped;
    if (userFlipped.current) (flipped ? back : front).current?.querySelector(".ticket__flip")?.focus();
  }, [flipped, flippable]);

  // Vé vừa đặt: in ra từ khe máy rồi bung đom đóm một lần
  useEffect(() => {
    if (!highlight) return;
    const t = setTimeout(() => setBurst({ x: 0.5, y: 0.5, key: Date.now() }), 600);
    return () => clearTimeout(t);
  }, [highlight]);

  const flip = (value) => { userFlipped.current = true; setFlipped(value); };

  return (
    <div className="ticket-wrap">
      <article className={`ticket${highlight ? " ticket--new ticket--print" : ""}${flipped ? " ticket--flipped" : ""}`}>
        <div className="ticket__face ticket__face--front" ref={front} aria-hidden={flipped || undefined}>
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
              {qrUrl && <button type="button" className="btn btn--primary btn--sm" onClick={onClaim} disabled={claiming}>
                {claiming ? "Đang gửi..." : "Tôi đã chuyển khoản"}
              </button>}
            </div>}
            {flippable && (
              <button type="button" className="btn btn--ghost btn--sm ticket__flip" onClick={() => flip(true)}>Lật vé</button>
            )}
          </div>
          <div className="ticket__stub">
            <span className="ticket__stub-label">Mã vé</span>
            <span className="ticket__code">{code ?? "—"}</span>
          </div>
        </div>
        {flippable && (
          <div className="ticket__face ticket__face--back" ref={back} aria-hidden={!flipped || undefined}>
            <span className="ticket__stub-label">Mã vé</span>
            <span className="ticket__code ticket__code--big">{code}</span>
            <p>Ghế {sortSeats(seats).join(", ")} · {fullDateTime(showtime.start_time)}</p>
            <p className="muted">Đưa mã này tại quầy</p>
            <button type="button" className="btn btn--ghost btn--sm ticket__flip" onClick={() => flip(false)}>Lật lại</button>
          </div>
        )}
        {highlight && <FireflyField count={0} burstAt={burst} className="ticket__burst" />}
      </article>
    </div>
  );
}
