from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, Text, DateTime, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base


def _active_model_version() -> str:
    from .classifier import classifier
    return classifier.version


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")  # "user" | "admin"
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)


class Movie(Base):
    __tablename__ = "movies"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    genre: Mapped[str] = mapped_column(String(100))  # nhiều thể loại, cách nhau bằng ", "
    duration_min: Mapped[int] = mapped_column(Integer)
    age_rating: Mapped[str] = mapped_column(String(5))
    release_date: Mapped[str] = mapped_column(String(10))
    status: Mapped[str] = mapped_column(String(20))  # "now_showing" | "coming_soon" | "ended"
    director: Mapped[str] = mapped_column(String(100))
    cast: Mapped[str] = mapped_column(String(255))
    score: Mapped[float] = mapped_column(Float, default=0)
    description: Mapped[str] = mapped_column(Text)
    poster_bg: Mapped[str] = mapped_column(String(9))
    poster_fg: Mapped[str] = mapped_column(String(9))
    poster_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    country: Mapped[str] = mapped_column(String(50), default="")
    formats: Mapped[str] = mapped_column(String(50), default="")  # "Phụ đề", "Lồng tiếng" hoặc cả hai


class Showtime(Base):
    __tablename__ = "showtimes"
    id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), index=True)
    start_time: Mapped[datetime] = mapped_column(DateTime, index=True)
    room: Mapped[str] = mapped_column(String(30))
    price: Mapped[int] = mapped_column(Integer)
    movie: Mapped[Movie] = relationship()


class Booking(Base):
    __tablename__ = "bookings"
    __table_args__ = (
        CheckConstraint(
            "status IN ('held', 'pending_verify', 'paid', 'expired', 'rejected')",
            name="ck_bookings_status",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    showtime_id: Mapped[int] = mapped_column(ForeignKey("showtimes.id"))
    total: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="held", server_default="held")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user: Mapped[User] = relationship()
    showtime: Mapped[Showtime] = relationship()
    seats: Mapped[list["BookingSeat"]] = relationship(back_populates="booking", cascade="all, delete-orphan")


class BookingSeat(Base):
    """Mỗi ghế đã đặt là 1 dòng. Ràng buộc UNIQUE đảm bảo 2 người không đặt trùng 1 ghế."""
    __tablename__ = "booking_seats"
    __table_args__ = (UniqueConstraint("showtime_id", "seat_code", name="uq_showtime_seat"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"))
    showtime_id: Mapped[int] = mapped_column(ForeignKey("showtimes.id"), index=True)
    seat_code: Mapped[str] = mapped_column(String(4))
    booking: Mapped[Booking] = relationship(back_populates="seats")


class Comment(Base):
    __tablename__ = "comments"
    __table_args__ = (CheckConstraint("human_label IN (0, 1) OR human_label IS NULL", name="ck_comments_human_label"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    is_negative: Mapped[bool] = mapped_column(Boolean)       # kết quả mô hình
    negative_score: Mapped[float] = mapped_column(Float)     # xác suất tiêu cực 0..1
    model_name: Mapped[str] = mapped_column(String(30))      # "phobert" | "phobert_b" | "keyword"
    model_version: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default=_active_model_version
    )
    human_label: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    hidden: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    user: Mapped[User] = relationship(foreign_keys=[user_id])
    reviewer: Mapped[User | None] = relationship(foreign_keys=[reviewed_by])
    movie: Mapped[Movie] = relationship()
