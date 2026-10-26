from datetime import datetime, timedelta

from app.models import Booking, Comment, Rating


def test_summary_counts_privacy_and_moderation(client, db, users, auth_headers, movie, showtime):
    user, other = users
    now = datetime.now()
    db.add_all([Booking(user_id=user.id, showtime_id=showtime.id, total=80000, status=status,
                        checked_in_at=now if i == 0 else None)
                for i, status in enumerate(["paid", "paid", "held", "expired", "rejected"])])
    db.add(Booking(user_id=other.id, showtime_id=showtime.id, total=999999, status="paid"))
    for i in range(4):
        db.add(Comment(user_id=user.id, movie_id=movie.id, content=f"Nội dung riêng {i}",
                       is_negative=i == 2, human_label=1 if i == 3 else 0 if i == 2 else None,
                       is_anonymous=True, hidden=i == 3, negative_score=.1,
                       model_name="fake", created_at=now+timedelta(seconds=i)))
    db.add(Comment(user_id=other.id, movie_id=movie.id, content="Bí mật người khác",
                   is_negative=False, negative_score=.1, model_name="fake"))
    db.add(Rating(user_id=user.id, movie_id=movie.id, stars=8))
    db.commit()
    response = client.get("/api/auth/me/summary", headers=auth_headers["user"])
    assert response.status_code == 200
    result = response.json()
    assert set(result) == {"member_since", "stats", "favorite_genre", "recent_comments", "ratings"}
    assert result["stats"] == {"bookings": 3, "paid": 2, "watched": 1, "total_spent": 160000, "comments": 4, "ratings": 1}
    assert result["favorite_genre"] == "Tâm lý"
    assert len(result["recent_comments"]) == 3
    assert result["recent_comments"][0]["effective_negative"] is True
    assert result["recent_comments"][1]["effective_negative"] is False
    assert result["recent_comments"][0]["hidden"] is True
    assert result["recent_comments"][0]["is_anonymous"] is True
    assert result["ratings"][0]["stars"] == 8
    assert "Bí mật người khác" not in response.text


def test_empty_summary_and_auth(client, auth_headers):
    response = client.get("/api/auth/me/summary")
    assert response.status_code == 401
    assert response.json() == client.get("/api/auth/me").json()
    data = client.get("/api/auth/me/summary", headers=auth_headers["user"]).json()
    assert all(value == 0 for value in data["stats"].values())
    assert data["favorite_genre"] is None
    assert data["recent_comments"] == data["ratings"] == []
