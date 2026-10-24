import { API_URL } from "../config";

const TOKEN_KEY = "firefly_token";

export const tokenStore = {
  get() {
    try { return localStorage.getItem(TOKEN_KEY); } catch { return null; }
  },
  set(token) {
    try {
      if (token) localStorage.setItem(TOKEN_KEY, token);
      else localStorage.removeItem(TOKEN_KEY);
    } catch { /* trình duyệt chặn storage */ }
  },
};

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.status = status;
  }
}

export async function request(path, { method = "GET", body, raw = false } = {}) {
  const headers = { "Content-Type": raw ? body.type : "application/json" };
  const token = tokenStore.get();
  if (token) headers.Authorization = `Bearer ${token}`;

  let res;
  try {
    res = await fetch(`${API_URL}${path}`, {
      method,
      headers,
      body: raw ? body : body ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(`Không kết nối được máy chủ. Kiểm tra backend đã chạy ở ${API_URL} chưa.`, 0);
  }

  const data = await res.json().catch(() => null);
  if (!res.ok) {
    const detail = data?.detail;
    const message = typeof detail === "string" ? detail : "Dữ liệu gửi lên không hợp lệ.";
    throw new ApiError(message, res.status);
  }
  return data;
}
