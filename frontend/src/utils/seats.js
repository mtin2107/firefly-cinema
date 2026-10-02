// Quy tắc sơ đồ ghế — PHẢI giống backend/app/seats.py
export const ROWS = ["A", "B", "C", "D", "E", "F", "G", "H"];
export const COLS = 12;
export const VIP_ROWS = ["F", "G", "H"];
export const VIP_SURCHARGE = 20000;
export const MAX_SEATS_PER_BOOKING = 8;

export const isVip = (seat) => VIP_ROWS.includes(seat[0]);
export const seatPrice = (seat, basePrice) => basePrice + (isVip(seat) ? VIP_SURCHARGE : 0);
export const totalPrice = (seats, basePrice) => seats.reduce((s, x) => s + seatPrice(x, basePrice), 0);

export const sortSeats = (seats) =>
  [...seats].sort((a, b) => a[0].localeCompare(b[0]) || Number(a.slice(1)) - Number(b.slice(1)));
