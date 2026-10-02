"""
Phân loại bình luận tiêu cực.

- Nếu MODEL_DIR trỏ tới thư mục model PhoBERT đã train (save_pretrained trên Colab)
  -> dùng PhoBERT.
- Nếu chưa có model -> dùng bộ lọc từ khóa tạm thời để web vẫn chạy được.
"""
import os

from .config import MODEL_DIR, NEGATIVE_LABEL_ID, USE_WORD_SEGMENT, NEGATIVE_THRESHOLD

_NEGATIVE_WORDS = ["dở", "chán", "tệ", "phí tiền", "nhảm", "thất vọng", "rác", "kém", "buồn ngủ", "xàm", "lừa"]


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
            except Exception as exc:  # thiếu thư viện, sai thư mục...
                self.error = str(exc)
                print(f"[classifier] Không load được model, dùng bộ lọc từ khóa. Lỗi: {exc}")
        elif MODEL_DIR:
            self.error = f"Không tìm thấy thư mục model: {MODEL_DIR}"
            print(f"[classifier] {self.error}")

    # Tách từ phải GIỐNG HỆT lúc train (vd "phim hay" -> "phim hay", "thất vọng" -> "thất_vọng")
    def _segment(self, text: str) -> str:
        if not USE_WORD_SEGMENT:
            return text
        try:
            from underthesea import word_tokenize
            return word_tokenize(text, format="text")
        except ImportError:
            return text

    def predict(self, text: str) -> tuple[bool, float]:
        """Trả về (is_negative, negative_score)."""
        if self.name == "phobert":
            inputs = self._tokenizer(self._segment(text), return_tensors="pt", truncation=True, max_length=256)
            with self._torch.no_grad():
                probs = self._torch.softmax(self._model(**inputs).logits, dim=-1)[0]
            score = float(probs[NEGATIVE_LABEL_ID])
        else:
            lowered = text.lower()
            score = 0.87 if any(w in lowered for w in _NEGATIVE_WORDS) else 0.08
        return score >= NEGATIVE_THRESHOLD, round(score, 4)


classifier = CommentClassifier()
