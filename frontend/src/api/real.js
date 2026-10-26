// Gọi backend FastAPI thật. Mỗi hàm ở đây khớp 1 endpoint trong backend/app/routers.
import { ApiError, request, tokenStore } from "./http";
import { API_URL } from "../config";

async function download(path) {
  const headers = {};
  const token = tokenStore.get();
  if (token) headers.Authorization = `Bearer ${token}`;
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, { headers });
  } catch {
    throw new ApiError(`Không kết nối được máy chủ. Kiểm tra backend đã chạy ở ${API_URL} chưa.`, 0);
  }
  if (!response.ok) {
    const data = await response.json().catch(() => null);
    throw new ApiError(typeof data?.detail === "string" ? data.detail : "Không thể tải file CSV.", response.status);
  }
  return response.blob();
}

export const realApi = {
  chat: {
    send: (messages) => request("/api/chat", { method: "POST", body: { messages } }),
  },
  auth: {
    register: (payload) => request("/api/auth/register", { method: "POST", body: payload }),
    login: (payload) => request("/api/auth/login", { method: "POST", body: payload }),
    changeEmail: (payload) => request("/api/auth/me/email", { method: "POST", body: payload }),
    putAvatar: (payload) => request("/api/auth/me/avatar", { method: "PUT", body: payload }),
    deleteAvatar: () => request("/api/auth/me/avatar", { method: "DELETE" }),
    meSummary: () => request("/api/auth/me/summary"),
    me: () => request("/api/auth/me"),
    updateMe: (payload) => request("/api/auth/me", { method: "PATCH", body: payload }),
    changePassword: (payload) => request("/api/auth/change-password", { method: "POST", body: payload }),
  },
  movies: {
    // filters: { status, genre, country, year, year_before, age_rating, format, collection, q } — bỏ trống trường nào thì không lọc trường đó
    list: (filters = {}) => {
      const params = new URLSearchParams(Object.entries(filters).filter(([, v]) => v !== undefined && v !== ""));
      return request(`/api/movies${params.toString() ? `?${params}` : ""}`);
    },
    get: (id) => request(`/api/movies/${id}`),
    showtimes: (id) => request(`/api/movies/${id}/showtimes`),
  },
  showtimes: {
    get: (id) => request(`/api/showtimes/${id}`),
  },
  bookings: {
    create: (payload) => request("/api/bookings", { method: "POST", body: payload }),
    mine: () => request("/api/bookings/me"),
    remove: (id) => request(`/api/bookings/${id}`, { method: "DELETE" }),
    claimTransfer: (id) => request(`/api/bookings/${id}/transfer-claim`, { method: "POST" }),
  },
  ratings: {
    mine: (id) => request(`/api/movies/${id}/my-rating`),
    set: (id, stars) => request(`/api/movies/${id}/rating`, { method: "PUT", body: { stars } }),
    remove: (id) => request(`/api/movies/${id}/rating`, { method: "DELETE" }),
  },
  comments: {
    list: (movieId) => request(`/api/movies/${movieId}/comments`),
    create: (movieId, payload) =>
      request(`/api/movies/${movieId}/comments`, { method: "POST", body: payload }),
    remove: (id) => request(`/api/comments/${id}`, { method: "DELETE" }),
  },
  admin: {
    meSummary: () => request("/api/admin/me/summary"),
    dashboard: (days = 30) => request(`/api/admin/dashboard?days=${days}`),
    checkin: {
      get: (code) => request(`/api/admin/checkin/${encodeURIComponent(code.trim())}`),
      confirm: (code) => request(`/api/admin/checkin/${encodeURIComponent(code.trim())}`, { method: "POST" }),
    },
    sentiment: (days = 30) => request(`/api/admin/sentiment?days=${days}`),
    trailers: {
      upload: (file) => request("/api/admin/trailers", { method: "POST", body: file, raw: true }),
    },
    posters: {
      upload: (payload) => request("/api/admin/posters", { method: "POST", body: payload }),
    },
    predict: (text) => request("/api/admin/predict", { method: "POST", body: { text } }),
    bookings: {
      list: (filters = {}) => {
        const params = new URLSearchParams(Object.entries(filters).filter(([, value]) => value !== undefined && value !== ""));
        return request(`/api/admin/bookings${params.toString() ? `?${params}` : ""}`);
      },
      confirm: (id) => request(`/api/admin/bookings/${id}/confirm`, { method: "POST" }),
      reject: (id) => request(`/api/admin/bookings/${id}/reject`, { method: "POST" }),
    },
    comments: {
      list: (filters = {}) => {
        const params = new URLSearchParams(Object.entries(filters).filter(([, value]) => value !== undefined && value !== ""));
        return request(`/api/admin/comments${params.toString() ? `?${params}` : ""}`);
      },
      update: (id, payload) => request(`/api/admin/comments/${id}`, { method: "PATCH", body: payload }),
      stats: () => request("/api/admin/comments/stats"),
      exportCsv: () => download("/api/admin/comments/export.csv"),
    },
    movies: {
      list: () => request("/api/admin/movies"),
      create: (payload) => request("/api/admin/movies", { method: "POST", body: payload }),
      update: (id, payload) => request(`/api/admin/movies/${id}`, { method: "PUT", body: payload }),
      remove: (id) => request(`/api/admin/movies/${id}`, { method: "DELETE" }),
    },
    showtimes: {
      list: (filters = {}) => {
        const params = new URLSearchParams(Object.entries(filters).filter(([, value]) => value !== undefined && value !== ""));
        return request(`/api/admin/showtimes${params.toString() ? `?${params}` : ""}`);
      },
      create: (payload) => request("/api/admin/showtimes", { method: "POST", body: payload }),
      update: (id, payload) => request(`/api/admin/showtimes/${id}`, { method: "PUT", body: payload }),
      remove: (id) => request(`/api/admin/showtimes/${id}`, { method: "DELETE" }),
    },
  },
};
