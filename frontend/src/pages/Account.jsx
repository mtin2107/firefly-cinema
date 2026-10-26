import { Link, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import { Loading } from "../components/StateViews";
import Poster from "../components/Poster";
import Icon, { Medal } from "../components/Icons";
import { money, fullDateTime, dayKey, timeOf } from "../utils/format";
import { avatarSrc, initials, membership, validateProfile } from "../utils/account";
import { MEMBERSHIP } from "../config";
import { usePageTitle } from "../utils/pageTitle";

const labels = { held: "Đang giữ chỗ", pending_verify: "Chờ xác minh", paid: "Đã thanh toán", expired: "Hết hạn giữ chỗ", rejected: "Đã từ chối" };
const tabs = [["giao-dich", "Vé & giao dịch", "ticket"], ["ho-so", "Thông tin cá nhân", "user"], ["hoat-dong", "Thông báo", "bell"], ["chinh-sach", "Chính sách", "policy"]];
const genders = [["male", "Nam"], ["female", "Nữ"], ["unspecified", "Không muốn trả lời"]];
const dateText = iso => iso ? iso.split("-").reverse().join("/") : "";
function birthISO(text) {
  if (!text.trim()) return null;
  if (!/^\d{2}\/\d{2}\/\d{4}$/.test(text)) throw new Error("Ngày sinh cần nhập theo dd/mm/yyyy.");
  const iso = text.split("/").reverse().join("-");
  validateProfile(iso, null);
  return iso;
}
function moderation(c) {
  if (c.hidden) return "Bị quản trị viên ẩn";
  if (c.human_label != null) return `Quản trị viên đã duyệt lại: ${c.human_label ? "giữ ẩn" : "hiển thị bình thường"}`;
  return c.is_negative ? "Bị mô hình đánh giá tiêu cực nên đang bị che" : "Đang hiển thị bình thường";
}
function Stat({ icon, value, label, to }) {
  const content = <><Icon name={icon} size={26} /><strong>{value}</strong><span>{label}</span></>;
  return to ? <Link className="ac-stat" to={to}>{content}</Link> : <div className="ac-stat">{content}</div>;
}
function TierLadder({ spent }) {
  const tier = membership(spent);
  const first = Math.min(...MEMBERSHIP.map(t => t.threshold));
  const span = Math.max(...MEMBERSHIP.map(t => t.threshold)) - first || 1;
  const position = threshold => (threshold - first) / span * 100;
  return <section className="ac-spend" aria-label="Hạng thành viên">
    <div className="ac-spent"><span>TỔNG CHI TIÊU {new Date().getFullYear()}</span><strong>{money(spent)}</strong></div>
    <div className="ac-rail" aria-label={`Hạng hiện tại: ${tier.name}`}>
      <i style={{width:`${Math.max(0,Math.min(100,position(spent)))}%`}} />
      {MEMBERSHIP.map((item,index) => <div key={item.name} className={`ac-medal${spent >= item.threshold ? " ac-medal--achieved" : ""}`} style={{left:`${position(item.threshold)}%`}} aria-current={item.threshold === tier.threshold ? "step" : undefined}>
        <Medal level={index} /><span><b>{item.name}</b>{money(item.threshold)}</span>
      </div>)}
    </div>
    <p className="ac-hint">{tier.next ? <>Còn <b>{money(tier.next.threshold-spent)}</b> để lên hạng <b>{tier.next.name}</b></> : "Đã đạt hạng cao nhất"}</p>
  </section>;
}
function Ticket({ ticket }) {
  const { movie, showtime } = ticket;
  const off = ["expired","rejected"].includes(ticket.status);
  return <Link to="/ve-cua-toi" className={`ac-ticket${off ? " ac-ticket--off" : ""}`} aria-label={`Xem vé ${ticket.code}: ${movie.title}`}>
    <div className="ac-ticket-main">
      <Poster movie={movie} size="sm" />
      <div className="ac-ticket-info">
        <div className="ac-ticket-heading"><h3 title={movie.title}>{movie.title}</h3><span className={`ac-status ac-status--${ticket.status}`}>{labels[ticket.status]}</span></div>
        <div className="ac-facts">
          <span><Icon name="calendar" size={14} />{new Date(showtime.start_time).toLocaleDateString("vi-VN",{weekday:"short",day:"2-digit",month:"2-digit",year:"numeric"})}</span>
          <span><Icon name="clock" size={14} />{timeOf(showtime.start_time)}</span>
          <span><Icon name="location" size={14} />{showtime.room}</span><span className="ac-age">{movie.age_rating}</span>
        </div>
        <div className="ac-seats">{ticket.seats.length ? ticket.seats.map(seat => <b key={seat}>{seat}</b>) : <span>Ghế đã được nhả</span>}</div>
      </div>
    </div>
    <div className="ac-stub"><small>MÃ VÉ</small><strong className="ac-code">{ticket.code}</strong><div className="ac-barcode" aria-hidden="true" /><strong className="ac-price">{money(ticket.total)}</strong></div>
  </Link>;
}

export default function Account() {
  usePageTitle("Tài khoản");
  const auth = useAuth(), { user } = auth;
  const admin = user.role === "admin";
  const location = useLocation(), navigate = useNavigate();
  const tab = tabs.some(([id]) => `#${id}` === location.hash) ? location.hash.slice(1) : "giao-dich";
  const [summary,setSummary] = useState(null), [tickets,setTickets] = useState(null), [error,setError] = useState("");
  const [message,setMessage] = useState(""), [busy,setBusy] = useState(false), [emailOpen,setEmailOpen] = useState(false), [passwordOpen,setPasswordOpen] = useState(false);
  const [name,setName] = useState(user.full_name), [birth,setBirth] = useState(dateText(user.birth_date)), [gender,setGender] = useState(user.gender || "");
  const [dragging,setDragging] = useState(false);
  const fileRef = useRef(null);
  useEffect(() => {
    let active = true;
    setSummary(null); setTickets(null); setError("");
    (admin ? api.admin.meSummary() : api.auth.meSummary()).then(data => { if(active) setSummary(data); }).catch(e => { if(active) setError(e.message); });
    if(!admin) api.bookings.mine().then(rows => { if(active) setTickets([...rows].sort((a,b) => b.created_at.localeCompare(a.created_at))); }).catch(e => { if(active) setError(e.message); });
    return () => { active = false; };
  },[user.id,admin]);
  async function run(action,text) {
    if(busy) return;
    setBusy(true); setError(""); setMessage("");
    try { await action(); setMessage(text); } catch(e) { setError(e.message); } finally { setBusy(false); }
  }
  function resetProfile() { setName(user.full_name); setBirth(dateText(user.birth_date)); setGender(user.gender || ""); setError(""); setMessage(""); }
  async function uploadFile(file) {
    if(!file || busy) return;
    if(file.size > 2*1024*1024) { setError("Ảnh đại diện tối đa 2 MB."); return; }
    await run(async () => {
      const data = await new Promise((resolve,reject) => { const reader = new FileReader(); reader.onload = () => resolve(reader.result.split(",")[1]); reader.onerror = () => reject(new Error("Không đọc được ảnh.")); reader.readAsDataURL(file); });
      await auth.putAvatar({filename:file.name,data});
    },"Đã cập nhật ảnh đại diện.");
  }
  const avatar = <div className="ac-avatar"><span>{user.avatar_url ? <img src={avatarSrc(user.avatar_url)} alt="" /> : initials(user.full_name)}</span><button type="button" aria-label="Đổi ảnh đại diện" disabled={busy} onClick={() => fileRef.current?.click()}><Icon name="camera" size={17} /></button></div>;
  const spent = summary?.spent_this_year || 0, tier = membership(spent);
  const notifications = summary?.recent_comments?.filter(c => c.hidden || c.is_negative || c.human_label != null).length || 0;
  const groups = (tickets || []).reduce((all,t) => { (all[dayKey(t.created_at).slice(0,7)] ||= []).push(t); return all; },{});
  const security = <div className="ac-profile-grid">
    <section className="ac-panel"><h2><Icon name={admin ? "lock" : "user"} />{admin ? "Bảo mật" : "Thông tin cá nhân"}</h2>
      <form className="ac-form" onSubmit={e => {e.preventDefault();run(async () => {
        const birth_date = admin ? undefined : birthISO(birth);
        await auth.updateProfile({full_name:name.trim(),...(!admin ? {birth_date,gender:gender || null} : {})});
      },"Đã lưu hồ sơ.");}}>
        <label className="ac-field">Họ và tên<span className="ac-input"><Icon name="user" size={18} /><input required minLength={2} maxLength={100} value={name} onChange={e => setName(e.target.value)} autoComplete="name" /></span></label>
        {!admin && <label className="ac-field">Ngày sinh<span className="ac-input"><Icon name="calendar" size={18} /><input type="text" inputMode="numeric" placeholder="dd/mm/yyyy" maxLength={10} value={birth} onChange={e => setBirth(e.target.value)} autoComplete="bday" /></span></label>}
        <label className="ac-field">Email<span className="ac-input"><Icon name="email" size={18} /><input aria-label="Email" readOnly value={user.email} type="email" /><button type="button" aria-label="Thay đổi email" aria-expanded={emailOpen} onClick={() => {setEmailOpen(!emailOpen);setPasswordOpen(false);}}>Thay đổi</button></span></label>
        <label className="ac-field">Mật khẩu<span className="ac-input"><Icon name="lock" size={18} /><input aria-label="Mật khẩu" readOnly value="••••••••••" /><button type="button" aria-label="Thay đổi mật khẩu" aria-expanded={passwordOpen} onClick={() => {setPasswordOpen(!passwordOpen);setEmailOpen(false);}}>Thay đổi</button></span></label>
        {!admin && <fieldset className="ac-gender"><legend>Giới tính</legend><div role="radiogroup" aria-label="Giới tính">{genders.map(([value,label]) => <button key={value} type="button" role="radio" aria-checked={gender === value} onClick={() => setGender(value)}>{label}</button>)}</div></fieldset>}
        <div className="ac-actions"><button type="button" className="ac-btn" disabled={busy} onClick={resetProfile}>Hủy</button><button className="ac-btn ac-btn--primary" disabled={busy}>{busy ? "Đang lưu..." : "Cập nhật"}</button></div>
      </form>
      {emailOpen && <form className="ac-editor ac-form" aria-label="Đổi email" onSubmit={e => {e.preventDefault();const form=e.currentTarget;const data=new FormData(form);run(async () => {await auth.changeEmail(Object.fromEntries(data));setEmailOpen(false);},"Đã đổi email.");}}>
        <h3>Đổi email</h3><label className="ac-field">Email mới<span className="ac-input"><Icon name="email" size={18} /><input name="new_email" type="email" required autoComplete="email" /></span></label><label className="ac-field">Mật khẩu hiện tại<span className="ac-input"><Icon name="lock" size={18} /><input name="current_password" type="password" required autoComplete="current-password" /></span></label><div className="ac-actions"><button type="button" className="ac-btn" onClick={() => setEmailOpen(false)}>Hủy đổi email</button><button className="ac-btn ac-btn--primary" disabled={busy}>Lưu email</button></div>
      </form>}
      {passwordOpen && <form className="ac-editor ac-form" aria-label="Đổi mật khẩu" onSubmit={e => {e.preventDefault();const data=new FormData(e.currentTarget);if(data.get("new_password") !== data.get("confirm")){setError("Mật khẩu nhập lại chưa khớp.");return;}run(async () => {await auth.changePassword(data.get("current_password"),data.get("new_password"));setPasswordOpen(false);},"Đã đổi mật khẩu.");}}>
        <h3>Đổi mật khẩu</h3><label className="ac-field ac-field--wide">Mật khẩu hiện tại<span className="ac-input"><Icon name="lock" size={18} /><input name="current_password" type="password" required autoComplete="current-password" /></span></label><label className="ac-field">Mật khẩu mới<span className="ac-input"><Icon name="lock" size={18} /><input name="new_password" type="password" minLength={6} maxLength={100} required autoComplete="new-password" /></span></label><label className="ac-field">Nhập lại mật khẩu mới<span className="ac-input"><Icon name="lock" size={18} /><input name="confirm" type="password" minLength={6} maxLength={100} required autoComplete="new-password" /></span></label><div className="ac-actions"><button type="button" className="ac-btn" onClick={() => setPasswordOpen(false)}>Hủy đổi mật khẩu</button><button className="ac-btn ac-btn--primary" disabled={busy}>Đổi mật khẩu</button></div>
      </form>}
    </section>
    <section className={`ac-panel ac-upload${dragging ? " ac-upload--over" : ""}`} onDragOver={e => {e.preventDefault();setDragging(true);}} onDragLeave={() => setDragging(false)} onDrop={e => {e.preventDefault();setDragging(false);uploadFile(e.dataTransfer.files?.[0]);}}>
      <h2>Ảnh đại diện</h2>{avatar}<p>Kéo ảnh vào đây hoặc <button type="button" className="ac-text-button" disabled={busy} onClick={() => fileRef.current?.click()}>chọn từ máy</button></p><p className="ac-upload-hint">JPG, PNG, WebP · tối đa 2 MB</p>{user.avatar_url && <button type="button" className="ac-btn" disabled={busy} onClick={() => run(auth.deleteAvatar,"Đã gỡ ảnh đại diện.")}>Gỡ ảnh</button>}
    </section>
  </div>;
  return <div className="container account-page ac-page">
    <p className="ac-eyebrow">Tài khoản của tôi</p>
    <input ref={fileRef} type="file" accept="image/jpeg,image/png,image/webp" hidden aria-label="Chọn ảnh đại diện" onChange={e => {uploadFile(e.target.files?.[0]);e.target.value="";}} />
    <section className={`ac-hero${admin ? " ac-hero--admin" : ""}`}>
      {avatar}<div className="ac-identity"><h1>{user.full_name}</h1><p>{user.email}{!admin && user.created_at && <> · Thành viên từ tháng {`${String(new Date(user.created_at).getMonth()+1).padStart(2,"0")}/${new Date(user.created_at).getFullYear()}`}</>}</p><div className="ac-badges"><span className="ac-badge ac-badge--tier"><Icon name={admin ? "lock" : "star"} size={14} />{admin ? "Quản trị viên" : `Hạng ${tier.name}`}</span>{!admin && summary?.favorite_genre && <span className="ac-badge">Hay xem {summary.favorite_genre}</span>}</div></div>
      {admin ? <div className="ac-shortcuts"><span>KHÔNG GIAN QUẢN TRỊ</span><Link to="/quan-tri/binh-luan"><Icon name="moderation" />Kiểm duyệt bình luận</Link><Link to="/quan-tri/soat-ve"><Icon name="checkin" />Soát vé</Link></div> : <TierLadder spent={spent} />}
    </section>
    {error && <p role="alert" className="notice notice--error ac-notice">{error}</p>}{message && <p role="status" className="notice notice--ok ac-notice">{message}</p>}
    {!summary && !error && <Loading />}
    {admin ? <>
      {summary && <><h2 className="ac-section-title"><Icon name="overview" />Việc cần làm</h2><div className="ac-stats ac-stats--three">{[["comments","Bình luận chờ duyệt","moderation","binh-luan"],["pending_verify","Vé chờ xác nhận chuyển khoản","tickets","ve"],["showtimes_today","Suất chiếu hôm nay","calendar","suat-chieu"]].map(([key,label,icon,path]) => <Stat key={key} icon={icon} label={label} value={summary.todo[key]} to={`/quan-tri/${path}`} />)}</div>
      <h2 className="ac-section-title"><Icon name="user" />Công việc của tôi</h2><div className="ac-stats">{[["reviewed_today","Bình luận duyệt hôm nay","moderation"],["reviewed_total","Tổng bình luận đã duyệt","comment"],["overrides","Nhãn khác mô hình","compare"],["checked_in_today","Vé đã soát hôm nay","checkin"]].map(([key,label,icon]) => <Stat key={key} icon={icon} label={label} value={summary.work[key]} />)}</div>
      <section className="ac-panel ac-admin-activity"><h2><Icon name="clock" />Hoạt động gần đây</h2>{!summary.recent_activity.length ? <p>Chưa có thao tác nào.</p> : summary.recent_activity.map(a => <article className="ac-activity" key={`${a.kind}-${a.id}`}><Icon name={a.kind === "review" ? "moderation" : "checkin"} /><div><strong>{a.label} · {a.movie_title}</strong><time dateTime={a.at}>{fullDateTime(a.at)}</time></div></article>)}</section></>}
      {security}
    </> : <>
      {summary && <div className="ac-stats">{[["bookings","Vé đã đặt","ticket"],["watched","Phim đã xem","watched"],["comments","Bình luận","comment"],["ratings","Phim đã chấm","star"]].map(([key,label,icon]) => <Stat key={key} icon={icon} value={summary.stats[key]} label={label} />)}</div>}
      <div className="ac-tabs" role="tablist" aria-label="Nội dung tài khoản">{tabs.map(([id,label,icon]) => <button type="button" key={id} id={`tab-${id}`} role="tab" aria-selected={tab === id} aria-controls={`panel-${id}`} onClick={() => navigate({hash:id},{replace:true})}><Icon name={icon} size={18} />{label}{id === "hoat-dong" && notifications > 0 && <sup aria-label={`${notifications} thông báo kiểm duyệt`}>{notifications}</sup>}</button>)}</div>
      <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`}>
        {tab === "giao-dich" && <section aria-label="Lịch sử giao dịch">{tickets === null ? !error && <Loading /> : !tickets.length ? <div className="ac-panel"><p>Bạn chưa có vé nào.</p><Link to="/">Khám phá phim đang chiếu</Link></div> : Object.entries(groups).map(([month,rows]) => <section key={month}><h2 className="ac-month">Tháng {month.slice(5)} · {month.slice(0,4)}</h2>{rows.map(t => <Ticket key={t.id} ticket={t} />)}</section>)}</section>}
        {tab === "ho-so" && security}
        {tab === "hoat-dong" && <section className="ac-panel"><h2><Icon name="bell" />Hoạt động & Thông báo</h2>{summary && <>{!summary.recent_comments.length && !summary.ratings.length && <p>Bạn chưa có hoạt động nào.</p>}{[...summary.recent_comments.map(c => ({key:`c${c.id}`,icon:"comment",at:c.reviewed_at || c.created_at,movie:c.movie_id,title:c.movie_title,content:c.content,notice:moderation(c)})),...summary.ratings.map(r => ({key:`r${r.movie_id}`,icon:"star",at:r.updated_at,movie:r.movie_id,title:r.movie_title,content:`Đã chấm ${r.stars}/10 điểm`}))].sort((a,b) => b.at.localeCompare(a.at)).map(a => <article className="ac-activity" key={a.key}><Icon name={a.icon} /><div><Link to={`/phim/${a.movie}`}>{a.title}</Link><p>{a.content}</p>{a.notice && <p className="ac-activity-notice">{a.notice}</p>}<time dateTime={a.at}>{fullDateTime(a.at)}</time></div></article>)}</>}</section>}
        {tab === "chinh-sach" && <section className="ac-panel ac-policy"><h2><Icon name="policy" />Chính sách</h2><h3><Icon name="clock" />Giữ chỗ và hủy vé</h3><p>Giữ chỗ tối đa 15 phút, kết thúc trước suất chiếu 30 phút. Bạn có thể hủy vé đang giữ chỗ chưa thanh toán tại Vé của tôi. Vé chờ xác minh hoặc đã thanh toán không thể tự hủy.</p><h3><Icon name="star" />Hạng thành viên</h3><p>Tính theo tổng tiền vé đã thanh toán trong năm hiện tại; bắt đầu tính lại mỗi năm.</p>{MEMBERSHIP.map(t => <p key={t.name}>{t.name}: từ {money(t.threshold)}</p>)}<h3><Icon name="user" />Quy định độ tuổi</h3><p>P: mọi độ tuổi. T13, T16, T18: đủ lần lượt 13, 16, 18 tuổi tính đến ngày suất chiếu. Nhân viên có thể kiểm tra giấy tờ tùy thân tại rạp.</p></section>}
      </div>
    </>}
  </div>;
}
