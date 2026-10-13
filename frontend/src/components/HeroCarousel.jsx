import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import Poster from "./Poster";
import AgeBadge from "./AgeBadge";
import FireflyField from "./FireflyField";
import { duration } from "../utils/format";
import {
  gsap, useGSAP, SplitText, EASE, carouselSlot, ringOffset, wrapIndex, useReducedMotion, useFlipNavigate,
} from "../utils/motion";

const AUTOPLAY_S = 6;
const SWIPE_PX = 40;

// Bảng hiệu rạp với băng chuyền poster 3D: phim giữa nổi lên, hai bên lùi sâu.
export default function HeroCarousel({ movies }) {
  const n = movies.length;
  const [i, setI] = useState(0);
  const m = movies[i];
  const root = useRef(null);
  const slots = useRef([]);
  const titleRef = useRef(null);
  const syncTimer = useRef(null);
  const paused = useRef({ hover: false, focus: false, user: false });
  const [userPaused, setUserPaused] = useState(false);
  const swipe = useRef({ x: null, moved: false });
  const reduced = useReducedMotion();
  const go = useFlipNavigate();

  const next = () => setI((k) => wrapIndex(k + 1, n));
  const prev = () => setI((k) => wrapIndex(k - 1, n));

  // Xếp poster lên vòng cung; tween nối tiếp từ vị trí hiện tại nên bấm liên tục không giật
  useGSAP(() => {
    const els = slots.current.filter(Boolean);
    if (reduced) { // bỏ hẳn 3D, CSS chỉ còn hiện poster đang chọn
      gsap.killTweensOf(els);
      gsap.set(els, { clearProps: "transform,opacity,visibility,zIndex" });
      return;
    }
    const depth = window.matchMedia("(max-width: 767px)").matches ? 0.5 : 1;
    slots.current.forEach((el, k) => {
      if (!el) return;
      const { zIndex, ...pose } = carouselSlot(ringOffset(k, i, n), depth);
      gsap.set(el, { zIndex });
      gsap.to(el, { ...pose, duration: 0.9, ease: EASE.out, overwrite: "auto" });
    });
  }, { dependencies: [i, n, reduced], scope: root });

  // Tên phim bật sáng từng ký tự như bảng hiệu
  useGSAP(() => {
    if (reduced || !titleRef.current) return;
    const split = SplitText.create(titleRef.current, { type: "words,chars", charsClass: "hero3d__char" });
    gsap.timeline()
      .from(split.chars, { opacity: 0.08, duration: 0.01, stagger: { each: 0.035, from: "random" } })
      .fromTo(split.chars, { textShadow: "0 0 0px rgba(255,199,44,0)" },
        { textShadow: "0 0 18px rgba(255,199,44,.6)", duration: 0.35, yoyo: true, repeat: 1 }, ">-0.1");
    return () => split.revert();
  }, { dependencies: [i, reduced], scope: root, revertOnUpdate: true });

  // Tự chuyển phim; dừng khi người dùng bấm Tạm dừng, rê chuột, focus trong hero hoặc tab bị ẩn
  useEffect(() => {
    if (reduced || n < 2) return;
    const dc = gsap.delayedCall(AUTOPLAY_S, next);
    const sync = () => {
      const { hover, focus, user } = paused.current;
      const stop = user || hover || focus || document.hidden;
      if (stop) dc.pause(); else dc.resume();
    };
    sync();
    document.addEventListener("visibilitychange", sync);
    syncTimer.current = sync;
    return () => { dc.kill(); syncTimer.current = null; document.removeEventListener("visibilitychange", sync); };
  }, [i, n, reduced]); // eslint-disable-line react-hooks/exhaustive-deps

  const setPaused = (key, value) => { paused.current[key] = value; syncTimer.current?.(); };
  const toggleUserPause = () => { setPaused("user", !userPaused); setUserPaused(!userPaused); };

  const onKey = (e) => {
    if (e.key === "ArrowRight") { e.preventDefault(); next(); }
    if (e.key === "ArrowLeft") { e.preventDefault(); prev(); }
  };
  const onPointerDown = (e) => { swipe.current = { x: e.clientX, moved: false }; };
  const onPointerUp = (e) => {
    const dx = swipe.current.x === null ? 0 : e.clientX - swipe.current.x;
    swipe.current.x = null;
    if (Math.abs(dx) < SWIPE_PX) return;
    swipe.current.moved = true;
    if (dx < 0) next(); else prev();
  };
  const activeSlot = () => slots.current[i];
  const onSlotClick = (e, k, movie) => {
    if (swipe.current.moved) { e.preventDefault(); swipe.current.moved = false; return; }
    if (k !== i) { e.preventDefault(); setI(k); return; }
    go(e, `/phim/${movie.id}`, movie, e.currentTarget);
  };

  return (
    <section className="marquee hero3d" ref={root} aria-roledescription="carousel" aria-label="Phim nổi bật"
      onMouseEnter={() => setPaused("hover", true)} onMouseLeave={() => setPaused("hover", false)}
      onFocus={() => setPaused("focus", true)}
      onBlur={(e) => { if (!e.currentTarget.contains(e.relatedTarget)) setPaused("focus", false); }}
      onKeyDown={onKey}>
      <FireflyField />
      <div className="marquee__text">
        <p className="marquee__kicker">Được khán giả chấm cao nhất tuần này</p>
        <h1 className="marquee__title" ref={titleRef} key={m.id}>{m.title}</h1>
        <p className="marquee__meta">
          <AgeBadge rating={m.age_rating} />
          <span>{m.genre}</span>
          <span>{duration(m.duration_min)}</span>
          <span className="score">★ {m.score}</span>
        </p>
        <p className="marquee__desc">{m.description}</p>
        <div className="marquee__actions">
          <Link className="btn btn--primary btn--lg" to={`/phim/${m.id}#lich-chieu`} state={{ intro: m }}
            onClick={(e) => go(e, `/phim/${m.id}#lich-chieu`, m, activeSlot())}>Đặt vé</Link>
          <Link className="btn btn--ghost btn--lg" to={`/phim/${m.id}`} state={{ intro: m }}
            onClick={(e) => go(e, `/phim/${m.id}`, m, activeSlot())}>Xem chi tiết</Link>
        </div>
        {n > 1 && (
          <div className="hero3d__nav">
            <button type="button" className="hero3d__btn" aria-label="Phim trước" onClick={prev}>‹</button>
            <span className="hero3d__count" aria-live="polite">
              <span className="sr-only">Phim {i + 1} trên {n}: {m.title}</span>
              <span aria-hidden="true">{String(i + 1).padStart(2, "0")} / {String(n).padStart(2, "0")}</span>
            </span>
            <button type="button" className="hero3d__btn" aria-label="Phim sau" onClick={next}>›</button>
            {!reduced && (
              <button type="button" className="hero3d__pause" onClick={toggleUserPause}
                aria-label={userPaused ? "Tiếp tục tự chuyển phim" : "Tạm dừng tự chuyển phim"}>
                <span aria-hidden="true">{userPaused ? "▶" : "❚❚"}</span>
                {userPaused ? "Tiếp tục" : "Tạm dừng"}
              </button>
            )}
          </div>
        )}
      </div>
      <div className="hero3d__stage" onPointerDown={onPointerDown} onPointerUp={onPointerUp}
        onPointerCancel={() => { swipe.current.x = null; }}>
        {movies.map((mv, k) => (
          <Link key={mv.id} to={`/phim/${mv.id}`} state={{ intro: mv }} draggable="false"
            className={`hero3d__slot${k === i ? " hero3d__slot--active" : ""}`}
            ref={(el) => { slots.current[k] = el; }}
            tabIndex={k === i ? 0 : -1} aria-hidden={k !== i || undefined}
            onClick={(e) => onSlotClick(e, k, mv)}>
            <Poster movie={mv} size="lg" />
          </Link>
        ))}
      </div>
    </section>
  );
}
