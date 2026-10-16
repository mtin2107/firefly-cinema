from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User
from ..rate_limit import SlidingWindowRateLimiter
from ..schemas import ChangePasswordIn, LoginIn, RegisterIn, TokenOut, UpdateProfileIn, UserOut
from ..security import hash_password, verify_password, create_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["Tài khoản"])
_login_failures = SlidingWindowRateLimiter()
_LOGIN_LIMIT_MESSAGE = "Bạn đăng nhập sai quá nhiều lần. Hãy thử lại sau 5 phút."


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
    if not verify_password(body.current_password, user.password_hash):
        raise HTTPException(400, "Mật khẩu hiện tại không đúng.")
    user.password_hash = hash_password(body.new_password)
    db.commit()
    return {"detail": "Đã đổi mật khẩu."}
