import { useEffect, useState } from "react";
import { api } from "../api";
import Poster from "../components/Poster";
import { Empty, ErrorState, Loading } from "../components/StateViews";
import { AGE_RATINGS, COUNTRY_LABELS, FORMAT_LABELS, GENRE_LABELS } from "../utils/taxonomy";

const STATUS_OPTIONS = [
  { value: "now_showing", label: "Đang chiếu" },
  { value: "coming_soon", label: "Sắp chiếu" },
  { value: "ended", label: "Đã chiếu xong" },
];

const EMPTY_FORM = {
  title: "", genre: [], duration_min: "", age_rating: "P", release_date: "",
  status: "now_showing", country: "Việt Nam", formats: ["Phụ đề"], director: "",
  cast: "", description: "", poster_bg: "#1c1c1c", poster_fg: "#ffc72c", poster_url: "",
};

const split = (value) => value.split(",").map((item) => item.trim()).filter(Boolean);
const statusLabel = (value) => STATUS_OPTIONS.find((item) => item.value === value)?.label ?? value;

function validate(form) {
  const errors = {};
  if (!form.title.trim()) errors.title = "Tên phim không được để trống.";
  else if (form.title.trim().length > 200) errors.title = "Tên phim không được dài quá 200 ký tự.";
  if (!form.genre.length) errors.genre = "Hãy chọn ít nhất một thể loại.";
  if (!Number.isInteger(Number(form.duration_min)) || Number(form.duration_min) < 1 || Number(form.duration_min) > 400) errors.duration_min = "Thời lượng phải từ 1 đến 400 phút.";
  if (!form.release_date) errors.release_date = "Hãy nhập ngày phát hành hợp lệ.";
  if (!/^#[0-9a-f]{6}$/i.test(form.poster_bg)) errors.poster_bg = "Màu nền phải có dạng #rrggbb.";
  if (!/^#[0-9a-f]{6}$/i.test(form.poster_fg)) errors.poster_fg = "Màu chữ phải có dạng #rrggbb.";
  if (form.poster_url && !/^https?:\/\//i.test(form.poster_url)) errors.poster_url = "Đường dẫn poster phải bắt đầu bằng http:// hoặc https://.";
  return errors;
}

export default function AdminMovies() {
  const [movies, setMovies] = useState(null);
  const [loadError, setLoadError] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [editingId, setEditingId] = useState(null);
  const [fieldErrors, setFieldErrors] = useState({});
  const [actionError, setActionError] = useState("");
  const [notice, setNotice] = useState("");
  const [saving, setSaving] = useState(false);

  const load = () => {
    setLoadError("");
    setMovies(null);
    api.admin.movies.list().then(setMovies).catch((error) => setLoadError(error.message));
  };
  useEffect(load, []);

  const update = (field, value) => {
    setForm((current) => ({ ...current, [field]: value }));
    setFieldErrors((current) => ({ ...current, [field]: "" }));
    setActionError("");
    setNotice("");
  };

  const toggle = (field, value) => {
    const selected = form[field].includes(value)
      ? form[field].filter((item) => item !== value)
      : [...form[field], value];
    update(field, selected);
  };

  const resetForm = () => {
    setForm(EMPTY_FORM);
    setEditingId(null);
    setFieldErrors({});
    setActionError("");
  };

  const startEdit = (movie) => {
    setEditingId(movie.id);
    setForm({
      title: movie.title,
      genre: split(movie.genre),
      duration_min: String(movie.duration_min),
      age_rating: movie.age_rating,
      release_date: movie.release_date,
      status: movie.status,
      country: movie.country,
      formats: split(movie.formats),
      director: movie.director,
      cast: movie.cast,
      description: movie.description,
      poster_bg: movie.poster_bg,
      poster_fg: movie.poster_fg,
      poster_url: movie.poster_url ?? "",
    });
    setFieldErrors({});
    setActionError("");
    setNotice("");
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const submit = async (event) => {
    event.preventDefault();
    const errors = validate(form);
    setFieldErrors(errors);
    if (Object.keys(errors).length) return;
    setSaving(true);
    setActionError("");
    setNotice("");
    const payload = { ...form, duration_min: Number(form.duration_min), poster_url: form.poster_url || null };
    try {
      if (editingId) await api.admin.movies.update(editingId, payload);
      else await api.admin.movies.create(payload);
      setNotice(editingId ? "Đã cập nhật phim." : "Đã thêm phim mới.");
      resetForm();
      const next = await api.admin.movies.list();
      setMovies(next);
    } catch (error) {
      setActionError(error.message);
    } finally {
      setSaving(false);
    }
  };

  const remove = async (movie) => {
    if (!window.confirm(`Xóa phim “${movie.title}”?`)) return;
    setActionError("");
    setNotice("");
    try {
      await api.admin.movies.remove(movie.id);
      setMovies((current) => current.filter((item) => item.id !== movie.id));
      if (editingId === movie.id) resetForm();
      setNotice("Đã xóa phim.");
    } catch (error) {
      setActionError(error.message);
    }
  };

  const preview = { ...form, genre: form.genre.join(", ") };

  return (
    <div className="container admin-movies">
      <h1 className="page-title">Quản lý phim</h1>
      <p className="muted admin__intro">Thêm phim mới, cập nhật thông tin hoặc chuyển phim sang trạng thái đã chiếu xong.</p>

      <section className="admin-movie-editor" aria-labelledby="movie-form-title">
        <div className="admin-movie-editor__form">
          <h2 id="movie-form-title" className="section-title">{editingId ? "Sửa phim" : "Thêm phim"}</h2>
          {actionError && <p className="notice notice--error" role="alert">{actionError}</p>}
          {notice && <p className="notice notice--ok" role="status">{notice}</p>}
          <form className="movie-form" onSubmit={submit} noValidate>
            <label className="field">
              <span>Tên phim *</span>
              <input value={form.title} maxLength={200} onChange={(event) => update("title", event.target.value)} aria-invalid={Boolean(fieldErrors.title)} />
              {fieldErrors.title && <span className="field__error">{fieldErrors.title}</span>}
            </label>

            <div className="movie-form__row">
              <label className="field"><span>Thời lượng (phút) *</span><input type="number" min="1" max="400" value={form.duration_min} onChange={(event) => update("duration_min", event.target.value)} aria-invalid={Boolean(fieldErrors.duration_min)} />{fieldErrors.duration_min && <span className="field__error">{fieldErrors.duration_min}</span>}</label>
              <label className="field"><span>Ngày phát hành *</span><input type="date" value={form.release_date} onChange={(event) => update("release_date", event.target.value)} aria-invalid={Boolean(fieldErrors.release_date)} />{fieldErrors.release_date && <span className="field__error">{fieldErrors.release_date}</span>}</label>
            </div>

            <div className="movie-form__row">
              <label className="field"><span>Phân loại tuổi *</span><select value={form.age_rating} onChange={(event) => update("age_rating", event.target.value)}>{AGE_RATINGS.map((item) => <option key={item}>{item}</option>)}</select></label>
              <label className="field"><span>Trạng thái *</span><select value={form.status} onChange={(event) => update("status", event.target.value)}>{STATUS_OPTIONS.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}</select></label>
              <label className="field"><span>Quốc gia *</span><select value={form.country} onChange={(event) => update("country", event.target.value)}>{COUNTRY_LABELS.map((item) => <option key={item}>{item}</option>)}</select></label>
            </div>

            <fieldset className="choice-field">
              <legend>Thể loại *</legend>
              <div className="choice-grid">{GENRE_LABELS.map((item) => <label key={item}><input type="checkbox" checked={form.genre.includes(item)} onChange={() => toggle("genre", item)} /> <span>{item}</span></label>)}</div>
              {fieldErrors.genre && <span className="field__error">{fieldErrors.genre}</span>}
            </fieldset>

            <fieldset className="choice-field">
              <legend>Định dạng</legend>
              <div className="choice-grid choice-grid--short">{FORMAT_LABELS.map((item) => <label key={item}><input type="checkbox" checked={form.formats.includes(item)} onChange={() => toggle("formats", item)} /> <span>{item}</span></label>)}</div>
              {fieldErrors.formats && <span className="field__error">{fieldErrors.formats}</span>}
            </fieldset>

            <div className="movie-form__row">
              <label className="field"><span>Đạo diễn</span><input value={form.director} maxLength={100} onChange={(event) => update("director", event.target.value)} /></label>
              <label className="field"><span>Diễn viên</span><input value={form.cast} maxLength={255} onChange={(event) => update("cast", event.target.value)} /></label>
            </div>
            <label className="field"><span>Mô tả</span><textarea rows="4" value={form.description} onChange={(event) => update("description", event.target.value)} /></label>
            <label className="field"><span>Đường dẫn poster (không bắt buộc)</span><input type="url" placeholder="https://..." value={form.poster_url} onChange={(event) => update("poster_url", event.target.value)} aria-invalid={Boolean(fieldErrors.poster_url)} />{fieldErrors.poster_url && <span className="field__error">{fieldErrors.poster_url}</span>}</label>
            <div className="movie-form__row movie-form__colors">
              <label className="field"><span>Màu nền poster *</span><div className="color-input"><input type="color" value={form.poster_bg} onChange={(event) => update("poster_bg", event.target.value)} /><input value={form.poster_bg} onChange={(event) => update("poster_bg", event.target.value)} /></div>{fieldErrors.poster_bg && <span className="field__error">{fieldErrors.poster_bg}</span>}</label>
              <label className="field"><span>Màu chữ poster *</span><div className="color-input"><input type="color" value={form.poster_fg} onChange={(event) => update("poster_fg", event.target.value)} /><input value={form.poster_fg} onChange={(event) => update("poster_fg", event.target.value)} /></div>{fieldErrors.poster_fg && <span className="field__error">{fieldErrors.poster_fg}</span>}</label>
            </div>
            <div className="actions">
              {editingId && <button type="button" className="btn btn--ghost" onClick={resetForm}>Hủy sửa</button>}
              <button type="submit" className="btn btn--primary" disabled={saving}>{saving ? "Đang lưu..." : editingId ? "Lưu thay đổi" : "Thêm phim"}</button>
            </div>
          </form>
        </div>
        <aside className="admin-movie-editor__preview" aria-label="Xem trước poster">
          <h2 className="section-title">Xem trước poster</h2>
          <Poster movie={preview} size="lg" />
        </aside>
      </section>

      <section className="section" aria-labelledby="movie-list-title">
        <h2 id="movie-list-title" className="section-title">Danh sách phim</h2>
        {loadError ? <ErrorState message={loadError} onRetry={load} />
          : !movies ? <Loading label="Đang tải danh sách phim..." />
          : movies.length === 0 ? <Empty><p>Chưa có phim nào. Hãy thêm bộ phim đầu tiên.</p></Empty>
          : (
            <div className="table-wrap">
              <table className="admin-table admin-movie-table">
                <thead><tr><th>Phim</th><th>Thể loại</th><th>Phát hành</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
                <tbody>{movies.map((movie) => (
                  <tr key={movie.id}>
                    <td><div className="admin-movie-title"><Poster movie={movie} size="sm" /><div><strong>{movie.title}</strong><span className="muted">{movie.duration_min} phút · {movie.age_rating}</span></div></div></td>
                    <td>{movie.genre}</td>
                    <td>{movie.release_date}</td>
                    <td><span className="label label--ok">{statusLabel(movie.status)}</span></td>
                    <td><div className="admin-movie-actions"><button type="button" className="btn btn--ghost btn--sm" onClick={() => startEdit(movie)}>Sửa</button><button type="button" className="btn btn--danger btn--sm" onClick={() => remove(movie)}>Xóa</button></div></td>
                  </tr>
                ))}</tbody>
              </table>
            </div>
          )}
      </section>
    </div>
  );
}
