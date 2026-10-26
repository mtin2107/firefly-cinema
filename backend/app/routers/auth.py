from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Booking, Comment, Rating
from ..rate_limit import SlidingWindowRateLimiter
from ..schemas import AccountSummary, ChangePasswordIn, LoginIn, RegisterIn, TokenOut, UpdateProfileIn, UserOut
from ..security import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Tài khoản"])
_login_failures = SlidingWindowRateLimiter()
_LOGIN_LIMIT_MESSAGE = "Bạn đăng nhập sai quá nhiều lần. Hãy thử lại sau 5 phút."
_CHANGE_PASSWORD_LIMIT_MESSAGE = "Bạn nhập sai mật khẩu quá nhiều lần. Hãy thử lại sau 5 phút."


@router.post("/register", response_model=TokenOut, status_code=201)
def register(body: RegisterIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if db.scalar(select(User).where(User.email == email)):
        raise HTTPException(400, "Email này đã được đăng ký.")
    user = User(full_name=body.full_name.strip(), email=email, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"access_token": create_token(user.id), "user": user}


@router.post("/login", response_model=TokenOut)
def login(body: LoginIn, db: Session = Depends(get_db)):
    email = body.email.lower()
    if _login_failures.is_blocked(email, limit=5, seconds=300):
        raise HTTPException(429, _LOGIN_LIMIT_MESSAGE)
    user = db.scalar(select(User).where(User.email == email))
    if not user or not verify_password(body.password, user.password_hash):
        _login_failures.hit(email, limit=5, seconds=300, message=_LOGIN_LIMIT_MESSAGE)
        raise HTTPException(401, "Email hoặc mật khẩu không đúng.")
    _login_failures.clear(email)
    return {"access_token": create_token(user.id), "user": user}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


@router.patch("/me", response_model=UserOut)
def update_me(
    body: UpdateProfileIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user.full_name = body.full_name
    db.commit()
    db.refresh(user)
    return user


@router.post("/change-password")
def change_password(
    body: ChangePasswordIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    email = user.email.lower()
    if _login_failures.is_blocked(email, limit=5, seconds=300):
        raise HTTPException(429, _CHANGE_PASSWORD_LIMIT_MESSAGE)
    if not verify_password(body.current_password, user.password_hash):
        _login_failures.hit(
            email,
            limit=5,
            seconds=300,
            message=_CHANGE_PASSWORD_LIMIT_MESSAGE,
        )
        raise HTTPException(400, "Mật khẩu hiện tại không đúng.")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    _login_failures.clear(email)
    return {"detail": "Đã đổi mật khẩu."}


@router.get("/me/summary", response_model=AccountSummary)
def me_summary(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    from collections import Counter
    bookings = db.scalars(select(Booking).where(Booking.user_id == user.id)).all()
    paid = [b for b in bookings if b.status == "paid"]
    comments = db.scalars(select(Comment).where(Comment.user_id == user.id)
                          .order_by(Comment.created_at.desc(), Comment.id.desc())).all()
    ratings = db.scalars(select(Rating).where(Rating.user_id == user.id)
                         .order_by(Rating.updated_at.desc(), Rating.id.desc())).all()
    genres = Counter(g.strip() for b in paid for g in b.showtime.movie.genre.split(",") if g.strip())
    return {
        "member_since": user.created_at,
        "stats": {"bookings": sum(b.status not in ("expired", "rejected") for b in bookings),
                  "paid": len(paid), "watched": sum(b.checked_in_at is not None for b in bookings),
                  "total_spent": sum(b.total for b in paid), "comments": len(comments), "ratings": len(ratings)},
        "favorite_genre": sorted(genres, key=lambda g: (-genres[g], g))[0] if genres else None,
        "recent_comments": [{"id": c.id, "movie_id": c.movie_id, "movie_title": c.movie.title,
                             "content": c.content, "created_at": c.created_at, "is_anonymous": c.is_anonymous,
                             "hidden": c.hidden,
                             "effective_negative": bool(c.human_label if c.human_label is not None else c.is_negative)}
                            for c in comments[:3]],
        "ratings": [{"movie_id": r.movie_id, "movie_title": r.movie.title, "stars": r.stars,
                     "updated_at": r.updated_at} for r in ratings[:5]],
    }
