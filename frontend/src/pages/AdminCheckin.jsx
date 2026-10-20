import { useState } from "react";
import { api } from "../api";
import { fullDateTime } from "../utils/format";
import { usePageTitle } from "../utils/pageTitle";
const reasons = { held: "Vé chưa thanh toán, đang giữ chỗ.", pending_verify: "Vé chưa thanh toán, đang chờ xác nhận chuyển khoản.", expired: "Vé đã hủy do quá hạn thanh toán.", rejected: "Vé đã hủy do không nhận được thanh toán.", paid: "Đã thanh toán, có thể vào rạp." };
export default function AdminCheckin() {
  usePageTitle("Soát vé tại quầy");
  const [code,setCode]=useState(""), [ticket,setTicket]=useState(null), [busy,setBusy]=useState(false), [error,setError]=useState("");
  async function search(e) { e.preventDefault(); setBusy(true); setTicket(null); setError(""); try { setTicket(await api.admin.checkin.get(code)); } catch(e) { setError(e.message); } finally { setBusy(false); } }
  async function confirm() { setBusy(true); setError(""); try { setTicket(await api.admin.checkin.confirm(ticket.code)); } catch(e) { setError(e.message); try { setTicket(await api.admin.checkin.get(ticket.code)); } catch { setTicket(null); } } finally { setBusy(false); } }
  return <div className="container narrow t23-page"><h1 className="page-title">Soát vé tại quầy</h1>
    <form className="t23-search" onSubmit={search}><label htmlFor="ticket-code">Mã vé</label><input id="ticket-code" placeholder="FF00042" value={code} onChange={(e) => { setCode(e.target.value); setTicket(null); setError(""); }} required disabled={busy} /><button className="btn btn--primary" disabled={busy}>{busy ? "Đang xử lý…" : "Tra cứu"}</button></form>
    {error && <p role="alert" className="notice notice--error">{error}</p>}
    {ticket && <section className="t23-card"><h2>{ticket.movie.title}</h2><p>Mã vé: {ticket.code}</p><p>Suất: {fullDateTime(ticket.showtime.start_time)} · {ticket.showtime.room}</p><p>Ghế: {ticket.seats.join(", ") || "Đã trả ghế"}</p><p>Khách: {ticket.customer_name} · {ticket.customer_email}</p><p role="status">{ticket.checked_in_at ? `Đã vào rạp lúc ${fullDateTime(ticket.checked_in_at)} · ${ticket.checked_in_by_name}` : reasons[ticket.status]}</p><button className="btn btn--primary" disabled={busy || ticket.status !== "paid" || !!ticket.checked_in_at} onClick={confirm}>Xác nhận vào rạp</button></section>}
  </div>;
}
