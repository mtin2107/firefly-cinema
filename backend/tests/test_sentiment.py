from datetime import datetime, timedelta

import pytest

from app.models import Comment, Movie


def _movie(title: str) -> Movie:
    return Movie(
        title=title, genre="Tâm lý", duration_min=100, age_rating="T13",
        release_date="2026-10-01", status="now_showing", director="", cast="",
        score=0, description="", poster_bg="#112233", poster_fg="#ffffff",
        country="Việt Nam", formats="Phụ đề",
    )


def _comment(movie_id, user_id, *, created_at, is_negative, score, human_label=None, hidden=False):
    return Comment(
        movie_id=movie_id, user_id=user_id, content="Bình luận thử nghiệm",
        is_negative=is_negative, negative_score=score, model_name="fake",
        model_version="test-1", human_label=human_label, hidden=hidden,
        created_at=created_at,
    )


def test_sentiment_requires_admin(client, auth_headers):
    assert client.get("/api/admin/sentiment").status_code == 401
    response = client.get("/api/admin/sentiment", headers=auth_headers["user"])
    assert response.status_code == 403


@pytest.mark.parametrize("days", [0, 366])
def test_sentiment_rejects_days_outside_range(client, auth_headers, days):
    response = client.get(f"/api/admin/sentiment?days={days}", headers=auth_headers["admin"])
    assert response.status_code == 422
    assert response.json() == {"detail": "Số ngày thống kê phải từ 1 đến 365."}


def test_sentiment_uses_effective_label_group_by_and_complete_daily(
    client, db, users, auth_headers,
):
    user, _ = users
    first = _movie("Phim A")
    second = _movie("Phim B")
    db.add_all([first, second])
    db.flush()
    now = datetime.now()
    db.add_all([
        _comment(first.id, user.id, created_at=now - timedelta(hours=1),
                 is_negative=True, score=0.9),
        # Đã ẩn vẫn tính; người duyệt đổi từ tiêu cực thành bình thường.
        _comment(first.id, user.id, created_at=now - timedelta(hours=2),
                 is_negative=True, score=0.7, human_label=0, hidden=True),
        # Người duyệt đổi từ bình thường thành tiêu cực.
        _comment(second.id, user.id, created_at=now - timedelta(days=1),
                 is_negative=False, score=0.2, human_label=1),
        _comment(second.id, user.id, created_at=now - timedelta(days=3),
                 is_negative=False, score=0.1, human_label=0),
        _comment(first.id, user.id, created_at=now - timedelta(days=8),
                 is_negative=True, score=0.99),
    ])
    db.commit()

    response = client.get("/api/admin/sentiment?days=7", headers=auth_headers["admin"])
    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"] == {
        "total": 4,
        "negative": 2,
        "negative_ratio": 0.5,
        "reviewed": 3,
        "model_human_accuracy": pytest.approx(1 / 3),
    }

    assert [row["title"] for row in payload["movies"]] == ["Phim A", "Phim B"]
    by_title = {row["title"]: row for row in payload["movies"]}
    assert by_title["Phim A"] == {
        "movie_id": first.id, "title": "Phim A", "total": 2, "negative": 1,
        "negative_ratio": 0.5, "avg_negative_score": pytest.approx(0.8),
    }
    assert by_title["Phim B"] == {
        "movie_id": second.id, "title": "Phim B", "total": 2, "negative": 1,
        "negative_ratio": 0.5, "avg_negative_score": pytest.approx(0.15),
    }

    daily = payload["daily"]
    assert len(daily) == 7
    assert daily[0]["date"] == (datetime.now().date() - timedelta(days=6)).isoformat()
    assert daily[-1]["date"] == datetime.now().date().isoformat()
    by_date = {row["date"]: row for row in daily}
    assert by_date[datetime.now().date().isoformat()] == {
        "date": datetime.now().date().isoformat(), "total": 2, "negative": 1,
    }
    yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
    assert by_date[yesterday] == {"date": yesterday, "total": 1, "negative": 1}
    assert sum(row["total"] for row in daily) == 4
    assert sum(row["negative"] for row in daily) == 2
    assert sum(row["total"] == 0 for row in daily) == 4
