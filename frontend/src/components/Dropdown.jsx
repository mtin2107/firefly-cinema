// Menu thả xuống: máy tính thì rê chuột để mở, điện thoại thì bấm để mở/đóng.
import { useRef } from "react";
const canHover = () => window.matchMedia?.("(hover: hover) and (min-width: 1101px)").matches;

export default function Dropdown({ id, label, openId, setOpenId, align = "left", wide = false, children }) {
  const open = openId === id;
  const triggerRef = useRef(null);
  return (
    <div className="dd" onKeyDown={(event) => {
      if (event.key === "Escape" && open) {
        setOpenId(null);
        triggerRef.current?.focus();
      }
    }}
      onMouseEnter={() => canHover() && setOpenId(id)}
      onMouseLeave={() => canHover() && setOpenId(null)}>
      <button ref={triggerRef} type="button" className={`dd__btn${open ? " dd__btn--open" : ""}`}
        aria-expanded={open} aria-controls={`dd-${id}`}
        onClick={() => setOpenId(open && !canHover() ? null : id)}>
        <span className="dd__label">{label}</span>
        <svg className="dd__chevron" width="12" height="12" viewBox="0 0 12 12" aria-hidden="true">
          <path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </button>
      {open && (
        <div id={`dd-${id}`} className={`dd__panel dd__panel--${align}${wide ? " dd__panel--wide" : ""}`}>
          {children}
        </div>
      )}
    </div>
  );
}
