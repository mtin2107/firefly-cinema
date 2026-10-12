import os
from pathlib import Path

# Đọc file backend/.env nếu có (không cần cài thêm thư viện)
_env = Path(__file__).resolve().parent.parent / ".env"
if _env.exists():
    for line in _env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip())

SECRET_KEY = os.getenv("SECRET_KEY", "doi-chuoi-bi-mat-nay")
TOKEN_EXPIRE_HOURS = 24
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./firefly.db")
FRONTEND_ORIGINS = [o.strip() for o in os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")]
BANK_ID = os.getenv("BANK_ID", "").strip()
BANK_ACCOUNT = os.getenv("BANK_ACCOUNT", "").strip()
BANK_ACCOUNT_NAME = os.getenv("BANK_ACCOUNT_NAME", "").strip()

MODEL_DIR = os.getenv("MODEL_DIR", "models/phobert-binhluan")
MODEL_DIR_B = os.getenv("MODEL_DIR_B", "models/phobert-binhluan-B")
MODEL_VERSION_A = os.getenv("MODEL_VERSION_A", "A-backend").strip()
MODEL_VERSION_B = os.getenv("MODEL_VERSION_B", "").strip()
ACTIVE_MODEL = os.getenv("ACTIVE_MODEL", "phobert_b").strip().lower()
SKLEARN_MODELS = os.getenv(
    "SKLEARN_MODELS",
    "svm:../ml/artifacts/baselines/svm_A.joblib,"
    "lr:../ml/artifacts/baselines/lr_A.joblib,"
    "nb:../ml/artifacts/baselines/nb_A.joblib",
)
NEGATIVE_LABEL_ID = int(os.getenv("NEGATIVE_LABEL_ID", "1"))
USE_WORD_SEGMENT = os.getenv("USE_WORD_SEGMENT", "false").lower() == "true"
NEGATIVE_THRESHOLD = float(os.getenv("NEGATIVE_THRESHOLD", "0.5"))

# T17 chatbot; keep secrets in backend/.env (never commit the file).
CHAT_BASE_URL = os.getenv("CHAT_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/").strip()
CHAT_API_KEY = os.getenv("CHAT_API_KEY", "").strip()
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-3.8-flash").strip()
CHAT_RATE_PER_MINUTE = max(1, int(os.getenv("CHAT_RATE_PER_MINUTE", "5")))
CHAT_RATE_PER_DAY = max(1, int(os.getenv("CHAT_RATE_PER_DAY", "50")))
