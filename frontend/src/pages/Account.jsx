import { Link } from "react-router-dom";
import { api } from "../api";
import { Loading } from "../components/StateViews";
import { money, fullDateTime } from "../utils/format";

import { usePageTitle } from "../utils/pageTitle";
import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";

const bookingLabels = { held: "Đang giữ chỗ", pending_verify: "Chờ xác minh", paid: "Đã thanh toán", expired: "Đã hết hạn", rejected: "Đã từ chối" };

export default function Account() {
  usePageTitle("Tài khoản");
  const { user, updateProfile, changePassword } = useAuth();
  const [summary, setSummary] = useState(null);
  const [tickets, setTickets] = useState(null);
  const [summaryError, setSummaryError] = useState("");
  const [ticketsError, setTicketsError] = useState("");
  useEffect(() => {
    let active = true;
    api.auth.meSummary().then((data) => { if (active) setSummary(data); }).catch((e) => { if (active) setSummaryError(e.message); });
    api.bookings.mine().then((data) => { if (active) setTickets([...data].sort((a,b) => b.created_at.localeCompare(a.created_at)).slice(0,3)); }).catch((e) => { if (active) setTicketsError(e.message); });
    return () => { active = false; };
  }, [user.id]);
  const [fullName, setFullName] = useState(user?.full_name ?? "");
  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [profileMessage, setProfileMessage] = useState("");
  const [passwordMessage, setPasswordMessage] = useState("");
  const [profileError, setProfileError] = useState("");
  const [passwordError, setPasswordError] = useState("");
  const [savingProfile, setSavingProfile] = useState(false);
  const [savingPassword, setSavingPassword] = useState(false);

  useEffect(() => setFullName(user?.full_name ?? ""), [user?.full_name]);

  const submitProfile = async (event) => {
    event.preventDefault();
    setProfileError(""); setProfileMessage(""); setSavingProfile(true);
    try {
      await updateProfile(fullName.trim());
      setProfileMessage("Đã cập nhật họ tên.");
    } catch (error) {
      setProfileError(error.message);
    } finally {
      setSavingProfile(false);
    }
  };

  const submitPassword = async (event) => {
    event.preventDefault();
    setPasswordError(""); setPasswordMessage("");
    if (newPassword !== confirmPassword) {
      setPasswordError("Mật khẩu nhập lại chưa khớp.");
      return;
    }
    setSavingPassword(true);
    try {
      await changePassword(currentPassword, newPassword);
      setCurrentPassword(""); setNewPassword(""); setConfirmPassword("");
      setPasswordMessage("Đã đổi mật khẩu.");
    } catch (error) {
      setPasswordError(error.message);
    } finally {
      setSavingPassword(false);
    }
  };

  return (
    <div className="container narrow account-page">
      <h1 className="page-title">Tài khoản</h1>
      <section className="account-card account-profile">
        <span className="account-avatar" aria-hidden="true">{user.full_name.trim().split(/\s+/).map((word) => word[0]).slice(-2).join("").toLocaleUpperCase("vi-VN")}</span>
        <div><h2>{user.full_name}</h2><p>{user.email}</p><p>{user.role === "admin" ? "Quản trị" : "Khách hàng"}</p>
        {summary && <p className="muted">Thành viên từ {new Date(summary.member_since).toLocaleDateString("vi-VN")}</p>}</div>
      </section>
      {summaryError ? <p role="alert" className="notice notice--error">{summaryError}</p> : !summary ? <Loading /> : <>
        <section className="account-card" aria-label="Số liệu cá nhân">
          <div className="account-stats">{[["bookings","Vé đã đặt"],["paid","Đã thanh toán"],["watched","Đã xem"],["total_spent","Tổng chi tiêu"],["comments","Bình luận"],["ratings","Phim đã chấm"]].map(([key,label]) => <div key={key}><strong>{key === "total_spent" ? money(summary.stats[key]) : summary.stats[key]}</strong><span>{label}</span></div>)}</div>
          {summary.favorite_genre && <p>Thể loại bạn hay xem: {summary.favorite_genre}</p>}
        </section>
      </>}
      <section className="account-card"><h2>Vé gần đây</h2><Link to="/ve-cua-toi">Xem tất cả</Link>
        {ticketsError ? <p role="alert">{ticketsError}</p> : !tickets ? <Loading /> : !tickets.length ? <p>Bạn chưa có vé nào.</p> : tickets.map((ticket) => <article className="account-activity" key={ticket.id}>
          <Link to={`/phim/${ticket.movie.id}`}>{ticket.movie.title}</Link><p>{fullDateTime(ticket.showtime.start_time)}</p><p>Ghế: {ticket.seats.join(", ") || "Không còn ghế giữ chỗ"} · {bookingLabels[ticket.status]}</p>
        </article>)}
      </section>
      {summary && <div className="account-grid">
        <section className="account-card"><h2>Bình luận gần đây</h2>{!summary.recent_comments.length ? <p>Bạn chưa có bình luận nào.</p> : summary.recent_comments.map((comment) => <article className="account-activity" key={comment.id}>
          <Link to={`/phim/${comment.movie_id}`}>{comment.movie_title}</Link><p>{comment.content}</p><small>{fullDateTime(comment.created_at)} {comment.is_anonymous && " · Ẩn danh"} {comment.effective_negative && " · Tiêu cực"} {comment.hidden && " · Đã bị ẩn"}</small>
        </article>)}</section>
        <section className="account-card"><h2>Điểm đã chấm</h2>{!summary.ratings.length ? <p>Bạn chưa chấm điểm phim nào.</p> : summary.ratings.map((rating) => <article className="account-activity" key={rating.movie_id}>
          <Link to={`/phim/${rating.movie_id}`}>{rating.movie_title}</Link><p>{rating.stars}/10 · {fullDateTime(rating.updated_at)}</p>
        </article>)}</section>
      </div>}
      <h2>Cài đặt tài khoản</h2>
      <div className="account-grid">
        <section className="account-card">
          <h2>Thông tin cá nhân</h2>
          <p className="muted">Email: {user.email}</p>
          <form className="account-form" onSubmit={submitProfile}>
            <label className="field">Họ tên
              <input value={fullName} onChange={(event) => setFullName(event.target.value)}
                minLength="2" maxLength="100" required />
            </label>
            {profileError && <p className="notice notice--error" role="alert">{profileError}</p>}
            {profileMessage && <p className="notice notice--ok" role="status">{profileMessage}</p>}
            <button className="btn btn--primary" type="submit" disabled={savingProfile}>
              {savingProfile ? "Đang lưu..." : "Lưu họ tên"}
            </button>
          </form>
        </section>

        <section className="account-card">
          <h2>Đổi mật khẩu</h2>
          <form className="account-form" onSubmit={submitPassword}>
            <label className="field">Mật khẩu hiện tại
              <input type="password" value={currentPassword}
                onChange={(event) => setCurrentPassword(event.target.value)} required />
            </label>
            <label className="field">Mật khẩu mới
              <input type="password" value={newPassword} onChange={(event) => setNewPassword(event.target.value)}
                minLength="6" maxLength="100" required />
            </label>
            <label className="field">Nhập lại mật khẩu mới
              <input type="password" value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)} minLength="6" maxLength="100" required />
            </label>
            {passwordError && <p className="notice notice--error" role="alert">{passwordError}</p>}
            {passwordMessage && <p className="notice notice--ok" role="status">{passwordMessage}</p>}
            <button className="btn btn--primary" type="submit" disabled={savingPassword}>
              {savingPassword ? "Đang đổi..." : "Đổi mật khẩu"}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
