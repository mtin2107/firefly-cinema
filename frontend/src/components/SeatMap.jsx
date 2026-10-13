import { useRef } from "react";
import { ROWS, COLS, isVip } from "../utils/seats";
import { gsap, useGSAP, EASE, DUR, useReducedMotion } from "../utils/motion";

export default function SeatMap({ booked, selected, onToggle }) {
  const root = useRef(null);
  const reduced = useReducedMotion();

  // Các hàng ghế hiện lần lượt từ phía màn hình ra; bật giảm chuyển động giữa chừng thì revert về trạng thái cuối
  useGSAP(() => {
    if (reduced) return;
    gsap.from(root.current.querySelectorAll(".seat-row"), { autoAlpha: 0, y: -18, stagger: 0.04, duration: DUR.slow, ease: EASE.out, clearProps: "all" });
  }, { dependencies: [reduced], revertOnUpdate: true });

  return (
    <div className="seatmap" ref={root}>
      <div className="seatmap__stage">
        <div className="screen" aria-hidden="true"><span>Màn hình</span></div>
        <div className="seatmap__scroll">
          <div className="seatmap__grid" role="group" aria-label="Sơ đồ ghế">
            {ROWS.map((row) => (
              <div className="seat-row" key={row}>
                <span className="seat-row__label" aria-hidden="true">{row}</span>
                {Array.from({ length: COLS }, (_, i) => {
                  const code = `${row}${i + 1}`;
                  const taken = booked.includes(code);
                  const chosen = selected.includes(code);
                  const cls = ["seat", isVip(code) && "seat--vip", taken && "seat--taken", chosen && "seat--chosen"]
                    .filter(Boolean).join(" ");
                  return (
                    <button key={code} type="button" className={cls} disabled={taken}
                      aria-pressed={chosen} aria-label={`Ghế ${code}${isVip(code) ? " VIP" : ""}${taken ? ", đã có người đặt" : ""}`}
                      onClick={() => onToggle(code)}>
                      {i + 1}
                    </button>
                  );
                })}
                <span className="seat-row__label" aria-hidden="true">{row}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      <ul className="legend">
        <li><span className="seat seat--demo" /> Ghế thường</li>
        <li><span className="seat seat--demo seat--vip" /> Ghế VIP</li>
        <li><span className="seat seat--demo seat--chosen" /> Đang chọn</li>
        <li><span className="seat seat--demo seat--taken" /> Đã có người đặt</li>
      </ul>
    </div>
  );
}
