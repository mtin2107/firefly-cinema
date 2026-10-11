from sqlalchemy import delete, func, select

from app.models import Showtime
from app.seed import _ensure_showtimes, seed


def test_deleted_seed_showtime_is_not_recreated_on_restart(db, movie, monkeypatch):
    monkeypatch.setattr("app.seed.date", __import__("datetime").date)
    _ensure_showtimes(db, days=1)
    before = db.scalar(select(func.count()).select_from(Showtime))
    deleted = db.scalars(select(Showtime).order_by(Showtime.id)).first()
    db.execute(delete(Showtime).where(Showtime.id == deleted.id))
    db.commit()
    seed(db)
    after = db.scalar(select(func.count()).select_from(Showtime))
    assert after == before - 1
