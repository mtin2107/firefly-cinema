import os
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Force model paths to be absent before importing the application. This makes the
# test suite independent of local checkpoints and prevents importing torch.
os.environ["MODEL_DIR"] = "tests/__missing__/phobert-a"
os.environ["MODEL_DIR_B"] = "tests/__missing__/phobert-b"
os.environ["SKLEARN_MODELS"] = ""
os.environ["ACTIVE_MODEL"] = "phobert_b"
os.environ["SECRET_KEY"] = "t20-test-secret-key-at-least-32-characters"

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Movie, Showtime, User  # noqa: E402
from app.security import create_token, hash_password  # noqa: E402


class FakeModel:
    def __init__(self, name="fake", *, result=(True, 0.91), error=None):
        self.name = name
        self.version = "test-1"
        self.loaded = True
        self.available = True
        self.error = None
        self._result = result
        self._raised = error

    def predict(self, text):
        if self._raised:
            raise self._raised
        return self._result


class FakeClassifier:
    name = "fake"
    version = "test-1"
    error = None

    def __init__(self):
        self.models = [FakeModel()]

    def predict(self, text):
        return ("thất vọng" in text.lower(), 0.91 if "thất vọng" in text.lower() else 0.08)

    def available_models(self):
        return self.models

    def release_if_inactive(self, model):
        return None

    def health(self):
        return [{"name": "fake", "version": "test-1", "loaded": True,
                 "available": True, "active": True, "error": None}]


@pytest.fixture
def db(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture
def fake_classifier(monkeypatch):
    from app import main
    from app.routers import admin_predict, comments

    fake = FakeClassifier()
    monkeypatch.setattr(main, "classifier", fake)
    monkeypatch.setattr(comments, "classifier", fake)
    monkeypatch.setattr(admin_predict, "classifier", fake)
    return fake


@pytest.fixture
def client(db, fake_classifier):
    from app.routers import auth, comments

    auth._login_failures.clear_all()
    comments._comment_limits.clear_all()
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def users(db):
    user = User(full_name="Người dùng", email="user@example.com",
                password_hash=hash_password("secret1"), role="user")
    admin = User(full_name="Quản trị", email="admin@example.com",
                 password_hash=hash_password("secret1"), role="admin")
    db.add_all([user, admin])
    db.commit()
    return user, admin


@pytest.fixture
def auth_headers(users):
    user, admin = users
    return {
        "user": {"Authorization": f"Bearer {create_token(user.id)}"},
        "admin": {"Authorization": f"Bearer {create_token(admin.id)}"},
    }


@pytest.fixture
def movie(db):
    row = Movie(
        title="Phim thử nghiệm", genre="Tâm lý", duration_min=120,
        age_rating="T13", release_date="2026-10-01", status="now_showing",
        director="Đạo diễn", cast="Diễn viên", score=0, description="Mô tả",
        poster_bg="#112233", poster_fg="#ffffff", country="Việt Nam",
        formats="Phụ đề",
    )
    db.add(row)
    db.commit()
    return row


@pytest.fixture
def showtime(db, movie):
    row = Showtime(movie_id=movie.id, start_time=datetime.now() + timedelta(days=2),
                   room="Phòng 1", price=80_000)
    db.add(row)
    db.commit()
    return row


@pytest.fixture
def movie_payload():
    return {
        "title": "Phim mới", "genre": ["Tâm lý"], "duration_min": 110,
        "age_rating": "T13", "release_date": "2026-10-11",
        "status": "now_showing", "country": "Việt Nam",
        "formats": ["Phụ đề"], "director": "", "cast": "",
        "description": "", "poster_bg": "#123456", "poster_fg": "#ffffff",
        "poster_url": None,
    }
