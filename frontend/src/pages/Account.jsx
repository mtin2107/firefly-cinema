import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function Account() {
  const { user, updateProfile, changePassword } = useAuth();
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
