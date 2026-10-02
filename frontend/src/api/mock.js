// ======================================================================
// DỮ LIỆU GIẢ — chỉ dùng khi VITE_USE_MOCK=true (chưa có backend).
// Mọi hàm trả về đúng cấu trúc JSON mà backend FastAPI trả về,
// nên khi chuyển sang backend thật, giao diện không phải sửa gì.
// ======================================================================
import MOVIES from "./movies.json";
import { ApiError } from "./http";
import { ROWS, COLS, totalPrice, MAX_SEATS_PER_BOOKING } from "../utils/seats";

const DB_KEY = "firefly_mockdb_v2";
const wait = (ms = 250) => new Promise((r) => setTimeout(r, ms));
const clone = (x) => JSON.parse(JSON.stringify(x));
const nowIso = () => new Date().toISOString();

// Bộ lọc từ khóa thay cho PhoBERT khi chạy mock
const NEGATIVE_WORDS = ["dở", "chán", "tệ", "phí tiền", "nhảm", "thất vọng", "rác", "kém", "buồn ngủ", "xàm", "lừa"];
function fakeClassify(text) {
  const t = text.toLowerCase();
  const hit = NEGATIVE_WORDS.some((w) => t.includes(w));
  return { is_negative: hit, negative_score: hit ? 0.87 : 0.08 };
}

function localIso(date, hhmm) {
  const [h, m] = hhmm.split(":").map(Number);
  const d = new Date(date);
  d.setHours(h, m, 0, 0);
  // ISO không có múi giờ, giống backend
  const p = (n) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}T${p(h)}:${p(m)}:00`;
}

function buildShowtimes() {
  const times = ["09:30", "13:15", "16:00", "19:30", "22:00"];
  const list = [];
  let id = 1;
  const today = new Date();
  for (let day = 0; day < 5; day++) {
    const date = new Date(today);
    date.setDate(today.getDate() + day);
    MOVIES.filter((m) => m.status === "now_showing").forEach((movie, idx) => {
      times
        .filter((_, i) => (i + idx + day) % 2 === 0 || i === 3)
        .forEach((t) => {
          const price = Number(t.slice(0, 2)) >= 17 ? 95000 : 75000;
          list.push({ id: id++, movie_id: movie.id, start_time: localIso(date, t), room: `Phòng ${(idx % 4) + 1}`, price });
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
  const sample = [
    [1, 2, "Xem xong muốn gọi điện về cho mẹ liền. Cảnh cuối trên toa tàu quá đẹp."],
    [1, 2, "Phim dài lê thê, nửa đầu buồn ngủ thật sự, phí tiền vé."],
    [4, 2, "Con mình 6 tuổi xem cười suốt, đoạn ở chợ Bến Thành dễ thương lắm."],
    [2, 2, "Kịch bản nhảm, hù dọa toàn tiếng động lớn, thất vọng."],
    [3, 2, "Cảnh lũ quay rất thật, âm thanh rạp này nghe đã."],
    [9, 2, "Nhạc phim hay muốn khóc, xem xong về nghe lại cả tối."],
    [9, 2, "Hình ảnh đẹp, đoạn diễn cuối nổi da gà."],
    [10, 2, "Kỹ xạo ổn nhưng kịch bản hơi kém, đoạn giữa xàm quá."],
    [8, 2, "Không khí ngột ngạt đúng chất, coi xong không dám đi tàu đêm."],
    [12, 2, "Phục trang đẹp, chuyện tình cảm động."],
    [5, 2, "Hài nhạt, cười được đúng hai lần, khá thất vọng."],
    [18, 2, "Mấy bé đá bóng dễ thương, cả rạp vỗ tay đoạn cuối."],
  ];
  const comments = sample.map(([movie_id, user_id, content], i) => ({
    id: i + 1, movie_id, user_id, content, ...fakeClassify(content),
    created_at: new Date(Date.now() - (i + 1) * 3600 * 1000 * 5).toISOString(),
  }));
  return { users, comments, bookings: [], showtimes: buildShowtimes(), seq: { user: 3, comment: 100, booking: 1 } };
}

function load() {
  try {
    const raw = localStorage.getItem(DB_KEY);
    if (raw) {
      const db = JSON.parse(raw);
      // làm mới suất chiếu mỗi ngày
      if (db.showtimesDay === new Date().toDateString()) return db;
      db.showtimes = buildShowtimes();
      db.showtimesDay = new Date().toDateString();
      db.bookings = [];
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
  const m = MOVIES.find((x) => x.id === Number(id));
  if (!m) throw new ApiError("Không tìm thấy phim.", 404);
  return m;
};
const bookedSeats = (showtimeId) => [
  ...seedBooked(showtimeId),
  ...db.bookings.filter((b) => b.showtime_id === showtimeId).flatMap((b) => b.seats),
];
const commentOut = (c) => ({
  id: c.id, movie_id: c.movie_id, user_name: db.users.find((u) => u.id === c.user_id)?.full_name ?? "Ẩn danh",
  content: c.content, is_negative: c.is_negative, negative_score: c.negative_score, created_at: c.created_at,
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

export const mockApi = {
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
  },
  movies: {
    async list(filters = {}) {
      await wait();
      const split = (v) => v.split(",").map((x) => x.trim()).filter(Boolean);
      const plain = (t) => t.normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/đ/gi, "d").toLowerCase();
      const f = filters;
      let list = MOVIES.filter((m) => {
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
        list = list.filter((m) => m.score >= 8).sort((a, b) => b.score - a.score);
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
      const st = db.showtimes.find((s) => s.id === Number(id));
      if (!st) throw new ApiError("Không tìm thấy suất chiếu.", 404);
      return clone({ showtime: st, movie: movieById(st.movie_id), booked_seats: bookedSeats(st.id) });
    },
  },
  bookings: {
    async create({ showtime_id, seats }) {
      await wait(500);
      const user = currentUser();
      const st = db.showtimes.find((s) => s.id === Number(showtime_id));
      if (!st) throw new ApiError("Không tìm thấy suất chiếu.", 404);
      if (!seats.length || seats.length > MAX_SEATS_PER_BOOKING) throw new ApiError(`Chọn từ 1 đến ${MAX_SEATS_PER_BOOKING} ghế.`, 400);
      const taken = bookedSeats(st.id).filter((s) => seats.includes(s));
      if (taken.length) throw new ApiError(`Ghế ${taken.join(", ")} vừa có người đặt. Hãy chọn ghế khác.`, 409);
      const booking = { id: db.seq.booking++, user_id: user.id, showtime_id: st.id, seats, total: totalPrice(seats, st.price), created_at: nowIso() };
      db.bookings.push(booking); save();
      return clone({ ...booking, showtime: st, movie: movieById(st.movie_id) });
    },
    async mine() {
      await wait();
      const user = currentUser();
      return clone(db.bookings.filter((b) => b.user_id === user.id).reverse().map((b) => {
        const st = db.showtimes.find((s) => s.id === b.showtime_id);
        return { ...b, showtime: st, movie: movieById(st.movie_id) };
      }));
    },
  },
  comments: {
    async list(movieId) {
      await wait();
      return db.comments.filter((c) => c.movie_id === Number(movieId))
        .sort((a, b) => b.created_at.localeCompare(a.created_at)).map(commentOut);
    },
    async create(movieId, content) {
      await wait(600);
      const user = currentUser();
      movieById(movieId);
      const text = content.trim();
      if (text.length < 2 || text.length > 1000) throw new ApiError("Bình luận cần từ 2 đến 1000 ký tự.", 400);
      const c = { id: db.seq.comment++, movie_id: Number(movieId), user_id: user.id, content: text, ...fakeClassify(text), created_at: nowIso() };
      db.comments.push(c); save();
      return commentOut(c);
    },
  },
  admin: {
    async comments(label) {
      await wait();
      if (currentUser().role !== "admin") throw new ApiError("Chỉ quản trị viên mới xem được trang này.", 403);
      return db.comments
        .filter((c) => (label === "negative" ? c.is_negative : label === "normal" ? !c.is_negative : true))
        .sort((a, b) => b.created_at.localeCompare(a.created_at))
        .map((c) => ({ ...commentOut(c), movie_title: movieById(c.movie_id).title }));
    },
  },
};
