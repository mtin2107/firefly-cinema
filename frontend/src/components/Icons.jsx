// Một nguồn SVG dùng chung cho menu, thẻ và số liệu tài khoản.
const shapes = {
  user: <><circle cx="12" cy="8" r="4" /><path d="M4 21c1-4 4-6 8-6s7 2 8 6" /></>,
  ticket: <><path d="M3 4h18v4a2 2 0 0 0 0 4v4H3v-4a2 2 0 0 0 0-4Z" /><path d="M14 4v12" strokeDasharray="2 2" /></>,
  overview: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="11" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="18" width="7" height="3" rx="1" /></>,
  checkin: <><path d="M8 3H3v5m13-5h5v5M3 16v5h5m13-5v5h-5M7 12l3 3 7-7" /></>,
  tickets: <><path d="M5 3h16v4M5 3v3M2 8h17v4a2 2 0 0 0 0 4v4H2v-4a2 2 0 0 0 0-4Z" /><path d="M13 8v12" strokeDasharray="2 2" /></>,
  film: <><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M7 3v18M17 3v18M3 8h4m-4 8h4M17 8h4m-4 8h4" /></>,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M3 10h18M8 3v4M16 3v4M8 14h2m4 0h2m-8 4h2" /></>,
  moderation: <><path d="M4 4h16v12H9l-5 4Z" /><path d="m8 10 3 3 5-6" /></>,
  compare: <><path d="M7 3v18m10-18v18M3 7h8M13 17h8" /><circle cx="7" cy="7" r="2" /><circle cx="17" cy="17" r="2" /></>,
  chart: <><path d="M3 3v18h18M7 16v-5m5 5V6m5 10v-8" /></>,
  logout: <><path d="M9 4H4v16h5M10 12h11m-4-4 4 4-4 4" /></>,
  watched: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m10 9 5 3-5 3Z" /></>,
  comment: <path d="M4 5h16v11H8l-4 4Z" />,
  star: <path d="m12 3 2.7 5.6 6.1.9-4.4 4.3 1 6.1L12 17l-5.4 2.9 1-6.1L3.2 9.5l6.1-.9Z" fill="currentColor" />,
  bell: <><path d="M6 8a6 6 0 0 1 12 0c0 7 3 8 3 8H3s3-1 3-8M10 20a2 2 0 0 0 4 0" /></>,
  policy: <><path d="M6 3h9l4 4v14H6Z" /><path d="M15 3v5h4M9 11h7M9 15h7" /></>,
  camera: <><path d="M4 8h3l2-3h6l2 3h3v11H4Z" /><circle cx="12" cy="13" r="3.5" /></>,
  email: <><rect x="3" y="5" width="18" height="14" rx="2" /><path d="m3 7 9 6 9-6" /></>,
  lock: <><rect x="5" y="11" width="14" height="10" rx="2" /><path d="M8 11V8a4 4 0 0 1 8 0v3" /></>,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  location: <><path d="M19 10c0 5-7 11-7 11S5 15 5 10a7 7 0 0 1 14 0Z" /><circle cx="12" cy="10" r="2" /></>,
  upload: <><path d="M12 16V3m-5 5 5-5 5 5M4 16v5h16v-5" /></>,
};

export default function Icon({ name, size = 20, className = "" }) {
  return <svg className={`account-icon ${className}`} data-icon={name} width={size} height={size}
    viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"
    strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" focusable="false">{shapes[name]}</svg>;
}

export function Medal({ level }) {
  const colors = [["#a8692c", "#e7c48f", "#2a1a06"], ["#9aa1a8", "#e5e8eb", "#2b2f33"], ["#d9a520", "#f3dc8f", "#3a2a00"]];
  const [fill, stroke, star] = colors[Math.min(level, colors.length - 1)];
  return <svg width="34" height="34" viewBox="0 0 40 40" aria-hidden="true" focusable="false">
    <circle cx="20" cy="20" r="17" fill={fill} stroke={stroke} strokeWidth="1.5" />
    <path d="m20 10 3 6.2 6.8 1-4.9 4.8 1.2 6.8-6.1-3.2-6.1 3.2 1.2-6.8-4.9-4.8 6.8-1Z" fill={star} />
  </svg>;
}
