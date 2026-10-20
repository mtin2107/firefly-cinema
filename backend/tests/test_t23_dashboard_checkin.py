from datetime import datetime, timedelta, time
from concurrent.futures import ThreadPoolExecutor
import pytest
from sqlalchemy import text, create_engine
from sqlalchemy.orm import Session
from app.models import Booking, BookingSeat, Rating, Comment, User
from app.routers.admin_checkin import checkin
from fastapi import HTTPException

def booking(db,users,showtime,status="paid",when=None,seat="A1"):
    b=Booking(user_id=users[0].id,showtime_id=showtime.id,status=status,total=80000,created_at=when or datetime.now())
    b.seats=[BookingSeat(showtime_id=showtime.id,seat_code=seat)]
    db.add(b); db.commit(); return b

@pytest.mark.parametrize("days",[7,30,90])
def test_dashboard_sql(client,db,users,showtime,auth_headers,days):
    now=datetime.now(); showtime.start_time=datetime.combine(now.date(),time(23,59))
    for i,status in enumerate(["paid","held","pending_verify","expired","rejected"]):
        booking(db,users,showtime,status,seat=f"A{i+1}")
    for i,ago in enumerate([6,7,29,30,89,90]):
        booking(db,users,showtime,when=datetime.combine(now.date()-timedelta(days=ago),time.min),seat=f"B{i+1}")
    booking(db,users,showtime,"held",now-timedelta(hours=1),"C1")
    db.add(Rating(user_id=users[0].id,movie_id=showtime.movie_id,stars=4))
    db.add(Comment(user_id=users[0].id,movie_id=showtime.movie_id,content="Thử",is_negative=True,negative_score=.9,model_name="fake",human_label=0,hidden=True))
    db.commit()
    d=client.get(f"/api/admin/dashboard?days={days}",headers=auth_headers["admin"]).json()
    first=now.date()-timedelta(days=days-1)
    params={"start":str(first),"end":str(now.date()+timedelta(days=1))}
    rows=db.execute(text("SELECT status,COUNT(*),SUM(total) FROM bookings WHERE created_at>=:start AND created_at<:end GROUP BY status"),params)
    by={s:(n,total) for s,n,total in rows}
    assert d["revenue"]==by["paid"][1] and d["paid_tickets"]==by["paid"][0]
    assert d["pending_tickets"]==by["held"][0]+by["pending_verify"][0]
    assert d["cancelled_tickets"]==by["expired"][0]+by["rejected"][0]
    sold=db.scalar(text("SELECT COUNT(*) FROM booking_seats s JOIN bookings b ON b.id=s.booking_id WHERE b.status='paid' AND b.created_at>=:start AND b.created_at<:end"),params)
    assert d["seats_sold"]==sold
    avg,count=db.execute(text("SELECT AVG(stars),COUNT(*) FROM ratings WHERE created_at>=:start AND created_at<:end"),params).one()
    assert d["rating_avg"]==avg and d["rating_count"]==count
    assert len(d["daily"])==days and d["daily"][0]["date"]==str(first)
    assert sum(r["revenue"] for r in d["daily"])==d["revenue"]
    assert d["movies"][0]["negative_rate"]==0
    all_paid=db.scalar(text("SELECT COUNT(*) FROM booking_seats s JOIN bookings b ON b.id=s.booking_id WHERE b.status='paid'"))
    assert d["movies"][0]["occupancy"]==pytest.approx(all_paid/96)

@pytest.mark.parametrize("method,path",[("get","/api/admin/dashboard"),("get","/api/admin/checkin/FF00001"),("post","/api/admin/checkin/FF00001")])
def test_security(client,auth_headers,method,path):
    assert getattr(client,method)(path).status_code==401
    assert getattr(client,method)(path,headers=auth_headers["user"]).status_code==403

@pytest.mark.parametrize("days",[0,1,8,365,"abc"])
def test_invalid_days(client,auth_headers,days):
    assert client.get(f"/api/admin/dashboard?days={days}",headers=auth_headers["admin"]).status_code==422

@pytest.mark.parametrize("status,reason",[("held","chưa thanh toán"),("pending_verify","chờ xác nhận"),("expired","quá hạn"),("rejected","không nhận")])
def test_invalid_checkin(client,db,users,showtime,auth_headers,status,reason):
    b=booking(db,users,showtime,status)
    r=client.post(f"/api/admin/checkin/FF{b.id:05d}",headers=auth_headers["admin"])
    assert r.status_code==409 and reason in r.json()["detail"]
    db.refresh(b); assert b.checked_in_at is None

@pytest.mark.parametrize("code",["FF99999","bad","FF9999999999999999999999999999"])
def test_not_found(client,auth_headers,code):
    for method in [client.get,client.post]:
        r=method(f"/api/admin/checkin/{code}",headers=auth_headers["admin"])
        assert r.status_code==404 and r.json()["detail"]=="Không tìm thấy vé."

def test_checkin_once_and_my_tickets(client,db,users,showtime,auth_headers):
    b=booking(db,users,showtime); path=f"/api/admin/checkin/ff{b.id:05d}"
    assert client.get(path,headers=auth_headers["admin"]).json()["checked_in_at"] is None
    r=client.post(path,headers=auth_headers["admin"]); assert r.status_code==200
    d=r.json(); assert d["checked_in_at"] and d["checked_in_by_name"]==users[1].full_name
    assert client.get("/api/bookings/me",headers=auth_headers["user"]).json()[0]["checked_in_at"]==d["checked_in_at"]
    r=client.post(path,headers=auth_headers["admin"]); assert r.status_code==409 and "Vé đã được soát lúc" in r.json()["detail"]
    db.refresh(b); assert b.checked_in_by==users[1].id

def test_concurrent_checkin(db,users,showtime):
    b=booking(db,users,showtime); bid=b.id; uid=users[1].id
    engine=create_engine(str(db.bind.url),connect_args={"check_same_thread":False})
    def run(_):
        with Session(engine) as session:
            try: checkin(f"FF{bid:05d}",session.get(User,uid),session); return 200
            except HTTPException as e: return e.status_code
    try:
        with ThreadPoolExecutor(max_workers=2) as pool: assert sorted(pool.map(run,range(2)))==[200,409]
    finally: engine.dispose()

@pytest.mark.parametrize("ahead",[timedelta(hours=3),timedelta(days=3)])  # suất sắp chiếu sau hôm nay vẫn tính lấp ghế
def test_payment_and_cancel_increase(client,db,users,showtime,auth_headers,ahead):
    showtime.start_time=datetime.now()+ahead; db.commit()
    headers=auth_headers["admin"]
    before=client.get("/api/admin/dashboard",headers=headers).json()
    b=client.post("/api/bookings",headers=auth_headers["user"],json={"showtime_id":showtime.id,"seats":["A1","A2"]}).json()
    assert client.post(f'/api/admin/bookings/{b["id"]}/confirm',headers=headers).status_code==200
    after=client.get("/api/admin/dashboard",headers=headers).json()
    assert after["revenue"]-before["revenue"]==160000
    assert after["paid_tickets"]-before["paid_tickets"]==1
    assert after["seats_sold"]-before["seats_sold"]==2
    assert after["movies"][0]["occupancy"]-before["movies"][0]["occupancy"]==pytest.approx(2/96)
    held=client.post("/api/bookings",headers=auth_headers["user"],json={"showtime_id":showtime.id,"seats":["A3"]}).json()
    assert client.delete(f'/api/bookings/{held["id"]}',headers=auth_headers["user"]).status_code==200
    assert client.get("/api/admin/dashboard",headers=headers).json()["revenue"]==after["revenue"]

def test_empty_dashboard(client, auth_headers):
    d=client.get('/api/admin/dashboard?days=7',headers=auth_headers['admin']).json()
    assert d['movies']==[] and len(d['daily'])==7
    for key in ['revenue','paid_tickets','pending_tickets','cancelled_tickets','seats_sold','rating_avg','rating_count']:
        assert d[key]==0
    assert all(r['revenue']==r['tickets']==0 for r in d['daily'])

def test_dashboard_query_count_does_not_scale_with_tickets(client,db,users,showtime,auth_headers):
    from sqlalchemy import event
    counts=[]
    def capture(*args): counts.append(1)
    event.listen(db.bind,'before_cursor_execute',capture)
    try:
        client.get('/api/admin/dashboard',headers=auth_headers['admin']); baseline=len(counts)
        for i in range(20): booking(db,users,showtime,seat=f'{"AB"[i//12]}{i%12+1}')
        counts.clear()
        response=client.get('/api/admin/dashboard',headers=auth_headers['admin'])
        assert response.status_code==200 and response.json()['paid_tickets']==20
        assert len(counts)<=baseline+1
    finally: event.remove(db.bind,'before_cursor_execute',capture)
