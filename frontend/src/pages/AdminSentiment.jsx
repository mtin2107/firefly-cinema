import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { ErrorState, Loading } from "../components/StateViews";

const PERIODS = [7, 30, 90];
const percent = (value) => `${(value * 100).toFixed(1)}%`;
const shortDate = (value) => new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit" })
  .format(new Date(`${value}T00:00:00`));

function DailyChart({ rows }) {
  const max = Math.max(1, ...rows.map((row) => row.total));
  const slot = 24;
  const width = Math.max(320, rows.length * slot);
  return <>
    <div className="sentiment-chart-scroll">
      <svg className="sentiment-chart" viewBox={`0 0 ${width} 220`} role="img"
        aria-label="Biểu đồ cột tổng số và số bình luận tiêu cực theo ngày">
        <line x1="0" y1="190" x2={width} y2="190" className="sentiment-chart__axis" />
        {rows.map((row, index) => {
          const totalHeight = row.total / max * 160;
          const negativeHeight = row.negative / max * 160;
          const x = index * slot + 3;
          return <g key={row.date}>
            <title>{`${row.date}: ${row.total} tổng, ${row.negative} tiêu cực`}</title>
            <rect x={x} y={190 - totalHeight} width="8" height={totalHeight} className="sentiment-chart__total" />
            <rect x={x + 9} y={190 - negativeHeight} width="8" height={negativeHeight} className="sentiment-chart__negative" />
            {(rows.length <= 30 || index % 7 === 0 || index === rows.length - 1) &&
              <text x={x + 8} y="208" textAnchor="middle">{shortDate(row.date)}</text>}
          </g>;
        })}
      </svg>
    </div>
    <div className="sentiment-legend" aria-hidden="true"><span><i className="sentiment-legend__total" />Tổng</span><span><i className="sentiment-legend__negative" />Tiêu cực</span></div>
  </>;
}

export default function AdminSentiment() {
  const [days, setDays] = useState(30);
  const [data, setData] = useState(null);
  const [error, setError] = useState("");

  const load = () => {
    setError("");
    setData(null);
    api.admin.sentiment(days).then(setData).catch((err) => setError(err.message));
  };
  useEffect(load, [days]);

  return <div className="container admin-sentiment">
    <div className="admin-sentiment__heading">
      <div>
        <h1 className="page-title">Thống kê cảm xúc</h1>
        <p className="muted admin__intro">Tính cả bình luận đã ẩn; nhãn người duyệt được ưu tiên hơn nhãn model.</p>
      </div>
      <div className="tabs" role="tablist" aria-label="Khoảng thời gian thống kê">
        {PERIODS.map((period) => <button key={period} role="tab" aria-selected={days === period}
          className={`tab${days === period ? " tab--active" : ""}`} onClick={() => setDays(period)}>
          {period} ngày
        </button>)}
      </div>
    </div>

    {error ? <ErrorState message={error} onRetry={load} /> : !data ? <Loading /> : <>
      <section className="sentiment-summary" aria-label={`Tóm tắt ${days} ngày`}>
        <div><span>Tổng bình luận</span><strong>{data.summary.total}</strong></div>
        <div><span>Bình luận tiêu cực</span><strong>{data.summary.negative}</strong></div>
        <div><span>Tỷ lệ tiêu cực</span><strong>{percent(data.summary.negative_ratio)}</strong></div>
        <div><span>Model khớp người duyệt</span><strong>{percent(data.summary.model_human_accuracy)}</strong><small>{data.summary.reviewed} bình luận đã duyệt</small></div>
      </section>

      {data.summary.total === 0 ? <p className="state">Chưa có bình luận trong {days} ngày gần đây.</p> : <>
        <section className="sentiment-panel" aria-labelledby="sentiment-movies-title">
          <h2 id="sentiment-movies-title">Tỷ lệ tiêu cực theo phim</h2>
          <div className="sentiment-movies">
            {data.movies.map((movie) => <div className="sentiment-movie" key={movie.movie_id}>
              <div className="sentiment-movie__label"><Link to={`/phim/${movie.movie_id}`}>{movie.title}</Link><span>{movie.negative}/{movie.total} · {percent(movie.negative_ratio)}</span></div>
              <div className="sentiment-bar" aria-label={`${movie.title}: ${percent(movie.negative_ratio)} tiêu cực`}>
                <span style={{ width: percent(movie.negative_ratio) }} />
              </div>
              <small className="muted">Điểm tiêu cực model trung bình: {movie.avg_negative_score.toFixed(2)}</small>
            </div>)}
          </div>
        </section>

        <section className="sentiment-panel" aria-labelledby="sentiment-daily-title">
          <h2 id="sentiment-daily-title">Diễn biến theo ngày</h2>
          <DailyChart rows={data.daily} />
          <div className="table-wrap sentiment-daily-table">
            <table className="admin-table">
              <caption>Số liệu bình luận theo từng ngày</caption>
              <thead><tr><th>Ngày</th><th>Tổng</th><th>Tiêu cực</th></tr></thead>
              <tbody>{data.daily.map((row) => <tr key={row.date}><td>{row.date}</td><td>{row.total}</td><td>{row.negative}</td></tr>)}</tbody>
            </table>
          </div>
        </section>
      </>}
    </>}
  </div>;
}
