#!/usr/bin/env python3
"""DRAFT ONLY: run API write smoke tests exclusively against a new DB clone."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import os
import socket
import sqlite3
import subprocess
import sys
import time
import urllib.error
import urllib.request
from contextlib import closing
from pathlib import Path

APPROVED_DECISION_ID = "PO-DECISION-T10-REALDB-A1-GATE2-20261010"
EXPECTED_REPO = Path(r"C:\Projects\firefly-cinema")
EXPECTED_SOURCE = EXPECTED_REPO / "backend" / "firefly.db"
EXPECTED_PYTHON = EXPECTED_REPO / "backend" / "venv" / "Scripts" / "python.exe"
PORT = 18110
PACKAGE_FILES = (
    "01_preflight.ps1", "02_fresh_backup.py", "03_schema_alter.py",
    "04_postverify.py", "05_clone_smoke.py", "T10_GATE2_EXECUTION_PACKAGE_DRAFT.md",
)
ISOLATED_BOOTSTRAP = r'''
import os
from pathlib import Path

from app.config import DATABASE_URL

expected = Path(os.environ["T10_EXPECTED_CLONE"]).resolve(strict=True)
forbidden = Path(os.environ["T10_FORBIDDEN_REAL_DB"]).resolve(strict=True)
expected_url = "sqlite:///" + expected.as_posix()
if DATABASE_URL != expected_url:
    raise SystemExit(f"HARD STOP: effective DATABASE_URL mismatch: {DATABASE_URL!r}")
configured = Path(DATABASE_URL[len("sqlite:///"):]).resolve(strict=True)
if configured != expected or configured == forbidden:
    raise SystemExit(f"HARD STOP: effective database path is not isolated: {configured}")
print(f"EFFECTIVE_DATABASE_VERIFIED={configured}", flush=True)

import uvicorn
uvicorn.run("app.main:app", host="127.0.0.1", port=int(os.environ["T10_SMOKE_PORT"]))
'''


def hard_stop(message: str) -> "NoReturn":
    raise RuntimeError(f"HARD STOP: {message}")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def independent_package_hashes() -> tuple[dict[str, str], str]:
    package_dir = Path(__file__).resolve().parent
    values = {name: sha256_file(package_dir / name) for name in PACKAGE_FILES}
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":")).encode("ascii")
    return values, hashlib.sha256(canonical).hexdigest().upper()


def load_helpers():
    path = Path(__file__).with_name("02_fresh_backup.py")
    spec = importlib.util.spec_from_file_location("t10_backup_helpers", path)
    if spec is None or spec.loader is None:
        hard_stop("cannot load reviewed backup helper module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def request(method: str, path: str, token: str | None = None, body: dict | None = None) -> tuple[int, object]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(
        f"http://127.0.0.1:{PORT}{path}", data=data, headers=headers, method=method
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            raw = response.read()
            return response.status, json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read()
        return exc.code, json.loads(raw) if raw else None


def wait_for_health(process: subprocess.Popen, timeout: int = 180) -> dict:
    deadline = time.monotonic() + timeout
    last_error = "not started"
    while time.monotonic() < deadline:
        if process.poll() is not None:
            hard_stop(f"clone backend exited early with code {process.returncode}")
        try:
            status, payload = request("GET", "/api/health")
            if status == 200 and isinstance(payload, dict):
                return payload
        except Exception as exc:
            last_error = str(exc)
        time.sleep(1)
    hard_stop(f"clone backend health timeout: {last_error}")


def stop_backend(process: subprocess.Popen) -> None:
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=10)


def verify_clone_isolation(clone: Path, smoke_dir: Path, helpers) -> Path:
    resolved_smoke = smoke_dir.resolve(strict=True)
    resolved_clone = clone.resolve(strict=True)
    source = EXPECTED_SOURCE.resolve(strict=True)
    if resolved_clone != resolved_smoke / "firefly_t10_smoke.db":
        hard_stop(f"clone path is outside the exact allowed smoke target: {resolved_clone}")
    if resolved_clone == source or resolved_clone.is_symlink():
        hard_stop("clone resolves to the real database or is a symlink")
    with closing(helpers.open_read_only(resolved_clone)) as conn:
        current = helpers.snapshot(conn)
        helpers.validate_snapshot("smoke clone isolation check", current)
        columns = current["tables"]["comments"]["columns"]
        matches = [row for row in columns if row[1] == "model_version"]
        if matches != [[len(columns) - 1, "model_version", "VARCHAR(100)", 0, None, 0]]:
            hard_stop("smoke clone does not have the exact T10 model_version schema")
    return resolved_clone


def assert_effective_database_marker(log_path: Path, clone: Path) -> None:
    marker = f"EFFECTIVE_DATABASE_VERIFIED={clone}"
    if marker not in log_path.read_text(encoding="utf-8", errors="replace"):
        hard_stop("backend did not prove its effective DATABASE_URL before uvicorn startup")


def start_backend(
    clone: Path, smoke_dir: Path, log_path: Path, extra_env: dict[str, str], helpers
) -> tuple[subprocess.Popen, object]:
    clone = verify_clone_isolation(clone, smoke_dir, helpers)
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env.pop("T10_SMOKE_USER_PASSWORD", None)
    env.pop("T10_SMOKE_ADMIN_PASSWORD", None)
    env.update(extra_env)
    env["DATABASE_URL"] = "sqlite:///" + clone.as_posix()
    env["PYTHONNOUSERSITE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    env["T10_EXPECTED_CLONE"] = str(clone)
    env["T10_FORBIDDEN_REAL_DB"] = str(EXPECTED_SOURCE.resolve(strict=True))
    env["T10_SMOKE_PORT"] = str(PORT)
    log_stream = log_path.open("w", encoding="utf-8")
    process = subprocess.Popen(
        [str(EXPECTED_PYTHON), "-c", ISOLATED_BOOTSTRAP],
        cwd=EXPECTED_REPO / "backend",
        env=env,
        stdout=log_stream,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return process, log_stream


def login(email: str, password: str) -> str:
    status, payload = request("POST", "/api/auth/login", body={"email": email, "password": password})
    if status != 200 or not isinstance(payload, dict) or "access_token" not in payload:
        hard_stop(f"login failed for {email}: HTTP {status}, {payload}")
    return str(payload["access_token"])


def capture_rows(conn: sqlite3.Connection, helpers) -> dict[str, dict[str, str]]:
    result: dict[str, dict[str, str]] = {}
    for table in sorted(helpers.EXPECTED_TABLES):
        info = conn.execute(f"PRAGMA table_info({helpers.quote_identifier(table)})").fetchall()
        names = [row[1] for row in info]
        pk_names = [row[1] for row in sorted((r for r in info if r[5]), key=lambda r: r[5])]
        if not pk_names:
            hard_stop(f"table has no primary key for preservation comparison: {table}")
        select_sql = ", ".join(helpers.quote_identifier(name) for name in names)
        order_sql = ", ".join(helpers.quote_identifier(name) for name in pk_names)
        rows: dict[str, str] = {}
        for row in conn.execute(
            f"SELECT {select_sql} FROM {helpers.quote_identifier(table)} ORDER BY {order_sql}"
        ):
            values = [helpers.canonical_cell(value) for value in row]
            key_values = [values[names.index(name)] for name in pk_names]
            key = json.dumps(key_values, ensure_ascii=True, separators=(",", ":"))
            rows[key] = json.dumps(values, ensure_ascii=True, separators=(",", ":"))
        result[table] = rows
    return result


def assert_original_rows_preserved(before: dict[str, dict[str, str]], after: dict[str, dict[str, str]]) -> None:
    for table, original_rows in before.items():
        for key, original in original_rows.items():
            if after[table].get(key) != original:
                hard_stop(f"original row changed or disappeared in clone: table={table}, pk={key}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--approved-package-hash-set-sha256", required=True)
    parser.add_argument("--postverify-evidence", required=True, type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if APPROVED_DECISION_ID == "PENDING_PO_GATE2":
        hard_stop("source package has no PO-approved Gate 2 Decision ID")
    if args.decision_id != APPROVED_DECISION_ID:
        hard_stop("Decision ID does not match the PO-approved package")
    approved_hash_set = args.approved_package_hash_set_sha256.upper()
    if approved_hash_set == "PENDING_PO_GATE2" or len(approved_hash_set) != 64 or any(
        char not in "0123456789ABCDEF" for char in approved_hash_set
    ):
        hard_stop("PO-approved package hash-set SHA-256 is missing or invalid")
    current_package_files, current_package_hash_set = independent_package_hashes()
    if current_package_hash_set != approved_hash_set:
        hard_stop("current package differs from the exact package hash-set approved by PO")
    helpers = load_helpers()
    if helpers.APPROVED_DECISION_ID != APPROVED_DECISION_ID:
        hard_stop("Decision ID constants differ between package scripts")
    helper_files, helper_hash_set = helpers.package_hashes()
    if helper_files != current_package_files or helper_hash_set != current_package_hash_set:
        hard_stop("verified helper reports package hashes inconsistent with independent verification")
    if not EXPECTED_PYTHON.is_file():
        hard_stop(f"expected interpreter is missing: {EXPECTED_PYTHON}")
    manifest_path = args.manifest.resolve(strict=True)
    backup_root = helpers.BACKUP_ROOT.resolve()
    if backup_root not in manifest_path.parents or not manifest_path.parent.name.startswith("gate2_"):
        hard_stop("manifest is outside the allowed fresh Gate 2 backup root")
    if sha256_file(manifest_path) != args.manifest_sha256.upper():
        hard_stop("manifest SHA-256 mismatch")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("decision_id") != APPROVED_DECISION_ID:
        hard_stop("manifest Decision ID mismatch")
    if manifest.get("manifest_format") != "T10_GATE2_A1_FRESH_BACKUP_V1":
        hard_stop("manifest is not from the fresh-backup stage")
    if manifest.get("package_files_sha256") != current_package_files:
        hard_stop("current package files differ from the fresh-backup manifest")
    if manifest.get("package_hash_set_sha256") != current_package_hash_set:
        hard_stop("current package hash-set differs from the fresh-backup manifest")
    evidence_path = args.postverify_evidence.resolve(strict=True)
    if evidence_path != manifest_path.parent / "postverify_evidence.json":
        hard_stop("postverify evidence is outside the exact fresh-backup directory")
    evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
    if evidence.get("result") != "PASS" or evidence.get("decision_id") != APPROVED_DECISION_ID:
        hard_stop("postverify evidence is not an approved PASS")
    if evidence.get("manifest_sha256") != args.manifest_sha256.upper():
        hard_stop("postverify evidence is not bound to the reviewed manifest")
    if evidence.get("package_hash_set_sha256") != current_package_hash_set:
        hard_stop("postverify evidence is not bound to the current package")
    source = EXPECTED_SOURCE.resolve(strict=True)
    if evidence.get("source_path") != str(source) or sha256_file(source) != evidence.get("post_alter_sha256"):
        hard_stop("real database changed after postverification")
    user_password = os.environ.get("T10_SMOKE_USER_PASSWORD")
    admin_password = os.environ.get("T10_SMOKE_ADMIN_PASSWORD")
    if not user_password or not admin_password:
        hard_stop("clone smoke credentials were not supplied through the required environment variables")
    with socket.socket() as probe:
        if probe.connect_ex(("127.0.0.1", PORT)) == 0:
            hard_stop(f"port {PORT} is already in use")

    smoke_dir = manifest_path.parent / "clone_smoke"
    smoke_dir.mkdir(exist_ok=False)
    clone = smoke_dir / "firefly_t10_smoke.db"
    with closing(helpers.open_read_only(source)) as src, closing(sqlite3.connect(clone)) as dst:
        src.backup(dst)
        dst.commit()
    with closing(helpers.open_read_only(source)) as real_conn:
        real_snapshot = helpers.snapshot(real_conn)
    with closing(helpers.open_read_only(clone)) as clone_conn:
        clone_snapshot = helpers.snapshot(clone_conn)
        original_rows = capture_rows(clone_conn, helpers)
    if clone_snapshot != real_snapshot:
        hard_stop("new smoke clone differs logically from postverified real database")

    results: dict[str, object] = {}
    process = None
    log_stream = None
    try:
        log_path_b = smoke_dir / "backend_b.log"
        process, log_stream = start_backend(
            clone, smoke_dir, log_path_b, {"ACTIVE_MODEL": "phobert_b"}, helpers
        )
        health_b = wait_for_health(process)
        assert_effective_database_marker(log_path_b, clone.resolve(strict=True))
        if health_b.get("active_model") != "phobert_b" or not health_b.get("active_version"):
            hard_stop(f"PhoBERT B is not active on clone: {health_b}")
        status, movies = request("GET", "/api/movies")
        if status != 200 or not isinstance(movies, list) or not movies:
            hard_stop(f"movies smoke failed: HTTP {status}, {movies}")
        movie_id = int(movies[0]["id"])
        status, comments = request("GET", f"/api/movies/{movie_id}/comments")
        if status != 200 or not isinstance(comments, list):
            hard_stop(f"GET comments failed: HTTP {status}, {comments}")
        user_token = login("demo@firefly.vn", user_password)
        admin_token = login("admin@firefly.vn", admin_password)
        security = {
            "anonymous": request("GET", "/api/admin/comments")[0],
            "user": request("GET", "/api/admin/comments", user_token)[0],
            "admin": request("GET", "/api/admin/comments", admin_token)[0],
        }
        if security != {"anonymous": 401, "user": 403, "admin": 200}:
            hard_stop(f"admin security mismatch: {security}")
        status, prediction = request(
            "POST", "/api/admin/predict", admin_token, {"text": "Phim dài lê thê, xem mà mệt"}
        )
        if status != 200 or not isinstance(prediction, list) or not any(
            row.get("model") == "phobert_b" and row.get("version") for row in prediction
        ):
            hard_stop(f"admin predict/model B failed: HTTP {status}, {prediction}")
        status, comment_b = request(
            "POST", f"/api/movies/{movie_id}/comments", user_token,
            {"content": "Phim dài lê thê, xem mà mệt"},
        )
        if status != 201 or not isinstance(comment_b, dict) or "id" not in comment_b:
            hard_stop(f"PhoBERT B comment persistence failed: HTTP {status}, {comment_b}")
        status, admin_comments = request("GET", "/api/admin/comments?page_size=100", admin_token)
        stored_b = next(
            (row for row in admin_comments.get("items", []) if row.get("id") == comment_b["id"]), None
        ) if status == 200 and isinstance(admin_comments, dict) else None
        if not stored_b or stored_b.get("model_name") != "phobert_b" or not stored_b.get("model_version"):
            hard_stop(f"PhoBERT B model/version was not stored: HTTP {status}, {stored_b}")
        results["b_active"] = {"health": health_b, "comment": stored_b, "security": security}
    finally:
        if process is not None:
            stop_backend(process)
        if log_stream is not None:
            log_stream.close()

    missing_b = smoke_dir / "deliberately_missing_phobert_b"
    process = None
    log_stream = None
    try:
        process, log_stream = start_backend(
            clone,
            smoke_dir,
            smoke_dir / "backend_fallback_a.log",
            {"ACTIVE_MODEL": "phobert_b", "MODEL_DIR_B": str(missing_b)},
            helpers,
        )
        health_a = wait_for_health(process)
        assert_effective_database_marker(
            smoke_dir / "backend_fallback_a.log", clone.resolve(strict=True)
        )
        if health_a.get("active_model") != "phobert" or not health_a.get("active_version"):
            hard_stop(f"PhoBERT A fallback did not activate: {health_a}")
        user_token = login("demo@firefly.vn", user_password)
        status, movies = request("GET", "/api/movies")
        movie_id = int(movies[0]["id"])
        status, comment_a = request(
            "POST", f"/api/movies/{movie_id}/comments", user_token,
            {"content": "Ko hay như quảng cáo, hơi thất vọng"},
        )
        if status != 201 or not isinstance(comment_a, dict) or "id" not in comment_a:
            hard_stop(f"PhoBERT A fallback persistence failed: HTTP {status}, {comment_a}")
        admin_token = login("admin@firefly.vn", admin_password)
        status, admin_comments = request("GET", "/api/admin/comments?page_size=100", admin_token)
        stored_a = next(
            (row for row in admin_comments.get("items", []) if row.get("id") == comment_a["id"]), None
        ) if status == 200 and isinstance(admin_comments, dict) else None
        if not stored_a or stored_a.get("model_name") != "phobert" or not stored_a.get("model_version"):
            hard_stop(f"PhoBERT A fallback model/version was not stored: HTTP {status}, {stored_a}")
        results["a_fallback"] = {"health": health_a, "comment": stored_a}
    finally:
        if process is not None:
            stop_backend(process)
        if log_stream is not None:
            log_stream.close()

    for log_name in ("backend_b.log", "backend_fallback_a.log"):
        log_text = (smoke_dir / log_name).read_text(encoding="utf-8", errors="replace")
        if "Traceback (most recent call last)" in log_text or " 500 Internal Server Error" in log_text:
            hard_stop(f"backend error found in clone-only log: {log_name}")

    with closing(helpers.open_read_only(clone)) as clone_after:
        after_rows = capture_rows(clone_after, helpers)
        helpers.validate_snapshot("clone after API smoke", helpers.snapshot(clone_after))
    assert_original_rows_preserved(original_rows, after_rows)
    if sha256_file(source) != evidence.get("post_alter_sha256"):
        hard_stop("real database changed during clone-only smoke")

    results.update({
        "real_database_sha256_unchanged": evidence["post_alter_sha256"],
        "original_clone_rows_preserved": True,
        "test_records_remain_only_in_clone": str(clone),
        "result": "PASS",
    })
    output = smoke_dir / "clone_smoke_evidence.json"
    output.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print("CLONE_API_SMOKE=PASS")
    print(f"EVIDENCE={output}")
    print("REAL_DATABASE_API_SMOKE=NOT_RUN")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        print("The real backend was not started by this script.", file=sys.stderr)
        raise SystemExit(1)
