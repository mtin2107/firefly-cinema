import AgeBadge from "./AgeBadge";
import { fullDateTime, money } from "../utils/format";
import { sortSeats } from "../utils/seats";

export default function TicketStub({ movie, showtime, seats, total, code, highlight = false }) {
  return (
    <article className={`ticket${highlight ? " ticket--new" : ""}`}>
      <div className="ticket__main">
        <h3 className="ticket__title">{movie.title}</h3>
        <p className="ticket__line"><AgeBadge rating={movie.age_rating} /> {showtime.room}</p>
        <dl className="ticket__facts">
          <div><dt>Suất chiếu</dt><dd>{fullDateTime(showtime.start_time)}</dd></div>
          <div><dt>Ghế</dt><dd>{sortSeats(seats).join(", ")}</dd></div>
          <div><dt>Tổng tiền</dt><dd>{money(total)}</dd></div>
        </dl>
      </div>
      <div className="ticket__stub">
        <span className="ticket__stub-label">Mã vé</span>
        <span className="ticket__code">{code ?? "—"}</span>
      </div>
    </article>
  );
}
