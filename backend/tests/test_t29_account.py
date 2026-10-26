import base64
from datetime import date, datetime, timedelta

import pytest
from app.models import Booking, Comment
from app.booking_rules import age_allowed


def test_profile(client, auth_headers):
    headers = auth_headers["user"]
    r = client.patch("/api/auth/me", headers=headers, json={"full_name":"Tên Mới", "birth_date":"2000-02-29", "gender":"female"})
    assert r.status_code == 200
    assert r.json()["birth_date"] == "2000-02-29"
    assert r.json()["gender"] == "female"
    assert "password_hash" not in r.json() and "created_at" in r.json()
    for fields in ({"birth_date":"1899-12-31"},{"birth_date":"2999-01-01"},{"birth_date":"2026-02-30"},{"gender":"other"}):
        response = client.patch("/api/auth/me", headers=headers, json={"full_name":"Tên Mới", **fields})
        assert response.status_code == 422
        assert isinstance(response.json()["detail"], str)
    assert client.patch("/api/auth/me",headers=headers,json={"full_name":"Tên Khác"}).json()["birth_date"] == "2000-02-29"
    assert client.patch("/api/auth/me",headers=headers,json={"full_name":"Tên Khác","birth_date":None,"gender":None}).json()["birth_date"] is None


def test_email(client, auth_headers):
    headers=auth_headers["user"]
    url="/api/auth/me/email"
    assert client.post(url,headers=headers,json={"new_email":"new@example.com","current_password":"wrong"}).status_code == 400
    assert client.post(url,headers=headers,json={"new_email":"bad","current_password":"secret1"}).status_code == 422
    assert client.post(url,headers=headers,json={"new_email":"admin@example.com","current_password":"secret1"}).json()["detail"] == "Email này đã được đăng ký."
    r=client.post(url,headers=headers,json={"new_email":"NEW@Example.com","current_password":"secret1"})
    assert r.status_code == 200 and r.json()["email"] == "new@example.com"
    assert client.get("/api/auth/me",headers=headers).status_code == 200
    assert client.post("/api/auth/login",json={"email":"user@example.com","password":"secret1"}).status_code == 401
    assert client.post("/api/auth/login",json={"email":"NEW@example.com","password":"secret1"}).status_code == 200


def test_email_password_limit(client,auth_headers):
    for _ in range(5):
        response=client.post("/api/auth/me/email",headers=auth_headers["user"],json={"new_email":"new@example.com","current_password":"wrong"})
    assert client.post("/api/auth/me/email",headers=auth_headers["user"],json={"new_email":"new@example.com","current_password":"secret1"}).status_code == 429


@pytest.mark.parametrize("signature,extension",[(b"\xff\xd8\xff", "jpg"),(b"\x89PNG\r\n\x1a\n","png"),(b"RIFF1234WEBP","webp")])
def test_avatar(client,auth_headers,tmp_path,monkeypatch,signature,extension):
    from app.routers import auth
    monkeypatch.setattr(auth,"UPLOAD_DIR",tmp_path)
    headers=auth_headers["user"]
    url="/api/auth/me/avatar"
    def put(data,who=headers):
        return client.put(url,headers=who,json={"filename":"../../fake.gif","data":base64.b64encode(data).decode()})
    first=put(signature)
    assert first.status_code == 200
    path=tmp_path / "avatars" / first.json()["avatar_url"].rsplit("/",1)[1]
    assert path.suffix == "."+extension and path.read_bytes() == signature
    other=put(signature,auth_headers["admin"])
    other_path=tmp_path / "avatars" / other.json()["avatar_url"].rsplit("/",1)[1]
    second=put(signature)
    assert second.status_code == 200 and not path.exists() and other_path.exists()
    assert put(b"GIF89a").status_code == 422
    assert put(signature+b"a"*(2*1024*1024-len(signature))).status_code == 200
    assert put(signature+b"a"*(2*1024*1024)).status_code == 422
    assert client.put(url,headers=headers,json={"filename":"x.png","data":"%%%"}).status_code == 422
    assert client.delete(url,headers=headers).json()["avatar_url"] is None
    assert list((tmp_path / "avatars").iterdir()) == [other_path]
    assert client.put(url,json={"filename":"x","data":"AA=="}).status_code == 401


@pytest.mark.parametrize("rating,years",[("P",0),("T13",13),("T16",16),("T18",18)])
def test_age_boundary(rating,years):
    birth=date(2008,10,27)
    birthday=date(2008+years,10,27)
    assert age_allowed(birth,rating,birthday)
    assert age_allowed(birth,rating,birthday-timedelta(days=1)) == (rating == "P")
    assert age_allowed(None,rating,birthday)
    assert age_allowed(date(2008,2,29),"T18",date(2026,3,1))
    assert not age_allowed(date(2008,2,29),"T18",date(2026,2,28))


def test_booking_age(client,auth_headers,users,db,showtime):
    users[0].birth_date=date.today()
    db.commit()
    response=client.post("/api/bookings",headers=auth_headers["user"],json={"showtime_id":showtime.id,"seats":["A1"]})
    assert response.status_code == 400 and "chưa đủ 13 tuổi" in response.json()["detail"]
    users[0].birth_date=None
    users[1].birth_date=date.today()
    db.commit()
    assert client.post("/api/bookings",headers=auth_headers["user"],json={"showtime_id":showtime.id,"seats":["A1"]}).status_code == 201
    assert client.post("/api/bookings",headers=auth_headers["admin"],json={"showtime_id":showtime.id,"seats":["A2"]}).status_code == 201


def test_admin_summary(client,auth_headers,users,db,showtime):
    now=datetime.now()
    showtime.start_time=now.replace(hour=22)
    c1=Comment(movie_id=showtime.movie_id,user_id=users[0].id,content="Chờ",is_negative=True,negative_score=.9,model_name="fake",model_version="test")
    c2=Comment(movie_id=showtime.movie_id,user_id=users[0].id,content="Duyệt",is_negative=True,negative_score=.9,model_name="fake",model_version="test",human_label=0,reviewed_by=users[1].id,reviewed_at=now)
    c3=Comment(movie_id=showtime.movie_id,user_id=users[0].id,content="Người khác",is_negative=True,negative_score=.9,model_name="fake",model_version="test",human_label=1,reviewed_by=users[0].id,reviewed_at=now)
    db.add_all([c1,c2,c3,Booking(user_id=users[0].id,showtime_id=showtime.id,total=80000,status="pending_verify"),Booking(user_id=users[0].id,showtime_id=showtime.id,total=80000,status="paid",checked_in_by=users[1].id,checked_in_at=now)])
    db.commit()
    assert client.get("/api/admin/me/summary",headers=auth_headers["user"]).status_code == 403
    assert client.get("/api/admin/me/summary").status_code == 401
    data=client.get("/api/admin/me/summary",headers=auth_headers["admin"]).json()
    assert data["todo"] == {"comments":1,"pending_verify":1,"showtimes_today":1}
    assert data["work"] == {"reviewed_today":1,"reviewed_total":1,"overrides":1,"checked_in_today":1}
    assert len(data["recent_activity"]) == 2
    summary=client.get("/api/auth/me/summary",headers=auth_headers["user"]).json()
    assert summary["spent_this_year"] == 80000
    assert len(summary["recent_comments"]) == 3


@pytest.mark.parametrize("rating,minimum", [("P", 0), ("T13", 13), ("T16", 16), ("T18", 18)])
@pytest.mark.parametrize("before", [True, False])
def test_booking_age_on_showtime_date(client, auth_headers, users, db, showtime, rating, minimum, before):
    showtime.movie.age_rating = rating
    showtime.start_time = datetime(2035, 3, 1, 20) - timedelta(days=int(before))
    users[0].birth_date = date(2035 - (minimum or 1), 3, 1)
    db.commit()
    response = client.post("/api/bookings", headers=auth_headers["user"], json={"showtime_id": showtime.id, "seats": ["A1"]})
    assert response.status_code == (400 if before and minimum else 201)
    if before and minimum:
        assert response.json()["detail"] == f"Bạn chưa đủ {minimum} tuổi để xem phim {rating}."


def test_annual_spending_and_private_profile(client, auth_headers, users, db, showtime):
    now = datetime.now()
    for who, status, total, year in [(users[0], "paid", 100, now.year), (users[0], "paid", 200, now.year-1), (users[0], "held", 300, now.year), (users[1], "paid", 900, now.year)]:
        db.add(Booking(user_id=who.id, showtime_id=showtime.id, total=total, status=status, created_at=now.replace(year=year)))
    db.commit()
    summary = client.get("/api/auth/me/summary", headers=auth_headers["user"]).json()
    assert summary["spent_this_year"] == 100
    assert summary["stats"]["total_spent"] == 300
    client.patch("/api/auth/me", headers=auth_headers["user"], json={"full_name": "Hồ Sơ Riêng", "birth_date": "2000-01-01", "gender": "male"})
    other = client.get("/api/auth/me", headers=auth_headers["admin"]).json()
    assert other["full_name"] == "Quản trị" and other["birth_date"] is None
    assert client.patch("/api/auth/me", json={"full_name": "Không đăng nhập"}).status_code == 401
    assert client.post("/api/auth/me/email", json={"new_email": "new@example.com", "current_password": "secret1"}).status_code == 401
    assert client.delete("/api/auth/me/avatar").status_code == 401
