import { SITE_NAME, CONTACT } from "../config";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer__inner">
        <div><p className="logo logo--small">{SITE_NAME}</p>
        <p>Website đặt vé xem phim trực tuyến tích hợp mô hình học sâu phân loại bình luận tiêu cực.</p>
        <p className="muted">Sản phẩm khóa luận tốt nghiệp. Phim và dữ liệu trên trang là hư cấu.</p></div>
        <section><h2>Liên hệ</h2><p>{CONTACT.name} — {CONTACT.description}</p>
          <p>Email: <a href={`mailto:${CONTACT.email}`} aria-label="Gửi email liên hệ">{CONTACT.email}</a></p>
          <p>Điện thoại: <a href={CONTACT.phoneHref} aria-label="Gọi điện thoại liên hệ">{CONTACT.phone}</a></p>
        </section>
      </div>
    </footer>
  );
}
