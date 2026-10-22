#!/usr/bin/env python3
"""DRAFT ONLY: create and fully validate a fresh SQLite online backup.

This file is intentionally fail-closed until PO replaces APPROVED_DECISION_ID
after reviewing this exact source and command line.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import sqlite3
import subprocess
import sys
from contextlib import closing
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

APPROVED_DECISION_ID = "PO-DECISION-T10-REALDB-A1-GATE2-20261010"
EXPECTED_SOURCE = Path(r"C:\Projects\firefly-cinema\backend\firefly.db")
EXPECTED_REPO = Path(r"C:\Projects\firefly-cinema")
BACKUP_ROOT = EXPECTED_REPO / "backup" / "T10_2026-10-10"
EXPECTED_TABLES = {"users", "movies", "showtimes", "bookings", "booking_seats", "comments"}
PACKAGE_FILES = (
    "01_preflight.ps1",
    "02_fresh_backup.py",
    "03_schema_alter.py",
    "04_postverify.py",
    "05_clone_smoke.py",
    "T10_GATE2_EXECUTION_PACKAGE_DRAFT.md",
)


def hard_stop(message: str) -> "NoReturn":
    raise RuntimeError(f"HARD STOP: {message}")


def require_authorization(value: str) -> None:
    if APPROVED_DECISION_ID == "PENDING_PO_GATE2":
        hard_stop("source package has no PO-approved Gate 2 Decision ID")
    if value != APPROVED_DECISION_ID:
        hard_stop("Decision ID does not match the PO-approved source package")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def package_hashes() -> tuple[dict[str, str], str]:
    package_dir = Path(__file__).resolve().parent
    values = {name: sha256_file(package_dir / name) for name in PACKAGE_FILES}
    canonical = json.dumps(values, sort_keys=True, separators=(",", ":")).encode("ascii")
    return values, hashlib.sha256(canonical).hexdigest().upper()


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def canonical_cell(value: object) -> object:
    if value is None:
        return ["null", None]
    if isinstance(value, bytes):
        return ["blob", base64.b64encode(value).decode("ascii")]
    if isinstance(value, float):
        return ["float", value.hex()]
    if isinstance(value, int):
        return ["int", str(value)]
    return ["text", str(value)]


def table_fingerprint(conn: sqlite3.Connection, table: str, columns: list[str]) -> str:
    info = conn.execute(f"PRAGMA table_info({quote_identifier(table)})").fetchall()
    pk_columns = [row[1] for row in sorted((r for r in info if r[5]), key=lambda r: r[5])]
    order_columns = pk_columns or columns
    select_sql = ", ".join(quote_identifier(c) for c in columns)
    order_sql = ", ".join(quote_identifier(c) for c in order_columns)
    digest = hashlib.sha256()
    for row in conn.execute(
        f"SELECT {select_sql} FROM {quote_identifier(table)} ORDER BY {order_sql}"
    ):
        payload = [canonical_cell(value) for value in row]
        digest.update(json.dumps(payload, ensure_ascii=True, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest().upper()


def snapshot(conn: sqlite3.Connection) -> dict:
    integrity = [row[0] for row in conn.execute("PRAGMA integrity_check").fetchall()]
    foreign_key_errors = [list(row) for row in conn.execute("PRAGMA foreign_key_check").fetchall()]
    schema_rows = conn.execute(
        "SELECT type, name, tbl_name, sql FROM sqlite_master "
        "WHERE name NOT LIKE 'sqlite_%' ORDER BY type, name"
    ).fetchall()
    triggers = [
        list(row)
        for row in conn.execute(
            "SELECT name, tbl_name, sql FROM sqlite_master WHERE type='trigger' ORDER BY name"
        )
    ]
    table_names = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        )
    }
    if table_names != EXPECTED_TABLES:
        hard_stop(f"expected exactly six tables {sorted(EXPECTED_TABLES)}, got {sorted(table_names)}")
    tables: dict[str, dict] = {}
    for table in sorted(table_names):
        columns = [list(row) for row in conn.execute(f"PRAGMA table_info({quote_identifier(table)})")]
        column_names = [row[1] for row in columns]
        indexes = []
        for index_row in conn.execute(f"PRAGMA index_list({quote_identifier(table)})"):
            index_name = index_row[1]
            indexes.append({
                "index_list": list(index_row),
                "index_xinfo": [
                    list(row)
                    for row in conn.execute(f"PRAGMA index_xinfo({quote_identifier(index_name)})")
                ],
            })
        tables[table] = {
            "columns": columns,
            "foreign_keys": [
                list(row) for row in conn.execute(f"PRAGMA foreign_key_list({quote_identifier(table)})")
            ],
            "indexes": indexes,
            "count": conn.execute(f"SELECT COUNT(*) FROM {quote_identifier(table)}").fetchone()[0],
            "fingerprint": table_fingerprint(conn, table, column_names),
        }
    return {
        "schema_sql": [list(row) for row in schema_rows],
        "triggers": triggers,
        "tables": tables,
        "integrity_check": integrity,
        "foreign_key_check": foreign_key_errors,
        "user_version": conn.execute("PRAGMA user_version").fetchone()[0],
    }


def open_read_only(path: Path) -> sqlite3.Connection:
    uri = path.resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True, timeout=5)
    conn.execute("PRAGMA query_only=ON")
    return conn


def validate_snapshot(label: str, value: dict) -> None:
    if value["integrity_check"] != ["ok"]:
        hard_stop(f"{label} integrity_check failed: {value['integrity_check']}")
    if value["foreign_key_check"]:
        hard_stop(f"{label} foreign_key_check failed: {value['foreign_key_check']}")


def validate_pre_t10_schema(value: dict) -> None:
    expected_comment_columns = [
        "id", "movie_id", "user_id", "content", "is_negative", "negative_score",
        "model_name", "human_label", "reviewed_by", "reviewed_at", "hidden", "created_at",
    ]
    actual = [row[1] for row in value["tables"]["comments"]["columns"]]
    if actual != expected_comment_columns:
        hard_stop(f"unexpected pre-T10 comments columns: {actual}")
    if value["triggers"]:
        hard_stop(f"unexpected triggers in pre-T10 schema: {value['triggers']}")


def git_head() -> str:
    return subprocess.run(
        ["git", "-C", str(EXPECTED_REPO), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--supervisor-confirmation", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    require_authorization(args.decision_id)
    if args.supervisor_confirmation != "APPLICATION_WRITERS_STOPPED_AND_VERIFIED":
        hard_stop("missing exact supervisor confirmation that all application writers are stopped")
    package_files_before, package_hash_set_before = package_hashes()
    source = EXPECTED_SOURCE.resolve(strict=True)
    if source != EXPECTED_SOURCE or source.is_symlink():
        hard_stop(f"unexpected or linked source path: {source}")
    source_sha_before = sha256_file(source)
    source_stat_before = source.stat()
    with closing(open_read_only(source)) as src:
        source_before = snapshot(src)
        validate_snapshot("source before backup", source_before)
        validate_pre_t10_schema(source_before)

        stamp = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).strftime("%Y%m%d_%H%M%S_%f%z")
        backup_dir = BACKUP_ROOT / f"gate2_{stamp}"
        backup_dir.mkdir(parents=True, exist_ok=False)
        backup_path = backup_dir / "firefly_online_backup.db"
        restore_dir = backup_dir / "restore_validation"
        restore_dir.mkdir(exist_ok=False)
        restore_path = restore_dir / "firefly_restored.db"

        with closing(sqlite3.connect(backup_path)) as dst:
            src.backup(dst)
            dst.commit()

    with closing(open_read_only(source)) as src_after:
        source_after = snapshot(src_after)
    source_sha_after = sha256_file(source)
    source_stat_after = source.stat()
    if source_before != source_after:
        hard_stop("source logical snapshot changed while backup was created")
    if source_sha_before != source_sha_after:
        hard_stop("source SHA-256 changed while backup was created")
    if (source_stat_before.st_size, source_stat_before.st_mtime_ns) != (
        source_stat_after.st_size,
        source_stat_after.st_mtime_ns,
    ):
        hard_stop("source size or mtime changed while backup was created")

    with closing(open_read_only(backup_path)) as backup_conn:
        backup_snapshot = snapshot(backup_conn)
    validate_snapshot("online backup", backup_snapshot)
    if backup_snapshot != source_before:
        hard_stop("online backup differs logically from source snapshot")

    with closing(open_read_only(backup_path)) as backup_src, closing(
        sqlite3.connect(restore_path)
    ) as restored:
        backup_src.backup(restored)
        restored.commit()
    with closing(open_read_only(restore_path)) as restore_conn:
        restore_snapshot = snapshot(restore_conn)
    validate_snapshot("restore validation clone", restore_snapshot)
    if restore_snapshot != source_before:
        hard_stop("restore validation clone differs logically from source snapshot")

    package_files, package_hash_set = package_hashes()
    if package_files != package_files_before or package_hash_set != package_hash_set_before:
        hard_stop("execution package changed while fresh backup was being created")
    manifest = {
        "manifest_format": "T10_GATE2_A1_FRESH_BACKUP_V1",
        "package_status": "GATE2_AUTHORIZED_AT_EXECUTION",
        "fresh_backup_id": backup_dir.name,
        "decision_id": APPROVED_DECISION_ID,
        "created_at": datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).isoformat(),
        "timezone": "Asia/Ho_Chi_Minh",
        "git_head": git_head(),
        "package_files_sha256": package_files,
        "package_hash_set_sha256": package_hash_set,
        "source": {
            "path": str(source),
            "sha256_before": source_sha_before,
            "sha256_after": source_sha_after,
            "size": source_stat_after.st_size,
            "mtime_ns": source_stat_after.st_mtime_ns,
        },
        "backup": {"path": str(backup_path), "sha256": sha256_file(backup_path)},
        "restore_validation": {"path": str(restore_path), "sha256": sha256_file(restore_path)},
        "database": source_before,
    }
    manifest_path = backup_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest_sha = sha256_file(manifest_path)
    (backup_dir / "manifest.sha256").write_text(
        f"{manifest_sha}  manifest.json\n", encoding="ascii"
    )
    print(f"BACKUP_VALIDATED={backup_path}")
    print(f"MANIFEST={manifest_path}")
    print(f"MANIFEST_SHA256={manifest_sha}")
    print("OPERATOR_CHECKPOINT_REQUIRED=YES")
    print("HARD STOP: do not continue to ALTER until supervisor reviews the manifest.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        raise SystemExit(1)
