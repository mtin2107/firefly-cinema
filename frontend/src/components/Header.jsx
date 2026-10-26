import { api } from "../api";
import { avatarSrc, initials } from "../utils/account";
import { useEffect, useRef, useState } from "react";
import { Link, NavLink, useLocation, useNavigate, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { SITE_NAME, USE_MOCK } from "../config";
import { FILTERS, exploreLink } from "../utils/taxonomy";
import Dropdown from "./Dropdown";
import SearchBox from "./SearchBox";

// Các menu thả xuống, lấy từ utils/taxonomy.js
const MENUS = FILTERS.filter((f) => f.key !== "trang-thai");

export default function Header() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [params] = useSearchParams();
  const [openId, setOpenId] = useState(null);
  const [mobileOpen, setMobileOpen] = useState(false);
  const ref = useRef(null);
  const [held, setHeld] = useState(null);
  useEffect(() => {
    let active = true;
    if (user && openId === "account") api.bookings.mine().then(rows => { if (active) setHeld(rows.filter(b => b.status === "held").length); }).catch(() => { if (active) setHeld(null); });
    return () => { active = false; };
  }, [openId, user?.id]);

  // Đổi trang thì đóng hết menu
  useEffect(() => { setOpenId(null); setMobileOpen(false); }, [location.pathname, location.search]);

  // Bấm ra ngoài hoặc nhấn Esc thì đóng menu
  useEffect(() => {
    const onDown = (e) => { if (!ref.current?.contains(e.target)) setOpenId(null); };
    const onKey = (e) => { if (e.key === "Escape") setOpenId(null); };
    document.addEventListener("mousedown", onDown);
    document.addEventListener("keydown", onKey);
    return () => { document.removeEventListener("mousedown", onDown); document.removeEventListener("keydown", onKey); };
  }, []);

  const onExplore = location.pathname === "/kham-pha";
  const isActive = (key, slug) => onExplore && params.get(key) === slug;
  const statusLink = (slug, label) => (
    <Link to={exploreLink("trang-thai", slug)}
      className={`nav__link${isActive("trang-thai", slug) ? " active" : ""}`}>{label}</Link>
  );

  return (
    <header className="header" ref={ref}>
      <div className="container header__inner">
        <Link to="/" className="logo" aria-label={`${SITE_NAME} - trang chủ`}>
          <span className="logo__mark" aria-hidden="true" />
          {SITE_NAME}
        </Link>

        <button type="button" className="menu-toggle" aria-expanded={mobileOpen} aria-controls="main-nav"
          onClick={() => setMobileOpen((v) => !v)}>
          {mobileOpen ? "Đóng" : "Menu"}
        </button>

        <nav id="main-nav" className={`nav${mobileOpen ? " nav--open" : ""}`} aria-label="Điều hướng chính">
          {statusLink("dang-chieu", "Đang chiếu")}
          {statusLink("sap-chieu", "Sắp chiếu")}
          {MENUS.map((menu) => (
            <Dropdown key={menu.key} id={menu.key} label={menu.label} openId={openId} setOpenId={setOpenId}
              wide={menu.options.length > 5}>
              <ul className="dd__list">
                {menu.options.map((o) => (
                  <li key={o.slug}>
                    <Link to={exploreLink(menu.key, o.slug)}
                      className={isActive(menu.key, o.slug) ? "active" : undefined}>{o.label}</Link>
                  </li>
                ))}
              </ul>
            </Dropdown>
          ))}
        </nav>

        <div className="header__account">
          <SearchBox />
          {USE_MOCK && <span className="mock-flag" title="Đang dùng dữ liệu giả, chưa nối backend">Dữ liệu mẫu</span>}
          {user ? (
            <Dropdown id="account" label={user.full_name} openId={openId} setOpenId={setOpenId} align="right">
              <div className={`account-menu${user.role === "admin" ? " account-menu--admin" : ""}`}>
                <div className="account-menu__profile">
                  <span className="account-avatar" aria-hidden="true">{user.avatar_url ? <img src={avatarSrc(user.avatar_url)} alt="" /> : initials(user.full_name)}</span>
                  <div><strong>{user.full_name}</strong><p>{user.email}</p><small>{user.role === "admin" ? "Quản trị viên" : "Khách hàng"}</small></div>
                </div>
                <ul className="dd__list dd__list--single">
                  <li><NavLink to="/tai-khoan"><MenuIcon />Tài khoản của tôi</NavLink></li>
                  <li><NavLink to="/ve-cua-toi"><MenuIcon />Vé của tôi{held !== null && <span className="account-menu__badge">{held}</span>}</NavLink></li>
                </ul>
                {user.role === "admin" && <><h3>Quản trị</h3><ul className="dd__list account-menu__admin">{[
                  ["tong-quan","Tổng quan quản trị"],["soat-ve","Soát vé tại quầy"],["ve","Quản lý vé"],["phim","Quản lý phim"],
                  ["suat-chieu","Quản lý suất chiếu"],["binh-luan","Kiểm duyệt bình luận"],["so-sanh-mo-hinh","So sánh mô hình"],["thong-ke","Thống kê cảm xúc"]
                ].map(([path,label]) => <li key={path}><NavLink to={`/quan-tri/${path}`}><MenuIcon />{label}</NavLink></li>)}</ul></>}
                <div className="account-menu__logout"><button type="button" className="dd__item-btn" onClick={() => { logout(); navigate("/"); }}><MenuIcon />Đăng xuất</button></div>
              </div>
            </Dropdown>
          ) : (
            <>
              <Link className="btn btn--ghost btn--sm" to="/dang-nhap">Đăng nhập</Link>
              <Link className="btn btn--primary btn--sm" to="/dang-ky">Đăng ký</Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}

function MenuIcon() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" aria-hidden="true"><rect x="4" y="4" width="16" height="16" rx="3" /><path d="M8 9h8M8 15h5" /></svg>;
}
