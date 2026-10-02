"""
Phân loại bình luận tiêu cực.

- Nếu MODEL_DIR trỏ tới thư mục model PhoBERT đã train (save_pretrained trên Colab)
  -> dùng PhoBERT.
- Nếu chưa có model -> dùng bộ lọc từ khóa tạm thời để web vẫn chạy được.

Tiền xử lý PHẢI giống lúc train:
- Model phần A được train trên cột text_norm (chữ thường, tách dấu câu, viết đầy đủ từ viết tắt)
  và KHÔNG tách từ  -> USE_TEXT_NORM=true, USE_WORD_SEGMENT=false
"""
import os
import re
import unicodedata

from .config import MODEL_DIR, NEGATIVE_LABEL_ID, USE_WORD_SEGMENT, NEGATIVE_THRESHOLD

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


class CommentClassifier:
    def __init__(self) -> None:
        self.name = "keyword"
        self.error: str | None = None
        if MODEL_DIR and os.path.isdir(MODEL_DIR):
            try:
                import torch
                from transformers import AutoTokenizer, AutoModelForSequenceClassification

                self._torch = torch
                self._tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
                self._model = AutoModelForSequenceClassification.from_pretrained(MODEL_DIR)
                self._model.eval()
                self.name = "phobert"
                print(f"[classifier] Đã nạp PhoBERT từ {MODEL_DIR}")
            except Exception as exc:  # thiếu thư viện, sai thư mục...
                self.error = str(exc)
                print(f"[classifier] Không load được model, dùng bộ lọc từ khóa. Lỗi: {exc}")
        elif MODEL_DIR:
            self.error = f"Không tìm thấy thư mục model: {MODEL_DIR}"
            print(f"[classifier] {self.error}")

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
        """Trả về (is_negative, negative_score)."""
        if self.name == "phobert":
            inputs = self._tokenizer(self._prepare(text), return_tensors="pt",
                                     truncation=True, max_length=MAX_LENGTH)
            with self._torch.no_grad():
                probs = self._torch.softmax(self._model(**inputs).logits, dim=-1)[0]
            score = float(probs[NEGATIVE_LABEL_ID])
        else:
            lowered = text.lower()
            score = 0.87 if any(w in lowered for w in _NEGATIVE_WORDS) else 0.08
        return score >= NEGATIVE_THRESHOLD, round(score, 4)


classifier = CommentClassifier()
