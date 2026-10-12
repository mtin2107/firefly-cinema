import { useEffect, useState } from "react";
import { api } from "../api";
import { Empty, ErrorState, Loading } from "../components/StateViews";
import { fullDateTime, money } from "../utils/format";

const STATUSES = [
  ["", "Tất cả trạng thái"],
  ["pending_verify", "Chờ xác nhận chuyển khoản"],
  ["held", "Giữ chỗ – chưa thanh toán"],
  ["paid", "Đã thanh toán"],
  ["expired", "Đã hủy – quá hạn thanh toán"],
  ["rejected", "Đã hủy – không nhận được thanh toán"],
];
const labelFor = (status) => STATUSES.find(([value]) => value === status)?.[1] ?? status;

export default function AdminBookings() {
  const [filters, setFilters] = useState({ status: "pending_verify", code: "" });
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = async (next = filters) => {
    setError(""); setRows(null);
    try { setRows(await api.admin.bookings.list(next)); }
    catch (err) { setError(err.message); }
  };
  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const submit = (event) => { event.preventDefault(); load(filters); };
  const act = async (booking, action) => {
    const verb = action === "confirm" ? "xác nhận đã nhận tiền" : "từ chối thanh toán";
    if (!window.confirm(`Bạn chắc chắn muốn ${verb} cho vé ${booking.code}?`)) return;
    setBusyId(booking.id); setError(""); setNotice("");
    try {
      if (action === "confirm") await api.admin.bookings.confirm(booking.id);
      else await api.admin.bookings.reject(booking.id);
      setNotice(action === "confirm" ? `Đã xác nhận vé ${booking.code}.` : `Đã từ chối vé ${booking.code} và trả ghế.`);
      await load(filters);
    } catch (err) { setError(err.message); }
    finally { setBusyId(null); }
  };

  return <div className="container admin-bookings">
    <h1 className="page-title">Quản lý vé</h1>
    <p className="muted admin__intro">Đối chiếu nội dung chuyển khoản theo mã vé rồi xác nhận hoặc từ chối. Danh sách hiển thị tối đa 200 vé mới nhất.</p>
    <form className="booking-filters" onSubmit={submit}>
      <label className="field"><span>Trạng thái</span><select value={filters.status} onChange={(event) => setFilters((value) => ({ ...value, status: event.target.value }))}>{STATUSES.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
      <label className="field"><span>Mã vé</span><input value={filters.code} placeholder="FF00042" onChange={(event) => setFilters((value) => ({ ...value, code: event.target.value.toUpperCase() }))} /></label>
      <button className="btn btn--ghost" type="submit">Lọc vé</button>
    </form>
    {notice && <p className="notice notice--ok" role="status">{notice}</p>}
    {error ? <ErrorState message={error} onRetry={() => load(filters)} />
      : !rows ? <Loading label="Đang tải danh sách vé..." />
      : rows.length === 0 ? <Empty><p>Không có vé phù hợp với bộ lọc.</p></Empty>
      : <div className="table-wrap"><table className="admin-table admin-booking-table"><thead><tr><th>Mã vé / khách</th><th>Phim / suất</th><th>Ghế</th><th>Thanh toán</th><th>Thao tác</th></tr></thead><tbody>{rows.map((booking) => <tr key={booking.id}>
        <td><strong>{booking.code}</strong><br />{booking.customer_name}<br /><span className="muted">{booking.customer_email}</span></td>
        <td><strong>{booking.movie.title}</strong><br /><span className="muted">{fullDateTime(booking.showtime.start_time)} · {booking.showtime.room}</span></td>
        <td>{booking.seats.join(", ") || "Đã trả ghế"}</td>
        <td><span className={`ticket-status ticket-status--${booking.status}`}>{labelFor(booking.status)}</span><br /><strong>{money(booking.total)}</strong></td>
        <td><div className="admin-movie-actions">{["held", "pending_verify"].includes(booking.status) && <><button className="btn btn--primary btn--sm" disabled={busyId === booking.id} onClick={() => act(booking, "confirm")}>Đã nhận tiền</button><button className="btn btn--danger btn--sm" disabled={busyId === booking.id} onClick={() => act(booking, "reject")}>Từ chối</button></>}</div></td>
      </tr>)}</tbody></table></div>}
  </div>;
}
