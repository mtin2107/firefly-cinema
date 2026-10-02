import { useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";

// Nút kính lúp: bấm vào thì ô tìm kiếm phủ lên thanh header
export default function SearchBox() {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const inputRef = useRef(null);

  useEffect(() => { if (open) { setText(params.get("q") ?? ""); inputRef.current?.focus(); } }, [open]); // eslint-disable-line

  const submit = (e) => {
    e.preventDefault();
    const q = text.trim();
    if (!q) return;
    setOpen(false);
    navigate(`/kham-pha?q=${encodeURIComponent(q)}`);
  };

  const icon = (
    <svg width="18" height="18" viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="11" cy="11" r="7" fill="none" stroke="currentColor" strokeWidth="2" />
      <path d="m20 20-4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );

  if (!open) {
    return (
      <button type="button" className="search-btn" aria-label="Tìm kiếm phim" onClick={() => setOpen(true)}>
        {icon}
      </button>
    );
  }
  return (
    <form className="search" role="search" onSubmit={submit}
      onKeyDown={(e) => { if (e.key === "Escape") setOpen(false); }}>
      <span className="search__icon">{icon}</span>
      <label htmlFor="search-input" className="sr-only">Tìm kiếm phim</label>
      <input id="search-input" ref={inputRef} type="search" value={text} autoComplete="off"
        placeholder="Tìm kiếm phim, không cần gõ dấu" onChange={(e) => setText(e.target.value)} />
      <button type="submit" className="btn btn--primary btn--sm">Tìm</button>
      <button type="button" className="btn btn--ghost btn--sm" onClick={() => setOpen(false)}>Đóng</button>
    </form>
  );
}
