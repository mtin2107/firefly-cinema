import { SITE_NAME } from "../config";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer__inner">
        <p className="logo logo--small">{SITE_NAME}</p>
        <p>Website đặt vé xem phim trực tuyến tích hợp mô hình học sâu phân loại bình luận tiêu cực.</p>
        <p className="muted">Sản phẩm khóa luận tốt nghiệp. Phim và dữ liệu trên trang là hư cấu.</p>
      </div>
    </footer>
  );
}
