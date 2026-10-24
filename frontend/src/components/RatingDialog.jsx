import { useEffect, useId, useRef, useState } from "react";
import StarRating from "./StarRating";
import Poster from "./Poster";
import { api } from "../api";
import { gsap, EASE, MOTION_OK, useReducedMotion } from "../utils/motion";

export default function RatingDialog({ open, movie, stars, busy, notice, onSave, onClose }) {
  const dialogRef = useRef(null);
  const titleId = useId();
  const [summary, setSummary] = useState(movie);
  const [saved, setSaved] = useState(null);
  const ringRef = useRef(null);
  const numberRef = useRef(null);
  const reduced = useReducedMotion();
  const effects = useRef([]);
  const displayedWidths = useRef({});
  const clearEffects = () => {
    effects.current.forEach((effect) => effect.kill()); effects.current = [];
    dialogRef.current?.querySelectorAll(".rating-firefly").forEach((node) => node.remove());
    if (dialogRef.current) {
      gsap.set(dialogRef.current, { clearProps: "transform,opacity" });
      gsap.set(dialogRef.current.querySelectorAll(".star-rating__button"), { clearProps: "transform" });
    }
  };
  const burst = (source, count) => {
    if (!window.matchMedia(MOTION_OK).matches) return;
    effects.current = effects.current.filter((effect) => effect.progress() < 1);
    const root = dialogRef.current, box = root.getBoundingClientRect(), origin = source.getBoundingClientRect();
    for (let i = 0; i < count; i++) {
      const dot = document.createElement("i"); dot.className = "rating-firefly"; dot.setAttribute("aria-hidden", "true");
      dot.style.left = `${origin.left - box.left + origin.width / 2}px`;
      dot.style.top = `${origin.top - box.top + root.scrollTop + origin.height / 2}px`; root.querySelector(".rating-dialog__particles").append(dot);
      const angle = i * Math.PI * 2 / count;
      effects.current.push(gsap.to(dot, { x: Math.cos(angle) * 65, y: Math.sin(angle) * 65 - 20, opacity: 0,
        duration: 0.75, onComplete: () => dot.remove() }));
    }
  };
  useEffect(() => { if (reduced) clearEffects(); return clearEffects; }, [reduced, open]);
  useEffect(() => {
    if (!open) return;
    let active = true;
    api.ratings.mine(movie.id).then((result) => { if (active) setSummary(result); }).catch(() => {});
    return () => { active = false; };
  }, [open, movie.id]);
  useEffect(() => { setSummary(movie); }, [movie]);
  const [draft, setDraft] = useState(stars);
  const [success, setSuccess] = useState(false);
  useEffect(() => {
    const dialog = dialogRef.current;
    if (open && !dialog.open) {
      setDraft(stars);
      displayedWidths.current = {};
      if (numberRef.current) numberRef.current.textContent = "0.0";
      setSuccess(false);
      dialog.showModal();
      if (window.matchMedia(MOTION_OK).matches) effects.current.push(gsap.fromTo(dialog, { y: 25, opacity: 0 }, { y: 0, opacity: 1, duration: 0.3, ease: EASE.out }));
    } else if (!open && dialog.open) dialog.close();
  }, [open, stars]);
  useEffect(() => {
    if (!open) return;
    const end = Number(summary.rating_avg ?? 0);
    const state = { value: Number(numberRef.current?.textContent) || 0 };
    const paint = () => {
      ringRef.current?.style.setProperty("--rating-angle", `${state.value * 36}deg`);
      if (numberRef.current) numberRef.current.textContent = state.value.toFixed(1);
    };
    const bars = [...dialogRef.current.querySelectorAll(".rating-distribution__fill")];
    const targets = bars.map((bar) => Number(bar.dataset.width));
    if (reduced || !window.matchMedia(MOTION_OK).matches) {
      state.value = end; paint();
      bars.forEach((bar, i) => { bar.style.width = `${targets[i]}%`; });
      return;
    }
    const tween = gsap.to(state, { value: end, duration: 0.7, ease: EASE.out, onUpdate: paint });
    const barTweens = bars.map((bar, i) => gsap.fromTo(bar,
      { width: `${displayedWidths.current[i] ?? 0}%` }, { width: `${targets[i]}%`, duration: 0.7, ease: EASE.out,
        onUpdate: () => { displayedWidths.current[i] = parseFloat(bar.style.width); } }));
    return () => { tween.kill(); barTweens.forEach((animation) => animation.kill()); };
  }, [open, summary, reduced]);
  // Leave the confirmation visible and announced before returning to the page.
  useEffect(() => {
    if (!success) return;
    const timer = window.setTimeout(() => dialogRef.current?.close(), 1200);
    return () => window.clearTimeout(timer);
  }, [success]);
  const save = async (value) => {
    if (busy || success) return;
    if (await onSave(value)) { setSaved(value); setSuccess(true); burst(ringRef.current, 18); }
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
    <header className="rating-dialog__header">
      <Poster movie={movie} />
      <div className="rating-dialog__heading"><small>ĐÁNH GIÁ PHIM</small><h2 id={titleId}>{movie.title}</h2>
        <p>{movie.age_rating} · {movie.genre} · {movie.duration_min} phút</p></div>
      <button type="button" className="rating-dialog__close" aria-label="Đóng" disabled={busy} onClick={() => dialogRef.current.close()}>✕</button>
    </header>
    <div className="rating-dialog__body">
      <div className="rating-dialog__summary">
        <div className="rating-ring" ref={ringRef}><div><strong ref={numberRef}>0.0</strong><small>/10</small><span>{summary.rating_count ?? 0} lượt</span></div></div>
        <div className="rating-distribution">{[9, 7, 5, 3, 1].map((low) => {
          const count = (summary.distribution?.[low] ?? 0) + (summary.distribution?.[low + 1] ?? 0);
          return <div className="rating-distribution__row" key={low}><span>{low}–{low + 1}</span><div className="rating-distribution__track"><i className="rating-distribution__fill" data-width={summary.rating_count ? count / summary.rating_count * 100 : 0} /></div><span>{count}</span></div>;
        })}</div>
      </div>
      <h3>Bạn chấm phim này mấy điểm?</h3>
      <StarRating value={draft} onChange={setDraft} disabled={locked} onSelect={(score, button) => {
        if (!window.matchMedia(MOTION_OK).matches) return;
        effects.current.push(gsap.fromTo([...dialogRef.current.querySelectorAll(".star-rating__button")].slice(0, score), { scale: 0.8 }, { scale: 1, duration: 0.4, stagger: 0.03, ease: "back.out(3)" }));
        burst(button, score >= 9 ? 18 : 8);
      }} />
      <p className="rating-dialog__notice" role="status" aria-live="polite">{success && saved != null ? `Đã lưu ${saved} điểm · cảm ơn bạn!` : notice}</p>
      {stars != null && <button type="button" className="btn btn--ghost" disabled={locked} onClick={() => save(null)}>Hủy đánh giá</button>}
    </div>
    <div className="rating-dialog__actions">
      <button type="button" className="btn btn--ghost" disabled={busy} onClick={() => dialogRef.current.close()}>Đóng</button>
      <button type="button" className="btn btn--primary" disabled={!draft || locked} onClick={() => save(draft)}>★ Lưu đánh giá</button>
    </div>
    <div className="rating-dialog__particles" aria-hidden="true" />
  </dialog>;
}
