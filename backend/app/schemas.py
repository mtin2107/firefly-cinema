from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


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


class ShowtimeOut(ORM):
    id: int
    movie_id: int
    start_time: datetime
    room: str
    price: int


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
