// Gọi backend FastAPI thật. Mỗi hàm ở đây khớp 1 endpoint trong backend/app/routers.
import { request } from "./http";

export const realApi = {
  auth: {
    register: (payload) => request("/api/auth/register", { method: "POST", body: payload }),
    login: (payload) => request("/api/auth/login", { method: "POST", body: payload }),
    me: () => request("/api/auth/me"),
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
  },
  comments: {
    list: (movieId) => request(`/api/movies/${movieId}/comments`),
    create: (movieId, content) =>
      request(`/api/movies/${movieId}/comments`, { method: "POST", body: { content } }),
  },
  admin: {
    comments: (label) => request(`/api/admin/comments${label ? `?label=${label}` : ""}`),
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
