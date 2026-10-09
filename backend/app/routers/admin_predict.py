from time import perf_counter

from fastapi import APIRouter, Depends

from ..classifier import classifier
from ..models import User
from ..schemas import AdminPredictIn, AdminPredictionOut
from ..security import require_admin

router = APIRouter(prefix="/api/admin", tags=["Quản trị mô hình"])


@router.post("/predict", response_model=list[AdminPredictionOut])
def compare_models(body: AdminPredictIn, _: User = Depends(require_admin)):
    results = []
    for model in classifier.available_models():
        started = perf_counter()
        is_negative, score = model.predict(body.text)
        elapsed_ms = (perf_counter() - started) * 1000
        results.append({
            "model": model.name,
            "version": model.version,
            "label": "tieu_cuc" if is_negative else "binh_thuong",
            "score": score,
            "ms": round(elapsed_ms, 3),
        })
    return results
