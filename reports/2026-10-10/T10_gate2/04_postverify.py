#!/usr/bin/env python3
"""DRAFT ONLY: read-only post-ALTER verification of the real database."""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sqlite3
import sys
from contextlib import closing
from pathlib import Path

APPROVED_DECISION_ID = "PO-DECISION-T10-REALDB-A1-GATE2-20261010"
EXPECTED_SOURCE = Path(r"C:\Projects\firefly-cinema\backend\firefly.db")
PACKAGE_FILES = (
    "01_preflight.ps1", "02_fresh_backup.py", "03_schema_alter.py",
    "04_postverify.py", "05_clone_smoke.py", "T10_GATE2_EXECUTION_PACKAGE_DRAFT.md",
)


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision-id", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--manifest-sha256", required=True)
    parser.add_argument("--approved-package-hash-set-sha256", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if APPROVED_DECISION_ID == "PENDING_PO_GATE2":
        hard_stop("source package has no PO-approved Gate 2 Decision ID")
    if args.decision_id != APPROVED_DECISION_ID:
        hard_stop("Decision ID does not match the PO-approved source package")
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
        hard_stop("Decision ID constants differ between backup and postverify scripts")
    helper_files, helper_hash_set = helpers.package_hashes()
    if helper_files != current_package_files or helper_hash_set != current_package_hash_set:
        hard_stop("verified helper reports package hashes inconsistent with independent verification")
    manifest_path = args.manifest.resolve(strict=True)
    backup_root = helpers.BACKUP_ROOT.resolve()
    if backup_root not in manifest_path.parents or not manifest_path.parent.name.startswith("gate2_"):
        hard_stop("manifest is outside the allowed fresh Gate 2 backup root")
    actual_manifest_sha = sha256_file(manifest_path)
    if actual_manifest_sha != args.manifest_sha256.upper():
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
    backup_path = Path(manifest["backup"]["path"])
    if not backup_path.is_file() or sha256_file(backup_path) != manifest["backup"]["sha256"]:
        hard_stop("validated backup is missing or its SHA-256 changed")
    source = EXPECTED_SOURCE.resolve(strict=True)
    if source != EXPECTED_SOURCE or source.is_symlink():
        hard_stop(f"unexpected or linked source path: {source}")

    before = manifest["database"]
    with closing(helpers.open_read_only(source)) as conn:
        after = helpers.snapshot(conn)
        helpers.validate_snapshot("post-ALTER source", after)
        if after["user_version"] != before["user_version"]:
            hard_stop("user_version changed unexpectedly")
        for table in sorted(helpers.EXPECTED_TABLES - {"comments"}):
            if after["tables"][table] != before["tables"][table]:
                hard_stop(f"table changed unexpectedly: {table}")

        old_comments = before["tables"]["comments"]
        new_comments = after["tables"]["comments"]
        original_columns = [row[1] for row in old_comments["columns"]]
        expected_new = [len(old_comments["columns"]), "model_version", "VARCHAR(100)", 0, None, 0]
        if new_comments["columns"] != old_comments["columns"] + [expected_new]:
            hard_stop("comments.model_version is absent or has the wrong type/null/default definition")
        if new_comments["count"] != old_comments["count"]:
            hard_stop("comments count changed")
        if new_comments["foreign_keys"] != old_comments["foreign_keys"]:
            hard_stop("comments foreign keys changed")
        if new_comments["indexes"] != old_comments["indexes"]:
            hard_stop("comments indexes changed")
        if helpers.table_fingerprint(conn, "comments", original_columns) != old_comments["fingerprint"]:
            hard_stop("existing comments data changed")
        if conn.execute("SELECT COUNT(*) FROM comments WHERE model_version IS NOT NULL").fetchone()[0]:
            hard_stop("one or more old comments have a non-NULL model_version")

        old_schema = {tuple(row[:3]): row[3] for row in before["schema_sql"]}
        new_schema = {tuple(row[:3]): row[3] for row in after["schema_sql"]}
        changed = {key for key in set(old_schema) | set(new_schema) if old_schema.get(key) != new_schema.get(key)}
        if changed != {("table", "comments", "comments")}:
            hard_stop(f"schema changed outside comments table: {sorted(changed)}")

    evidence = {
        "decision_id": APPROVED_DECISION_ID,
        "source_path": str(source),
        "post_alter_sha256": sha256_file(source),
        "manifest_path": str(manifest_path),
        "manifest_sha256": actual_manifest_sha,
        "package_files_sha256": manifest["package_files_sha256"],
        "package_hash_set_sha256": manifest["package_hash_set_sha256"],
        "integrity_check": "ok",
        "foreign_key_check_errors": 0,
        "tables_preserved": sorted(helpers.EXPECTED_TABLES),
        "comments_count": old_comments["count"],
        "old_comments_model_version_null": old_comments["count"],
        "result": "PASS",
    }
    evidence_path = manifest_path.parent / "postverify_evidence.json"
    if evidence_path.exists():
        hard_stop(f"refusing to overwrite existing evidence: {evidence_path}")
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print("POSTVERIFY=PASS")
    print(f"EVIDENCE={evidence_path}")
    print("REAL_DB_RUNTIME_STARTUP_AUTHORIZED=NO")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(str(exc), file=sys.stderr)
        print("Do not start the real backend and do not restore automatically.", file=sys.stderr)
        raise SystemExit(1)
