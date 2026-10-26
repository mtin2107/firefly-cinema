import { Link, useLocation, useNavigate } from "react-router-dom";
import { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import { Loading } from "../components/StateViews";
import { money, fullDateTime, dayKey } from "../utils/format";
import { avatarSrc, initials, membership } from "../utils/account";
import { MEMBERSHIP } from "../config";
import { usePageTitle } from "../utils/pageTitle";
const labels = {
  held: "Đang giữ chỗ",
  pending_verify: "Chờ xác minh",
  paid: "Đã thanh toán",
  expired: "Đã hết hạn",
  rejected: "Đã từ chối"
};
const tabs = [["giao-dich", "Lịch sử giao dịch"], ["ho-so", "Thông tin cá nhân"], ["hoat-dong", "Hoạt động & Thông báo"], ["chinh-sach", "Chính sách"]];
function moderation(c) {
  if (c.hidden) return "Bị quản trị viên ẩn";
  if (c.human_label != null) return `Quản trị viên đã duyệt lại: ${c.human_label ? "giữ ẩn" : "hiển thị bình thường"}`;
  return c.is_negative ? "Bị mô hình đánh giá tiêu cực nên đang bị che" : "Đang hiển thị bình thường";
}
export default function Account() {
  usePageTitle("Tài khoản");
  const auth = useAuth();
  const {
    user
  } = auth;
  const admin = user.role === "admin";
  const location = useLocation();
  const navigate = useNavigate();
  const tab = tabs.some(([id]) => `#${id}` === location.hash) ? location.hash.slice(1) : "giao-dich";
  const [summary, setSummary] = useState(null),
    [tickets, setTickets] = useState([]),
    [error, setError] = useState("");
  const [message, setMessage] = useState(""),
    [busy, setBusy] = useState(false),
    [emailOpen, setEmailOpen] = useState(false);
  const [name, setName] = useState(user.full_name),
    [birth, setBirth] = useState(user.birth_date || ""),
    [gender, setGender] = useState(user.gender || "");
  const fileRef = useRef(null);
  useEffect(() => {
    let active = true;
    setSummary(null);
    setError("");
    (admin ? api.admin.meSummary() : api.auth.meSummary()).then(data => {
      if (active) setSummary(data);
    }).catch(e => {
      if (active) setError(e.message);
    });
    if (!admin) api.bookings.mine().then(rows => {
      if (active) setTickets(rows.sort((a, b) => b.created_at.localeCompare(a.created_at)));
    }).catch(e => {
      if (active) setError(e.message);
    });
    return () => {
      active = false;
    };
  }, [user.id, admin]);
  async function run(action, text) {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      await action();
      setMessage(text);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }
  async function upload(event) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file) return;
    if (file.size > 2 * 1024 * 1024) {
      setError("Ảnh tối đa 2 MB.");
      return;
    }
    await run(async () => {
      const data = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result.split(",")[1]);
        reader.onerror = () => reject(new Error("Không đọc được ảnh."));
        reader.readAsDataURL(file);
      });
      await auth.putAvatar({
        filename: file.name,
        data
      });
    }, "Đã cập nhật ảnh đại diện.");
  }
  const tier = membership(summary?.spent_this_year || 0);
  const groups = tickets.reduce((all, t) => {
    (all[dayKey(t.created_at).slice(0, 7)] ||= []).push(t);
    return all;
  }, {});
  const security = <section className="account-card">
    <h2>{admin ? "Bảo mật" : "Thông tin cá nhân"}</h2>
    <form className="account-form" onSubmit={e => {
      e.preventDefault();
      run(() => auth.updateProfile({
        full_name: name.trim(),
        ...(!admin ? {
          birth_date: birth || null,
          gender: gender || null
        } : {})
      }), "Đã lưu hồ sơ.");
    }}>
      <label className="field">Họ tên<input required minLength="2" maxLength="100" value={name} onChange={e => setName(e.target.value)} /></label>
      {!admin && <><label className="field">Ngày sinh<input type="date" min="1900-01-01" value={birth} onChange={e => setBirth(e.target.value)} /></label><label className="field">Giới tính<select value={gender} onChange={e => setGender(e.target.value)}><option value="">Chưa khai báo</option><option value="male">Nam</option><option value="female">Nữ</option><option value="unspecified">Không muốn trả lời</option></select></label></>}
      <button className="btn btn--primary" disabled={busy}>Lưu hồ sơ</button>
    </form>
    <div className="account-security"><p>Email: {user.email}</p><button className="btn btn--ghost" onClick={() => setEmailOpen(!emailOpen)} aria-expanded={emailOpen}>Thay đổi email</button>
    {emailOpen && <form className="account-form" onSubmit={e => {
        e.preventDefault();
        const form = e.currentTarget;
        const data = new FormData(form);
        run(async () => {
          await auth.changeEmail(Object.fromEntries(data));
          form.reset();
          setEmailOpen(false);
        }, "Đã đổi email.");
      }}><label className="field">Email mới<input name="new_email" type="email" required /></label><label className="field">Mật khẩu hiện tại<input name="current_password" type="password" autoComplete="current-password" required /></label><button className="btn btn--primary" disabled={busy}>Lưu email</button></form>}</div>
    <div className="account-security"><h3>Ảnh đại diện</h3><p className="muted">JPG, PNG hoặc WebP, tối đa 2 MB.</p><div className="account-actions"><button className="btn btn--ghost" disabled={busy} onClick={() => fileRef.current?.click()}>Tải ảnh lên</button>{user.avatar_url && <button className="btn btn--ghost" disabled={busy} onClick={() => run(auth.deleteAvatar, "Đã gỡ ảnh đại diện.")}>Gỡ ảnh</button>}</div></div>
    <div className="account-security"><h3>Đổi mật khẩu</h3><form className="account-form" onSubmit={e => {
        e.preventDefault();
        const form = e.currentTarget;
        const data = new FormData(form);
        if (data.get("new_password") !== data.get("confirm")) {
          setError("Mật khẩu nhập lại chưa khớp.");
          return;
        }
        run(async () => {
          await auth.changePassword(data.get("current_password"), data.get("new_password"));
          form.reset();
        }, "Đã đổi mật khẩu.");
      }}>
      <label className="field">Mật khẩu hiện tại<input name="current_password" type="password" autoComplete="current-password" required /></label><label className="field">Mật khẩu mới<input name="new_password" type="password" autoComplete="new-password" minLength="6" maxLength="100" required /></label><label className="field">Nhập lại mật khẩu mới<input name="confirm" type="password" autoComplete="new-password" minLength="6" maxLength="100" required /></label><button className="btn btn--primary" disabled={busy}>Đổi mật khẩu</button>
    </form></div>
  </section>;
  return <div className="container account-page">
    <h1 className="page-title">Tài khoản của tôi</h1>
    <input ref={fileRef} type="file" accept="image/jpeg,image/png,image/webp" hidden onChange={upload} aria-label="Chọn ảnh đại diện" />
    {error && <p role="alert" className="notice notice--error">{error}</p>}{message && <p role="status" className="notice notice--ok">{message}</p>}
    <div className="account-layout"><aside className="account-card account-sidebar">
      <button className="account-avatar" title="Đổi ảnh đại diện" aria-label="Đổi ảnh đại diện" disabled={busy} onClick={() => fileRef.current?.click()}>{user.avatar_url ? <img src={avatarSrc(user.avatar_url)} alt="" /> : initials(user.full_name)}</button>
      <h2>{user.full_name}</h2><p>{user.email}</p><p className="account-tier">{admin ? "Quản trị viên" : tier.name}</p>
      {user.created_at && <p className="muted">Thành viên từ {new Date(user.created_at).toLocaleDateString("vi-VN")}</p>}
      {!admin && <><h3>Tổng chi tiêu {new Date().getFullYear()}</h3><strong>{money(summary?.spent_this_year || 0)}</strong><progress max="100" value={tier.progress} aria-label="Tiến độ hạng thành viên" /><p className="muted">{tier.next ? `Còn ${money(tier.next.threshold - (summary?.spent_this_year || 0))} để đạt hạng ${tier.next.name}` : "Bạn đã đạt hạng cao nhất."}</p></>}
    </aside><div className="account-content">
      {admin ? <>
        {!summary ? !error && <Loading /> : <><section className="account-card"><h2>Việc cần làm</h2><div className="account-todo">{[["comments", "Bình luận chờ duyệt", "binh-luan"], ["pending_verify", "Vé chờ xác nhận chuyển khoản", "ve"], ["showtimes_today", "Suất chiếu hôm nay", "suat-chieu"]].map(([key, label, path]) => <Link key={key} to={`/quan-tri/${path}`}><strong>{summary.todo[key]}</strong><span>{label}</span></Link>)}</div></section>
        <section className="account-card"><h2>Công việc của tôi</h2><div className="account-stats">{[["reviewed_today", "Bình luận duyệt hôm nay"], ["reviewed_total", "Tổng bình luận đã duyệt"], ["overrides", "Nhãn khác mô hình"], ["checked_in_today", "Vé đã soát hôm nay"]].map(([key, label]) => <div key={key}><strong>{summary.work[key]}</strong><span>{label}</span></div>)}</div></section>
        <section className="account-card"><h2>Hoạt động gần đây</h2>{!summary.recent_activity.length ? <p>Chưa có thao tác nào.</p> : summary.recent_activity.map(a => <p key={`${a.kind}-${a.id}`}>{a.label} #{a.id} · {fullDateTime(a.at)}</p>)}</section></>}
        {security}
      </> : <>
        <div className="account-tabs" role="tablist" aria-label="Nội dung tài khoản">{tabs.map(([id, label]) => <button key={id} id={`tab-${id}`} role="tab" aria-selected={tab === id} aria-controls={`panel-${id}`} onClick={() => navigate({
              hash: id
            }, {
              replace: true
            })}>{label}</button>)}</div>
        <div role="tabpanel" id={`panel-${tab}`} aria-labelledby={`tab-${tab}`}>
        {tab === "ho-so" && security}
        {tab === "giao-dich" && <section className="account-card"><h2>Lịch sử giao dịch</h2>{!summary && !error && <Loading />}{!tickets.length ? <p>Bạn chưa có vé nào.</p> : Object.entries(groups).map(([month, rows]) => <section key={month}><h3>Tháng {month.slice(5)}/{month.slice(0, 4)}</h3>{rows.map(t => <article className="account-ticket" key={t.id}><Link className="account-ticket__poster" to={`/phim/${t.movie.id}`} aria-label={`Xem phim ${t.movie.title}`} style={{background:t.movie.poster_bg,color:t.movie.poster_fg}}>{t.movie.poster_url ? <img src={avatarSrc(t.movie.poster_url)} alt="" /> : <span aria-hidden="true">{initials(t.movie.title)}</span>}</Link><div><Link to={`/phim/${t.movie.id}`}>{t.movie.title}</Link><p>{fullDateTime(t.showtime.start_time)}</p><p>Ghế: {t.seats.join(", ") || "Không còn ghế giữ chỗ"}</p><p>{labels[t.status]} · {money(t.total)}</p><Link to="/ve-cua-toi">Xem vé #{t.id}</Link></div></article>)}</section>)}</section>}
        {tab === "hoat-dong" && <section className="account-card"><h2>Hoạt động & Thông báo</h2>{!summary ? !error && <Loading /> : <>{!summary.recent_comments.length && !summary.ratings.length && <p>Bạn chưa có hoạt động nào.</p>}{[...summary.recent_comments.map(c => ({
                  key: `c${c.id}`,
                  at: c.reviewed_at || c.created_at,
                  movie: c.movie_id,
                  title: c.movie_title,
                  content: c.content,
                  notice: moderation(c)
                })), ...summary.ratings.map(r => ({
                  key: `r${r.movie_id}`,
                  at: r.updated_at,
                  movie: r.movie_id,
                  title: r.movie_title,
                  content: `Đã chấm ${r.stars}/10 điểm`
                }))].sort((a, b) => b.at.localeCompare(a.at)).map(a => <article className="account-activity" key={a.key}><Link to={`/phim/${a.movie}`}>{a.title}</Link><p>{a.content}</p>{a.notice && <p className="muted">{a.notice}</p>}<small>{fullDateTime(a.at)}</small></article>)}</>}</section>}
        {tab === "chinh-sach" && <section className="account-card"><h2>Chính sách</h2><h3>Giữ chỗ và hủy vé</h3><p>Giữ chỗ tối đa 15 phút, kết thúc trước suất chiếu 30 phút. Bạn có thể hủy vé đang giữ chỗ chưa thanh toán tại Vé của tôi. Vé chờ xác minh hoặc đã thanh toán không thể tự hủy.</p><h3>Hạng thành viên</h3><p>Tính theo tổng tiền vé đã thanh toán trong năm hiện tại; bắt đầu tính lại mỗi năm.</p>{MEMBERSHIP.map(t => <p key={t.name}>{t.name}: từ {money(t.threshold)}</p>)}<h3>Quy định độ tuổi</h3><p>P: mọi độ tuổi. T13, T16, T18: đủ lần lượt 13, 16, 18 tuổi tính đến ngày suất chiếu. Nhân viên có thể kiểm tra giấy tờ tùy thân tại rạp.</p></section>}
        </div>
      </>}
    </div></div>
  </div>;
}
