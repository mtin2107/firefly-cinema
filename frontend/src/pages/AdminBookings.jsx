import { usePageTitle } from "../utils/pageTitle";
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

const PAYMENT_RESULTS = [
  ["needs_review", "Cần xử lý tay"],
  ["paid", "Đã tự xác nhận vé"],
  ["resolved", "Đã xử lý"],
  ["ignored", "Bỏ qua (tiền ra)"],
  ["", "Tất cả giao dịch"],
];
const paymentLabel = (result) => PAYMENT_RESULTS.find(([value]) => value === result)?.[1] ?? result;

// T33: giao dịch SePay báo về. Giao dịch thiếu tiền, sai mã hoặc vé hết hạn cần admin hoàn tiền/xử lý tay.
function SepayPayments() {
  const [result, setResult] = useState("needs_review");
  const [rows, setRows] = useState(null);
  const [error, setError] = useState("");
  const [busyId, setBusyId] = useState(null);

  const load = async (next = result) => {
    setError(""); setRows(null);
    try { setRows(await api.admin.payments.list({ result: next })); }
    catch (err) { setError(err.message); }
  };
  useEffect(() => { load(); }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const resolve = async (row) => {
    if (!window.confirm(`Đánh dấu giao dịch ${row.id} là đã xử lý (đã hoàn tiền hoặc đã duyệt tay)?`)) return;
    setBusyId(row.id); setError("");
    try { await api.admin.payments.resolve(row.id); await load(); }
    catch (err) { setError(err.message); }
    finally { setBusyId(null); }
  };

  return <section className="admin-payments">
    <h2>Giao dịch SePay</h2>
    <p className="muted admin__intro">Tiền vào đúng mã vé và đủ số tiền được tự xác nhận. Các giao dịch còn lại cần hoàn tiền hoặc duyệt tay ở bảng vé phía trên, sau đó bấm "Đã xử lý".</p>
    <form className="booking-filters" onSubmit={(event) => { event.preventDefault(); load(result); }}>
      <label className="field"><span>Kết quả</span><select value={result} onChange={(event) => setResult(event.target.value)}>{PAYMENT_RESULTS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}</select></label>
      <button className="btn btn--ghost" type="submit">Lọc giao dịch</button>
    </form>
    {error ? <ErrorState message={error} onRetry={() => load(result)} />
      : !rows ? <Loading label="Đang tải giao dịch..." />
      : rows.length === 0 ? <Empty><p>Không có giao dịch phù hợp.</p></Empty>
      : <div className="table-wrap"><table className="admin-table"><thead><tr><th>Mã GD / thời gian</th><th>Nội dung</th><th>Số tiền</th><th>Kết quả</th><th>Thao tác</th></tr></thead><tbody>{rows.map((row) => <tr key={row.id}>
        <td><strong>{row.id}</strong><br /><span className="muted">{row.transaction_date || fullDateTime(row.received_at)}</span></td>
        <td>{row.content || "(trống)"}<br /><span className="muted">Mã vé: {row.booking_code ?? "không tìm thấy"}</span></td>
        <td><strong>{money(row.amount)}</strong></td>
        <td>{paymentLabel(row.result)}{row.note && <><br /><span className="muted">{row.note}</span></>}</td>
        <td>{row.result === "needs_review" && <button className="btn btn--primary btn--sm" disabled={busyId === row.id} onClick={() => resolve(row)}>Đã xử lý</button>}</td>
      </tr>)}</tbody></table></div>}
  </section>;
}

export default function AdminBookings() {
  usePageTitle("Quản lý vé");
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
    <SepayPayments />
  </div>;
}
