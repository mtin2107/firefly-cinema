import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { ErrorState, Loading } from "../components/StateViews";
import { money } from "../utils/format";
import { usePageTitle } from "../utils/pageTitle";
import { COLS, MAX_SEATS_PER_BOOKING, ROWS, VIP_ROWS, VIP_SURCHARGE, seatPrice } from "../utils/seats";

const NORMAL_ROWS = ROWS.filter((r) => !VIP_ROWS.includes(r));
const span = (rows) => `${rows[0]}–${rows[rows.length - 1]}`;

export default function Prices() {
  usePageTitle("Giá vé");
  const [prices, setPrices] = useState(null);
  const [error, setError] = useState("");

  const load = () => {
    setError(""); setPrices(null);
    api.showtimes.list()
      .then((rows) => setPrices([...new Set(rows.map((s) => s.price))].sort((a, b) => a - b)))
      .catch((e) => setError(e.message));
  };
  useEffect(load, []);

  return (
    <div className="container prices">
      <h1 className="page-title">Giá vé</h1>
      <p className="muted">Mỗi suất chiếu có giá gốc riêng. Ghế VIP ở hàng {span(VIP_ROWS)} cộng thêm {money(VIP_SURCHARGE)} mỗi ghế.</p>

      <div className="price-cards">
        <div className="price-card">
          <h2>Ghế thường</h2>
          <p className="price-card__rows">Hàng {span(NORMAL_ROWS)} · {COLS} ghế mỗi hàng</p>
          <p className="price-card__value">Giá suất chiếu</p>
        </div>
        <div className="price-card price-card--vip">
          <h2>Ghế VIP</h2>
          <p className="price-card__rows">Hàng {span(VIP_ROWS)} · giữa phòng, tầm nhìn đẹp</p>
          <p className="price-card__value">Giá suất + {money(VIP_SURCHARGE)}</p>
        </div>
      </div>

      <h2 className="section-title">Giá theo suất đang mở bán</h2>
      {error ? <ErrorState message={error} onRetry={load} />
        : !prices ? <Loading label="Đang tải bảng giá..." />
        : prices.length === 0 ? <p className="muted">Hiện chưa có suất chiếu nào mở bán.</p>
        : (
          <table className="price-table">
            <thead><tr><th scope="col">Giá suất</th><th scope="col">Ghế thường</th><th scope="col">Ghế VIP</th></tr></thead>
            <tbody>
              {prices.map((p) => (
                <tr key={p}><td>{money(p)}</td><td>{money(seatPrice(`${NORMAL_ROWS[0]}1`, p))}</td><td>{money(seatPrice(`${VIP_ROWS[0]}1`, p))}</td></tr>
              ))}
            </tbody>
          </table>
        )}

      <ul className="prices__notes muted">
        <li>Mỗi lần đặt tối đa {MAX_SEATS_PER_BOOKING} ghế.</li>
        <li>Giá đúng của từng suất hiện ở <Link to="/lich-chieu">Lịch chiếu</Link> và khi chọn ghế.</li>
      </ul>
    </div>
  );
}
