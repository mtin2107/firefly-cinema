// Đổi tên rạp ở đây nếu muốn
export const SITE_NAME = "Firefly Cinema";

// Đọc từ file .env (xem .env.example)
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== "false";
export const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
export const USE_HASH_ROUTER = import.meta.env.VITE_ROUTER === "hash";
