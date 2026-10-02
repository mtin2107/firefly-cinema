// Toàn bộ giao diện chỉ import { api } từ file này.
// Đổi VITE_USE_MOCK trong .env để chuyển giữa dữ liệu giả và backend thật.
import { USE_MOCK } from "../config";
import { realApi } from "./real";
import { mockApi } from "./mock";

export const api = USE_MOCK ? mockApi : realApi;
export { ApiError, tokenStore } from "./http";
