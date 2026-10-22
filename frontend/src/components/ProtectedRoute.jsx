import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Loading, ErrorState } from "./StateViews";
import { useEffect } from "react";

export default function ProtectedRoute({ adminOnly = false }) {
  const { user, checking } = useAuth();
  const location = useLocation();
  const blocked = !checking && user && adminOnly && user.role !== "admin";
  useEffect(() => {
    if (blocked) document.title = "Không có quyền truy cập – Firefly Cinema";
  }, [blocked, location.pathname]);
  if (checking) return <Loading />;
  if (!user) return <Navigate to="/dang-nhap" replace state={{ from: location }} />;
  if (adminOnly && user.role !== "admin")
    return <ErrorState message="Trang này chỉ dành cho quản trị viên." />;
  return <Outlet />;
}
