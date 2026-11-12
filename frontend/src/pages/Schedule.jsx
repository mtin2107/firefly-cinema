import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api";
import AgeBadge from "../components/AgeBadge";
import Poster from "../components/Poster";
import { Empty, ErrorState, Loading } from "../components/StateViews";
import { dayKey, dayLabel, duration, money, timeOf } from "../utils/format";
import { usePageTitle } from "../utils/pageTitle";

// 7 ngày tính từ hôm nay, dạng YYYY-MM-DD theo giờ máy
const nextDays = () => Array.from({ length: 7 }, (_, i) => {
  const d = new Date();
  d.setDate(d.getDate() + i);
  return dayKey(d);
});

export default function Schedule() {
  usePageTitle("Lịch chiếu");
  const [params, setParams] = useSearchParams();
  const days = nextDays();
  const day = days.includes(params.get("ngay")) ? params.get("ngay") : days[0];
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");

  const load = () => {
    setError(""); setRows(null);
    api.showtimes.list({ date: day }).then(setRows).catch((e) => setError(e.message));
  };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(load, [day]);

  // Nhóm suất theo phim, giữ thứ tự suất sớm nhất
  const groups = [];
  for (const s of rows ?? []) {
    let g = groups.find((x) => x.movie.id === s.movie.id);
    if (!g) groups.push(g = { movie: s.movie, times: [] });
    g.times.push(s);
  }

  return (
    <div className="container schedule">
      <h1 className="page-title">Lịch chiếu</h1>
      <div className="days" role="tablist" aria-label="Chọn ngày">
        {days.map((d) => {
          const l = dayLabel(d);
          return (
            <button key={d} type="button" role="tab" aria-selected={d === day}
              className={`day${d === day ? " day--active" : ""}`} onClick={() => setParams({ ngay: d })}>
              <span className="day__weekday">{l.weekday}</span>
              <span className="day__date">{l.date}</span>
            </button>
          );
        })}
      </div>

      {error ? <ErrorState message={error} onRetry={load} />
        : !rows ? <Loading label="Đang tải lịch chiếu..." />
        : groups.length === 0 ? (
          <Empty>
            <p>Ngày này chưa có suất chiếu nào còn đặt online. Thử chọn ngày khác nhé.</p>
            <Link className="btn btn--primary" to="/kham-pha?trang-thai=sap-chieu">Xem phim sắp chiếu</Link>
          </Empty>
        ) : (
          <ul className="schedule__list">
            {groups.map(({ movie, times }) => (
              <li key={movie.id} className="schedule__item">
                <Link to={`/phim/${movie.id}`} className="schedule__poster" tabIndex={-1} aria-hidden="true">
                  <Poster movie={movie} size="sm" />
                </Link>
                <div>
                  <h2 className="schedule__title">
                    <Link to={`/phim/${movie.id}`}>{movie.title}</Link> <AgeBadge rating={movie.age_rating} />
                  </h2>
                  <p className="muted schedule__meta">{movie.genre} · {duration(movie.duration_min)}</p>
                  <ul className="times">
                    {times.map((s) => (
                      <li key={s.id}>
                        <Link className="time" to={`/dat-ve/${s.id}`}>
                          <span className="time__clock">{timeOf(s.start_time)}</span>
                          <span className="time__info">{s.room}, từ {money(s.price)}</span>
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              </li>
            ))}
          </ul>
        )}
    </div>
  );
}
