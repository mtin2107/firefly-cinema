import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { ErrorState, Loading } from "../components/StateViews";

const PERIODS = [7, 30, 90];
const percent = (value) => `${(value * 100).toFixed(1)}%`;
const shortDate = (value) => new Intl.DateTimeFormat("vi-VN", { day: "2-digit", month: "2-digit" })
  .format(new Date(`${value}T00:00:00`));

function DailyChart({ rows }) {
  const frameRef = useRef(null);
  const [frameWidth, setFrameWidth] = useState(0);

  useEffect(() => {
    const frame = frameRef.current;
    if (!frame) return undefined;
    const updateWidth = () => setFrameWidth(Math.floor(frame.getBoundingClientRect().width));
    updateWidth();
    const observer = new ResizeObserver(updateWidth);
    observer.observe(frame);
    return () => observer.disconnect();
  }, []);

  const max = Math.max(1, ...rows.map((row) => row.total));
  const visibleWidth = Math.max(frameWidth, 320);
  const width = frameWidth < 600 && rows.length === 90
    ? Math.max(visibleWidth, rows.length * 16)
    : visibleWidth;
  const sidePadding = 22;
  const plotWidth = width - sidePadding * 2;
  const slot = plotWidth / rows.length;
  const pairWidth = Math.min(40, Math.max(6, slot * 0.72));
  const barGap = Math.min(2, pairWidth * 0.12);
  const barWidth = (pairWidth - barGap) / 2;
  const labelEvery = Math.max(1, Math.ceil(48 / slot));
  const lastIndex = rows.length - 1;
  return <>
    <div className="sentiment-chart-scroll" ref={frameRef}>
      <svg className="sentiment-chart" width={width} height="240" viewBox={`0 0 ${width} 240`} role="img"
        aria-label="Biểu đồ cột tổng số và số bình luận tiêu cực theo ngày">
        <line x1={sidePadding} y1="202" x2={width - sidePadding} y2="202" className="sentiment-chart__axis" />
        {rows.map((row, index) => {
          const totalHeight = row.total / max * 170;
          const negativeHeight = row.negative / max * 170;
          const center = sidePadding + (index + 0.5) * slot;
          const x = center - pairWidth / 2;
          const showLabel = index === lastIndex
            || (index % labelEvery === 0 && (lastIndex - index) * slot >= 48);
          return <g key={row.date}>
            <title>{`${row.date}: ${row.total} tổng, ${row.negative} tiêu cực`}</title>
            <rect x={x} y={202 - totalHeight} width={barWidth} height={totalHeight} className="sentiment-chart__total" />
            <rect x={x + barWidth + barGap} y={202 - negativeHeight} width={barWidth} height={negativeHeight} className="sentiment-chart__negative" />
            {showLabel && <text x={center} y="224" textAnchor="middle">{shortDate(row.date)}</text>}
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
  const [reloadKey, setReloadKey] = useState(0);

  useEffect(() => {
    let active = true;
    setError("");
    setData(null);
    api.admin.sentiment(days)
      .then((result) => { if (active) setData(result); })
      .catch((err) => { if (active) setError(err.message); });
    return () => { active = false; };
  }, [days, reloadKey]);

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

    {error ? <ErrorState message={error} onRetry={() => setReloadKey((value) => value + 1)} /> : !data ? <Loading /> : <>
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
