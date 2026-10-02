import { useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { USE_MOCK } from "../config";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const from = location.state?.from;
  const backTo = from ? `${from.pathname}${from.hash ?? ""}` : "/";

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true); setError("");
    try {
      await login(email.trim(), password);
      navigate(backTo, { replace: true });
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="container auth">
      <form className="auth__form" onSubmit={submit}>
        <h1 className="page-title">Đăng nhập</h1>
        {from && <p className="muted">Đăng nhập để đặt vé và viết bình luận.</p>}
        <label className="field">
          <span>Email</span>
          <input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="field">
          <span>Mật khẩu</span>
          <input type="password" required autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error && <p className="notice notice--error" role="alert">{error}</p>}
        <button className="btn btn--primary btn--lg btn--block" disabled={loading}>
          {loading ? "Đang đăng nhập..." : "Đăng nhập"}
        </button>
        <p className="auth__switch">Chưa có tài khoản? <Link to="/dang-ky" state={location.state}>Đăng ký</Link></p>
        {USE_MOCK && (
          <p className="auth__demo muted">
            Tài khoản mẫu: demo@firefly.vn / 123456. Quản trị: admin@firefly.vn / admin123
          </p>
        )}
      </form>
    </div>
  );
}
