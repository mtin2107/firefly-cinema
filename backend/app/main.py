from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .classifier import classifier
from .config import FRONTEND_ORIGINS
from .database import Base, engine, SessionLocal
from .routers import auth, movies, bookings, comments, admin_movies, admin_predict, admin_showtimes
from .seed import seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # tạo bảng nếu chưa có
    with SessionLocal() as db:
        seed(db)                           # thêm dữ liệu mẫu lần đầu
    yield


app = FastAPI(title="Firefly Cinema API", version="1.0.0", lifespan=lifespan)

# Cho phép giao diện React (localhost:5173) gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trả lỗi kiểm tra dữ liệu dạng 1 câu để giao diện hiển thị được
@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    err = exc.errors()[0]
    field = err["loc"][-1]
    return JSONResponse(status_code=422, content={"detail": f"Trường '{field}' không hợp lệ: {err['msg']}"})


app.include_router(auth.router)
app.include_router(movies.router)
app.include_router(bookings.router)
app.include_router(comments.router)
app.include_router(admin_movies.router)
app.include_router(admin_showtimes.router)
app.include_router(admin_predict.router)


@app.get("/api/health", tags=["Hệ thống"])
def health():
    """Kiểm tra backend đang chạy và đang dùng model nào."""
    return {
        "status": "ok",
        "classifier": classifier.name,
        "classifier_error": classifier.error,
        "models": classifier.health(),
        "active_model": classifier.name,
    }
