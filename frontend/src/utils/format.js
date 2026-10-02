export const money = (n) => `${Number(n).toLocaleString("vi-VN")} đ`;

const WEEKDAYS = ["Chủ nhật", "Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7"];

export const toDate = (iso) => new Date(iso);
export const timeOf = (iso) =>
  toDate(iso).toLocaleTimeString("vi-VN", { hour: "2-digit", minute: "2-digit", hour12: false });
export const dayKey = (iso) => {
  const d = toDate(iso);
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};
export const dayLabel = (key) => {
  const [y, m, d] = key.split("-").map(Number);
  const date = new Date(y, m - 1, d);
  const isToday = date.toDateString() === new Date().toDateString();
  return { weekday: isToday ? "Hôm nay" : WEEKDAYS[date.getDay()], date: `${d}/${m}` };
};
export const fullDateTime = (iso) => {
  const d = toDate(iso);
  return `${timeOf(iso)}, ${WEEKDAYS[d.getDay()]} ${d.getDate()}/${d.getMonth() + 1}/${d.getFullYear()}`;
};
export const relativeTime = (iso) => {
  const diff = (Date.now() - toDate(iso).getTime()) / 1000;
  if (diff < 60) return "vừa xong";
  if (diff < 3600) return `${Math.floor(diff / 60)} phút trước`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} giờ trước`;
  return `${Math.floor(diff / 86400)} ngày trước`;
};
export const duration = (min) => `${Math.floor(min / 60)} giờ ${min % 60} phút`;
