// Đổi tên rạp ở đây nếu muốn
export const SITE_NAME = "Firefly Cinema";

// Đọc từ file .env (xem .env.example)
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const USE_HASH_ROUTER = import.meta.env.VITE_ROUTER === "hash";


export const CONTACT = {
  name: "Lê Minh Tín",
  description: "Sinh viên ngành Khoa học dữ liệu, Trường Đại học Nguyễn Tất Thành",
  email: "2311558892@nttu.edu.vn",
  phone: "0329 711 217",
  phoneHref: "tel:0329711217",
};

export const MEMBERSHIP = [
  { name: "Thành viên", threshold: 0 },
  { name: "Bạc", threshold: 1000000 },
  { name: "Vàng", threshold: 3000000 },
];
