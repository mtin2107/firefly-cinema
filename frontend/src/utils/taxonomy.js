// Danh mục cho menu Thể loại / Quốc gia / Năm phát hành / Chủ đề và trang lọc phim.
// Thêm mục mới: chỉ cần thêm chữ vào mảng tương ứng (trùng đúng chữ trong dữ liệu phim).

// "Hành động" -> "hanh-dong" để dùng trên đường dẫn
export const slugify = (s) =>
  s.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/g, "d").replace(/Đ/g, "D")
    .toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");

const make = (labels) => labels.map((label) => ({ label, slug: slugify(label) }));

export const GENRE_LABELS = [
  "Hành động", "Tình cảm", "Hài hước",
  "Cổ trang", "Tâm lý", "Hình sự",
  "Chiến tranh", "Thể thao", "Võ thuật",
  "Viễn tưởng", "Phiêu lưu", "Khoa học",
  "Kinh dị", "Âm nhạc", "Thần thoại",
  "Tài liệu", "Gia đình", "Chính kịch",
  "Bí ẩn", "Học đường", "Kinh điển", "Anime & Hoạt hình",
];

export const COUNTRY_LABELS = [
  "Việt Nam", "Hàn Quốc", "Nhật Bản", "Trung Quốc", "Thái Lan", "Mỹ", "Anh", "Pháp", "Ấn Độ",
];

export const FORMAT_LABELS = ["Phụ đề", "Lồng tiếng"];
export const AGE_RATINGS = ["P", "T13", "T16", "T18"];

export const STATUSES = [
  { label: "Đang chiếu", slug: "dang-chieu", value: "now_showing" },
  { label: "Sắp chiếu", slug: "sap-chieu", value: "coming_soon" },
  { label: "Đã chiếu", slug: "da-chieu", value: "ended" },
];

// Thứ tự giống menu tham khảo (đọc theo hàng, 3 cột)
export const GENRES = [
  ...make(GENRE_LABELS.slice(0, -1)),
  // Hai mục đặc biệt: 18+ lọc theo độ tuổi, không phải thể loại
  { label: "Phim 18+", slug: "phim-18", query: { age_rating: "T18" } },
  ...make(GENRE_LABELS.slice(-1)),
];

export const COUNTRIES = make(COUNTRY_LABELS);

export const YEARS = [
  { label: "2026", slug: "2026", query: { year: 2026 } },
  { label: "2025", slug: "2025", query: { year: 2025 } },
  { label: "2024", slug: "2024", query: { year: 2024 } },
  { label: "Trước 2024", slug: "truoc-2024", query: { year_before: 2024 } },
];

// Chủ đề = các bộ sưu tập phim, tính từ dữ liệu thật của rạp
export const COLLECTIONS = [
  { label: "Phim hot trong tuần", slug: "hot-trong-tuan", query: { collection: "hot_week" } },
  { label: "Phim hot trong tháng", slug: "hot-trong-thang", query: { collection: "hot_month" } },
  { label: "Top bình luận", slug: "top-binh-luan", query: { collection: "top_comments" } },
  { label: "Đánh giá cao", slug: "danh-gia-cao", query: { collection: "top_rated" } },
  { label: "Phim lồng tiếng", slug: "long-tieng", query: { format: "Lồng tiếng" } },
  { label: "Phim phụ đề", slug: "phu-de", query: { format: "Phụ đề" } },
];

// key = tên tham số trên đường dẫn, ví dụ /kham-pha?the-loai=hanh-dong&quoc-gia=han-quoc
export const FILTERS = [
  { key: "trang-thai", label: "Trạng thái", options: STATUSES, toQuery: (o) => ({ status: o.value }) },
  { key: "the-loai", label: "Thể loại", options: GENRES, toQuery: (o) => o.query ?? { genre: o.label } },
  { key: "quoc-gia", label: "Quốc gia", options: COUNTRIES, toQuery: (o) => ({ country: o.label }) },
  { key: "nam", label: "Năm phát hành", options: YEARS, toQuery: (o) => o.query },
  { key: "chu-de", label: "Chủ đề", options: COLLECTIONS, toQuery: (o) => o.query },
];

/** Đọc ?the-loai=...&nam=... thành danh sách bộ lọc đang chọn và object gửi cho API */
export function readFilters(searchParams) {
  const active = [];
  let query = {};
  FILTERS.forEach((f) => {
    const option = f.options.find((o) => o.slug === searchParams.get(f.key));
    if (option) {
      active.push({ filter: f, option });
      query = { ...query, ...f.toQuery(option) };
    }
  });
  const q = (searchParams.get("q") ?? "").trim();
  if (q) query = { ...query, q };
  return { active, query, q };
}

export const exploreLink = (key, slug) => `/kham-pha?${key}=${slug}`;


export function effectiveStatus(movie, today = new Date()) {
  const day = typeof today === "string" ? today : `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}-${String(today.getDate()).padStart(2, "0")}`;
  return movie.status === "coming_soon" && movie.release_date <= day ? "now_showing" : movie.status;
}
