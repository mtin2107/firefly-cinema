import { API_URL, MEMBERSHIP } from "../config";
export const avatarSrc = url => url?.startsWith("/uploads/") ? `${API_URL}${url}` : url;
export const initials = (name = "") => name.trim().split(/\s+/).map(w => w[0]).slice(-2).join("").toLocaleUpperCase("vi-VN");
export function membership(spent) {
  const tier = [...MEMBERSHIP].reverse().find(t => spent >= t.threshold) || MEMBERSHIP[0];
  const next = MEMBERSHIP.find(t => t.threshold > spent);
  return {
    ...tier,
    next,
    progress: next ? Math.min(100, Math.max(0, (spent - tier.threshold) / (next.threshold - tier.threshold) * 100)) : 100
  };
}
export function ageAllowed(birthDate, rating, onDate) {
  const minimum = {
    T13: 13,
    T16: 16,
    T18: 18
  }[rating] || 0;
  if (!birthDate || !minimum) return true;
  const [by, bm, bd] = birthDate.slice(0, 10).split("-").map(Number);
  // Mock dùng ISO có múi giờ; lấy ngày suất chiếu theo cùng giờ địa phương
  // như lịch chiếu, tránh cắt ngày UTC ở các suất sau nửa đêm.
  const showtime = new Date(onDate);
  const y = showtime.getFullYear(), m = showtime.getMonth() + 1, d = showtime.getDate();
  return y - by - Number(m < bm || m === bm && d < bd) >= minimum;
}
export function ageNotice(user, movie, start) {
  if (user?.role === "admin" || movie.age_rating === "P") return "";
  if (!user?.birth_date) return `Nhân viên sẽ kiểm tra giấy tờ tùy thân tại rạp với phim ${movie.age_rating}.`;
  return ageAllowed(user.birth_date, movie.age_rating, start) ? "" : `Bạn chưa đủ ${movie.age_rating.slice(1)} tuổi để xem phim ${movie.age_rating}.`;
}
export function validateProfile(birth_date, gender) {
  const today = new Date();
  const end = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  if (birth_date != null) {
    const parsed = new Date(`${birth_date}T00:00:00`);
    const valid = typeof birth_date === "string" && /^\d{4}-\d{2}-\d{2}$/.test(birth_date)
      && !Number.isNaN(parsed.getTime()) && birth_date >= "1900-01-01" && birth_date <= end
      && parsed.getFullYear() === Number(birth_date.slice(0, 4))
      && parsed.getMonth() + 1 === Number(birth_date.slice(5, 7))
      && parsed.getDate() === Number(birth_date.slice(8, 10));
    if (!valid) throw new Error("Ngày sinh phải từ 01/01/1900 đến hôm nay.");
  }
  if (gender != null && !["male", "female", "unspecified"].includes(gender)) throw new Error("Giới tính không hợp lệ.");
}
