import { returnTo } from "../utils/pageTitle";
import { usePageTitle } from "../utils/pageTitle";
import { useEffect, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Register() {
  usePageTitle("Đăng ký");
  const { register, user, checking } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ full_name: "", email: "", password: "", confirm: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  useEffect(() => {
    if (!checking && user) navigate(returnTo(location.state?.from), { replace: true });
  }, [user, checking, navigate, location.state]);

  const submit = async (e) => {
    e.preventDefault();
    if (form.password.length < 6) return setError("Mật khẩu cần ít nhất 6 ký tự.");
    if (form.password !== form.confirm) return setError("Hai mật khẩu chưa khớp nhau.");
    setLoading(true); setError("");
    try {
      await register(form.full_name.trim(), form.email.trim(), form.password);
      const from = location.state?.from;
      navigate(returnTo(from), { replace: true });
    } catch (err) {
      setError(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="container auth">
      <form className="auth__form" onSubmit={submit}>
        <h1 className="page-title">Tạo tài khoản</h1>
        <label className="field">
          <span>Họ và tên</span>
          <input required autoComplete="name" value={form.full_name} onChange={set("full_name")} />
        </label>
        <label className="field">
          <span>Email</span>
          <input type="email" required autoComplete="email" value={form.email} onChange={set("email")} />
        </label>
        <label className="field">
          <span>Mật khẩu</span>
          <input type="password" required autoComplete="new-password" value={form.password} onChange={set("password")} />
        </label>
        <label className="field">
          <span>Nhập lại mật khẩu</span>
          <input type="password" required autoComplete="new-password" value={form.confirm} onChange={set("confirm")} />
        </label>
        {error && <p className="notice notice--error" role="alert">{error}</p>}
        <button className="btn btn--primary btn--lg btn--block" disabled={loading}>
          {loading ? "Đang tạo tài khoản..." : "Tạo tài khoản"}
        </button>
        <p className="auth__switch">Đã có tài khoản? <Link to="/dang-nhap" state={location.state}>Đăng nhập</Link></p>
      </form>
    </div>
  );
}
