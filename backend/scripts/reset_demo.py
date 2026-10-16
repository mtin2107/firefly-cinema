"""Đặt lại database demo an toàn, chỉ dành cho SQLite file cục bộ."""

from __future__ import annotations

import os
import shutil
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import NoReturn

from sqlalchemy import func
from sqlalchemy.engine import make_url


BACKEND_DIR = Path(__file__).resolve().parents[1]
REPO_DIR = BACKEND_DIR.parent
BACKUP_DIR = REPO_DIR / "backup"


def fail(message: str) -> NoReturn:
    print(f"LỖI: {message}", file=sys.stderr)
    raise SystemExit(2)


def local_sqlite_path(database_url: str) -> Path:
    """Kiểm tra URL và quy mọi đường dẫn tương đối về thư mục backend."""
    try:
        url = make_url(database_url)
    except Exception:
        fail("DATABASE_URL không hợp lệ.")
    if url.drivername not in {"sqlite", "sqlite+pysqlite"}:
        fail("Chỉ được đặt lại database SQLite dạng file cục bộ.")
    if url.host or url.username or url.password or url.port or url.query:
        fail("DATABASE_URL phải là SQLite file cục bộ, không dùng máy chủ hoặc tham số URI.")
    if not url.database or url.database == ":memory:" or url.database.startswith("file:"):
        fail("DATABASE_URL phải trỏ tới một SQLite file cục bộ, không dùng bộ nhớ hoặc URI.")

    raw_path = Path(url.database)
    database_path = raw_path if raw_path.is_absolute() else BACKEND_DIR / raw_path
    database_path = database_path.resolve()
    if database_path.anchor.startswith("\\\\"):
        fail("Không được đặt lại database trên đường dẫn mạng.")
    return database_path


def ensure_database_unlocked(database_path: Path) -> None:
    """Trên Windows, đổi tên là probe đáng tin cậy khi backend đang giữ DB."""
    if not database_path.exists():
        return
    probe_path = database_path.with_name(
        f".{database_path.name}.reset-probe-{os.getpid()}"
    )
    if probe_path.exists():
        fail("Không thể kiểm tra khóa database vì còn file probe từ lần chạy trước.")

    moved = False
    try:
        os.replace(database_path, probe_path)
        moved = True
        os.replace(probe_path, database_path)
        moved = False
    except OSError:
        # Trường hợp rất hiếm lỗi sau lần đổi tên đầu: cố đưa DB về tên cũ,
        # nhưng không để lỗi phục hồi che thông báo khóa dễ hiểu cho người dùng.
        if moved and probe_path.exists() and not database_path.exists():
            try:
                os.replace(probe_path, database_path)
            except OSError:
                try:
                    shutil.copy2(probe_path, database_path)
                except OSError:
                    pass
        fail("Database đang được Backend sử dụng. Hãy tắt Backend trước khi đặt lại dữ liệu demo.")


def backup_existing(database_path: Path) -> tuple[Path | None, Path | None]:
    if not database_path.exists():
        return None, None
    connection = None
    try:
        connection = sqlite3.connect(database_path)
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            fail(f"Database hiện tại không toàn vẹn ({integrity}); không xóa file.")
        checkpoint = connection.execute("PRAGMA wal_checkpoint(FULL)").fetchone()
        if checkpoint and checkpoint[0]:
            fail("Database đang được tiến trình khác sử dụng; không xóa file.")
    except sqlite3.Error as exc:
        fail(f"Không thể kiểm tra database hiện tại; không xóa file: {exc}")
    finally:
        if connection is not None:
            connection.close()

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    backup_path = BACKUP_DIR / f"{database_path.stem}-{stamp}{database_path.suffix}"
    shutil.copy2(database_path, backup_path)

    state_path = database_path.with_name(database_path.name + ".showtime-seed.json")
    state_backup = None
    if state_path.exists():
        state_backup = BACKUP_DIR / f"{state_path.name}-{stamp}.bak"
        shutil.copy2(state_path, state_backup)
    return backup_path, state_backup


def restore_after_failure(
    database_path: Path,
    state_path: Path,
    backup_path: Path | None,
    state_backup: Path | None,
    engine,
) -> list[str]:
    """Phục hồi best-effort và luôn thử cả DB lẫn sidecar."""
    errors: list[str] = []
    try:
        engine.dispose()
    except Exception as exc:  # pragma: no cover - lỗi driver hiếm, vẫn phải phục hồi file
        errors.append(f"đóng kết nối: {exc}")

    for target in (database_path, state_path):
        try:
            target.unlink(missing_ok=True)
        except OSError as exc:
            errors.append(f"dọn {target.name}: {exc}")

    for source, target in (
        (backup_path, database_path),
        (state_backup, state_path),
    ):
        if source is None:
            continue
        try:
            shutil.copy2(source, target)
        except OSError as exc:
            errors.append(f"phục hồi {target.name}: {exc}")
    return errors


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    os.chdir(BACKEND_DIR)
    sys.path.insert(0, str(BACKEND_DIR))

    from app import config

    database_path = local_sqlite_path(config.DATABASE_URL)
    if not config.ADMIN_PASSWORD:
        fail("Chưa cấu hình ADMIN_PASSWORD trong môi trường; không thể tạo tài khoản admin demo.")

    database_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_url = f"sqlite:///{database_path.as_posix()}"
    os.environ["DATABASE_URL"] = normalized_url
    config.DATABASE_URL = normalized_url

    # Phải probe khóa trước khi xóa DB hoặc sidecar. Đặt trước cả import seed
    # để lỗi "backend còn mở" trả nhanh mà không cần nạp model.
    ensure_database_unlocked(database_path)
    backup_path, state_backup = backup_existing(database_path)
    state_path = database_path.with_name(database_path.name + ".showtime-seed.json")

    # Import sau khi URL đã được chuẩn hóa để engine luôn dùng đúng một file,
    # bất kể lệnh được gọi từ thư mục gốc hay từ backend.
    from app.database import Base, SessionLocal, engine
    from app.models import Booking, Comment, Movie, Showtime
    from app.seed import seed

    started = datetime.now()
    try:
        database_path.unlink(missing_ok=True)
        state_path.unlink(missing_ok=True)
        Base.metadata.create_all(engine)
        with SessionLocal() as db:
            seed(db)
            counts = {
                "phim": db.query(Movie).count(),
                "suất": db.query(Showtime).count(),
                "vé": db.query(Booking).count(),
                "bình luận": db.query(Comment).count(),
                "nhãn model tiêu cực": db.query(Comment).filter(Comment.is_negative.is_(True)).count(),
                "nhãn admin đã duyệt": db.query(Comment).filter(Comment.human_label.is_not(None)).count(),
            }
            statuses = dict(db.query(Booking.status, func.count())
                            .group_by(Booking.status).all())
    except Exception:
        recovery_errors = restore_after_failure(
            database_path, state_path, backup_path, state_backup, engine
        )
        if recovery_errors:
            print(
                "Seed thất bại; phục hồi có cảnh báo: " + "; ".join(recovery_errors),
                file=sys.stderr,
            )
        else:
            print("Seed thất bại; đã phục hồi dữ liệu trước đó.", file=sys.stderr)
        raise

    elapsed = (datetime.now() - started).total_seconds()
    engine.dispose()
    print(f"Đã tạo lại dữ liệu demo tại: {database_path}")
    if backup_path is not None:
        print(f"Bản sao lưu: {backup_path}")
    print("Kết quả: " + ", ".join(f"{key}={value}" for key, value in counts.items()))
    print("Trạng thái vé: " + ", ".join(f"{key}={value}" for key, value in sorted(statuses.items())))
    print(f"Thời gian seed (không tính nạp model): {elapsed:.2f} giây")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
