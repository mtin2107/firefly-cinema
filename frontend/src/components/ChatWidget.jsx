import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api";
import { useAuth } from "../context/AuthContext";

const SAMPLES = ["Tối nay có phim gì?", "Gợi ý phim hài đang chiếu", "Ghế VIP giá bao nhiêu?"];
const GREETING = { role: "assistant", content: "Xin chào! Tôi có thể tư vấn phim, lịch chiếu và giá vé Firefly Cinema." };

// The launcher behaves like AssistiveTouch: drag with a pointer, tap to toggle.
// Only side/relative vertical position is saved; no chat content is persisted.
const POSITION_KEY = "firefly_chat_launcher_position_v1";
const EDGE = 10;
const DRAG_THRESHOLD = 8;
const clamp = (value, min, max) => Math.min(Math.max(value, min), Math.max(min, max));
const viewportSize = () => ({ width: window.innerWidth, height: window.innerHeight });

function savedPosition() {
  try {
    const value = JSON.parse(localStorage.getItem(POSITION_KEY) || "null");
    if ((value?.side === "left" || value?.side === "right") &&
        typeof value.fraction === "number" && Number.isFinite(value.fraction)) {
      return { side: value.side, fraction: clamp(value.fraction, 0, 1) };
    }
  } catch { /* Storage can be blocked; use the default location. */ }
  return { side: "right", fraction: 0.6 };
}

export default function ChatWidget() {
  const { user, checking } = useAuth();
  const [open, setOpen] = useState(false);
  const [viewport, setViewport] = useState(viewportSize);
  const [dock, setDock] = useState(savedPosition);
  const [dragPoint, setDragPoint] = useState(null);
  const drag = useRef(null);
  const suppressPointerClick = useRef(false);
  const [history, setHistory] = useState([GREETING]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [movies, setMovies] = useState([]);
  const field = useRef(null);
  const toggle = useRef(null);
  const end = useRef(null);
  const sessionVersion = useRef(0);
  const buttonSize = viewport.width <= 600 ? 46 : 52;
  const freeY = Math.max(0, viewport.height - buttonSize - 2 * EDGE);
  const launcher = dragPoint || {
    x: dock.side === "left" ? EDGE : Math.max(EDGE, viewport.width - buttonSize - EDGE),
    y: EDGE + dock.fraction * freeY,
  };
  const panelWidth = Math.max(0, Math.min(380, viewport.width - 2 * EDGE));
  const roomAbove = Math.max(0, launcher.y - 12 - EDGE);
  const roomBelow = Math.max(0, viewport.height - (launcher.y + buttonSize) - 12 - EDGE);
  const panelAbove = roomAbove >= roomBelow;
  const panelHeight = Math.min(540, panelAbove ? roomAbove : roomBelow);
  const panelLeft = clamp(
    launcher.x + buttonSize / 2 <= viewport.width / 2 ? EDGE : viewport.width - panelWidth - EDGE,
    EDGE,
    viewport.width - panelWidth - EDGE,
  );
  const panelTop = panelAbove ? launcher.y - 12 - panelHeight : launcher.y + buttonSize + 12;

  useEffect(() => {
    const onResize = () => setViewport(viewportSize());
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  function pointWithinViewport(x, y) {
    return {
      x: clamp(x, EDGE, window.innerWidth - buttonSize - EDGE),
      y: clamp(y, EDGE, window.innerHeight - buttonSize - EDGE),
    };
  }

  function onPointerDown(event) {
    if (event.pointerType === "mouse" && event.button !== 0) return;
    suppressPointerClick.current = false;
    drag.current = {
      id: event.pointerId, startX: event.clientX, startY: event.clientY,
      launcherX: launcher.x, launcherY: launcher.y, moved: false,
    };
    event.currentTarget.setPointerCapture?.(event.pointerId);
  }

  function onPointerMove(event) {
    const current = drag.current;
    if (!current || current.id !== event.pointerId) return;
    const dx = event.clientX - current.startX;
    const dy = event.clientY - current.startY;
    if (!current.moved && Math.hypot(dx, dy) < DRAG_THRESHOLD) return;
    current.moved = true;
    setDragPoint(pointWithinViewport(current.launcherX + dx, current.launcherY + dy));
  }

  function onPointerUp(event) {
    const current = drag.current;
    if (!current || current.id !== event.pointerId) return;
    const dx = event.clientX - current.startX;
    const dy = event.clientY - current.startY;
    if (current.moved || Math.hypot(dx, dy) >= DRAG_THRESHOLD) {
      const finish = pointWithinViewport(current.launcherX + dx, current.launcherY + dy);
      const nextDock = {
        side: finish.x + buttonSize / 2 <= window.innerWidth / 2 ? "left" : "right",
        fraction: clamp((finish.y - EDGE) / Math.max(1, window.innerHeight - buttonSize - 2 * EDGE), 0, 1),
      };
      setDock(nextDock);
      try { localStorage.setItem(POSITION_KEY, JSON.stringify(nextDock)); }
      catch { /* Remember for this page only if storage is unavailable. */ }
      suppressPointerClick.current = true;
    }
    setDragPoint(null);
    drag.current = null;
  }

  function onPointerCancel() {
    drag.current = null;
    setDragPoint(null);
  }

  useEffect(() => { if (open && user) field.current?.focus(); }, [open, user]);
  useEffect(() => { if (open) end.current?.scrollIntoView({ block: "end" }); }, [history, busy, open, error]);
  useEffect(() => {
    const closeWithEscape = (event) => {
      if (event.key === "Escape" && open) { setOpen(false); toggle.current?.focus(); }
    };
    window.addEventListener("keydown", closeWithEscape);
    return () => window.removeEventListener("keydown", closeWithEscape);
  }, [open]);
  useEffect(() => { sessionVersion.current += 1; setHistory([GREETING]); setMovies([]); setInput(""); setError(""); setBusy(false); }, [user?.id]);

  async function send(question) {
    const text = question.trim();
    if (!text || busy || !user || user.role === "admin") return;
    if (text.length > 500) { setError("Tin nhắn tối đa 500 ký tự."); return; }
    const version = sessionVersion.current;
    const next = [...history, { role: "user", content: text }];
    setInput(""); setHistory(next); setBusy(true); setError(""); setMovies([]);
    try {
      const messages = next.filter((entry) => entry !== GREETING).slice(-10);
      const result = await api.chat.send(messages);
      if (version !== sessionVersion.current) return;
      setHistory((prev) => [...prev, { role: "assistant", content: result.reply }]);
      setMovies(Array.isArray(result.movies) ? result.movies.slice(0, 5) : []);
    } catch (reason) {
      if (version !== sessionVersion.current) return;
      setError(reason?.message || "Không gửi được tin nhắn. Hãy thử lại.");
    } finally { if (version === sessionVersion.current) setBusy(false); }
  }

  return (
    <div className={`chat-widget${dragPoint ? " chat-widget--dragging" : ""}`}
      style={{ left: launcher.x, top: launcher.y }}>
      {open && <section className="chat-panel" aria-label="Trợ lý tư vấn phim"
        style={{ left: panelLeft, top: panelTop, width: panelWidth, height: panelHeight }}>
        <header className="chat-panel__header">
          <div><strong>Trợ lý Firefly</strong><span>Tư vấn phim và suất chiếu</span></div>
          <button type="button" className="chat-panel__close" aria-label="Đóng trợ lý"
            onClick={() => { setOpen(false); toggle.current?.focus(); }}>×</button>
        </header>
        <div className="chat-panel__messages" role="log" aria-live="polite">
          {checking ? <p className="chat-panel__notice">Đang kiểm tra đăng nhập...</p>
            : !user ? <p className="chat-panel__notice">Đăng nhập để trò chuyện với trợ lý. <Link to="/dang-nhap" onClick={() => setOpen(false)}>Đăng nhập</Link></p>
              : user.role === "admin" ? <p className="chat-panel__notice">Trợ lý chỉ dành cho khách hàng.</p> : <>
                {history.map((entry, index) => <p key={index}
                  className={`chat-message chat-message--${entry.role}`}>{entry.content}</p>)}
                {history.length === 1 && <div className="chat-panel__samples">{SAMPLES.map((sample) =>
                  <button key={sample} type="button" disabled={busy} onClick={() => send(sample)}>{sample}</button>)}</div>}
                {busy && <p role="status" className="chat-panel__notice">Trợ lý đang trả lời...</p>}
                {error && <p role="alert" className="chat-panel__error">{error}</p>}
                {movies.length > 0 && <div className="chat-panel__links" aria-label="Phim được giới thiệu">
                  {movies.map((movie) => <Link key={movie.id} to={`/phim/${movie.id}`}
                    onClick={() => setOpen(false)}>{movie.title} →</Link>)}</div>}
                <div ref={end}/>
              </>}
        </div>
        {user?.role === "user" && <form className="chat-panel__form"
          onSubmit={(event) => { event.preventDefault(); send(input); }}>
          <label className="chat-panel__label" htmlFor="firefly-chat-input">Câu hỏi</label>
          <div className="chat-panel__form-row">
            <input id="firefly-chat-input" ref={field} value={input} disabled={busy}
              maxLength={500} onChange={(event) => setInput(event.target.value)} placeholder="Hỏi về phim..." />
            <button disabled={busy || !input.trim()} type="submit">Gửi</button>
          </div>
        </form>}
        <small className="chat-panel__privacy">Không nhập thông tin cá nhân vào khung chat.</small>
      </section>}
      <button ref={toggle} type="button" className="chat-widget__toggle"
        aria-label={open ? "Đóng trợ lý" : "Mở trợ lý"} aria-expanded={open}
        title="Kéo để di chuyển, chạm để mở trợ lý"
        onPointerDown={onPointerDown} onPointerMove={onPointerMove}
        onPointerUp={onPointerUp} onPointerCancel={onPointerCancel}
        onClick={(event) => {
          if (suppressPointerClick.current && event.detail !== 0) {
            suppressPointerClick.current = false;
            return;
          }
          setOpen((old) => !old);
        }}>{open ? "×" : "✦"}</button>
    </div>
  );
}
