import { useEffect, useRef } from "react";
import { prefersReduced } from "../utils/motion";

const SLOW_FRAME_MS = 40;   // khung chậm hơn mức này liên tục thì giảm số đốm
const SLOW_FRAMES = 30;
const BURST_COUNT = 24;
const BURST_LIFE_MS = 900;

const rand = (a, b) => a + Math.random() * (b - a);
const makeFly = () => ({ x: Math.random(), y: Math.random(), r: rand(1, 2.8), vx: rand(-1, 1) * 0.00012,
  vy: rand(-1, 1) * 0.00012, phase: rand(0, Math.PI * 2), speed: rand(0.0012, 0.003) });

// Đom đóm trôi trên nền (canvas 2D). burstAt = { x, y, key } (x, y theo tỉ lệ 0–1): đổi key thì bung một đợt.
export default function FireflyField({ count = 30, className = "", burstAt }) {
  const canvasRef = useRef(null);
  const state = useRef({ flies: [], sparks: [] });

  useEffect(() => {
    if (prefersReduced()) return;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");
    const s = state.current;
    s.flies = Array.from({ length: count }, makeFly);
    let w = 0, h = 0, raf = 0, visible = true, last = performance.now(), slow = 0;

    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      w = canvas.clientWidth; h = canvas.clientHeight;
      canvas.width = w * dpr; canvas.height = h * dpr;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    };
    const glow = (x, y, r, a) => {
      const g = ctx.createRadialGradient(x, y, 0, x, y, r * 4);
      g.addColorStop(0, `rgba(255,243,196,${a})`);
      g.addColorStop(0.35, `rgba(255,199,44,${a * 0.55})`);
      g.addColorStop(1, "rgba(255,199,44,0)");
      ctx.fillStyle = g;
      ctx.beginPath(); ctx.arc(x, y, r * 4, 0, Math.PI * 2); ctx.fill();
    };
    const frame = (now) => {
      const dt = Math.min(now - last, 64); last = now;
      slow = dt > SLOW_FRAME_MS ? slow + 1 : 0;
      if (slow > SLOW_FRAMES && s.flies.length > 8) { s.flies.length = Math.floor(s.flies.length / 2); slow = 0; }
      ctx.clearRect(0, 0, w, h);
      for (const f of s.flies) {
        f.x = (f.x + f.vx * dt + 1) % 1; f.y = (f.y + f.vy * dt + 1) % 1;
        glow(f.x * w, f.y * h, f.r, 0.25 + 0.75 * (0.5 + 0.5 * Math.sin(now * f.speed + f.phase)));
      }
      s.sparks = s.sparks.filter((p) => now - p.born < BURST_LIFE_MS);
      for (const p of s.sparks) {
        const t = (now - p.born) / BURST_LIFE_MS;
        glow(p.x + p.vx * t, p.y + p.vy * t - 20 * t * t, p.r, 1 - t);
      }
      const idle = !s.flies.length && !s.sparks.length; // canvas chỉ dùng để bung: nghỉ khi hết tia
      raf = visible && !document.hidden && !idle ? requestAnimationFrame(frame) : 0;
    };
    const start = () => { if (!raf && visible && !document.hidden) { last = performance.now(); raf = requestAnimationFrame(frame); } };

    resize();
    const ro = new ResizeObserver(resize); ro.observe(canvas);
    const io = new IntersectionObserver(([e]) => { visible = e.isIntersecting; start(); }); io.observe(canvas);
    document.addEventListener("visibilitychange", start);
    s.start = start;
    s.size = () => ({ w, h });
    start();
    return () => {
      cancelAnimationFrame(raf); ro.disconnect(); io.disconnect();
      document.removeEventListener("visibilitychange", start);
      s.start = null;
    };
  }, [count]);

  useEffect(() => {
    const s = state.current;
    if (!burstAt || !s.start) return;
    const { w, h } = s.size();
    const born = performance.now();
    for (let i = 0; i < BURST_COUNT; i++) {
      const a = rand(0, Math.PI * 2), d = rand(40, 140);
      s.sparks.push({ x: burstAt.x * w, y: burstAt.y * h, vx: Math.cos(a) * d, vy: Math.sin(a) * d, r: rand(1.2, 2.6), born });
    }
    s.start();
  }, [burstAt?.key]); // eslint-disable-line react-hooks/exhaustive-deps

  return <canvas ref={canvasRef} className={`fireflies ${className}`.trim()} aria-hidden="true" />;
}
