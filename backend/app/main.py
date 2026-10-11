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
    error_type = err["type"]
    custom_prefixes = ("movie_", "showtime_", "comment_", "predict_")
    if error_type.startswith(custom_prefixes):
        message = err["msg"]
    else:
        messages = {
            "missing": "Trường này là bắt buộc.",
            "int_parsing": "Giá trị phải là số nguyên.",
            "int_type": "Giá trị phải là số nguyên.",
            "bool_parsing": "Giá trị phải là đúng hoặc sai.",
            "bool_type": "Giá trị phải là đúng hoặc sai.",
            "list_type": "Giá trị phải là một danh sách.",
            "string_type": "Giá trị phải là chuỗi ký tự.",
            "string_too_short": "Nội dung quá ngắn.",
            "string_too_long": "Nội dung quá dài.",
            "literal_error": "Giá trị không thuộc danh sách cho phép.",
            "extra_forbidden": "Trường này không được hỗ trợ.",
            "value_error": "Giá trị không đúng định dạng yêu cầu.",
            "json_invalid": "Nội dung JSON không hợp lệ.",
        }
        message = messages.get(error_type, "Giá trị không hợp lệ.")
    return JSONResponse(
        status_code=422,
        content={"detail": f"Trường '{field}' không hợp lệ: {message}"},
    )


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
    models = []
    for item in classifier.health():
        public_item = dict(item)
        public_item["error"] = "Model không khả dụng." if item.get("error") else None
        models.append(public_item)
    return {
        "status": "ok",
        "classifier": classifier.name,
        "classifier_error": "Model được cấu hình không khả dụng." if classifier.error else None,
        "models": models,
        "active_model": classifier.name,
        "active_version": classifier.version,
    }
