export const ratingText = (movie) => movie.rating_count
  ? `★ ${Number(movie.rating_avg).toFixed(1)} (${movie.rating_count} lượt)` : "Chưa có đánh giá";
export const byRating = (a, b) => (b.rating_avg ?? 0) - (a.rating_avg ?? 0)
  || (b.rating_count ?? 0) - (a.rating_count ?? 0) || a.id - b.id;
