// Chuyển động dùng chung (T18): đăng ký plugin GSAP một lần, hằng easing/thời lượng, hàm tính vị trí.
import gsap from "gsap";
import { ScrollTrigger } from "gsap/ScrollTrigger";
import { SplitText } from "gsap/SplitText";
import { useGSAP } from "@gsap/react";
import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

gsap.registerPlugin(useGSAP, ScrollTrigger, SplitText);

// Khớp token --ease-out / --ease-in-out / --dur-* trong global.css
export const EASE = { out: "expo.out", inOut: "power3.inOut", back: "back.out(1.6)" };
export const DUR = { fast: 0.15, base: 0.3, slow: 0.6 };
export const MOTION_OK = "(prefers-reduced-motion: no-preference)";
export const REDUCED = "(prefers-reduced-motion: reduce)";
export const FINE_POINTER = "(hover: hover) and (pointer: fine)";

export const prefersReduced = () => window.matchMedia?.(REDUCED).matches ?? false;

// Theo dõi "giảm chuyển động" cả khi người dùng đổi lúc trang đang mở; hiệu ứng nào phụ thuộc giá trị này sẽ tự dọn/chạy lại
export function useReducedMotion() {
  const [reduced, setReduced] = useState(prefersReduced);
  useEffect(() => {
    const mq = window.matchMedia?.(REDUCED);
    if (!mq) return;
    const sync = () => setReduced(mq.matches);
    sync();
    mq.addEventListener("change", sync);
    return () => mq.removeEventListener("change", sync);
  }, []);
  return reduced;
}

export const wrapIndex = (i, n) => ((i % n) + n) % n;

// Khoảng cách ngắn nhất trên vòng tròn n phần tử, từ active tới k (âm = bên trái)
export function ringOffset(k, active, n) {
  const half = Math.floor(n / 2);
  return wrapIndex(k - active + half, n) - half;
}

// Vị trí poster nguồn, gửi qua Link state để trang chi tiết làm FLIP
export function posterRect(el) {
  const target = el?.classList?.contains("poster") ? el : el?.querySelector?.(".poster") ?? el;
  const r = target?.getBoundingClientRect?.();
  return r ? { x: r.left, y: r.top, w: r.width, h: r.height } : null;
}

// Biến đổi đưa phần tử đích (to) về chỗ nguồn (from) — tween ngược về 0, transformOrigin "0 0"
export function flipFrom(from, to) {
  return { x: from.x - to.x, y: from.y - to.y, scaleX: from.w / to.w, scaleY: from.h / to.h };
}

// Vị trí ô trên vòng cung băng chuyền; offset 0 là ô giữa, depth < 1 trên màn hẹp
export function carouselSlot(offset, depth = 1) {
  const a = Math.abs(offset);
  return {
    xPercent: offset * 44 * (depth < 1 ? 0.8 : 1),
    z: -a * 160 * depth,
    rotationY: -offset * 28 * depth,
    opacity: a > 2 ? 0 : 1 - a * 0.35,
    zIndex: 10 - a,
  };
}

// Điều hướng sang trang phim kèm vị trí poster nguồn; Ctrl/Cmd/chuột giữa vẫn mở tab mới như Link thường
export function useFlipNavigate() {
  const navigate = useNavigate();
  return (e, to, movie, sourceEl) => {
    if (e.defaultPrevented || e.button !== 0 || e.metaKey || e.ctrlKey || e.shiftKey || e.altKey) return;
    e.preventDefault();
    navigate(to, { state: { intro: movie, from: posterRect(sourceEl) } });
  };
}

// Lưới phim hiện lần lượt khi cuộn tới; chạy lại khi deps đổi (đổi tab, đổi bộ lọc)
export function useGridReveal(ref, deps) {
  useGSAP(() => {
    const mm = gsap.matchMedia();
    mm.add(MOTION_OK, () => {
      const cards = gsap.utils.toArray(ref.current?.children ?? []);
      if (!cards.length) return;
      gsap.set(cards, { autoAlpha: 0, y: 28 });
      ScrollTrigger.batch(cards, {
        start: "top 95%", once: true,
        onEnter: (batch) => gsap.to(batch, { autoAlpha: 1, y: 0, stagger: 0.06, duration: DUR.slow, ease: EASE.out, overwrite: true }),
      });
    });
    return () => mm.revert();
  }, { dependencies: deps, revertOnUpdate: true });
}

export { gsap, useGSAP, ScrollTrigger, SplitText };
