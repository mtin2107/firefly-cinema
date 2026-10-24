import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { money } from "../utils/format";
import { usePageTitle } from "../utils/pageTitle";
import { Loading, ErrorState } from "../components/StateViews";
const percent = (n) => `${(n * 100).toFixed(1)}%`;
export default function AdminDashboard() {
  usePageTitle("Tổng quan quản trị");
  const [days, setDays] = useState(30), [data, setData] = useState(null), [error, setError] = useState("");
  const chartRef = useRef(null);
  const [chartWidth, setChartWidth] = useState(320);
  useEffect(() => {
    if (!chartRef.current) return;
    const observer = new ResizeObserver(([entry]) => setChartWidth(Math.max(280, entry.contentRect.width)));
    observer.observe(chartRef.current);
    return () => observer.disconnect();
  }, [!!data]);
  const [retry, setRetry] = useState(0);
  useEffect(() => {
    let active = true; setData(null); setError("");
    api.admin.dashboard(days).then((d) => { if (active) setData(d); }).catch((e) => { if (active) setError(e.message); });
    return () => { active = false; };
  }, [days, retry]);
  const maximum = data ? Math.max(1, ...data.daily.map((d) => d.revenue)) : 1;
  return <div className="container t23-page">
    <h1 className="page-title">Tổng quan quản trị</h1>
    <Link to="/quan-tri/soat-ve">Soát vé tại quầy →</Link>
    <div className="tabs" role="tablist" aria-label="Khoảng thời gian thống kê">
      {[7, 30, 90].map((n) => <button key={n} role="tab" aria-selected={days === n}
        className={`tab${days === n ? " tab--active" : ""}`} onClick={() => setDays(n)}>{n} ngày</button>)}
    </div>
    <p className="muted">Doanh thu, số vé và ghế bán theo ngày đặt vé; tỷ lệ lấp ghế tính trên các suất từ đầu khoảng thời gian, gồm suất sắp chiếu. Điểm và bình luận theo ngày tạo, gồm hôm nay.</p>
    {error && <ErrorState message={error} onRetry={() => setRetry((n) => n + 1)} />}
    {!data && !error && <Loading label="Đang tải tổng quan…" />}
    {data && <>
      <div className="sentiment-summary">{[["Doanh thu", money(data.revenue)], ["Vé đã thanh toán", data.paid_tickets], ["Vé đang chờ", data.pending_tickets], ["Vé đã hủy", data.cancelled_tickets], ["Ghế đã bán", data.seats_sold], ["Điểm", `${data.rating_avg.toFixed(1)} / 10 · ${data.rating_count} lượt`]].map(([label,value]) => <div key={label}><span>{label}</span><strong>{value}</strong></div>)}</div>
      <h2>Doanh thu theo ngày</h2>
      <div className="t23-chart" ref={chartRef}><svg viewBox={`0 0 ${chartWidth} 250`} role="img" aria-label={`Doanh thu ${days} ngày`}>
        <line x1="30" x2={chartWidth-30} y1="210" y2="210" stroke="currentColor" />
        {data.daily.map((d,i) => { const slot=(chartWidth-60)/days, x=30+(i+.5)*slot, height=d.revenue/maximum*180; return <g key={d.date}><title>{d.date}: {money(d.revenue)}, {d.tickets} vé</title><rect x={x-slot*.35} y={210-height} width={slot*.7} height={height} fill="#d4ad62" />{(i===0 || i===days-1 || (i % Math.ceil(days/4)===0 && days-1-i>days/8)) && <text x={x} y="240" textAnchor="middle" fill="currentColor" fontSize="12">{d.date.slice(5).split("-").reverse().join("/")}</text>}</g>; })}
      </svg></div>
      <p className="muted">Di chuột vào cột để xem số tiền và số vé. Ngày không có doanh thu hiển thị 0.</p>
      <h2>Theo phim</h2><div className="t23-table"><table><thead><tr>{["Phim","Vé paid","Doanh thu","Lấp ghế","Điểm","Lượt chấm","Tiêu cực"].map((h) => <th key={h}>{h}</th>)}</tr></thead><tbody>{[...data.movies].sort((a, b) => b.revenue - a.revenue || a.title.localeCompare(b.title, "vi")).map((m) => <tr key={m.movie_id}><td>{m.title}</td><td>{m.paid_tickets}</td><td>{money(m.revenue)}</td><td>{percent(m.occupancy)}</td><td>{m.rating_avg.toFixed(1)} / 10</td><td>{m.rating_count}</td><td>{percent(m.negative_rate)}</td></tr>)}</tbody></table></div>
      {!data.movies.length && <p>Chưa có phim.</p>}
    </>}
  </div>;
}
