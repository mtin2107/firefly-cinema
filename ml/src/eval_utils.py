"""Shared, reproducible evaluation utilities for Firefly Cinema ML tasks.

T02 evaluates frozen artifacts only. It never fits a model or selects a
hyperparameter on the test split.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import platform
import re
import sys
import time
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Callable, Iterable, Sequence

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

RANDOM_STATE = 42
LABEL_COLUMN = "has_negative"
EXPECTED_TEST = {"rows": 2224, "labels": {0: 981, 1: 1243}}
COMPARISON_COLUMNS = (
    "model",
    "input",
    "precision_neg",
    "recall_neg",
    "f1_neg",
    "macro_f1",
    "accuracy",
    "ms_cpu",
    "ms_gpu",
    "size_mb",
)

# Verbatim preprocessing contract from backend/app/classifier.py on 2026-10-05.
_ABBR = {
    "ko": "không", "k": "không", "kh": "không", "khg": "không",
    "kg": "không", "hok": "không", "hong": "không", "đc": "được",
    "dc": "được", "đk": "được", "dk": "được", "j": "gì",
    "vs": "với", "mn": "mọi người", "ng": "người", "bt": "bình thường",
    "r": "rồi", "z": "vậy", "v": "vậy", "mik": "mình", "mk": "mình",
    "trc": "trước", "sp": "sản phẩm",
}
_PUNCT = re.compile(r'([.,!?;:()\[\]"“”…])')
_REPEAT = re.compile(r"(\w)\1{2,}")


def normalize(text: str) -> str:
    """Apply the current production preprocessing contract without mutation."""
    text = unicodedata.normalize("NFC", text).lower()
    text = _REPEAT.sub(r"\1", text)
    text = _PUNCT.sub(r" \1 ", text)
    return " ".join(_ABBR.get(word, word) for word in text.split())


def compute_metrics(y_true: Sequence[int], y_pred: Sequence[int]) -> dict[str, float]:
    """Return the canonical binary metrics; label 1 is the negative class."""
    return {
        "precision_neg": precision_score(
            y_true, y_pred, pos_label=1, zero_division=0
        ),
        "recall_neg": recall_score(y_true, y_pred, pos_label=1, zero_division=0),
        "f1_neg": f1_score(y_true, y_pred, pos_label=1, zero_division=0),
        "macro_f1": f1_score(y_true, y_pred, average="macro", zero_division=0),
        "accuracy": accuracy_score(y_true, y_pred),
    }


def load_test(path: Path) -> pd.DataFrame:
    """Load and validate the frozen UIT-ViSFD test split."""
    frame = pd.read_csv(path)
    required = {"text_norm", "text_raw", LABEL_COLUMN}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} is missing columns: {sorted(missing)}")
    labels = frame[LABEL_COLUMN].astype(int)
    actual = {"rows": len(frame), "labels": labels.value_counts().sort_index().to_dict()}
    if actual != EXPECTED_TEST:
        raise ValueError(f"Unexpected test split: {actual}; expected {EXPECTED_TEST}")
    frame = frame.copy()
    frame["normalize"] = frame["text_raw"].astype(str).map(normalize)
    return frame


def measure_cpu_latency(
    predict_one: Callable[[str], int], texts: Sequence[str], sample_count: int = 1000
) -> float:
    """Measure warm CPU batch-1 latency with perf_counter for every model."""
    if len(texts) < sample_count:
        raise ValueError(f"Need at least {sample_count} benchmark samples")
    samples = list(texts[:sample_count])
    predict_one(samples[0])
    started = time.perf_counter()
    for text in samples:
        predict_one(text)
    return (time.perf_counter() - started) * 1000 / sample_count


def artifact_size_mb(path: Path) -> float:
    files = path.rglob("*") if path.is_dir() else (path,)
    return sum(item.stat().st_size for item in files if item.is_file()) / (1024**2)


def plot_confusion_matrix(
    y_true: Sequence[int], y_pred: Sequence[int], model_name: str, path: Path
) -> None:
    matrix = confusion_matrix(y_true, y_pred, labels=[0, 1])
    display = ConfusionMatrixDisplay(
        confusion_matrix=matrix, display_labels=["Bình thường", "Tiêu cực"]
    )
    _, axis = plt.subplots(figsize=(6.4, 5.2))
    display.plot(ax=axis, cmap="Blues", colorbar=False, values_format="d")
    axis.set_title(f"Ma trận nhầm lẫn — {model_name} — text_norm")
    axis.set_xlabel("Nhãn dự đoán")
    axis.set_ylabel("Nhãn thực tế")
    plt.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(path, dpi=180)
    plt.close()


def classify_error(text: str, truth: int, prediction: int) -> str:
    lowered = text.lower()
    if any(token in lowered for token in ("không", "chẳng", "chưa", "ko ", " k ")):
        return "Phủ định"
    if any(token in lowered for token in ("nhưng", "tuy", "mỗi tội", "ngoại trừ")):
        return "Chê một phần"
    if any(token in lowered for token in ("haha", "=))", ":)", "quá tuyệt", "xin chúc mừng")):
        return "Châm biếm"
    if any(token in lowered.split() for token in _ABBR) or re.search(r"\w*(\w)\1{2,}", lowered):
        return "Từ lóng/viết tắt"
    if truth != prediction and len(lowered.split()) <= 3:
        return "Nhãn nhiễu/thiếu ngữ cảnh"
    return "Khác"


def select_errors(
    frame: pd.DataFrame, predictions: Sequence[int], count: int = 20
) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    for row_index, (truth, prediction) in enumerate(
        zip(frame[LABEL_COLUMN].astype(int), predictions)
    ):
        if truth == int(prediction):
            continue
        raw = str(frame.iloc[row_index]["text_raw"])
        candidates.append(
            {
                "index": int(frame.iloc[row_index].get("index", row_index)),
                "text": raw.replace("|", "\\|").replace("\n", " "),
                "true": int(truth),
                "pred": int(prediction),
                "group": classify_error(raw, int(truth), int(prediction)),
            }
        )
    buckets: dict[str, list[dict[str, object]]] = defaultdict(list)
    for item in candidates:
        buckets[str(item["group"])].append(item)
    selected: list[dict[str, object]] = []
    groups = (
        "Phủ định", "Chê một phần", "Châm biếm", "Từ lóng/viết tắt",
        "Nhãn nhiễu/thiếu ngữ cảnh", "Khác",
    )
    while len(selected) < count:
        added = False
        for group in groups:
            if buckets[group] and len(selected) < count:
                selected.append(buckets[group].pop(0))
                added = True
        if not added:
            break
    return selected


def environment_info() -> dict[str, object]:
    import sklearn
    import torch
    import transformers

    memory_gib = None
    try:
        import psutil

        memory_gib = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        pass
    return {
        "platform": platform.platform(),
        "processor": platform.processor() or os.environ.get("PROCESSOR_IDENTIFIER", "unknown"),
        "logical_cpu": os.cpu_count(),
        "memory_gib": memory_gib,
        "python": sys.version.split()[0],
        "scikit_learn": sklearn.__version__,
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "device": "CPU",
        "benchmark": "batch=1, warm-up=1, first 1000 test rows, time.perf_counter",
    }


def write_error_analysis(
    path: Path,
    errors: dict[str, list[dict[str, object]]],
    comparison_rows: list[dict[str, object]],
) -> None:
    counts = {
        model: Counter(str(item["group"]) for item in items)
        for model, items in errors.items()
    }
    groups = (
        "Phủ định", "Chê một phần", "Châm biếm", "Từ lóng/viết tắt",
        "Nhãn nhiễu/thiếu ngữ cảnh", "Khác",
    )
    lines = [
        "# Phân tích lỗi T02 — UIT-ViSFD test",
        "",
        "Phân tích dùng dự đoán `text_norm`. Mỗi mô hình có đúng 20 câu sai, "
        "được gán nhóm bằng quy tắc từ khóa cố định để hỗ trợ rà soát thủ công; "
        "nhóm không phải nhãn chuẩn của bộ dữ liệu.",
        "",
        "## Tổng hợp nhóm lỗi trong 20 câu/mô hình",
        "",
        "| Nhóm | PhoBERT A | SVM | Logistic Regression | Naive Bayes |",
        "|---|---:|---:|---:|---:|",
    ]
    model_order = ("PhoBERT A", "SVM", "Logistic Regression", "Naive Bayes")
    for group in groups:
        lines.append(
            "| " + group + " | " + " | ".join(str(counts[m][group]) for m in model_order) + " |"
        )
    for model in model_order:
        lines.extend(
            [
                "",
                f"## 20 câu sai — {model}",
                "",
                "| # | Index | Nhãn thật | Dự đoán | Nhóm | Câu |",
                "|---:|---:|---:|---:|---|---|",
            ]
        )
        for number, item in enumerate(errors[model], start=1):
            lines.append(
                f"| {number} | {item['index']} | {item['true']} | {item['pred']} | "
                f"{item['group']} | {item['text']} |"
            )
    by_model = {row["model"]: row for row in comparison_rows if row["input"] == "text_norm"}
    lines.extend(
        [
            "",
            "## Nhận xét trade-off",
            "",
            f"- PhoBERT A đạt F1 tiêu cực `{float(by_model['PhoBERT A']['f1_neg']):.6f}`, "
            "cao nhất nhưng có dung lượng và độ trễ CPU lớn nhất; GPU chỉ được ghi như số tham khảo lịch sử.",
            f"- SVM đạt F1 tiêu cực `{float(by_model['SVM']['f1_neg']):.6f}` và thường là lựa chọn "
            "truyền thống cân bằng nhất giữa chất lượng, tốc độ và dung lượng.",
            f"- Logistic Regression đạt `{float(by_model['Logistic Regression']['f1_neg']):.6f}`; "
            "xác suất/điểm quyết định dễ khai thác hơn SVM nếu cần hiệu chỉnh sau này.",
            f"- Naive Bayes nhỏ và đơn giản, nhưng F1 tiêu cực `{float(by_model['Naive Bayes']['f1_neg']):.6f}` "
            "thấp nhất trong bốn mô hình.",
            "- Các ví dụ sai cho thấy phủ định, câu vừa khen vừa chê và cách viết mạng xã hội vẫn là các nguồn lỗi chính; "
            "không dùng những lỗi test này để đổi siêu tham số.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")


def run_comparison(
    project_root: Path,
    benchmark_count: int = 1000,
    gpu_reference_ms: float = 1.817131,
) -> tuple[pd.DataFrame, dict[str, object]]:
    """Evaluate frozen PhoBERT/baseline artifacts and write all T02 results."""
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    torch.manual_seed(RANDOM_STATE)
    torch.set_num_threads(max(1, min(4, os.cpu_count() or 1)))

    test_path = project_root / "data" / "uit-visfd" / "processed" / "test.csv"
    artifact_dir = project_root / "ml" / "artifacts"
    result_dir = project_root / "ml" / "results"
    figure_dir = result_dir / "figures"
    frame = load_test(test_path)
    labels = frame[LABEL_COLUMN].astype(int).tolist()

    baseline_paths = {
        "SVM": artifact_dir / "baselines" / "svm_A.joblib",
        "Logistic Regression": artifact_dir / "baselines" / "lr_A.joblib",
        "Naive Bayes": artifact_dir / "baselines" / "nb_A.joblib",
    }
    predictors: dict[str, tuple[Callable[[Sequence[str]], list[int]], Callable[[str], int], Path]] = {}
    for name, artifact_path in baseline_paths.items():
        pipeline = joblib.load(artifact_path)
        predictors[name] = (
            lambda texts, model=pipeline: model.predict(list(texts)).astype(int).tolist(),
            lambda text, model=pipeline: int(model.predict([text])[0]),
            artifact_path,
        )

    phobert_path = artifact_dir / "phobert_A_best"
    tokenizer = AutoTokenizer.from_pretrained(phobert_path, local_files_only=True)
    phobert = AutoModelForSequenceClassification.from_pretrained(
        phobert_path, local_files_only=True
    ).to("cpu")
    phobert.eval()

    def predict_phobert(texts: Sequence[str], batch_size: int = 16) -> list[int]:
        predictions: list[int] = []
        for start in range(0, len(texts), batch_size):
            batch = tokenizer(
                list(texts[start : start + batch_size]),
                padding=True,
                truncation=True,
                max_length=256,
                return_tensors="pt",
            )
            with torch.inference_mode():
                logits = phobert(**batch).logits
            probabilities = torch.softmax(logits, dim=-1)[:, 1]
            predictions.extend((probabilities >= 0.5).to(torch.int64).tolist())
        return predictions

    def predict_phobert_one(text: str) -> int:
        return predict_phobert([text], batch_size=1)[0]

    predictors = {
        "PhoBERT A": (predict_phobert, predict_phobert_one, phobert_path),
        **predictors,
    }

    rows: list[dict[str, object]] = []
    errors: dict[str, list[dict[str, object]]] = {}
    predictions_by_model: dict[str, list[int]] = {}
    for model_name, (predict_many, predict_one, path) in predictors.items():
        for input_name in ("text_norm", "normalize"):
            texts = frame[input_name].astype(str).tolist()
            predictions = predict_many(texts)
            metrics = compute_metrics(labels, predictions)
            latency = measure_cpu_latency(predict_one, texts, benchmark_count)
            row = {
                "model": model_name,
                "input": input_name,
                **{key: round(value, 6) for key, value in metrics.items()},
                "ms_cpu": round(latency, 6),
                "ms_gpu": (
                    round(gpu_reference_ms, 6)
                    if model_name == "PhoBERT A" and input_name == "text_norm"
                    else ""
                ),
                "size_mb": round(artifact_size_mb(path), 6),
            }
            rows.append(row)
            print(json.dumps(row, ensure_ascii=False))
            if input_name == "text_norm":
                predictions_by_model[model_name] = predictions
                errors[model_name] = select_errors(frame, predictions)

    result_dir.mkdir(parents=True, exist_ok=True)
    comparison_path = result_dir / "comparison_A.csv"
    with comparison_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=COMPARISON_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    figure_names = {
        "PhoBERT A": "phobert",
        "SVM": "svm",
        "Logistic Regression": "lr",
        "Naive Bayes": "nb",
    }
    for model_name, predictions in predictions_by_model.items():
        plot_confusion_matrix(
            labels,
            predictions,
            model_name,
            figure_dir / f"cm_{figure_names[model_name]}_A.png",
        )
    write_error_analysis(result_dir / "error_analysis.md", errors, rows)
    info = environment_info()
    return pd.DataFrame(rows, columns=COMPARISON_COLUMNS), info


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--benchmark-count", type=int, default=1000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    comparison, info = run_comparison(args.project_root, args.benchmark_count)
    print(comparison.to_string(index=False))
    print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
