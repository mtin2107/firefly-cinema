"""Validate, de-duplicate and split the T03 Vietnamese movie-comment data."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import pandas as pd
from sklearn.metrics import cohen_kappa_score
from sklearn.model_selection import train_test_split


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import the production function instead of copying or modifying it. Prevent the
# classifier module's global instance from loading a model; T03 only needs text
# normalization and restores the caller's environment immediately afterwards.
_original_model_dir = os.environ.get("MODEL_DIR")
os.environ["MODEL_DIR"] = ""
from backend.app.classifier import normalize  # noqa: E402

if _original_model_dir is None:
    os.environ.pop("MODEL_DIR", None)
else:
    os.environ["MODEL_DIR"] = _original_model_dir


EXPECTED_COLUMNS = ["id", "text", "label", "source_type", "note"]
KAPPA_COLUMNS = ["id", "text", "label_a", "label_b"]
ALLOWED_SOURCE_TYPES = {
    "review_site",
    "social",
    "self_written",
    "web_firefly",
}
SEED = 42
MIN_FINAL_ROWS = 400
KAPPA_SAMPLE_SIZE = 100
TARGET_NEGATIVE_MIN = 0.35
TARGET_NEGATIVE_MAX = 0.60

EMAIL_RE = re.compile(r"(?i)(?<![\w.+-])[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE_RE = re.compile(
    r"(?<!\d)(?:\+?84|0)(?:[ .-]*\d){9}(?!\d)"
)
USERNAME_RE = re.compile(r"(?<![\w@])@[A-Za-z0-9_](?:[A-Za-z0-9_.]{1,29})")


class DataValidationError(ValueError):
    """Raised when input data violates a hard validation rule."""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Chuẩn bị dữ liệu bình luận phim T03 (seed=42)."
    )
    parser.add_argument("--input", type=Path, required=True, help="CSV dữ liệu gốc")
    parser.add_argument("--out", type=Path, required=True, help="Thư mục CSV đầu ra")
    return parser.parse_args()


def read_raw_data(path: Path) -> pd.DataFrame:
    if not path.is_file():
        raise DataValidationError(f"Không tìm thấy input: {path}")

    frame = pd.read_csv(path, dtype=str, keep_default_na=False, encoding="utf-8-sig")
    actual_columns = list(frame.columns)
    if actual_columns != EXPECTED_COLUMNS:
        raise DataValidationError(
            "Schema không hợp lệ. "
            f"Cần đúng thứ tự {EXPECTED_COLUMNS}, nhận được {actual_columns}."
        )

    if frame.empty:
        return frame

    for column in ("id", "text", "label", "source_type"):
        blank_ids = frame.index[frame[column].str.strip().eq("")].tolist()
        if blank_ids:
            rows = [index + 2 for index in blank_ids[:10]]
            raise DataValidationError(
                f"Cột {column!r} bị trống tại dòng CSV {rows}."
            )

    frame["id"] = frame["id"].str.strip()
    duplicate_ids = frame.loc[frame["id"].duplicated(keep=False), "id"].unique()
    if len(duplicate_ids):
        raise DataValidationError(
            f"ID phải duy nhất; ID trùng: {duplicate_ids[:10].tolist()}"
        )

    invalid_labels = sorted(set(frame["label"]) - {"0", "1"})
    if invalid_labels:
        raise DataValidationError(
            f"label chỉ được là 0 hoặc 1; giá trị sai: {invalid_labels[:10]}"
        )
    frame["label"] = frame["label"].astype(int)

    invalid_sources = sorted(set(frame["source_type"]) - ALLOWED_SOURCE_TYPES)
    if invalid_sources:
        raise DataValidationError(
            "source_type chỉ thuộc "
            f"{sorted(ALLOWED_SOURCE_TYPES)}; giá trị sai: {invalid_sources[:10]}"
        )
    return frame


def scan_pii(frame: pd.DataFrame) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    checks = (("email", EMAIL_RE), ("phone", PHONE_RE), ("username", USERNAME_RE))
    for _, row in frame.iterrows():
        for column in ("text", "note"):
            value = str(row[column])
            for pii_type, pattern in checks:
                if pattern.search(value):
                    findings.append(
                        {"id": str(row["id"]), "column": column, "type": pii_type}
                    )
    return findings


def remove_normalized_duplicates(frame: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    if frame.empty:
        return frame.copy(), 0
    normalized = frame["text"].map(normalize)
    empty_ids = frame.loc[normalized.eq(""), "id"].tolist()
    if empty_ids:
        raise DataValidationError(
            f"text rỗng sau normalize() tại ID: {empty_ids[:10]}"
        )
    duplicate_mask = normalized.duplicated(keep="first")
    cleaned = frame.loc[~duplicate_mask].copy()
    cleaned["_normalized"] = normalized.loc[~duplicate_mask]
    return cleaned, int(duplicate_mask.sum())


def split_data(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    counts = frame["label"].value_counts()
    if set(counts.index) != {0, 1} or int(counts.min()) < 2:
        raise DataValidationError(
            "Cần cả hai nhãn và ít nhất 2 dòng mỗi nhãn để chia stratified 70/30."
        )
    train, test = train_test_split(
        frame,
        test_size=0.30,
        random_state=SEED,
        stratify=frame["label"],
    )
    return train.copy(), test.copy()


def cross_split_duplicate_count(train: pd.DataFrame, test: pd.DataFrame) -> int:
    return len(set(train["_normalized"]) & set(test["_normalized"]))


def write_split(frame: pd.DataFrame, path: Path) -> None:
    frame[EXPECTED_COLUMNS].to_csv(path, index=False, encoding="utf-8-sig")


def prepare_kappa_sample(
    frame: pd.DataFrame, sample_path: Path
) -> tuple[str, float | None]:
    expected = frame.sample(n=KAPPA_SAMPLE_SIZE, random_state=SEED)
    expected_ids = expected["id"].tolist()

    if not sample_path.exists():
        sample = expected[["id", "text", "label"]].rename(
            columns={"label": "label_a"}
        )
        sample["label_b"] = ""
        sample[KAPPA_COLUMNS].to_csv(sample_path, index=False, encoding="utf-8-sig")
        return "WAITING_FOR_HUMAN_LABEL", None

    sample = pd.read_csv(
        sample_path, dtype=str, keep_default_na=False, encoding="utf-8-sig"
    )
    if list(sample.columns) != KAPPA_COLUMNS:
        raise DataValidationError(
            f"Schema kappa_sample.csv phải đúng {KAPPA_COLUMNS}."
        )
    if len(sample) != KAPPA_SAMPLE_SIZE:
        raise DataValidationError(
            f"kappa_sample.csv phải có đúng {KAPPA_SAMPLE_SIZE} dòng."
        )
    if sample["id"].tolist() != expected_ids:
        raise DataValidationError(
            "ID trong kappa_sample.csv không khớp mẫu random_state=42 của dữ liệu hiện tại. "
            "Không ghi đè nhãn người thật; hãy kiểm tra việc thay đổi dataset."
        )

    expected_labels = expected["label"].astype(str).tolist()
    if sample["label_a"].tolist() != expected_labels:
        raise DataValidationError(
            "label_a trong kappa_sample.csv không khớp nhãn của Annotator A trong dataset."
        )

    invalid_b = sorted(set(sample["label_b"]) - {"", "0", "1"})
    if invalid_b:
        raise DataValidationError(
            f"label_b chỉ được để trống hoặc là 0/1; giá trị sai: {invalid_b[:10]}"
        )
    missing_b = int(sample["label_b"].eq("").sum())
    if missing_b:
        return f"WAITING_FOR_HUMAN_LABEL ({missing_b}/100 chưa gán)", None

    kappa = float(
        cohen_kappa_score(
            sample["label_a"].astype(int), sample["label_b"].astype(int)
        )
    )
    status = "KAPPA_ACCEPTED" if kappa >= 0.6 else "KAPPA_BELOW_THRESHOLD"
    return status, kappa


def percentage(value: int, total: int) -> str:
    return f"{value / total:.2%}" if total else "N/A"


def distribution_lines(frame: pd.DataFrame, column: str) -> list[str]:
    if frame.empty:
        return ["- Chưa có dữ liệu."]
    counts = frame[column].value_counts().sort_index()
    return [
        f"- `{key}`: {int(count)} ({percentage(int(count), len(frame))})"
        for key, count in counts.items()
    ]


def collection_coverage_lines(frame: pd.DataFrame) -> list[str]:
    """Summarize the project-specific provenance encoded in the note column."""
    if frame.empty:
        return ["- Chưa có dữ liệu."]

    notes = frame["note"].astype(str)
    origins = notes.str.split("|", n=1).str[0].str.strip()
    origin_counts = origins[origins.ne("")].value_counts()
    lines = [
        f"- `{origin}`: {int(count)} ({percentage(int(count), len(frame))})"
        for origin, count in origin_counts.items()
    ]

    movie_mask = notes.str.contains(r"\|\s*phim:", case=False, regex=True)
    cinema_mask = notes.str.contains(r"\|\s*rạp:", case=False, regex=True)
    movie_names = notes.loc[movie_mask].str.split(":", n=1).str[1].str.strip()
    cinema_names = notes.loc[cinema_mask].str.split(":", n=1).str[1].str.strip()
    lines.extend(
        [
            f"- Phim: {movie_names.nunique()} phim, {int(movie_mask.sum())} câu.",
            f"- Rạp: {cinema_names.nunique()} rạp, {int(cinema_mask.sum())} câu.",
        ]
    )
    return lines


def write_stats(
    *,
    raw_rows: int,
    duplicate_removed: int,
    cleaned: pd.DataFrame,
    train_size: int | None,
    test_size: int | None,
    cross_duplicates: int | None,
    pii_findings: list[dict[str, str]],
    kappa_status: str,
    kappa: float | None,
    workflow_status: str,
) -> None:
    stats_path = REPO_ROOT / "ml" / "results" / "movie_data_stats.md"
    label_lines = distribution_lines(cleaned, "label")
    source_lines = distribution_lines(cleaned, "source_type")
    coverage_lines = collection_coverage_lines(cleaned)
    kappa_value = f"{kappa:.6f}" if kappa is not None else "Chưa có"
    split_value = (
        f"train={train_size}, test={test_size}"
        if train_size is not None and test_size is not None
        else "Chưa tạo"
    )
    cross_value = str(cross_duplicates) if cross_duplicates is not None else "Chưa đo"
    pii_value = "0 phát hiện" if not pii_findings else f"{len(pii_findings)} phát hiện"

    content = [
        "# Thống kê dữ liệu bình luận phim — T03",
        "",
        "> File này do `ml/src/prepare_movie_data.py` cập nhật từ dữ liệu cục bộ ngoài Git. Không điền metric thủ công.",
        "",
        f"- Trạng thái: **{workflow_status}**",
        f"- Raw rows: {raw_rows}",
        f"- Duplicate removed sau `normalize()`: {duplicate_removed}",
        f"- Final rows: {len(cleaned)}",
        f"- Train/test size: {split_value}",
        f"- Duplicate cross-split count sau `normalize()`: {cross_value}",
        f"- PII scan: {pii_value}",
        f"- Kappa: {kappa_value} ({kappa_status})",
        f"- Seed: {SEED}",
        "",
        "## Phân bố nhãn",
        "",
        *label_lines,
        "",
        "## Phân bố source_type",
        "",
        *source_lines,
        "",
        "## Nguồn cụ thể và độ phủ",
        "",
        *coverage_lines,
        "",
        "## Ghi chú nghiệm thu",
        "",
        "- Mục tiêu dữ liệu cuối: 400–600 câu sau khử trùng lặp.",
        "- Mục tiêu label 1: 35–60%. Dữ liệu thật có 67,94%; PO đã chọn phương án A ngày 08/10/2026: chấp nhận độ lệch, không thêm/bớt câu và không sửa nhãn. Điều kiện này chỉ cảnh báo, không chặn gate.",
        "- Cohen's kappa chỉ được ghi khi `label_b` của 100 câu do người thật gán đầy đủ.",
        "",
    ]
    stats_path.write_text("\n".join(content), encoding="utf-8")


def main() -> int:
    args = parse_args()
    input_path = args.input.resolve()
    out_dir = args.out.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        raw = read_raw_data(input_path)
        raw_rows = len(raw)
        pii_findings = scan_pii(raw)
        if pii_findings:
            details = ", ".join(
                f"id={item['id']}:{item['column']}:{item['type']}"
                for item in pii_findings[:20]
            )
            raise DataValidationError(
                f"Phát hiện PII ({len(pii_findings)}): {details}. "
                "Hãy loại PII khỏi dữ liệu gốc trước khi tạo split."
            )

        cleaned, duplicate_removed = remove_normalized_duplicates(raw)
        print(f"Raw rows: {raw_rows}")
        print(f"Duplicate removed after normalize(): {duplicate_removed}")
        print(f"Final rows: {len(cleaned)}")
        print("PII scan: 0 findings")

        if cleaned.empty:
            status = "WAITING_FOR_DATA"
            write_stats(
                raw_rows=raw_rows,
                duplicate_removed=duplicate_removed,
                cleaned=cleaned,
                train_size=None,
                test_size=None,
                cross_duplicates=None,
                pii_findings=[],
                kappa_status="WAITING_FOR_DATA",
                kappa=None,
                workflow_status=status,
            )
            print(f"STATUS: {status} — CSV mới có header, chưa có bình luận thật.")
            return 0

        negative_count = int(cleaned["label"].eq(1).sum())
        negative_ratio = negative_count / len(cleaned)
        print(f"Label 1 ratio: {negative_ratio:.2%}")
        label_ratio_ok = TARGET_NEGATIVE_MIN <= negative_ratio <= TARGET_NEGATIVE_MAX
        if not label_ratio_ok:
            print(
                "WARNING: Tỷ lệ label 1 ngoài mục tiêu 35–60%; "
                "PO đã chấp nhận theo phương án A ngày 08/10/2026 (không chặn gate)."
            )

        source_counts = cleaned["source_type"].value_counts()
        primary_count = int(
            source_counts.get("review_site", 0) + source_counts.get("social", 0)
        )
        self_written_count = int(source_counts.get("self_written", 0))
        primary_ratio = primary_count / len(cleaned)
        self_written_ratio = self_written_count / len(cleaned)
        print(f"review_site + social ratio: {primary_ratio:.2%}")
        print(f"self_written ratio: {self_written_ratio:.2%}")
        primary_source_ok = primary_ratio >= 0.80
        self_written_ok = self_written_ratio <= 0.20
        if not primary_source_ok:
            print("WARNING: review_site + social chưa đạt tối thiểu 80%.")
        if not self_written_ok:
            print("WARNING: self_written vượt tối đa 20%.")
        size_upper_bound_ok = len(cleaned) <= 600
        if not size_upper_bound_ok:
            print("WARNING: Dữ liệu vượt mục tiêu tối đa 600 câu.")

        train, test = split_data(cleaned)
        cross_duplicates = cross_split_duplicate_count(train, test)
        if cross_duplicates:
            raise DataValidationError(
                f"Có {cross_duplicates} duplicate sau normalize() giữa train/test."
            )
        write_split(train, out_dir / "movie_train.csv")
        write_split(test, out_dir / "movie_test.csv")
        print(f"Train/test rows: {len(train)}/{len(test)}")
        print(f"Cross-split normalized duplicates: {cross_duplicates}")

        if len(cleaned) < MIN_FINAL_ROWS:
            kappa_status = "WAITING_FOR_DATA"
            kappa = None
            workflow_status = "BLOCKED_BY_DATA_COLLECTION"
            print(
                f"STATUS: {workflow_status} — cần ít nhất {MIN_FINAL_ROWS} câu, "
                f"hiện có {len(cleaned)}."
            )
        else:
            kappa_status, kappa = prepare_kappa_sample(
                cleaned, out_dir / "kappa_sample.csv"
            )
            if kappa_status.startswith("WAITING_FOR_HUMAN_LABEL"):
                workflow_status = "WAITING_FOR_HUMAN_LABEL"
            elif kappa_status == "KAPPA_BELOW_THRESHOLD":
                workflow_status = "KAPPA_BELOW_THRESHOLD"
            elif not all((primary_source_ok, self_written_ok, size_upper_bound_ok)):
                workflow_status = "BLOCKED_BY_DATA_QUALITY"
            else:
                workflow_status = "READY_FOR_AC_REVIEW"
            print(f"Kappa: {kappa if kappa is not None else 'chưa có'}")
            print(f"STATUS: {workflow_status} ({kappa_status})")

        write_stats(
            raw_rows=raw_rows,
            duplicate_removed=duplicate_removed,
            cleaned=cleaned,
            train_size=len(train),
            test_size=len(test),
            cross_duplicates=cross_duplicates,
            pii_findings=[],
            kappa_status=kappa_status,
            kappa=kappa,
            workflow_status=workflow_status,
        )
        return 0
    except (DataValidationError, pd.errors.ParserError, UnicodeDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
