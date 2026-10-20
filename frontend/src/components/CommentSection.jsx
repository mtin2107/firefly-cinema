import StarRating from "./StarRating";
import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import { relativeTime } from "../utils/format";
import { Loading, ErrorState } from "./StateViews";

function CommentItem({ comment, onRemove }) {
  const [revealed, setRevealed] = useState(false);
  const hidden = comment.effective_negative && !revealed;
  return (
    <li className={`comment${comment.effective_negative ? " comment--negative" : ""}`}>
      <div className="comment__head">
        <span className="comment__author">{comment.user_name}</span>
        {comment.author_stars != null && <span aria-label={`${comment.author_stars} sao`}>{"★".repeat(comment.author_stars)}</span>}
        {comment.can_delete && <button type="button" className="link-btn" onClick={() => onRemove(comment.id)}>Xóa bình luận</button>}
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

export default function CommentSection({ movieId, allowed = true, stars, ratingBusy, onSendingChange, version, onCreated }) {
  const { user } = useAuth();
  const location = useLocation();
  const [comments, setComments] = useState(null);
  const [error, setError] = useState("");
  const [draftStars, setDraftStars] = useState(stars);
  useEffect(() => { setDraftStars(stars); }, [stars, movieId, user]);
  const [anonymous, setAnonymous] = useState(false);
  const [text, setText] = useState("");
  const [sending, setSending] = useState(false);
  const [notice, setNotice] = useState(null);

  const load = () => {
    setError("");
    api.comments.list(movieId).then(setComments).catch((e) => setError(e.message));
  };
  useEffect(load, [movieId, version, user]);
  const remove = async (id) => {
    if (!window.confirm("Xóa bình luận này?")) return;
    try { await api.comments.remove(id); setComments((list) => list.filter((c) => c.id !== id)); }
    catch (e) { setNotice({ type: "error", text: e.message }); }
  };

  const submit = async (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    setSending(true); onSendingChange?.(true); setNotice(null);
    try {
      const created = await api.comments.create(movieId, { content: text, is_anonymous: anonymous, ...(draftStars != null ? { stars: draftStars } : {}) });
      setComments((list) => [created, ...(list ?? [])]);
      setText("");
      setDraftStars(created.author_stars);
      onCreated?.(created);
      setNotice(created.effective_negative
        ? { type: "warn", text: "Đã đăng. Hệ thống đánh giá bình luận này mang tính tiêu cực nên sẽ ẩn mặc định với người xem khác." }
        : { type: "ok", text: "Đã đăng bình luận." });
    } catch (err) {
      setNotice({ type: "error", text: err.message });
    } finally {
      setSending(false); onSendingChange?.(false);
    }
  };

  return (
    <section className="comments" aria-labelledby="comments-title">
      <h2 id="comments-title" className="section-title">Bình luận</h2>

      {!allowed ? <p className="muted">Phim sắp chiếu chưa nhận bình luận hoặc chấm sao.</p> : user ? (
        <form className="comment-form" onSubmit={submit}>
          <StarRating value={draftStars} onChange={setDraftStars} disabled={ratingBusy || sending} />
          <p className="muted">Sao chỉ được lưu khi gửi bình luận. Bỏ chọn để giữ nguyên điểm hiện tại.</p>
          <label className="anonymous-option"><input type="checkbox" checked={anonymous} onChange={(e) => setAnonymous(e.target.checked)} /> Bình luận ẩn danh</label>
          <label htmlFor="comment-text" className="sr-only">Viết bình luận</label>
          <textarea id="comment-text" rows={3} maxLength={1000} value={text}
            placeholder="Bạn thấy phim thế nào?" onChange={(e) => setText(e.target.value)} />
          <div className="comment-form__foot">
            <span className="muted">{text.length}/1000</span>
            <button className="btn btn--primary" disabled={sending || ratingBusy || !text.trim()}>
              {sending ? "Đang gửi..." : "Gửi bình luận"}
            </button>
          </div>

        </form>
      ) : (
        <p className="comment-login">
          <Link to="/dang-nhap" state={{ from: location }}>Đăng nhập</Link> để viết bình luận.
        </p>
      )}

      {notice && <p className={`notice notice--${notice.type}`} role="status">{notice.text}</p>}
      {error ? <ErrorState message={error} onRetry={load} />
        : comments === null ? <Loading label="Đang tải bình luận..." />
        : comments.length === 0 ? <p className="muted">Chưa có bình luận nào. Hãy là người đầu tiên.</p>
        : <ul className="comment-list">{comments.map((c) => <CommentItem key={c.id} comment={c} onRemove={remove} />)}</ul>}
    </section>
  );
}
