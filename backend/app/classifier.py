"""Registry các mô hình phân loại bình luận tiêu cực."""
import math
import os
import re
import unicodedata
from pathlib import Path
from typing import Protocol

from .config import (
    ACTIVE_MODEL,
    MODEL_DIR,
    NEGATIVE_LABEL_ID,
    NEGATIVE_THRESHOLD,
    SKLEARN_MODELS,
    USE_WORD_SEGMENT,
)

USE_TEXT_NORM = os.getenv("USE_TEXT_NORM", "true").lower() == "true"
MAX_LENGTH = 256

_NEGATIVE_WORDS = ["dở", "chán", "tệ", "phí tiền", "nhảm", "thất vọng", "rác", "kém", "buồn ngủ", "xàm", "lừa"]

# Từ viết tắt thường gặp trong bình luận -> dạng đầy đủ (giống bước chuẩn hóa text_norm)
_ABBR = {
    "ko": "không", "k": "không", "kh": "không", "khg": "không", "kg": "không", "hok": "không", "hong": "không",
    "đc": "được", "dc": "được", "đk": "được", "dk": "được",
    "j": "gì", "vs": "với", "mn": "mọi người", "ng": "người", "bt": "bình thường",
    "r": "rồi", "z": "vậy", "v": "vậy", "mik": "mình", "mk": "mình", "trc": "trước", "sp": "sản phẩm",
}
_PUNCT = re.compile(r'([.,!?;:()\[\]"“”…])')
_REPEAT = re.compile(r"(\w)\1{2,}")  # "quáaaa" -> "quá"


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFC", text).lower()
    text = _REPEAT.sub(r"\1", text)
    text = _PUNCT.sub(r" \1 ", text)
    return " ".join(_ABBR.get(w, w) for w in text.split())


class ClassifierModel(Protocol):
    name: str
    version: str
    loaded: bool
    error: str | None

    def predict(self, text: str) -> tuple[bool, float]: ...


def _model_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    return (Path(__file__).resolve().parent.parent / path).resolve()


class PhoBertModel:
    name = "phobert"
    version = "A-backend"

    def __init__(self, model_dir: str) -> None:
        self.loaded = False
        self.error: str | None = None
        self._path = _model_path(model_dir) if model_dir else None
        if not self._path or not self._path.is_dir():
            self.error = f"Không tìm thấy thư mục model: {model_dir or '(chưa cấu hình)'}"
            return
        try:
            import torch
            from transformers import AutoModelForSequenceClassification, AutoTokenizer

            self._torch = torch
            self._tokenizer = AutoTokenizer.from_pretrained(self._path, local_files_only=True)
            self._model = AutoModelForSequenceClassification.from_pretrained(
                self._path, local_files_only=True
            )
            self._model.eval()
            self.loaded = True
            print(f"[classifier] Loaded phobert from {self._path}")
        except Exception as exc:
            self.error = str(exc)
            print(f"[classifier] Failed to load phobert: {self.error!a}")

    def _prepare(self, text: str) -> str:
        if USE_TEXT_NORM:
            text = normalize(text)
        if USE_WORD_SEGMENT:
            try:
                from underthesea import word_tokenize
                text = word_tokenize(text, format="text")
            except ImportError:
                pass
        return text

    def predict(self, text: str) -> tuple[bool, float]:
        inputs = self._tokenizer(
            self._prepare(text), return_tensors="pt", truncation=True, max_length=MAX_LENGTH
        )
        with self._torch.no_grad():
            probs = self._torch.softmax(self._model(**inputs).logits, dim=-1)[0]
        score = float(probs[NEGATIVE_LABEL_ID])
        return score >= NEGATIVE_THRESHOLD, round(score, 4)


class SklearnModel:
    def __init__(self, name: str, path_value: str) -> None:
        self.name = name
        self.version = Path(path_value).stem.rsplit("_", 1)[-1] or "A"
        self.loaded = False
        self.error: str | None = None
        self._path = _model_path(path_value)
        if not self._path.is_file():
            self.error = f"Không tìm thấy file model: {path_value}"
            print(f"[classifier] Failed to load {name}: {self.error!a}")
            return
        try:
            import joblib

            self._model = joblib.load(self._path)
            self.loaded = True
            print(f"[classifier] Loaded {name} from {self._path}")
        except Exception as exc:
            self.error = str(exc)
            print(f"[classifier] Failed to load {name}: {self.error!a}")

    def predict(self, text: str) -> tuple[bool, float]:
        prepared = normalize(text)
        if self.name == "svm":
            decision = float(self._model.decision_function([prepared])[0])
            score = (
                1.0 / (1.0 + math.exp(-decision))
                if decision >= 0
                else math.exp(decision) / (1.0 + math.exp(decision))
            )
        elif hasattr(self._model, "predict_proba"):
            classes = list(self._model.classes_)
            score = float(self._model.predict_proba([prepared])[0][classes.index(1)])
        else:
            score = float(self._model.predict([prepared])[0])
        return score >= NEGATIVE_THRESHOLD, round(score, 4)


class KeywordModel:
    name = "keyword"
    version = "1"
    loaded = True
    error = None

    def predict(self, text: str) -> tuple[bool, float]:
        lowered = text.lower()
        score = 0.87 if any(word in lowered for word in _NEGATIVE_WORDS) else 0.08
        return score >= NEGATIVE_THRESHOLD, score


class ModelRegistry:
    def __init__(self) -> None:
        self._models: dict[str, ClassifierModel] = {"phobert": PhoBertModel(MODEL_DIR)}
        for name, path in self._parse_sklearn_models(SKLEARN_MODELS):
            self._models[name] = SklearnModel(name, path)
        self._models["keyword"] = KeywordModel()
        self.requested_active_model = ACTIVE_MODEL
        requested = self._models.get(ACTIVE_MODEL)
        self.active_error = (
            requested.error if requested and not requested.loaded
            else None if requested
            else f"ACTIVE_MODEL không được cấu hình: {ACTIVE_MODEL}"
        )
        self.active = self._select_active(ACTIVE_MODEL)

    @staticmethod
    def _parse_sklearn_models(value: str) -> list[tuple[str, str]]:
        entries: list[tuple[str, str]] = []
        for raw in value.split(","):
            raw = raw.strip()
            if not raw:
                continue
            if ":" not in raw:
                print(f"[classifier] Invalid SKLEARN_MODELS entry ignored: {raw}")
                continue
            name, path = (part.strip() for part in raw.split(":", 1))
            if name and path:
                entries.append((name.lower(), path))
        return entries

    def _select_active(self, requested: str) -> ClassifierModel:
        candidates = (requested, "phobert", "keyword")
        for name in candidates:
            model = self._models.get(name)
            if model and model.loaded:
                if name != requested:
                    print(f"[classifier] ACTIVE_MODEL={requested} unavailable; using {name}")
                return model
        return self._models["keyword"]

    @property
    def name(self) -> str:
        return self.active.name

    @property
    def version(self) -> str:
        return self.active.version

    @property
    def error(self) -> str | None:
        return self.active_error

    def predict(self, text: str) -> tuple[bool, float]:
        return self.active.predict(text)

    def available_models(self) -> list[ClassifierModel]:
        primary = [model for name, model in self._models.items() if name != "keyword" and model.loaded]
        return primary or [self._models["keyword"]]

    def health(self) -> list[dict[str, object]]:
        return [
            {"name": model.name, "version": model.version, "loaded": model.loaded, "error": model.error}
            for model in self._models.values()
        ]


classifier = ModelRegistry()
