GENRES = (
    "Hành động", "Tình cảm", "Hài hước", "Cổ trang", "Tâm lý", "Hình sự",
    "Chiến tranh", "Thể thao", "Võ thuật", "Viễn tưởng", "Phiêu lưu", "Khoa học",
    "Kinh dị", "Âm nhạc", "Thần thoại", "Tài liệu", "Gia đình", "Chính kịch",
    "Bí ẩn", "Học đường", "Kinh điển", "Anime & Hoạt hình",
)

COUNTRIES = (
    "Việt Nam", "Hàn Quốc", "Nhật Bản", "Trung Quốc", "Thái Lan",
    "Mỹ", "Anh", "Pháp", "Ấn Độ",
)

FORMATS = ("Phụ đề", "Lồng tiếng")
AGE_RATINGS = ("P", "T13", "T16", "T18")
MOVIE_STATUSES = ("now_showing", "coming_soon", "ended")


def effective_status(movie=None, today=None, *, sql=False):
    """Shared release-date rule, including its SQL expression."""
    from datetime import date
    today = today or date.today()
    day = today.isoformat() if hasattr(today, "isoformat") else today
    if sql:
        from sqlalchemy import case, and_
        from .models import Movie
        return case((and_(Movie.status == "coming_soon", Movie.release_date <= day),
                     "now_showing"), else_=Movie.status)
    status = movie.get("status") if isinstance(movie, dict) else movie.status
    release = movie.get("release_date") if isinstance(movie, dict) else movie.release_date
    return "now_showing" if status == "coming_soon" and release <= day else status
