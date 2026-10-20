// ======================================================================
// DỮ LIỆU GIẢ — chỉ dùng khi VITE_USE_MOCK=true (chưa có backend).
// Mọi hàm trả về đúng cấu trúc JSON mà backend FastAPI trả về,
// nên khi chuyển sang backend thật, giao diện không phải sửa gì.
// ======================================================================
import MOVIES from "./movies.json";
import { ApiError } from "./http";
import { ROWS, COLS, totalPrice, MAX_SEATS_PER_BOOKING } from "../utils/seats";
import { AGE_RATINGS, COUNTRY_LABELS, FORMAT_LABELS, GENRE_LABELS } from "../utils/taxonomy";

const DB_KEY = "firefly_mockdb_v5";
const ROOMS = ["Phòng 1", "Phòng 2", "Phòng 3", "Phòng 4"];
const CLEANUP_MINUTES = 15;
const HOLD_CUTOFF_MINUTES = 30;
const HOLD_MINUTES = 15;
const MOCK_BANK = { id: "970436", account: "123456789", name: "FIREFLY CINEMA DEMO" };
const wait = (ms = 250) => new Promise((r) => setTimeout(r, ms));
const clone = (x) => JSON.parse(JSON.stringify(x));
const nowIso = () => new Date().toISOString();
const commentUsage = new Map();

function checkCommentLimit(userId) {
  const now = Date.now();
  const recent = (commentUsage.get(userId) ?? []).filter((value) => now - value < 60000);
  if (recent.length >= 3) throw new ApiError("Bạn bình luận quá nhanh. Hãy thử lại sau ít phút.", 429);
  recent.push(now);
  commentUsage.set(userId, recent);
}

// Bộ lọc từ khóa thay cho PhoBERT khi chạy mock
const NEGATIVE_WORDS = ["dở", "chán", "tệ", "phí tiền", "nhảm", "thất vọng", "rác", "kém", "buồn ngủ", "xàm", "lừa"];
function fakeClassify(text) {
  const t = text.toLowerCase();
  const hit = NEGATIVE_WORDS.some((w) => t.includes(w));
  return { is_negative: hit, negative_score: hit ? 0.87 : 0.08 };
}

const COMMENT_ABBR = {
  ko: "không", k: "không", kh: "không", khg: "không", kg: "không", hok: "không", hong: "không",
  "đc": "được", dc: "được", "đk": "được", dk: "được", j: "gì", vs: "với", mn: "mọi người",
  ng: "người", bt: "bình thường", r: "rồi", z: "vậy", v: "vậy", mik: "mình", mk: "mình",
  trc: "trước", sp: "sản phẩm",
};
function normalizeComment(text) {
  const normalized = text.normalize("NFC").toLowerCase()
    .replace(/([\p{L}\p{N}_])\1{2,}/gu, "$1")
    .replace(/([.,!?;:()\[\]"“”…])/g, " $1 ");
  return normalized.split(/\s+/).filter(Boolean).map((word) => COMMENT_ABBR[word] ?? word).join(" ");
}

function localIso(date, hhmm) {
  const [h, m] = hhmm.split(":").map(Number);
  const d = new Date(date);
  d.setHours(h, m, 0, 0);
  // ISO không có múi giờ, giống backend
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(h)}:${p(m)}:00`;
}

function intervalsOverlap(candidate, existing, movies) {
  if (candidate.room !== existing.room) return false;
  const candidateMovie = movies.find((movie) => movie.id === candidate.movie_id);
  const existingMovie = movies.find((movie) => movie.id === existing.movie_id);
  if (!candidateMovie || !existingMovie) return false;
  const candidateStart = new Date(candidate.start_time).getTime();
  const existingStart = new Date(existing.start_time).getTime();
  const candidateEnd = candidateStart + (candidateMovie.duration_min + CLEANUP_MINUTES) * 60000;
  const existingEnd = existingStart + (existingMovie.duration_min + CLEANUP_MINUTES) * 60000;
  return candidateStart < existingEnd && existingStart < candidateEnd;
}

function buildShowtimes(movies = MOVIES, existing = [], startId = 1) {
  const times = ["09:30", "13:15", "16:00", "19:30", "22:00"];
  const list = [];
  let id = startId;
  const today = new Date();
  const nowShowing = movies.filter((movie) => movie.status === "now_showing");

  const addFirstAvailable = (movie, movieIndex, date, dayIndex, candidateIndexes) => {
    for (const timeIndex of candidateIndexes) {
      const start_time = localIso(date, times[timeIndex]);
      const all = [...existing, ...list];
      if (all.some((item) => item.movie_id === movie.id && item.start_time === start_time)) continue;
      const roomStart = (movieIndex + dayIndex + timeIndex) % ROOMS.length;
      for (let roomStep = 0; roomStep < ROOMS.length; roomStep++) {
        const candidate = {
          id, movie_id: movie.id, start_time,
          room: ROOMS[(roomStart + roomStep) % ROOMS.length],
          price: Number(times[timeIndex].slice(0, 2)) >= 17 ? 95000 : 75000,
        };
        if (all.some((item) => intervalsOverlap(candidate, item, movies))) continue;
        list.push(candidate);
        id += 1;
        return true;
      }
    }
    return false;
  };

  for (let day = 0; day < 5; day++) {
    const date = new Date(today);
    date.setDate(today.getDate() + day);
    const dayKey = localIso(date, "00:00").slice(0, 10);
    const present = new Set([...existing, ...list]
      .filter((item) => item.start_time.slice(0, 10) === dayKey)
      .map((item) => item.movie_id));

    nowShowing.forEach((movie, idx) => {
      if (present.has(movie.id)) return;
      const preferred = (idx + day) % times.length;
      const candidates = times.map((_, step) => (preferred + step) % times.length);
      if (addFirstAvailable(movie, idx, date, day, candidates)) present.add(movie.id);
    });

    nowShowing.forEach((movie, idx) => {
      times.forEach((_, timeIndex) => {
        if ((timeIndex + idx + day) % 2 === 0 || timeIndex === 3) {
          addFirstAvailable(movie, idx, date, day, [timeIndex]);
        }
      });
    });
  }
  return list;
}

function seedBooked(showtimeId) {
  // Một vài ghế đã có người đặt sẵn để sơ đồ trông thật
  const seats = [];
  ROWS.forEach((r, ri) => {
    for (let c = 1; c <= COLS; c++) if ((showtimeId * 7 + ri * 5 + c * 3) % 11 === 0) seats.push(`${r}${c}`);
  });
  return seats;
}

function createDb() {
  const users = [
    { id: 1, full_name: "Quản trị viên", email: "admin@firefly.vn", password: "admin123", role: "admin" },
    { id: 2, full_name: "Nguyễn Văn Demo", email: "demo@firefly.vn", password: "123456", role: "user" },
  ];
  const viewers = Array.from({ length: 6 }, (_, index) => ({
    id: index + 3, full_name: `Khán giả mẫu ${index + 1}`, email: `khan-gia-${index + 1}@firefly.vn`,
    password: Array.from(crypto.getRandomValues(new Uint8Array(24)), (byte) => byte.toString(16).padStart(2, "0")).join(""),
    role: "user",
  }));
  users.push(...viewers);
  // [movie, nội dung, ngày lùi, giờ lùi, duyệt]; đồng bộ demo_comments.json.
  const sample = [
    [1, "Cảnh cuối trên toa tàu đẹp và ấm áp, xem xong chỉ muốn gọi về cho mẹ.", 0, 2, "confirm"],
    [1, "Diễn xuất tự nhiên, câu chuyện gia đình kể nhẹ nhàng mà vẫn xúc động.", 2, 4],
    [1, "Phần hình ảnh rất thơ, riêng đoạn giữa hơi chậm một chút.", 5, 1],
    [1, "Phim dài lê thê, nửa đầu buồn ngủ thật sự, phí tiền vé.", 9, 3],
    [1, "Nhạc nền vừa đủ, không lấn át lời thoại và kết phim có dư âm.", 14, 5],
    [2, "Kịch bản nhảm, hù dọa chỉ dựa vào tiếng động lớn nên rất thất vọng.", 1, 1, "confirm"],
    [2, "Tưởng đáng sợ lắm, ai ngờ mình ngủ ngon được nửa phim, thật tuyệt vời.", 3, 6, "opposite"],
    [2, "Nhân vật xử lý vô lý, đoạn cuối đoán được từ quá sớm.", 6, 2],
    [2, "Âm thanh quá to nhưng không tạo được cảm giác sợ, xem khá mệt.", 10, 7],
    [2, "Poster hấp dẫn hơn nội dung, bỏ phí một ý tưởng có tiềm năng.", 15, 4],
    [3, "Cảnh cứu hộ giữa dòng nước quay rất thật, âm thanh trong rạp nghe đã.", 0, 8],
    [3, "Nhịp phim chắc, các thành viên trong đội đều có vai trò rõ ràng.", 4, 3, "confirm"],
    [3, "Đoạn mở đầu hơi nhiều lời giải thích nhưng về sau cuốn hơn hẳn.", 7, 5],
    [3, "Một vài cảnh kỹ xảo nước còn giả, bù lại diễn xuất rất thuyết phục.", 11, 2],
    [3, "Kết thúc vội và thiếu cảm xúc, mình thấy khá thất vọng.", 16, 6],
    [4, "Con mình cười suốt, chú mèo đáng yêu và màu phim rất tươi.", 1, 5],
    [4, "Một bộ phim gia đình dễ thương, người lớn xem cùng trẻ nhỏ vẫn vui.", 3, 2, "confirm"],
    [4, "Đoạn ở chợ Bến Thành nhiều chi tiết vui, lồng tiếng nghe tự nhiên.", 8, 4],
    [4, "Cốt truyện đơn giản nhưng kể duyên, bé nhà mình muốn xem lại.", 12, 1],
    [4, "Nhạc vui tai, hình ảnh sáng và thông điệp về gia đình rất vừa vặn.", 14, 8],
    [5, "Hài nhạt, cười được đúng hai lần, càng về cuối càng chán.", 2, 3, "confirm"],
    [5, "Đúng là một đêm không ngủ, vì mình cứ chờ mãi xem khi nào phim mới hay.", 4, 7, "opposite"],
    [5, "Các mảng miếng lặp lại, nhân vật nói nhiều mà câu chuyện không tiến lên.", 6, 5],
    [5, "Dàn diễn viên có duyên nhưng kịch bản rời rạc và đoạn kết quá gượng.", 10, 2],
    [5, "Có vài câu thoại vui, xem giải trí cuối tuần cũng tạm ổn.", 13, 6],
    [9, "Nhạc phim hay, đoạn biểu diễn cuối làm mình nổi da gà.", 0, 6],
    [9, "Màu sắc đẹp và tình bạn của nhóm được xây dựng rất chân thành.", 5, 8, "confirm"],
    [9, "Bài hát chính bắt tai nhưng hai bài ở giữa hơi giống nhau.", 7, 1],
    [9, "Nửa đầu chậm và vài đoạn hội thoại dài khiến mình buồn ngủ.", 11, 4],
    [9, "Kết phim trọn vẹn, phần hòa âm ở rạp nghe rất đã.", 16, 2],
  ];
  const comments = sample.map(([movie_id, content, daysAgo, hoursAgo, review], i) => {
    const prediction = fakeClassify(content);
    const createdAt = new Date(Date.now() - (daysAgo * 24 + hoursAgo) * 3600 * 1000);
    const humanLabel = review === "confirm" ? Number(prediction.is_negative)
      : review === "opposite" ? Number(!prediction.is_negative) : null;
    return {
      id: i + 1, movie_id, user_id: 2, content, ...prediction,
      model_name: "phobert_b", model_version: "phobert-B-demo-mock",
      human_label: humanLabel, reviewed_by: humanLabel === null ? null : 1,
      reviewed_at: humanLabel === null ? null : new Date(createdAt.getTime() + 3600000).toISOString(),
      hidden: false, created_at: createdAt.toISOString(),
    };
  });
  const showtimes = buildShowtimes();
  const bookings = [
    { id: 1, user_id: 2, showtime_id: showtimes[0].id, seats: ["A1", "A2"],
      total: totalPrice(["A1", "A2"], showtimes[0].price), status: "paid",
      created_at: new Date(Date.now() - 2 * 86400000).toISOString() },
    { id: 2, user_id: 2, showtime_id: showtimes[1].id, seats: ["A3", "A4"],
      total: totalPrice(["A3", "A4"], showtimes[1].price), status: "pending_verify",
      created_at: new Date(Date.now() - 4 * 60000).toISOString() },
    { id: 3, user_id: 2, showtime_id: showtimes[2].id, seats: [], total: 0, status: "expired",
      created_at: new Date(Date.now() - (HOLD_MINUTES + 1) * 60000).toISOString() },
  ];
  return {
    ratings: MOVIES.filter((m) => ["now_showing", "ended"].includes(m.status)).flatMap((m) =>
      viewers.slice(0, 2 + m.id % 5).map((viewer, index) => ({ movie_id: m.id, user_id: viewer.id, stars: 3 + ((m.id + index) % 3) }))),
    users, movies: clone(MOVIES), comments, bookings, showtimes,
    adminShowtimeIds: [],
    seq: { user: users.length + 1, movie: Math.max(...MOVIES.map((m) => m.id)) + 1, comment: 31, booking: 4, showtime: Math.max(...showtimes.map((item) => item.id), 0) + 1 },
  };
}

function load() {
  try {
    const raw = localStorage.getItem(DB_KEY);
    if (raw) {
      const db = JSON.parse(raw);
      if (!db.movies) db.movies = clone(MOVIES);
      if (!db.showtimes) db.showtimes = buildShowtimes(db.movies);
      if (!db.seq.movie) db.seq.movie = Math.max(...db.movies.map((m) => m.id)) + 1;
      if (!db.adminShowtimeIds) db.adminShowtimeIds = [];
      if (!db.seq.showtime) db.seq.showtime = Math.max(...db.showtimes.map((item) => item.id), 0) + 1;
      db.comments.forEach((comment) => {
        if (!comment.model_name) comment.model_name = "keyword";
        if (!("model_version" in comment)) comment.model_version = null;
        if (!("human_label" in comment)) comment.human_label = null;
        if (!("reviewed_by" in comment)) comment.reviewed_by = null;
        if (!("reviewed_at" in comment)) comment.reviewed_at = null;
        if (!("hidden" in comment)) comment.hidden = false;
      });
      db.bookings.forEach((booking) => {
        if (!booking.status) booking.status = "paid";
      });
      // làm mới suất chiếu mỗi ngày
      if (db.showtimesDay === new Date().toDateString()) {
        const additions = buildShowtimes(db.movies, db.showtimes, db.seq.showtime);
        if (additions.length) {
          db.showtimes.push(...additions);
          db.seq.showtime = Math.max(...db.showtimes.map((item) => item.id), 0) + 1;
          localStorage.setItem(DB_KEY, JSON.stringify(db));
        }
        return db;
      }
      const bookingShowtimeIds = new Set(db.bookings.map((item) => item.showtime_id));
      const retainedShowtimes = db.showtimes.filter((item) =>
        db.adminShowtimeIds.includes(item.id) || bookingShowtimeIds.has(item.id));
      const firstSeedId = Math.max(...retainedShowtimes.map((item) => item.id), 0) + 1;
      db.showtimes = [...retainedShowtimes, ...buildShowtimes(db.movies, retainedShowtimes, firstSeedId)];
      db.seq.showtime = Math.max(...db.showtimes.map((item) => item.id), 0) + 1;
      db.showtimesDay = new Date().toDateString();
      return db;
    }
  } catch { /* bỏ qua */ }
  const db = createDb();
  db.showtimesDay = new Date().toDateString();
  return db;
}
let db = load();
const save = () => { try { localStorage.setItem(DB_KEY, JSON.stringify(db)); } catch { /* bỏ qua */ } };

const publicUser = (u) => ({ id: u.id, full_name: u.full_name, email: u.email, role: u.role });
const tokenFor = (u) => `mock-token-${u.id}`;

function currentUser() {
  let token = null;
  try { token = localStorage.getItem("firefly_token"); } catch { /* */ }
  const id = Number(token?.replace("mock-token-", ""));
  const user = db.users.find((u) => u.id === id);
  if (!user) throw new ApiError("Bạn cần đăng nhập để tiếp tục.", 401);
  return user;
}
const movieById = (id) => {
  const m = db.movies.find((x) => x.id === Number(id));
  if (!m) throw new ApiError("Không tìm thấy phim.", 404);
  return Object.assign(m, ratingSummary(m.id));
};
function ratingSummary(id) {
  const rows = db.ratings.filter((r) => r.movie_id === Number(id));
  return { rating_avg: rows.length ? Math.round(rows.reduce((n, r) => n + r.stars, 0) / rows.length * 10) / 10 : 0,
    rating_count: rows.length };
}
function rateable(id) {
  const movie = movieById(id);
  if (movie.status === "coming_soon") throw new ApiError("Phim sắp chiếu chưa nhận bình luận hoặc chấm sao.", 400);
}
const ratingUsage = new Map();
function ratingLimit(userId) {
  const recent = (ratingUsage.get(userId) ?? []).filter((t) => Date.now() - t < 60000);
  if (recent.length >= 20) throw new ApiError("Bạn chấm sao quá nhanh. Hãy thử lại sau ít phút.", 429);
  recent.push(Date.now()); ratingUsage.set(userId, recent);
}
function saveRating(movieId, userId, stars) {
  if (!Number.isInteger(stars) || stars < 1 || stars > 5) throw new ApiError("Số sao phải từ 1 đến 5.", 422);
  const rating = db.ratings.find((r) => r.movie_id === Number(movieId) && r.user_id === userId);
  if (rating) rating.stars = stars;
  else db.ratings.push({ movie_id: Number(movieId), user_id: userId, stars, created_at: new Date().toISOString() });
}
function ownsComment(c) {
  try { return currentUser().id === c.user_id; } catch { return false; }
}
const bookingCode = (id) => `FF${String(id).padStart(5, "0")}`;
const holdExpiresAt = (booking) => {
  const showtime = db.showtimes.find((item) => item.id === booking.showtime_id);
  return new Date(Math.min(
    new Date(booking.created_at).getTime() + HOLD_MINUTES * 60000,
    new Date(showtime.start_time).getTime() - HOLD_CUTOFF_MINUTES * 60000,
  )).toISOString();
};
function expireHolds() {
  let changed = false;
  const now = Date.now();
  db.bookings.forEach((booking) => {
    const showtime = db.showtimes.find((item) => item.id === booking.showtime_id);
    if (booking.status === "held" && showtime && new Date(holdExpiresAt(booking)).getTime() <= now) {
      booking.status = "expired";
      booking.seats = [];
      changed = true;
    }
  });
  if (changed) save();
}
const bookingOut = (booking) => {
  const showtime = db.showtimes.find((item) => item.id === booking.showtime_id);
  const code = bookingCode(booking.id);
  const qr = booking.status === "held"
    ? `https://img.vietqr.io/image/${MOCK_BANK.id}-${MOCK_BANK.account}-compact2.png?${new URLSearchParams({ amount: booking.total, addInfo: code, accountName: MOCK_BANK.name })}`
    : null;
  return {
    ...booking, checked_in_at: booking.checked_in_at ?? null, code, hold_expires_at: holdExpiresAt(booking), qr_url: qr,
    showtime, movie: movieById(showtime.movie_id),
  };
};
function findCheckin(code) {
  const match=/^FF([0-9]+)$/i.exec(code.trim());
  const b=match && db.bookings.find((b)=>b.id===Number(match[1]));
  if (!b) throw new ApiError("Không tìm thấy vé.",404);
  return b;
}
const adminBookingOut = (booking) => {
  const user = db.users.find((item) => item.id === booking.user_id);
  return { ...bookingOut(booking), checked_in_by_name: db.users.find((u) => u.id === booking.checked_in_by)?.full_name ?? null, customer_name: user?.full_name ?? "Không rõ", customer_email: user?.email ?? "Không rõ" };
};
const bookedSeats = (showtimeId) => [
  ...(db.adminShowtimeIds.includes(showtimeId) ? [] : seedBooked(showtimeId)),
  ...db.bookings.filter((b) => b.showtime_id === showtimeId && !["expired", "rejected"].includes(b.status)).flatMap((b) => b.seats),
];
const commentOut = (c) => ({
  id: c.id, movie_id: c.movie_id, user_name: c.is_anonymous ? "Khán giả ẩn danh" : db.users.find((u) => u.id === c.user_id)?.full_name ?? "Khán giả",
  is_anonymous: Boolean(c.is_anonymous), can_delete: ownsComment(c),
  author_stars: db.ratings.find((r) => r.movie_id === c.movie_id && r.user_id === c.user_id)?.stars ?? null,
  content: c.content, is_negative: c.is_negative,
  effective_negative: c.human_label === 0 || c.human_label === 1 ? c.human_label === 1 : c.is_negative,
  reviewed: c.human_label === 0 || c.human_label === 1,
  negative_score: c.negative_score, created_at: c.created_at,
});
const adminCommentOut = (c) => ({
  ...commentOut(c), can_delete: false, user_name: db.users.find((u) => u.id === c.user_id)?.full_name ?? "Khán giả", movie_title: movieById(c.movie_id).title, model_name: c.model_name,
  model_version: c.model_version,
  human_label: c.human_label, reviewed_by: c.reviewed_by,
  reviewed_by_name: db.users.find((u) => u.id === c.reviewed_by)?.full_name ?? null,
  reviewed_at: c.reviewed_at, hidden: c.hidden,
});

// Lượt đặt mẫu (trong 7 ngày, từ 8 đến 30 ngày trước) — giống backend/app/seed.py
const SAMPLE_SALES = { 9: [14, 16], 4: [12, 8], 10: [6, 16], 1: [5, 13], 3: [8, 7], 8: [9, 3], 2: [4, 5], 5: [2, 4], 18: [7, 1] };
function ranking(collection) {
  const rank = {};
  if (collection === "top_comments") {
    db.comments.forEach((c) => { rank[c.movie_id] = (rank[c.movie_id] ?? 0) + 1; });
    return rank;
  }
  Object.entries(SAMPLE_SALES).forEach(([id, [week, older]]) => {
    rank[id] = (collection === "hot_week" ? week : week + older) * 2;
  });
  db.bookings.forEach((b) => {
    const st = db.showtimes.find((s) => s.id === b.showtime_id);
    if (st) rank[st.movie_id] = (rank[st.movie_id] ?? 0) + b.seats.length;
  });
  return rank;
}

const POSTER_PATH = /^\/uploads\/posters\/[0-9a-f]{32}\.(jpg|png|webp)$/;
const POSTER_DATA_URL = /^data:image\/(jpeg|png|webp);base64,[A-Za-z0-9+/]+={0,2}$/;

function decodePosterBase64(data) {
  if (typeof data !== "string" || !data || data.length % 4 !== 0 || !/^[A-Za-z0-9+/]+={0,2}$/.test(data)) {
    throw new ApiError("Ảnh poster không hợp lệ.", 422);
  }
  try {
    return atob(data);
  } catch {
    throw new ApiError("Ảnh poster không hợp lệ.", 422);
  }
}

function posterMime(binary) {
  const codes = [...binary.slice(0, 12)].map((ch) => ch.charCodeAt(0));
  if (codes[0] === 0xff && codes[1] === 0xd8 && codes[2] === 0xff) return "image/jpeg";
  if ([137, 80, 78, 71, 13, 10, 26, 10].every((v, i) => codes[i] === v)) return "image/png";
  if ([82, 73, 70, 70].every((v, i) => codes[i] === v) && [87, 69, 66, 80].every((v, i) => codes[i + 8] === v)) return "image/webp";
  throw new ApiError("Chỉ nhận ảnh JPG, PNG hoặc WebP.", 422);
}

function validateMovie(payload) {
  const value = {
    ...payload,
    title: payload.title?.trim() ?? "",
    genre: [...new Set((payload.genre ?? []).map((item) => item.trim()).filter(Boolean))],
    formats: [...new Set((payload.formats ?? []).map((item) => item.trim()).filter(Boolean))],
    country: payload.country?.trim() ?? "",
    director: payload.director?.trim() ?? "",
    cast: payload.cast?.trim() ?? "",
    description: payload.description?.trim() ?? "",
    poster_bg: payload.poster_bg?.trim().toLowerCase() ?? "",
    poster_fg: payload.poster_fg?.trim().toLowerCase() ?? "",
    poster_url: payload.poster_url?.trim() || null,
  };
  const fail = (message) => { throw new ApiError(message, 422); };
  if (!value.title) fail("Tên phim không được để trống.");
  if (value.title.length > 200) fail("Tên phim không được dài quá 200 ký tự.");
  if (!value.genre.length) fail("Hãy chọn ít nhất một thể loại.");
  const badGenre = value.genre.find((item) => !GENRE_LABELS.includes(item));
  if (badGenre) fail(`Thể loại không hợp lệ: ${badGenre}.`);
  if (!Number.isInteger(Number(value.duration_min)) || Number(value.duration_min) < 1 || Number(value.duration_min) > 400) fail("Thời lượng phải từ 1 đến 400 phút.");
  value.duration_min = Number(value.duration_min);
  if (!AGE_RATINGS.includes(value.age_rating)) fail("Phân loại độ tuổi phải là P, T13, T16 hoặc T18.");
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value.release_date ?? "") || Number.isNaN(new Date(`${value.release_date}T00:00:00Z`).getTime()) || new Date(`${value.release_date}T00:00:00Z`).toISOString().slice(0, 10) !== value.release_date) fail("Ngày phát hành phải là ngày hợp lệ theo dạng YYYY-MM-DD.");
  if (!["now_showing", "coming_soon", "ended"].includes(value.status)) fail("Trạng thái phim không hợp lệ.");
  if (!COUNTRY_LABELS.includes(value.country)) fail("Quốc gia không thuộc danh mục cho phép.");
  const badFormat = value.formats.find((item) => !FORMAT_LABELS.includes(item));
  if (badFormat) fail(`Định dạng không hợp lệ: ${badFormat}.`);
  if (!/^#[0-9a-f]{6}$/.test(value.poster_bg) || !/^#[0-9a-f]{6}$/.test(value.poster_fg)) fail("Màu poster phải có dạng #rrggbb.");
  if (value.poster_url && !POSTER_PATH.test(value.poster_url) && !POSTER_DATA_URL.test(value.poster_url)) {
    try {
      const url = new URL(value.poster_url);
      if (!["http:", "https:"].includes(url.protocol) || !url.host) fail("Đường dẫn poster phải bắt đầu bằng http:// hoặc https://.");
    } catch { fail("Đường dẫn poster phải bắt đầu bằng http:// hoặc https://."); }
  }
  return value;
}

function requireAdmin() {
  if (currentUser().role !== "admin") throw new ApiError("Chỉ quản trị viên mới xem được trang này.", 403);
}

function validateShowtime(payload, excludeId = null) {
  const movie = db.movies.find((item) => item.id === Number(payload.movie_id));
  const fail = (message) => { throw new ApiError(message, 422); };
  if (!movie) fail("Phim không tồn tại.");
  if (movie.status === "ended") fail("Phim đã chiếu xong, không thể tạo suất mới.");
  const start = new Date(payload.start_time);
  if (Number.isNaN(start.getTime()) || start.getTime() <= Date.now()) fail("Suất chiếu phải ở tương lai.");
  if (!ROOMS.includes(payload.room)) fail("Phòng chiếu không hợp lệ.");
  const price = Number(payload.price);
  if (!Number.isInteger(price) || price < 10000 || price > 500000 || price % 1000 !== 0) {
    fail("Giá vé phải từ 10.000 đến 500.000 đồng và là bội số 1.000.");
  }
  const value = { movie_id: movie.id, start_time: payload.start_time, room: payload.room, price };
  const conflict = db.showtimes.find((item) => item.id !== excludeId && intervalsOverlap(value, item, db.movies));
  if (conflict) {
    const conflictMovie = movieById(conflict.movie_id);
    const time = conflict.start_time.slice(11, 16);
    throw new ApiError(`Phòng ${value.room.replace("Phòng ", "")} đã có suất ${conflictMovie.title} lúc ${time}. Hãy chọn giờ khác hoặc phòng khác.`, 409);
  }
  return value;
}

function ensureMutableShowtime(showtime) {
  // Ghế trang trí từ seedBooked chỉ dùng cho sơ đồ; chỉ vé người dùng tạo mới khóa CRUD admin.
  const tickets = db.bookings
    .filter((booking) => booking.showtime_id === showtime.id)
    .reduce((count, booking) => count + booking.seats.length, 0);
  if (tickets) throw new ApiError(`Suất chiếu đã có ${tickets} vé, không sửa hay xóa được.`, 409);
}

// T17 mock chatbot uses existing catalogue and showtimes only, with no provider calls.
function mockChat(messages) {
  const user = currentUser();
  if (user.role === "admin") throw new ApiError("Trợ lý chỉ dành cho khách hàng.", 403);
  if (!Array.isArray(messages) || messages.length < 1 || messages.length > 10 ||
      messages.some((m) => !["user", "assistant"].includes(m?.role) || typeof m.content !== "string" ||
        !m.content.trim() || m.content.length > 500) || messages.at(-1).role !== "user") {
    throw new ApiError("Tin nhắn không hợp lệ. Hãy nhập tối đa 10 tin, mỗi tin không quá 500 ký tự.", 422);
  }
  const plain = (value) => String(value).normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/gi, "d").toLowerCase();
  const question = plain(messages.at(-1).content);
  const titleMatch = db.movies.find((m) => question.includes(plain(m.title)));
  // "hài" becomes "hai" after normalization; it is a genre, not a price keyword.
  const wantsComedy = /(?:^|\s)(?:phim hai|the loai hai|hai huoc|phim cuoi)(?:\s|$)/.test(question);
  let films = titleMatch ? [titleMatch] : db.movies.filter((m) => m.status === "now_showing").slice(0, 3);
  if (wantsComedy && !titleMatch) {
    films = db.movies.filter((m) => m.status === "now_showing" &&
      m.genre.split(",").some((genre) => plain(genre.trim()) === "hai huoc")).slice(0, 3);
  }
  if (question.includes("thuong") || question.includes("vip") || question.includes("gia")) {
    if (question.includes("vip") && !titleMatch) films = [];
    const base = titleMatch ? db.showtimes.filter((s) => s.movie_id === titleMatch.id && new Date(s.start_time) > new Date()).slice(0, 2) : [];
    const dates = base.map((s) => `${s.start_time.replace("T", " ").slice(0, 16)}: ${s.price.toLocaleString("vi-VN")}đ`).join("; ");
    return { reply: `${titleMatch ? titleMatch.title + ": " : ""}${dates || "Giá vé thường tùy từng suất chiếu."} Ghế VIP phụ thu ${(totalPrice(["F1"], 0) - totalPrice(["A1"], 0)).toLocaleString("vi-VN")}đ. Xem trang phim để chọn suất.`,
      movies: films.map(({ id, title }) => ({ id, title })) };
  }
  const movieTitles = films.map((m) => m.title).join(", ");
  return { reply: films.length ? `Các phim bạn có thể xem: ${movieTitles}. Mở trang phim để xem suất chiếu và đặt vé.` : "Hiện chưa có phim phù hợp. Hãy xem danh sách phim trên website.",
    movies: films.map(({ id, title }) => ({ id, title })) };
}

export const mockApi = {
  chat: {
    async send(messages) { await wait(); return clone(mockChat(messages)); },
  },
  auth: {
    async register({ full_name, email, password }) {
      await wait();
      if (db.users.some((u) => u.email === email.toLowerCase())) throw new ApiError("Email này đã được đăng ký.", 400);
      if (password.length < 6) throw new ApiError("Mật khẩu cần ít nhất 6 ký tự.", 400);
      const user = { id: db.seq.user++, full_name, email: email.toLowerCase(), password, role: "user" };
      db.users.push(user); save();
      return { access_token: tokenFor(user), user: publicUser(user) };
    },
    async login({ email, password }) {
      await wait();
      const user = db.users.find((u) => u.email === email.toLowerCase() && u.password === password);
      if (!user) throw new ApiError("Email hoặc mật khẩu không đúng.", 401);
      return { access_token: tokenFor(user), user: publicUser(user) };
    },
    async me() { await wait(100); return publicUser(currentUser()); },
    async updateMe({ full_name }) {
      await wait();
      const user = currentUser();
      const value = String(full_name ?? "").trim();
      if (value.length < 2 || value.length > 100) {
        throw new ApiError("Họ tên cần từ 2 đến 100 ký tự.", 422);
      }
      user.full_name = value;
      save();
      return clone(publicUser(user));
    },
    async changePassword({ current_password, new_password }) {
      await wait();
      const user = currentUser();
      if (String(new_password ?? "").length < 6 || new_password.length > 100) {
        throw new ApiError("Mật khẩu mới cần từ 6 đến 100 ký tự.", 422);
      }
      if (user.password !== current_password) throw new ApiError("Mật khẩu hiện tại không đúng.", 400);
      user.password = new_password;
      save();
      return { detail: "Đã đổi mật khẩu." };
    },
  },
  movies: {
    async list(filters = {}) {
      await wait();
      const split = (v) => v.split(",").map((x) => x.trim()).filter(Boolean);
      const plain = (t) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/gi, "d").toLowerCase();
      const f = filters;
      let list = db.movies.map((m) => movieById(m.id)).filter((m) => {
        const year = Number(m.release_date.slice(0, 4));
        return (!f.status || m.status === f.status)
          && (!f.genre || split(m.genre).includes(f.genre))
          && (!f.country || m.country === f.country)
          && (!f.format || split(m.formats).includes(f.format))
          && (!f.age_rating || m.age_rating === f.age_rating)
          && (!f.year || year === Number(f.year))
          && (!f.year_before || year < Number(f.year_before))
          && (!f.q || plain(m.title).includes(plain(f.q.trim())));
      }).sort((a, b) => b.release_date.localeCompare(a.release_date));

      if (f.collection === "top_rated") {
        list = list.filter((m) => m.rating_avg >= 4).sort((a, b) => b.rating_avg - a.rating_avg || b.rating_count - a.rating_count);
      } else if (f.collection) {
        const rank = ranking(f.collection);
        list = list.filter((m) => rank[m.id] > 0).sort((a, b) => rank[b.id] - rank[a.id]);
      }
      return clone(list);
    },
    async get(id) { await wait(); return clone(movieById(id)); },
    async showtimes(id) {
      await wait();
      const now = Date.now();
      return clone(db.showtimes.filter((s) => s.movie_id === Number(id) && new Date(s.start_time).getTime() > now));
    },
  },
  showtimes: {
    async get(id) {
      await wait();
      expireHolds();
      const st = db.showtimes.find((s) => s.id === Number(id));
      if (!st) throw new ApiError("Không tìm thấy suất chiếu.", 404);
      return clone({ showtime: st, movie: movieById(st.movie_id), booked_seats: bookedSeats(st.id) });
    },
  },
  bookings: {
    async create({ showtime_id, seats }) {
      await wait(500);
      expireHolds();
      const user = currentUser();
      const st = db.showtimes.find((s) => s.id === Number(showtime_id));
      if (!st) throw new ApiError("Không tìm thấy suất chiếu.", 404);
      if (movieById(st.movie_id).status === "ended") throw new ApiError("Phim đã chiếu xong, không thể đặt vé.", 400);
      if (new Date(st.start_time).getTime() <= Date.now() + HOLD_CUTOFF_MINUTES * 60000) {
        throw new ApiError("Suất chiếu sắp bắt đầu, vui lòng mua vé tại quầy.", 400);
      }
      if (db.bookings.some((item) => item.user_id === user.id && item.showtime_id === st.id && item.status === "held")) {
        throw new ApiError("Bạn đang giữ chỗ cho suất này. Hãy thanh toán vé đang giữ trước khi đặt thêm.", 409);
      }
      if (db.bookings.filter((item) => item.user_id === user.id && item.status === "held").length >= 2) {
        throw new ApiError("Bạn đang giữ 2 vé chưa thanh toán. Hãy thanh toán hoặc chờ vé hết hạn.", 409);
      }
      if (!seats.length || seats.length > MAX_SEATS_PER_BOOKING) throw new ApiError(`Chọn từ 1 đến ${MAX_SEATS_PER_BOOKING} ghế.`, 400);
      const taken = bookedSeats(st.id).filter((s) => seats.includes(s));
      if (taken.length) throw new ApiError(`Ghế ${taken.join(", ")} vừa có người đặt. Hãy chọn ghế khác.`, 409);
      const booking = { id: db.seq.booking++, user_id: user.id, showtime_id: st.id, seats, total: totalPrice(seats, st.price), status: "held", created_at: nowIso() };
      db.bookings.push(booking); save();
      return clone(bookingOut(booking));
    },
    async mine() {
      await wait();
      expireHolds();
      const user = currentUser();
      return clone(db.bookings.filter((b) => b.user_id === user.id).sort((a, b) => b.id - a.id).map(bookingOut));
    },
    async remove(id) {
      await wait();
      expireHolds();
      const user = currentUser();
      const booking = db.bookings.find((item) => item.id === Number(id) && item.user_id === user.id);
      if (!booking) throw new ApiError("Không tìm thấy vé.", 404);
      if (booking.status !== "held") {
        throw new ApiError("Chỉ hủy được vé đang giữ chỗ chưa thanh toán.", 409);
      }
      db.bookings = db.bookings.filter((item) => item.id !== booking.id);
      save();
      return { detail: "Đã hủy vé." };
    },
    async claimTransfer(id) {
      await wait();
      expireHolds();
      const user = currentUser();
      const booking = db.bookings.find((item) => item.id === Number(id) && item.user_id === user.id);
      if (!booking) throw new ApiError("Không tìm thấy vé.", 404);
      if (booking.status !== "held") throw new ApiError("Vé không ở trạng thái có thể báo chuyển khoản.", 409);
      if (!MOCK_BANK.id || !MOCK_BANK.account || !MOCK_BANK.name) throw new ApiError("Rạp chưa bật thanh toán chuyển khoản.", 409);
      booking.status = "pending_verify";
      save();
      return clone(bookingOut(booking));
    },
  },
  ratings: {
    async mine(id) {
      await wait(); const user = currentUser(); movieById(id);
      return { stars: db.ratings.find((r) => r.movie_id === Number(id) && r.user_id === user.id)?.stars ?? null };
    },
    async set(id, stars) {
      await wait(); const user = currentUser(); rateable(id); ratingLimit(user.id);
      saveRating(id, user.id, stars); save(); return { stars, ...ratingSummary(id) };
    },
    async remove(id) {
      await wait(); const user = currentUser(); rateable(id); ratingLimit(user.id);
      db.ratings = db.ratings.filter((r) => !(r.movie_id === Number(id) && r.user_id === user.id));
      save(); return { stars: null, ...ratingSummary(id) };
    },
  },
  comments: {
    async list(movieId) {
      await wait();
      movieById(movieId);
      return db.comments.filter((c) => c.movie_id === Number(movieId) && !c.hidden)
        .sort((a, b) => b.created_at.localeCompare(a.created_at)).map(commentOut);
    },
    async create(movieId, payload) {
      await wait(600);
      const user = currentUser();
      rateable(movieId);
      const text = String(payload.content ?? "").trim();
      if (text.length < 2 || text.length > 1000) throw new ApiError("Bình luận cần từ 2 đến 1000 ký tự.", 422);
      checkCommentLimit(user.id);
      if (payload.stars != null) { ratingLimit(user.id); saveRating(movieId, user.id, payload.stars); }
      const c = { id: db.seq.comment++, movie_id: Number(movieId), user_id: user.id, content: text, is_anonymous: Boolean(payload.is_anonymous),
        ...fakeClassify(text), model_name: "phobert_b", model_version: "phobert-B-2026-10-09-mock", human_label: null, reviewed_by: null,
        reviewed_at: null, hidden: false, created_at: nowIso() };
      db.comments.push(c); save();
      return commentOut(c);
    },
    async remove(id) {
      await wait(); const user = currentUser();
      const comment = db.comments.find((c) => c.id === Number(id) && c.user_id === user.id);
      if (!comment) throw new ApiError("Không tìm thấy bình luận.", 404);
      db.comments = db.comments.filter((c) => c.id !== comment.id); save(); return { ok: true };
    },
  },
  admin: {
    async dashboard(days = 30) {
      await wait(); requireAdmin(); expireHolds();
      days = Number(days);
      if (![7,30,90].includes(days)) throw new ApiError("Số ngày phải là 7, 30 hoặc 90.", 422);
      const start = new Date(); start.setHours(0,0,0,0); start.setDate(start.getDate()-days+1);
      const end = new Date(); end.setHours(24,0,0,0);
      const inRange = (v) => new Date(v) >= start && new Date(v) < end;
      const dateKey = (v) => { const d=new Date(v); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`; };
      const bookings=db.bookings.filter((b)=>inRange(b.created_at)), paid=bookings.filter((b)=>b.status==="paid");
      const ratings=db.ratings.filter((r)=>inRange(r.created_at ?? new Date().toISOString()));
      const avg=(rs)=>rs.length ? rs.reduce((n,r)=>n+r.stars,0)/rs.length : 0;
      const sum=(bs)=>bs.reduce((n,b)=>n+b.total,0);
      const daily=Array.from({length:days},(_,i)=> { const d=new Date(start); d.setDate(d.getDate()+i); const date=dateKey(d), bs=paid.filter((b)=>dateKey(b.created_at)===date); return {date,revenue:sum(bs),tickets:bs.length}; });
      const movies=db.movies.map((m)=> {
        const bs=paid.filter((b)=>db.showtimes.find((s)=>s.id===b.showtime_id)?.movie_id===m.id);
        const shows=db.showtimes.filter((s)=>s.movie_id===m.id && new Date(s.start_time) >= start);
        const ids=new Set(shows.map((s)=>s.id));
        const sold=db.bookings.filter((b)=>b.status==="paid" && ids.has(b.showtime_id)).reduce((n,b)=>n+b.seats.length,0);
        const rs=ratings.filter((r)=>r.movie_id===m.id), cs=db.comments.filter((c)=>c.movie_id===m.id && inRange(c.created_at));
        return {movie_id:m.id,title:m.title,paid_tickets:bs.length,revenue:sum(bs),occupancy:shows.length ? sold/(shows.length*ROWS.length*COLS) : 0,rating_avg:avg(rs),rating_count:rs.length,negative_rate:cs.length ? cs.filter((c)=>(c.human_label ?? Number(c.is_negative))===1).length/cs.length : 0};
      }).sort((a,b)=>a.title.localeCompare(b.title,"vi") || a.movie_id-b.movie_id);
      return clone({days,revenue:sum(paid),paid_tickets:paid.length,pending_tickets:bookings.filter((b)=>["held","pending_verify"].includes(b.status)).length,cancelled_tickets:bookings.filter((b)=>["expired","rejected"].includes(b.status)).length,seats_sold:paid.reduce((n,b)=>n+b.seats.length,0),rating_avg:avg(ratings),rating_count:ratings.length,daily,movies});
    },
    checkin: {
      async get(code) { await wait(); requireAdmin(); expireHolds(); return clone(adminBookingOut(findCheckin(code))); },
      async confirm(code) {
        await wait(); requireAdmin(); const admin=currentUser(); expireHolds(); const b=findCheckin(code);
        if (b.checked_in_at) throw new ApiError(`Vé đã được soát lúc ${new Date(b.checked_in_at).toLocaleString("vi-VN")}.`,409);
        if (b.status!=="paid") throw new ApiError({held:"Vé chưa thanh toán, đang giữ chỗ.",pending_verify:"Vé chưa thanh toán, đang chờ xác nhận chuyển khoản.",expired:"Vé đã hủy do quá hạn thanh toán.",rejected:"Vé đã hủy do không nhận được thanh toán."}[b.status],409);
        b.checked_in_at=new Date().toISOString(); b.checked_in_by=admin.id; save(); return clone(adminBookingOut(b));
      },
    },
    async sentiment(days = 30) {
      await wait();
      requireAdmin();
      const range = Number(days);
      if (!Number.isInteger(range) || range < 1 || range > 365) {
        throw new ApiError("Số ngày thống kê phải từ 1 đến 365.", 422);
      }
      const dateKey = (value) => {
        const date = new Date(value);
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, "0");
        const day = String(date.getDate()).padStart(2, "0");
        return `${year}-${month}-${day}`;
      };
      const today = new Date();
      const dates = Array.from({ length: range }, (_, index) => {
        const date = new Date(today.getFullYear(), today.getMonth(), today.getDate() - (range - 1 - index));
        return dateKey(date);
      });
      const allowedDates = new Set(dates);
      const rows = db.comments.filter((comment) => allowedDates.has(dateKey(comment.created_at)));
      const effectiveNegative = (comment) => comment.human_label === 0 || comment.human_label === 1
        ? comment.human_label === 1 : Boolean(comment.is_negative);
      const reviewed = rows.filter((comment) => comment.human_label === 0 || comment.human_label === 1);
      const negative = rows.filter(effectiveNegative).length;
      const movieGroups = new Map();
      rows.forEach((comment) => {
        const group = movieGroups.get(comment.movie_id) ?? { total: 0, negative: 0, score: 0 };
        group.total += 1;
        group.negative += effectiveNegative(comment) ? 1 : 0;
        group.score += comment.negative_score;
        movieGroups.set(comment.movie_id, group);
      });
      const movies = [...movieGroups.entries()].map(([movieId, group]) => ({
        movie_id: movieId,
        title: movieById(movieId).title,
        total: group.total,
        negative: group.negative,
        negative_ratio: group.negative / group.total,
        avg_negative_score: group.score / group.total,
      })).sort((a, b) => b.negative_ratio - a.negative_ratio || b.total - a.total
        || a.title.localeCompare(b.title, "vi") || a.movie_id - b.movie_id);
      const daily = dates.map((date) => {
        const dateRows = rows.filter((comment) => dateKey(comment.created_at) === date);
        return { date, total: dateRows.length, negative: dateRows.filter(effectiveNegative).length };
      });
      const agree = reviewed.filter((comment) => Boolean(comment.is_negative) === (comment.human_label === 1)).length;
      return clone({
        summary: {
          total: rows.length,
          negative,
          negative_ratio: rows.length ? negative / rows.length : 0,
          reviewed: reviewed.length,
          model_human_accuracy: reviewed.length ? agree / reviewed.length : 0,
        },
        movies,
        daily,
      });
    },
    posters: {
      async upload({ filename, data }) {
        await wait();
        requireAdmin();
        const binary = decodePosterBase64(data);
        if (binary.length > 500 * 1024) throw new ApiError("Ảnh poster tối đa 500 KB.", 422);
        const mime = posterMime(binary); // không tin filename; cùng logic với backend
        return { poster_url: `data:${mime};base64,${data}` };
      },
    },
    async predict(text) {
      await wait(600);
      requireAdmin();
      const value = String(text ?? "").trim();
      if (!value) throw new ApiError("Nội dung cần chấm điểm không được để trống.", 422);
      const predictionB = fakeClassify(value);
      const isLeTheSample = normalizeComment(value).includes("dài lê thê");
      const predictionA = isLeTheSample
        ? { is_negative: false, negative_score: 0.0485 }
        : predictionB;
      return [
        {
          model: "phobert",
          version: "phobert-A-demo-mock",
          label: predictionA.is_negative ? "tieu_cuc" : "binh_thuong",
          score: predictionA.negative_score,
          ms: 0.2,
        },
        {
          model: "phobert_b",
          version: "phobert-B-demo-mock",
          label: predictionB.is_negative ? "tieu_cuc" : "binh_thuong",
          score: predictionB.negative_score,
          ms: 0.2,
        },
      ];
    },
    bookings: {
      async list(filters = {}) {
        await wait();
        requireAdmin();
        expireHolds();
        const code = String(filters.code ?? "").trim().toUpperCase();
        return clone(db.bookings
          .filter((item) => !filters.status || item.status === filters.status)
          .filter((item) => !code || bookingCode(item.id) === code)
          .sort((a, b) => b.id - a.id)
          .slice(0, 200)
          .map(adminBookingOut));
      },
      async confirm(id) {
        await wait();
        requireAdmin();
        expireHolds();
        const booking = db.bookings.find((item) => item.id === Number(id));
        if (!booking) throw new ApiError("Không tìm thấy vé.", 404);
        if (!["held", "pending_verify"].includes(booking.status)) throw new ApiError("Vé không ở trạng thái có thể xác nhận thanh toán.", 409);
        booking.status = "paid";
        save();
        return clone(adminBookingOut(booking));
      },
      async reject(id) {
        await wait();
        requireAdmin();
        expireHolds();
        const booking = db.bookings.find((item) => item.id === Number(id));
        if (!booking) throw new ApiError("Không tìm thấy vé.", 404);
        if (!["held", "pending_verify"].includes(booking.status)) throw new ApiError("Vé không ở trạng thái có thể từ chối thanh toán.", 409);
        booking.status = "rejected";
        booking.seats = [];
        save();
        return clone(adminBookingOut(booking));
      },
    },
    comments: {
      async list(filters = {}) {
        await wait();
        requireAdmin();
        const page = Number(filters.page ?? 1);
        const pageSize = Number(filters.page_size ?? 20);
        if (!Number.isInteger(page) || page < 1) throw new ApiError("Trang phải là số nguyên từ 1 trở lên.", 422);
        if (!Number.isInteger(pageSize) || pageSize < 1 || pageSize > 100) throw new ApiError("Số bình luận mỗi trang phải từ 1 đến 100.", 422);
        const reviewed = filters.reviewed === true || filters.reviewed === "true"
          ? true : filters.reviewed === false || filters.reviewed === "false" ? false : null;
        const rows = db.comments
          .filter((c) => (filters.label === "negative" ? c.is_negative : filters.label === "normal" ? !c.is_negative : true))
          .filter((c) => reviewed === null || (c.human_label === 0 || c.human_label === 1) === reviewed)
          .sort((a, b) => b.created_at.localeCompare(a.created_at) || b.id - a.id);
        const start = (page - 1) * pageSize;
        return clone({ items: rows.slice(start, start + pageSize).map(adminCommentOut), total: rows.length });
      },
      async update(id, payload) {
        await wait();
        const admin = currentUser();
        if (admin.role !== "admin") throw new ApiError("Chỉ quản trị viên mới xem được trang này.", 403);
        const comment = db.comments.find((item) => item.id === Number(id));
        if (!comment) throw new ApiError("Không tìm thấy bình luận.", 404);
        if (payload.action === "confirm") {
          comment.human_label = comment.is_negative ? 1 : 0;
          comment.reviewed_by = admin.id;
          comment.reviewed_at = nowIso();
        } else if (payload.action === "relabel") {
          if (payload.label !== 0 && payload.label !== 1) throw new ApiError("Đổi nhãn cần label là 0 hoặc 1.", 422);
          comment.human_label = payload.label;
          comment.reviewed_by = admin.id;
          comment.reviewed_at = nowIso();
        } else if (payload.action === "hide") comment.hidden = true;
        else if (payload.action === "unhide") comment.hidden = false;
        else throw new ApiError("Thao tác kiểm duyệt không hợp lệ.", 422);
        save();
        return clone(adminCommentOut(comment));
      },
      async stats() {
        await wait();
        requireAdmin();
        const rows = db.comments.filter((c) => c.human_label === 0 || c.human_label === 1);
        const tp = rows.filter((c) => c.is_negative && c.human_label === 1).length;
        const fp = rows.filter((c) => c.is_negative && c.human_label === 0).length;
        const tn = rows.filter((c) => !c.is_negative && c.human_label === 0).length;
        const fn = rows.filter((c) => !c.is_negative && c.human_label === 1).length;
        const agree = tp + tn;
        return { reviewed: rows.length, agree, disagree: fp + fn,
          accuracy: rows.length ? agree / rows.length : 0, tp, fp, tn, fn };
      },
      async exportCsv() {
        await wait();
        requireAdmin();
        const safe = (value) => {
          const text = String(value);
          const trimmed = text.trimStart();
          return text && (/^[\t\r]/.test(text) || /^[=+\-@]/.test(trimmed)) ? `'${text}` : text;
        };
        const escape = (value) => `"${safe(value).replace(/"/g, '""')}"`;
        const lines = ["text,text_norm,label", ...db.comments
          .filter((c) => c.human_label === 0 || c.human_label === 1)
          .sort((a, b) => a.id - b.id)
          .map((c) => `${escape(c.content)},${escape(normalizeComment(c.content))},${c.human_label}`)];
        return new Blob(["\ufeff", lines.join("\r\n"), "\r\n"], { type: "text/csv;charset=utf-8" });
      },
    },
    movies: {
      async list() {
        await wait();
        if (currentUser().role !== "admin") throw new ApiError("Chỉ quản trị viên mới xem được trang này.", 403);
        return clone(db.movies.map((m) => movieById(m.id)).sort((a, b) => b.release_date.localeCompare(a.release_date) || b.id - a.id));
      },
      async create(payload) {
        await wait();
        if (currentUser().role !== "admin") throw new ApiError("Chỉ quản trị viên mới xem được trang này.", 403);
        const value = validateMovie(payload);
        if (!value.poster_url) throw new ApiError("Hãy chọn ảnh poster hoặc dán đường dẫn poster.", 422);
        const movie = { id: db.seq.movie++, ...value, genre: value.genre.join(", "), formats: value.formats.join(", "), score: 0 };
        db.movies.push(movie); save();
        return clone(movieById(movie.id));
      },
      async update(id, payload) {
        await wait();
        if (currentUser().role !== "admin") throw new ApiError("Chỉ quản trị viên mới xem được trang này.", 403);
        const movie = movieById(id);
        const value = validateMovie(payload);
        Object.assign(movie, value, { genre: value.genre.join(", "), formats: value.formats.join(", ") });
        save();
        return clone(movieById(movie.id));
      },
      async remove(id) {
        await wait();
        if (currentUser().role !== "admin") throw new ApiError("Chỉ quản trị viên mới xem được trang này.", 403);
        const movie = movieById(id);
        const showtimeIds = db.showtimes.filter((item) => item.movie_id === movie.id).map((item) => item.id);
        if (db.bookings.some((item) => showtimeIds.includes(item.showtime_id) && !["expired", "rejected"].includes(item.status))) {
          throw new ApiError("Phim đã có vé, không xóa được. Hãy chuyển trạng thái sang Đã chiếu xong.", 409);
        }
        db.movies = db.movies.filter((item) => item.id !== movie.id);
        db.showtimes = db.showtimes.filter((item) => item.movie_id !== movie.id);
        db.comments = db.comments.filter((item) => item.movie_id !== movie.id);
        db.ratings = db.ratings.filter((item) => item.movie_id !== movie.id);
        save();
        return { detail: "Đã xóa phim." };
      },
    },
    showtimes: {
      async list(filters = {}) {
        await wait();
        requireAdmin();
        return clone(db.showtimes
          .filter((item) => (!filters.movie_id || item.movie_id === Number(filters.movie_id))
            && (!filters.date || item.start_time.slice(0, 10) === filters.date))
          .sort((a, b) => a.start_time.localeCompare(b.start_time) || a.room.localeCompare(b.room) || a.id - b.id));
      },
      async create(payload) {
        await wait();
        requireAdmin();
        const value = validateShowtime(payload);
        const showtime = { id: db.seq.showtime++, ...value };
        db.showtimes.push(showtime);
        db.adminShowtimeIds.push(showtime.id);
        save();
        return clone(showtime);
      },
      async update(id, payload) {
        await wait();
        requireAdmin();
        const showtime = db.showtimes.find((item) => item.id === Number(id));
        if (!showtime) throw new ApiError("Không tìm thấy suất chiếu.", 404);
        ensureMutableShowtime(showtime);
        Object.assign(showtime, validateShowtime(payload, showtime.id));
        save();
        return clone(showtime);
      },
      async remove(id) {
        await wait();
        requireAdmin();
        const showtime = db.showtimes.find((item) => item.id === Number(id));
        if (!showtime) throw new ApiError("Không tìm thấy suất chiếu.", 404);
        ensureMutableShowtime(showtime);
        db.showtimes = db.showtimes.filter((item) => item.id !== showtime.id);
        db.adminShowtimeIds = db.adminShowtimeIds.filter((item) => item !== showtime.id);
        save();
        return { detail: "Đã xóa suất chiếu." };
      },
    },
  },
};
