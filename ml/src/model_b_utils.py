"""Shared, CPU-testable utilities for the T09 PhoBERT B experiment.

This module deliberately contains no final-test orchestration.  The T09
notebook locks every validation-based choice before it loads either fixed test
set, so importing helpers here cannot accidentally expose test data to model
selection.
"""

from __future__ import annotations

import hashlib
import json
import os
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import joblib
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

try:
    import torch
except ImportError:  # Traditional CPU gates do not require PyTorch.
    torch = None

SEED = 42
MOVIE_VALIDATION_SIZE = 0.15
LABELS = {0: "binh_thuong", 1: "tieu_cuc"}
METRIC_COLUMNS = ("precision_neg", "recall_neg", "f1_neg", "macro_f1")


def seed_everything(seed: int = SEED) -> None:
    """Set every random source used by the notebook and CPU baselines."""

    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    if torch is not None:
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
        torch.use_deterministic_algorithms(True, warn_only=True)


def discover_project_root(start: Path | None = None) -> Path:
    """Find the repository without assuming the notebook working directory."""

    candidates: list[Path] = []
    explicit = os.environ.get("FIREFLY_PROJECT_ROOT")
    if explicit:
        candidates.append(Path(explicit))
    current = (start or Path.cwd()).resolve()
    candidates.extend([current, *current.parents, Path("/content/firefly-cinema")])
    for candidate in candidates:
        if (candidate / "ml" / "src" / "eval_utils.py").is_file():
            return candidate.resolve()
    raise FileNotFoundError(
        "Không tìm thấy repo Firefly Cinema. Hãy đặt FIREFLY_PROJECT_ROOT hoặc "
        "clone/upload repo vào /content/firefly-cinema."
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _require_columns(frame: pd.DataFrame, path: Path, required: set[str]) -> None:
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"{path} thiếu cột: {sorted(missing)}")


def _validate_binary_labels(values: pd.Series, path: Path) -> None:
    labels = set(values.dropna().astype(int).unique().tolist())
    if labels != {0, 1}:
        raise ValueError(f"{path} phải có đủ nhãn 0 và 1, nhận được {sorted(labels)}")


def load_movie_train(path: Path) -> pd.DataFrame:
    frame = pd.read_csv(path, encoding="utf-8-sig")
    _require_columns(frame, path, {"id", "text", "label"})
    if frame.shape[0] != 347:
        raise ValueError(f"movie_train phải có 347 dòng, nhận được {frame.shape[0]}")
    if frame[["id", "text", "label"]].isna().any().any():
        raise ValueError(f"{path} có dữ liệu rỗng")
    _validate_binary_labels(frame["label"], path)
    return frame.copy()


def load_phone_pool(train_path: Path, dev_path: Path) -> pd.DataFrame:
    frames = []
    for path, expected_rows in ((train_path, 7786), (dev_path, 1112)):
        frame = pd.read_csv(path, encoding="utf-8-sig")
        _require_columns(frame, path, {"text_raw", "has_negative"})
        if frame.shape[0] != expected_rows:
            raise ValueError(
                f"{path.name} phải có {expected_rows} dòng, nhận được {frame.shape[0]}"
            )
        if frame[["text_raw", "has_negative"]].isna().any().any():
            raise ValueError(f"{path} có dữ liệu rỗng")
        frames.append(
            frame[["text_raw", "has_negative"]].rename(
                columns={"text_raw": "text", "has_negative": "label"}
            )
        )
    result = pd.concat(frames, ignore_index=True)
    _validate_binary_labels(result["label"], train_path.parent)
    return result


def stratified_movie_split(
    movie_train: pd.DataFrame,
    validation_size: float = MOVIE_VALIDATION_SIZE,
    seed: int = SEED,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    train, validation = train_test_split(
        movie_train,
        test_size=validation_size,
        random_state=seed,
        stratify=movie_train["label"],
    )
    return (
        train.sort_index().reset_index(drop=True),
        validation.sort_index().reset_index(drop=True),
    )


def stratified_phone_sample(
    phone_pool: pd.DataFrame, sample_size: int, seed: int = SEED
) -> pd.DataFrame:
    if sample_size > len(phone_pool):
        raise ValueError("Không đủ dữ liệu phone cho mẫu 1:1")
    sampled, _ = train_test_split(
        phone_pool,
        train_size=sample_size,
        random_state=seed,
        stratify=phone_pool["label"],
    )
    return sampled.sort_index().reset_index(drop=True)


def build_training_configs(
    movie_train_part: pd.DataFrame,
    phone_pool: pd.DataFrame,
    normalize_fn,
    seed: int = SEED,
) -> dict[str, pd.DataFrame]:
    movie = movie_train_part[["text", "label"]].copy()
    movie["text"] = movie["text"].map(normalize_fn)
    phone = stratified_phone_sample(phone_pool, len(movie), seed=seed)
    phone["text"] = phone["text"].map(normalize_fn)
    if movie["text"].eq("").any() or phone["text"].eq("").any():
        raise ValueError("Có text rỗng sau normalize()")
    return {
        "a": movie.reset_index(drop=True),
        "b": pd.concat([movie, phone], ignore_index=True),
    }


def metrics(labels: Sequence[int], predictions: Sequence[int]) -> dict[str, float]:
    return {
        "precision_neg": precision_score(
            labels, predictions, pos_label=1, zero_division=0
        ),
        "recall_neg": recall_score(labels, predictions, pos_label=1, zero_division=0),
        "f1_neg": f1_score(labels, predictions, pos_label=1, zero_division=0),
        "macro_f1": f1_score(labels, predictions, average="macro", zero_division=0),
    }


def constant_positive_metrics(labels: Sequence[int]) -> dict[str, float]:
    return metrics(labels, np.ones(len(labels), dtype=int))


@dataclass(frozen=True)
class TraditionalSpec:
    display_name: str
    artifact_stem: str
    parameter_name: str
    parameter_values: tuple[float, ...]


TRADITIONAL_SPECS = (
    TraditionalSpec("SVM", "svm", "C", (0.1, 0.3, 1.0)),
    TraditionalSpec("Logistic Regression", "lr", "C", (0.5, 1.0, 5.0)),
    TraditionalSpec("Naive Bayes", "nb", "alpha", (0.1, 0.3, 1.0)),
)
VECTORIZERS = ("word", "char", "word_char")
MIN_DF_VALUES = (2, 3)
SUBLINEAR_TF_VALUES = (False, True)


def _vectorizer(name: str, min_df: int, sublinear_tf: bool) -> BaseEstimator:
    word = TfidfVectorizer(
        analyzer="word", ngram_range=(1, 2), min_df=min_df, sublinear_tf=sublinear_tf
    )
    char = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(2, 5),
        min_df=min_df,
        sublinear_tf=sublinear_tf,
        max_features=150_000,
    )
    if name == "word":
        return word
    if name == "char":
        return char
    if name == "word_char":
        return FeatureUnion((("word", word), ("char", char)))
    raise ValueError(f"Vectorizer không hỗ trợ: {name}")


def _classifier(spec: TraditionalSpec, value: float) -> BaseEstimator:
    if spec.display_name == "SVM":
        return LinearSVC(
            C=value,
            class_weight="balanced",
            max_iter=10_000,
            random_state=SEED,
        )
    if spec.display_name == "Logistic Regression":
        return LogisticRegression(
            C=value,
            class_weight="balanced",
            max_iter=2_000,
            random_state=SEED,
            solver="liblinear",
        )
    return MultinomialNB(alpha=value)


def _pipeline(spec: TraditionalSpec, params: Mapping[str, object]) -> Pipeline:
    return Pipeline(
        (
            (
                "vectorizer",
                _vectorizer(
                    str(params["vectorizer"]),
                    int(params["min_df"]),
                    bool(params["sublinear_tf"]),
                ),
            ),
            (
                "classifier",
                _classifier(spec, float(params[spec.parameter_name])),
            ),
        )
    )


def select_traditional_models(
    configs: Mapping[str, pd.DataFrame], validation: pd.DataFrame, normalize_fn
) -> tuple[dict[str, dict[str, object]], pd.DataFrame]:
    """Select config and hyperparameters exclusively on movie validation macro-F1."""

    validation_texts = validation["text"].map(normalize_fn).tolist()
    validation_labels = validation["label"].astype(int).tolist()
    best: dict[str, dict[str, object]] = {}
    rows: list[dict[str, object]] = []
    for config_name in ("a", "b"):
        training = configs[config_name]
        for vectorizer_name in VECTORIZERS:
            for min_df in MIN_DF_VALUES:
                for sublinear_tf in SUBLINEAR_TF_VALUES:
                    for spec in TRADITIONAL_SPECS:
                        for value in spec.parameter_values:
                            params = {
                                "vectorizer": vectorizer_name,
                                "min_df": min_df,
                                "sublinear_tf": sublinear_tf,
                                spec.parameter_name: value,
                            }
                            model = _pipeline(spec, params)
                            model.fit(training["text"], training["label"])
                            score = metrics(
                                validation_labels, model.predict(validation_texts)
                            )
                            row = {
                                "model": spec.display_name,
                                "train_config": config_name,
                                **params,
                                **score,
                            }
                            rows.append(row)
                            candidate_key = (
                                score["macro_f1"],
                                score["f1_neg"],
                                -(("a", "b").index(config_name)),
                            )
                            current = best.get(spec.display_name)
                            if current is None or candidate_key > current["selection_key"]:
                                best[spec.display_name] = {
                                    "train_config": config_name,
                                    "params": params,
                                    "validation_metrics": score,
                                    "selection_key": candidate_key,
                                }
    for selected in best.values():
        selected.pop("selection_key", None)
    return best, pd.DataFrame(rows)


def fit_selected_traditional_models(
    selections: Mapping[str, Mapping[str, object]],
    final_configs: Mapping[str, pd.DataFrame],
    artifact_dir: Path,
) -> dict[str, Pipeline]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    models: dict[str, Pipeline] = {}
    specs = {spec.display_name: spec for spec in TRADITIONAL_SPECS}
    for name, selection in selections.items():
        spec = specs[name]
        config_name = str(selection["train_config"])
        params = selection["params"]
        if not isinstance(params, Mapping):
            raise TypeError(f"Params không hợp lệ cho {name}")
        model = _pipeline(spec, params)
        training = final_configs[config_name]
        model.fit(training["text"], training["label"])
        joblib.dump(model, artifact_dir / f"{spec.artifact_stem}_B_best.joblib", compress=3)
        models[name] = model
    return models


def selection_manifest(
    movie_train_path: Path,
    phone_train_path: Path,
    phone_dev_path: Path,
    movie_train_part: pd.DataFrame,
    movie_validation: pd.DataFrame,
    traditional_selections: Mapping[str, Mapping[str, object]],
    phobert_selection: Mapping[str, object],
) -> dict[str, object]:
    """Build the immutable record written before either test set is loaded."""

    return {
        "seed": SEED,
        "movie_validation_size": MOVIE_VALIDATION_SIZE,
        "labels": LABELS,
        "max_length": 256,
        "data_hashes": {
            "movie_train": sha256(movie_train_path),
            "phone_train": sha256(phone_train_path),
            "phone_dev": sha256(phone_dev_path),
        },
        "split": {
            "movie_train_rows": len(movie_train_part),
            "movie_validation_rows": len(movie_validation),
            "movie_train_ids_sha256": hashlib.sha256(
                "\n".join(movie_train_part["id"].astype(str)).encode("utf-8")
            ).hexdigest(),
            "movie_validation_ids_sha256": hashlib.sha256(
                "\n".join(movie_validation["id"].astype(str)).encode("utf-8")
            ).hexdigest(),
        },
        "traditional_selections": traditional_selections,
        "phobert_selection": phobert_selection,
        "selection_rule": "max movie validation macro_f1, then f1_neg; never test",
        "test_loaded": False,
    }


def write_json(path: Path, value: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )


def comparison_rows(
    model_name: str,
    train_config: str,
    labels_by_test: Mapping[str, Sequence[int]],
    predictions_by_test: Mapping[str, Sequence[int]],
) -> list[dict[str, object]]:
    rows = []
    for test_set in ("phone", "movie"):
        score = metrics(labels_by_test[test_set], predictions_by_test[test_set])
        rows.append(
            {
                "model": model_name,
                "train_config": train_config,
                "test_set": test_set,
                **{key: round(score[key], 6) for key in METRIC_COLUMNS},
            }
        )
    return rows


def assert_comparison_schema(frame: pd.DataFrame) -> None:
    expected = ["model", "train_config", "test_set", *METRIC_COLUMNS]
    if frame.columns.tolist() != expected:
        raise ValueError(f"Schema comparison_B sai: {frame.columns.tolist()} != {expected}")
    required_models = {
        "PhoBERT A",
        "PhoBERT B",
        "SVM A",
        "SVM B",
        "Logistic Regression A",
        "Logistic Regression B",
        "Naive Bayes A",
        "Naive Bayes B",
    }
    missing = required_models - set(frame["model"])
    if missing:
        raise ValueError(f"comparison_B thiếu model: {sorted(missing)}")
    for model in required_models:
        tests = set(frame.loc[frame["model"] == model, "test_set"])
        if tests != {"phone", "movie"}:
            raise ValueError(f"{model} thiếu kết quả hai test: {sorted(tests)}")
