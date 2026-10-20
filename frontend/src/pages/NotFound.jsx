import { usePageTitle } from "../utils/pageTitle";
import { Link } from "react-router-dom";
export default function NotFound() {
  usePageTitle("Không tìm thấy trang");
  return (
    <div className="container state">
      <h1 className="page-title">Không tìm thấy trang</h1>
      <p className="muted">Đường dẫn này không tồn tại hoặc đã bị gỡ.</p>
      <Link className="btn btn--primary" to="/">Về trang chủ</Link>
    </div>
  );
}
