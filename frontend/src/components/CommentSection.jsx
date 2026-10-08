import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import { relativeTime } from "../utils/format";
import { Loading, ErrorState } from "./StateViews";

function CommentItem({ comment }) {
  const [revealed, setRevealed] = useState(false);
  const hidden = comment.effective_negative && !revealed;
  return (
    <li className={`comment${comment.effective_negative ? " comment--negative" : ""}`}>
      <div className="comment__head">
        <span className="comment__author">{comment.user_name}</span>
        <span className="muted">{relativeTime(comment.created_at)}</span>
      </div>
      {hidden ? (
        <p className="comment__hidden">
          Bình luận này đã được ẩn vì mô hình đánh giá có nội dung tiêu cực.{" "}
          <button className="link-btn" onClick={() => setRevealed(true)}>Vẫn xem</button>
        </p>
      ) : (
        <p className="comment__content">{comment.content}</p>
      )}
    </li>
  );
}

export default function CommentSection({ movieId }) {
  const { user } = useAuth();
  const location = useLocation();
  const [comments, setComments] = useState(null);
  const [error, setError] = useState("");
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [notice, setNotice] = useState(null);

  const load = () => {
    setError("");
    api.comments.list(movieId).then(setComments).catch((e) => setError(e.message));
  };
  useEffect(load, [movieId]);

  const submit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setSending(true); setNotice(null);
    try {
      const created = await api.comments.create(movieId, text);
      setComments((list) => [created, ...(list ?? [])]);
      setText("");
      setNotice(created.effective_negative
        ? { type: "warn", text: "Đã đăng. Hệ thống đánh giá bình luận này mang tính tiêu cực nên sẽ ẩn mặc định với người xem khác." }
        : { type: "ok", text: "Đã đăng bình luận." });
    } catch (err) {
      setNotice({ type: "error", text: err.message });
    } finally {
      setSending(false);
    }
  };

  return (
    <section className="comments" aria-labelledby="comments-title">
      <h2 id="comments-title" className="section-title">Bình luận</h2>

      {user ? (
        <form className="comment-form" onSubmit={submit}>
          <label htmlFor="comment-text" className="sr-only">Viết bình luận</label>
          <textarea id="comment-text" rows={3} maxLength={1000} value={text}
            placeholder="Bạn thấy phim thế nào?" onChange={(e) => setText(e.target.value)} />
          <div className="comment-form__foot">
            <span className="muted">{text.length}/1000</span>
            <button className="btn btn--primary" disabled={sending || !text.trim()}>
              {sending ? "Đang gửi..." : "Gửi bình luận"}
            </button>
          </div>
          {notice && <p className={`notice notice--${notice.type}`} role="status">{notice.text}</p>}
        </form>
      ) : (
        <p className="comment-login">
          <Link to="/dang-nhap" state={{ from: location }}>Đăng nhập</Link> để viết bình luận.
        </p>
      )}

      {error ? <ErrorState message={error} onRetry={load} />
        : comments === null ? <Loading label="Đang tải bình luận..." />
        : comments.length === 0 ? <p className="muted">Chưa có bình luận nào. Hãy là người đầu tiên.</p>
        : <ul className="comment-list">{comments.map((c) => <CommentItem key={c.id} comment={c} />)}</ul>}
    </section>
  );
}
