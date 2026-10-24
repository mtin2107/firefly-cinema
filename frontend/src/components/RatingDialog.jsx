import { useEffect, useId, useRef, useState } from "react";
import StarRating from "./StarRating";
import { ratingText } from "../utils/ratings";

export default function RatingDialog({ open, movie, stars, busy, notice, onSave, onClose }) {
  const dialogRef = useRef(null);
  const titleId = useId();
  const [draft, setDraft] = useState(stars);
  const [success, setSuccess] = useState(false);
  useEffect(() => {
    const dialog = dialogRef.current;
    if (open && !dialog.open) {
      setDraft(stars);
      setSuccess(false);
      dialog.showModal();
    } else if (!open && dialog.open) dialog.close();
  }, [open, stars]);
  // Leave the confirmation visible and announced before returning to the page.
  useEffect(() => {
    if (!success) return;
    const timer = window.setTimeout(() => dialogRef.current?.close(), 1000);
    return () => window.clearTimeout(timer);
  }, [success]);
  const save = async (value) => {
    if (busy || success) return;
    if (await onSave(value)) setSuccess(true);
  };
  const locked = busy || success;
  return <dialog ref={dialogRef} className="rating-dialog" aria-labelledby={titleId}
    onKeyDown={(event) => {
      if (event.key !== "Tab") return;
      const buttons = [...event.currentTarget.querySelectorAll("button:not(:disabled)")];
      const first = buttons[0], last = buttons[buttons.length - 1];
      if (!first) { event.preventDefault(); return; }
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault(); last.focus();
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault(); first.focus();
      }
    }}
    onClose={onClose} onClick={(event) => {
      if (event.target !== event.currentTarget) return;
      const rect = event.currentTarget.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) event.currentTarget.close();
    }}>
    <h2 id={titleId}>Đánh giá phim {movie.title}</h2>
    <p className="score">{ratingText(movie)}</p>
    <StarRating value={draft} onChange={setDraft} disabled={locked} />
    <p className="rating-dialog__notice" role="status" aria-live="polite">{notice}</p>
    <div className="rating-dialog__actions">
      <button type="button" className="btn btn--primary" disabled={!draft || locked} onClick={() => save(draft)}>Lưu đánh giá</button>
      {stars != null && <button type="button" className="btn btn--ghost" disabled={locked} onClick={() => save(null)}>Hủy đánh giá</button>}
      <button type="button" className="btn btn--ghost" disabled={busy} onClick={() => dialogRef.current.close()}>Đóng</button>
    </div>
  </dialog>;
}
