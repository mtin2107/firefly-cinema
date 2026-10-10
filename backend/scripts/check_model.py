"""Kiểm tra parity runtime PhoBERT B với baseline tham chiếu T10."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = BACKEND_ROOT.parent
BASELINE_PATH = PROJECT_ROOT / "ml" / "test_sentences.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", default="phobert_b", choices=["phobert_b"])
    args = parser.parse_args()

    baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    cases = baseline["sentences"]
    if len(cases) != 10:
        raise SystemExit(f"Baseline phải có đúng 10 câu, nhận được {len(cases)}.")

    os.environ["ACTIVE_MODEL"] = args.model
    sys.path.insert(0, str(BACKEND_ROOT))
    from app.classifier import classifier, normalize  # noqa: PLC0415
    from app.config import MODEL_DIR_B  # noqa: PLC0415

    if classifier.name != args.model:
        raise SystemExit(
            f"Model yêu cầu {args.model} không active; runtime đang dùng {classifier.name}: "
            f"{classifier.error or 'không rõ lỗi'}"
        )

    runtime_dir = Path(MODEL_DIR_B)
    if not runtime_dir.is_absolute():
        runtime_dir = (BACKEND_ROOT / runtime_dir).resolve()
    for filename in ("model.safetensors", "config.json"):
        expected = baseline["model"]["sha256"][filename]
        actual = sha256(runtime_dir / filename)
        if actual != expected:
            raise SystemExit(f"SHA-256 {filename} sai: {actual} != {expected}")

    tolerance = float(baseline["score_tolerance"])
    passed = 0
    max_delta = 0.0
    for case in cases:
        normalized = normalize(case["text"])
        if normalized != case["normalized_text"]:
            raise SystemExit(
                f"{case['id']} normalize sai: {normalized!r} != {case['normalized_text']!r}"
            )
        is_negative, score = classifier.predict(case["text"])
        expected_score = float(case["expected_negative_score"])
        delta = abs(score - expected_score)
        max_delta = max(max_delta, delta)
        label = "tieu_cuc" if is_negative else "binh_thuong"
        ok = delta <= tolerance and label == case["expected_label"]
        passed += int(ok)
        print(
            f"{case['id']} {'PASS' if ok else 'FAIL'} "
            f"runtime={score:.6f} reference={expected_score:.12f} delta={delta:.6f} "
            f"label={label}"
        )

    print(f"PARITY={passed}/10 MAX_ABS_DELTA={max_delta:.6f} TOLERANCE={tolerance:.6f}")
    return 0 if passed == 10 and max_delta <= tolerance else 1


if __name__ == "__main__":
    raise SystemExit(main())
