import { useEffect, useMemo, useRef, useState } from "react";
import { api } from "../api";
import { Empty, ErrorState, Loading } from "../components/StateViews";
import { money } from "../utils/format";

const ROOMS = ["Phòng 1", "Phòng 2", "Phòng 3", "Phòng 4"];
const pad = (value) => String(value).padStart(2, "0");
const localDate = (date = new Date()) => `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}`;
const localDateTime = (date) => `${localDate(date)}T${pad(date.getHours())}:${pad(date.getMinutes())}`;
const initialStart = () => {
  const value = new Date(Date.now() + 60 * 60 * 1000);
  value.setMinutes(Math.ceil(value.getMinutes() / 15) * 15, 0, 0);
  return localDateTime(value);
};
const emptyForm = () => ({ movie_id: "", start_time: initialStart(), room: ROOMS[0], price: "75000" });

function validate(form) {
  const errors = {};
  if (!form.movie_id) errors.movie_id = "Hãy chọn phim.";
  const start = new Date(form.start_time);
  if (!form.start_time || Number.isNaN(start.getTime()) || start.getTime() <= Date.now()) errors.start_time = "Suất chiếu phải ở tương lai.";
  if (!ROOMS.includes(form.room)) errors.room = "Phòng chiếu không hợp lệ.";
  const price = Number(form.price);
  if (!Number.isInteger(price) || price < 10000 || price > 500000 || price % 1000 !== 0) errors.price = "Giá vé phải từ 10.000 đến 500.000 đồng và là bội số 1.000.";
  return errors;
}
export default function AdminShowtimes() {
  const [movies, setMovies] = useState(null);
  const [showtimes, setShowtimes] = useState(null);
  const [filters, setFilters] = useState({ date: localDate(), movie_id: "" });
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [loadError, setLoadError] = useState("");
  const [actionError, setActionError] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);
  const formTitle = useRef(null);

  const movieMap = useMemo(() => new Map((movies ?? []).map((movie) => [movie.id, movie])), [movies]);
  const selectableMovies = useMemo(() => (movies ?? []).filter((movie) => movie.status !== "ended"), [movies]);

  const load = async (nextFilters = filters) => {
    setLoadError("");
    setShowtimes(null);
    try {
      const [movieRows, showtimeRows] = await Promise.all([
        api.admin.movies.list(),
        api.admin.showtimes.list(nextFilters),
      ]);
      setMovies(movieRows);
      setShowtimes(showtimeRows);
      setForm((current) => current.movie_id || !movieRows.length
        ? current
        : { ...current, movie_id: String(movieRows.find((movie) => movie.status !== "ended")?.id ?? "") });
    } catch (error) {
      setLoadError(error.message);
    }
  };

  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const applyFilters = (event) => {
    event.preventDefault();
    load(filters);
  };

  const update = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => ({ ...current, [field]: "" }));
    setActionError("");
    setNotice("");
  };

  const resetForm = () => {
    setEditingId(null);
    setForm({ ...emptyForm(), movie_id: String(selectableMovies[0]?.id ?? "") });
    setFieldErrors({});
    setActionError("");
  };

  const startEdit = (showtime) => {
    setEditingId(showtime.id);
    setForm({
      movie_id: String(showtime.movie_id),
      start_time: showtime.start_time.slice(0, 16),
      room: showtime.room,
      price: String(showtime.price),
    });
    setFieldErrors({});
    setActionError("");
    setNotice("");
    formTitle.current?.focus();
    window.scrollTo({ top: 0, behavior: window.matchMedia("(prefers-reduced-motion: reduce)").matches ? "auto" : "smooth" });
  };

  const submit = async (event) => {
    event.preventDefault();
    const errors = validate(form);
    setFieldErrors(errors);
    if (Object.keys(errors).length) return;
    setSaving(true);
    setActionError("");
    setNotice("");
    const payload = { movie_id: Number(form.movie_id), start_time: form.start_time, room: form.room, price: Number(form.price) };
    try {
      if (editingId) await api.admin.showtimes.update(editingId, payload);
      else await api.admin.showtimes.create(payload);
      setNotice(editingId ? "Đã cập nhật suất chiếu." : "Đã thêm suất chiếu mới.");
      resetForm();
      const rows = await api.admin.showtimes.list(filters);
      setShowtimes(rows);
    } catch (error) {
      setActionError(error.message);
    } finally {
      setSaving(false);
    }
  };

  const remove = async (showtime) => {
    const movie = movieMap.get(showtime.movie_id);
    if (!window.confirm(`Xóa suất ${movie?.title ?? "này"} lúc ${showtime.start_time.slice(11, 16)}?`)) return;
    setActionError("");
    setNotice("");
    try {
      await api.admin.showtimes.remove(showtime.id);
      setShowtimes((current) => current.filter((item) => item.id !== showtime.id));
      if (editingId === showtime.id) resetForm();
      setNotice("Đã xóa suất chiếu.");
    } catch (error) {
      setActionError(error.message);
    }
  };

  return (
    <div className="container admin-showtimes">
      <h1 className="page-title">Quản lý suất chiếu</h1>
      <p className="muted admin__intro">Xếp lịch theo phòng, thời lượng phim và 15 phút dọn phòng giữa hai suất.</p>

      <section className="admin-showtime-editor" aria-labelledby="showtime-form-title">
        <h2 id="showtime-form-title" className="section-title" tabIndex="-1" ref={formTitle}>{editingId ? "Sửa suất chiếu" : "Thêm suất chiếu"}</h2>
        {actionError && <p className="notice notice--error" role="alert">{actionError}</p>}
        {notice && <p className="notice notice--ok" role="status">{notice}</p>}
        <form className="showtime-form" onSubmit={submit} noValidate>
          <label className="field"><span>Phim *</span><select value={form.movie_id} onChange={(event) => update("movie_id", event.target.value)} aria-invalid={Boolean(fieldErrors.movie_id)}><option value="">Chọn phim</option>{selectableMovies.map((movie) => <option key={movie.id} value={movie.id}>{movie.title} ({movie.duration_min} phút)</option>)}</select>{fieldErrors.movie_id && <span className="field__error">{fieldErrors.movie_id}</span>}</label>
          <label className="field"><span>Ngày giờ bắt đầu *</span><input type="datetime-local" value={form.start_time} min={localDateTime(new Date())} onChange={(event) => update("start_time", event.target.value)} aria-invalid={Boolean(fieldErrors.start_time)} />{fieldErrors.start_time && <span className="field__error">{fieldErrors.start_time}</span>}</label>
          <label className="field"><span>Phòng *</span><select value={form.room} onChange={(event) => update("room", event.target.value)}>{ROOMS.map((room) => <option key={room}>{room}</option>)}</select>{fieldErrors.room && <span className="field__error">{fieldErrors.room}</span>}</label>
          <label className="field"><span>Giá vé (đồng) *</span><input type="number" min="10000" max="500000" step="1000" value={form.price} onChange={(event) => update("price", event.target.value)} aria-invalid={Boolean(fieldErrors.price)} />{fieldErrors.price && <span className="field__error">{fieldErrors.price}</span>}</label>
          <div className="actions">{editingId && <button type="button" className="btn btn--ghost" onClick={resetForm}>Hủy sửa</button>}<button type="submit" className="btn btn--primary" disabled={saving || !selectableMovies.length}>{saving ? "Đang lưu..." : editingId ? "Lưu thay đổi" : "Thêm suất chiếu"}</button></div>
        </form>
      </section>

      <section className="section" aria-labelledby="showtime-list-title">
        <div className="admin-showtime-list-head">
          <h2 id="showtime-list-title" className="section-title">Danh sách suất chiếu</h2>
          <form className="showtime-filters" onSubmit={applyFilters}>
            <label className="field"><span>Ngày</span><input type="date" value={filters.date} onChange={(event) => setFilters((current) => ({ ...current, date: event.target.value }))} /></label>
            <label className="field"><span>Phim</span><select value={filters.movie_id} onChange={(event) => setFilters((current) => ({ ...current, movie_id: event.target.value }))}><option value="">Tất cả phim</option>{(movies ?? []).map((movie) => <option key={movie.id} value={movie.id}>{movie.title}</option>)}</select></label>
            <button type="submit" className="btn btn--ghost">Lọc</button>
          </form>
        </div>
        {loadError ? <ErrorState message={loadError} onRetry={() => load(filters)} />
          : !showtimes ? <Loading label="Đang tải danh sách suất chiếu..." />
          : showtimes.length === 0 ? <Empty><p>Không có suất chiếu phù hợp với bộ lọc.</p></Empty>
          : <div className="table-wrap"><table className="admin-table admin-showtime-table"><thead><tr><th>Ngày giờ</th><th>Phim</th><th>Phòng</th><th>Giá vé</th><th>Thao tác</th></tr></thead><tbody>{showtimes.map((showtime) => <tr key={showtime.id}><td><strong>{new Date(showtime.start_time).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit" })}</strong><br /><span className="muted">{new Date(showtime.start_time).toLocaleDateString("vi-VN")}</span></td><td>{movieMap.get(showtime.movie_id)?.title ?? `Phim #${showtime.movie_id}`}</td><td>{showtime.room}</td><td>{money(showtime.price)}</td><td><div className="admin-movie-actions"><button type="button" className="btn btn--ghost btn--sm" onClick={() => startEdit(showtime)}>Sửa</button><button type="button" className="btn btn--danger btn--sm" onClick={() => remove(showtime)}>Xóa</button></div></td></tr>)}</tbody></table></div>}
      </section>
    </div>
  );
}
