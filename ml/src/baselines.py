"""Train reproducible traditional baselines for UIT-ViSFD Task A.

Hyperparameters are selected exclusively on the development split. The test
split is deliberately not loaded until every model configuration is fixed and
the final pipelines have been trained and saved.
"""

from __future__ import annotations

import argparse
import csv
import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import joblib
from sklearn.base import BaseEstimator
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

RANDOM_STATE = 42
TEXT_COLUMN = "text_norm"
LABEL_COLUMN = "has_negative"
EXPECTED_SPLITS = {
    "train": {"rows": 7786, "labels": {0: 3484, 1: 4302}},
    "dev": {"rows": 1112, "labels": {0: 516, 1: 596}},
    "test": {"rows": 2224, "labels": {0: 981, 1: 1243}},
}
MIN_DF_VALUES = (2, 3)
SUBLINEAR_TF_VALUES = (False, True)
VECTORIZER_NAMES = ("word", "char", "word_char")
RESULT_COLUMNS = (
    "model",
    "vectorizer",
    "best_params",
    "split",
    "precision_neg",
    "recall_neg",
    "f1_neg",
    "macro_f1",
    "accuracy",
    "ms_per_sentence",
    "model_size_mb",
)


@dataclass(frozen=True)
class ModelSpec:
    result_name: str
    artifact_name: str
    parameter_name: str
    parameter_values: tuple[float, ...]
    build_classifier: Callable[[float], BaseEstimator]


MODEL_SPECS = (
    ModelSpec(
        result_name="MultinomialNB",
        artifact_name="nb_A.joblib",
        parameter_name="alpha",
        parameter_values=(0.1, 0.3, 1.0),
        build_classifier=lambda value: MultinomialNB(alpha=value),
    ),
    ModelSpec(
        result_name="LogisticRegression",
        artifact_name="lr_A.joblib",
        parameter_name="C",
        parameter_values=(0.5, 1.0, 5.0),
        build_classifier=lambda value: LogisticRegression(
            C=value,
            class_weight="balanced",
            max_iter=2000,
            random_state=RANDOM_STATE,
            solver="liblinear",
        ),
    ),
    ModelSpec(
        result_name="LinearSVC",
        artifact_name="svm_A.joblib",
        parameter_name="C",
        parameter_values=(0.1, 0.3, 1.0),
        build_classifier=lambda value: LinearSVC(
            C=value,
            class_weight="balanced",
            max_iter=10000,
            random_state=RANDOM_STATE,
        ),
    ),
)


def parse_args() -> argparse.Namespace:
    project_root = Path(__file__).resolve().parents[2]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        type=Path,
        default=project_root / "data" / "uit-visfd" / "processed",
        help="Directory containing train.csv, dev.csv and test.csv.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=project_root / "ml" / "results",
        help="Directory for baselines.csv.",
    )
    parser.add_argument(
        "--artifacts",
        type=Path,
        default=project_root / "ml" / "artifacts" / "baselines",
        help="Ignored directory for complete joblib pipelines.",
    )
    parser.add_argument(
        "--drive-artifacts",
        type=Path,
        help="Optional mounted MyDrive/thesis_results/baselines directory.",
    )
    return parser.parse_args()


def load_split(data_dir: Path, split: str) -> tuple[list[str], list[int]]:
    path = data_dir / f"{split}.csv"
    if not path.is_file():
        raise FileNotFoundError(f"Missing required split: {path}")

    texts: list[str] = []
    labels: list[int] = []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        missing = {TEXT_COLUMN, LABEL_COLUMN} - set(reader.fieldnames or ())
        if missing:
            raise ValueError(f"{path} is missing columns: {sorted(missing)}")
        for row_number, row in enumerate(reader, start=2):
            text = row[TEXT_COLUMN]
            label_text = row[LABEL_COLUMN]
            if text is None or not text.strip():
                raise ValueError(f"Empty {TEXT_COLUMN} at {path}:{row_number}")
            if label_text not in {"0", "1"}:
                raise ValueError(
                    f"Invalid {LABEL_COLUMN}={label_text!r} at {path}:{row_number}"
                )
            texts.append(text)
            labels.append(int(label_text))

    label_counts = {label: labels.count(label) for label in (0, 1)}
    expected = EXPECTED_SPLITS[split]
    if len(texts) != expected["rows"] or label_counts != expected["labels"]:
        raise ValueError(
            f"{split} does not match ml/model_card_A.md: "
            f"rows={len(texts)}, labels={label_counts}, expected={expected}"
        )
    print(f"{split}: rows={len(texts)}, labels={label_counts} (model card OK)")
    return texts, labels


def build_vectorizer(name: str, min_df: int, sublinear_tf: bool) -> BaseEstimator:
    word = TfidfVectorizer(
        analyzer="word",
        ngram_range=(1, 2),
        min_df=min_df,
        sublinear_tf=sublinear_tf,
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
    raise ValueError(f"Unknown vectorizer: {name}")


def calculate_metrics(labels: list[int], predictions: list[int]) -> dict[str, float]:
    return {
        "precision_neg": precision_score(labels, predictions, pos_label=1, zero_division=0),
        "recall_neg": recall_score(labels, predictions, pos_label=1, zero_division=0),
        "f1_neg": f1_score(labels, predictions, pos_label=1, zero_division=0),
        "macro_f1": f1_score(labels, predictions, average="macro", zero_division=0),
        "accuracy": accuracy_score(labels, predictions),
    }


def tune_on_dev(
    train_texts: list[str],
    train_labels: list[int],
    dev_texts: list[str],
    dev_labels: list[int],
) -> dict[str, dict[str, object]]:
    """Select every hyperparameter using train and dev only."""
    best: dict[str, dict[str, object]] = {
        spec.result_name: {"score": -1.0, "params": None} for spec in MODEL_SPECS
    }
    candidate_count = len(VECTORIZER_NAMES) * len(MIN_DF_VALUES) * len(
        SUBLINEAR_TF_VALUES
    ) * len(MODEL_SPECS[0].parameter_values)
    print(f"Tuning {candidate_count} configurations per model on dev macro-F1...")

    for vectorizer_name in VECTORIZER_NAMES:
        for min_df in MIN_DF_VALUES:
            for sublinear_tf in SUBLINEAR_TF_VALUES:
                vectorizer = build_vectorizer(vectorizer_name, min_df, sublinear_tf)
                train_features = vectorizer.fit_transform(train_texts)
                dev_features = vectorizer.transform(dev_texts)

                for spec in MODEL_SPECS:
                    for parameter_value in spec.parameter_values:
                        classifier = spec.build_classifier(parameter_value)
                        classifier.fit(train_features, train_labels)
                        predictions = classifier.predict(dev_features)
                        score = f1_score(
                            dev_labels, predictions, average="macro", zero_division=0
                        )
                        if score > float(best[spec.result_name]["score"]):
                            best[spec.result_name] = {
                                "score": score,
                                "params": {
                                    "vectorizer": vectorizer_name,
                                    "min_df": min_df,
                                    "sublinear_tf": sublinear_tf,
                                    spec.parameter_name: parameter_value,
                                },
                            }
                print(
                    "  evaluated "
                    f"vectorizer={vectorizer_name}, min_df={min_df}, "
                    f"sublinear_tf={sublinear_tf}"
                )
    return best


def build_pipeline(spec: ModelSpec, params: dict[str, object]) -> Pipeline:
    return Pipeline(
        (
            (
                "vectorizer",
                build_vectorizer(
                    str(params["vectorizer"]),
                    int(params["min_df"]),
                    bool(params["sublinear_tf"]),
                ),
            ),
            ("classifier", spec.build_classifier(float(params[spec.parameter_name]))),
        )
    )


def train_final_pipelines(
    best: dict[str, dict[str, object]],
    train_texts: list[str],
    train_labels: list[int],
    dev_texts: list[str],
    dev_labels: list[int],
    artifact_dir: Path,
) -> tuple[dict[str, Pipeline], dict[str, dict[str, float]]]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    pipelines: dict[str, Pipeline] = {}
    dev_metrics: dict[str, dict[str, float]] = {}
    for spec in MODEL_SPECS:
        params = best[spec.result_name]["params"]
        if not isinstance(params, dict):
            raise RuntimeError(f"No selected configuration for {spec.result_name}")
        pipeline = build_pipeline(spec, params)
        pipeline.fit(train_texts, train_labels)
        dev_predictions = pipeline.predict(dev_texts)
        dev_metrics[spec.result_name] = calculate_metrics(dev_labels, dev_predictions)
        artifact_path = artifact_dir / spec.artifact_name
        joblib.dump(pipeline, artifact_path, compress=3)
        pipelines[spec.result_name] = pipeline
        print(
            f"Selected {spec.result_name}: {json.dumps(params, sort_keys=True)}, "
            f"dev_macro_f1={dev_metrics[spec.result_name]['macro_f1']:.6f}"
        )
    return pipelines, dev_metrics


def measure_cpu_latency(pipeline: Pipeline, test_texts: list[str]) -> float:
    if len(test_texts) < 1000:
        raise ValueError("At least 1,000 test sentences are required for latency measurement")
    samples = test_texts[:1000]
    pipeline.predict([samples[0]])  # Warm up outside the measurement.
    started = time.process_time_ns()
    for text in samples:
        pipeline.predict([text])
    elapsed_ns = time.process_time_ns() - started
    return elapsed_ns / 1_000_000 / len(samples)


def evaluate_test_and_write_results(
    best: dict[str, dict[str, object]],
    pipelines: dict[str, Pipeline],
    dev_metrics: dict[str, dict[str, float]],
    test_texts: list[str],
    test_labels: list[int],
    artifact_dir: Path,
    output_dir: Path,
) -> Path:
    rows: list[dict[str, object]] = []
    for spec in MODEL_SPECS:
        pipeline = pipelines[spec.result_name]
        # This is the only metric evaluation on test, after configuration selection.
        test_predictions = pipeline.predict(test_texts)
        test_metrics = calculate_metrics(test_labels, test_predictions)
        latency = measure_cpu_latency(pipeline, test_texts)
        size_mb = (artifact_dir / spec.artifact_name).stat().st_size / (1024 * 1024)
        params = best[spec.result_name]["params"]
        if not isinstance(params, dict):
            raise RuntimeError(f"No selected configuration for {spec.result_name}")
        common = {
            "model": spec.result_name,
            "vectorizer": params["vectorizer"],
            "best_params": json.dumps(params, ensure_ascii=False, sort_keys=True),
            "ms_per_sentence": round(latency, 6),
            "model_size_mb": round(size_mb, 6),
        }
        for split, metrics in (("dev", dev_metrics[spec.result_name]), ("test", test_metrics)):
            rows.append(
                {
                    **common,
                    "split": split,
                    **{key: round(value, 6) for key, value in metrics.items()},
                }
            )
        print(
            f"Test {spec.result_name}: macro_f1={test_metrics['macro_f1']:.6f}, "
            f"f1_neg={test_metrics['f1_neg']:.6f}, latency={latency:.6f} ms/sentence"
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    result_path = output_dir / "baselines.csv"
    with result_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    return result_path


def main() -> None:
    args = parse_args()
    print(f"random_state={RANDOM_STATE}")
    print("Selection phase: loading train and dev only (test remains unread).")
    train_texts, train_labels = load_split(args.data, "train")
    dev_texts, dev_labels = load_split(args.data, "dev")
    best = tune_on_dev(train_texts, train_labels, dev_texts, dev_labels)
    pipelines, dev_metrics = train_final_pipelines(
        best,
        train_texts,
        train_labels,
        dev_texts,
        dev_labels,
        args.artifacts,
    )

    print("Evaluation phase: configurations are fixed; loading test now.")
    test_texts, test_labels = load_split(args.data, "test")
    result_path = evaluate_test_and_write_results(
        best,
        pipelines,
        dev_metrics,
        test_texts,
        test_labels,
        args.artifacts,
        args.out,
    )
    if args.drive_artifacts is not None:
        args.drive_artifacts.mkdir(parents=True, exist_ok=True)
        for spec in MODEL_SPECS:
            shutil.copy2(
                args.artifacts / spec.artifact_name,
                args.drive_artifacts / spec.artifact_name,
            )
        print(f"Copied pipelines to Drive: {args.drive_artifacts.resolve()}")
    print(f"Wrote results: {result_path.resolve()}")
    print(f"Wrote pipelines: {args.artifacts.resolve()}")


if __name__ == "__main__":
    main()
