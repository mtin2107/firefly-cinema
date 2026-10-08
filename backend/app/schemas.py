from datetime import date, datetime, timezone
import re
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator
from pydantic_core import PydanticCustomError

from .taxonomy import AGE_RATINGS, COUNTRIES, FORMATS, GENRES, MOVIE_STATUSES


class ORM(BaseModel):
    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


# ---------- Tài khoản ----------
class RegisterIn(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORM):
    id: int
    full_name: str
    email: str
    role: str


class TokenOut(BaseModel):
    access_token: str
    user: UserOut


# ---------- Phim, suất chiếu ----------
class MovieOut(ORM):
    id: int
    title: str
    genre: str
    duration_min: int
    age_rating: str
    release_date: str
    status: str
    director: str
    cast: str
    score: float
    description: str
    poster_bg: str
    poster_fg: str
    poster_url: str | None = None
    country: str
    formats: str


class MovieIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    genre: list[str]
    duration_min: int
    age_rating: str
    release_date: str
    status: str
    country: str
    formats: list[str]
    director: str = ""
    cast: str = ""
    description: str = ""
    poster_bg: str
    poster_fg: str
    poster_url: str | None = None

    @field_validator("title")
    @classmethod
    def validate_title(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise PydanticCustomError("movie_title", "Tên phim không được để trống.")
        if len(value) > 200:
            raise PydanticCustomError("movie_title", "Tên phim không được dài quá 200 ký tự.")
        return value

    @field_validator("genre")
    @classmethod
    def validate_genre(cls, value: list[str]) -> list[str]:
        cleaned = list(dict.fromkeys(item.strip() for item in value if item.strip()))
        if not cleaned:
            raise PydanticCustomError("movie_genre", "Hãy chọn ít nhất một thể loại.")
        invalid = [item for item in cleaned if item not in GENRES]
        if invalid:
            raise PydanticCustomError("movie_genre", f"Thể loại không hợp lệ: {', '.join(invalid)}.")
        return cleaned

    @field_validator("duration_min")
    @classmethod
    def validate_duration(cls, value: int) -> int:
        if not 0 < value <= 400:
            raise PydanticCustomError("movie_duration", "Thời lượng phải từ 1 đến 400 phút.")
        return value

    @field_validator("age_rating")
    @classmethod
    def validate_age_rating(cls, value: str) -> str:
        if value not in AGE_RATINGS:
            raise PydanticCustomError("movie_age_rating", "Phân loại độ tuổi phải là P, T13, T16 hoặc T18.")
        return value

    @field_validator("release_date")
    @classmethod
    def validate_release_date(cls, value: str) -> str:
        try:
            parsed = date.fromisoformat(value)
        except (TypeError, ValueError):
            raise PydanticCustomError("movie_release_date", "Ngày phát hành phải là ngày hợp lệ theo dạng YYYY-MM-DD.")
        if parsed.isoformat() != value:
            raise PydanticCustomError("movie_release_date", "Ngày phát hành phải là ngày hợp lệ theo dạng YYYY-MM-DD.")
        return value

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str) -> str:
        if value not in MOVIE_STATUSES:
            raise PydanticCustomError("movie_status", "Trạng thái phim không hợp lệ.")
        return value

    @field_validator("country")
    @classmethod
    def validate_country(cls, value: str) -> str:
        value = value.strip()
        if value not in COUNTRIES:
            raise PydanticCustomError("movie_country", "Quốc gia không thuộc danh mục cho phép.")
        return value

    @field_validator("formats")
    @classmethod
    def validate_formats(cls, value: list[str]) -> list[str]:
        cleaned = list(dict.fromkeys(item.strip() for item in value if item.strip()))
        invalid = [item for item in cleaned if item not in FORMATS]
        if invalid:
            raise PydanticCustomError("movie_formats", f"Định dạng không hợp lệ: {', '.join(invalid)}.")
        return cleaned

    @field_validator("director")
    @classmethod
    def validate_director(cls, value: str) -> str:
        value = value.strip()
        if len(value) > 100:
            raise PydanticCustomError("movie_director", "Tên đạo diễn không được dài quá 100 ký tự.")
        return value

    @field_validator("cast")
    @classmethod
    def validate_cast(cls, value: str) -> str:
        value = value.strip()
        if len(value) > 255:
            raise PydanticCustomError("movie_cast", "Danh sách diễn viên không được dài quá 255 ký tự.")
        return value

    @field_validator("description")
    @classmethod
    def clean_description(cls, value: str) -> str:
        return value.strip()

    @field_validator("poster_bg", "poster_fg")
    @classmethod
    def validate_color(cls, value: str) -> str:
        value = value.strip().lower()
        if not re.fullmatch(r"#[0-9a-f]{6}", value):
            raise PydanticCustomError("movie_color", "Màu poster phải có dạng #rrggbb.")
        return value

    @field_validator("poster_url")
    @classmethod
    def validate_poster_url(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        value = value.strip()
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise PydanticCustomError("movie_poster_url", "Đường dẫn poster phải bắt đầu bằng http:// hoặc https://.")
        if len(value) > 500:
            raise PydanticCustomError("movie_poster_url", "Đường dẫn poster không được dài quá 500 ký tự.")
        return value


class ShowtimeOut(ORM):
    id: int
    movie_id: int
    start_time: datetime
    room: str
    price: int


class ShowtimeIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    movie_id: int
    start_time: datetime
    room: str
    price: int

    @field_validator("movie_id")
    @classmethod
    def validate_movie_id(cls, value: int) -> int:
        if value < 1:
            raise PydanticCustomError("showtime_movie", "Phim không hợp lệ.")
        return value

    @field_validator("start_time")
    @classmethod
    def validate_start_time(cls, value: datetime) -> datetime:
        if value.tzinfo is not None:
            if value <= datetime.now(timezone.utc):
                raise PydanticCustomError("showtime_start", "Suất chiếu phải ở tương lai.")
            value = value.astimezone().replace(tzinfo=None)
        elif value <= datetime.now():
            raise PydanticCustomError("showtime_start", "Suất chiếu phải ở tương lai.")
        return value.replace(second=0, microsecond=0)

    @field_validator("room")
    @classmethod
    def clean_room(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise PydanticCustomError("showtime_room", "Hãy chọn phòng chiếu.")
        return value

    @field_validator("price")
    @classmethod
    def validate_price(cls, value: int) -> int:
        if not 10_000 <= value <= 500_000 or value % 1_000:
            raise PydanticCustomError("showtime_price", "Giá vé phải từ 10.000 đến 500.000 đồng và là bội số 1.000.")
        return value


class ShowtimeDetailOut(BaseModel):
    showtime: ShowtimeOut
    movie: MovieOut
    booked_seats: list[str]


# ---------- Đặt vé ----------
class BookingIn(BaseModel):
    showtime_id: int
    seats: list[str]


class BookingOut(BaseModel):
    id: int
    seats: list[str]
    total: int
    created_at: datetime
    showtime: ShowtimeOut
    movie: MovieOut


# ---------- Bình luận ----------
class CommentIn(BaseModel):
    content: str = Field(min_length=2, max_length=1000)


class CommentOut(BaseModel):
    id: int
    movie_id: int
    user_name: str
    content: str
    is_negative: bool
    negative_score: float
    created_at: datetime


class AdminCommentOut(CommentOut):
    model_config = ConfigDict(protected_namespaces=())
    movie_title: str
    model_name: str
