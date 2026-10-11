from sqlalchemy import func, select

from app.models import BookingSeat
from app.seats import ROWS, VIP_ROWS, VIP_SURCHARGE, is_valid_seat, seat_price


def test_booking_duplicate_seat_and_vip_price(client, auth_headers, showtime, db):
    first = client.post("/api/bookings", headers=auth_headers["user"],
                        json={"showtime_id": showtime.id, "seats": ["A1", "F1"]})
    assert first.status_code == 201
    assert first.json()["total"] == showtime.price * 2 + 20_000

    duplicate = client.post("/api/bookings", headers=auth_headers["admin"],
                            json={"showtime_id": showtime.id, "seats": ["A1"]})
    assert duplicate.status_code == 409
    count = db.scalar(select(func.count()).select_from(BookingSeat).where(
        BookingSeat.showtime_id == showtime.id, BookingSeat.seat_code == "A1"
    ))
    assert count == 1


def test_booking_rejects_too_many_and_invalid_seats(client, auth_headers, showtime):
    too_many = [f"A{i}" for i in range(1, 10)]
    assert client.post("/api/bookings", headers=auth_headers["user"],
                       json={"showtime_id": showtime.id, "seats": too_many}).status_code == 400
    assert client.post("/api/bookings", headers=auth_headers["user"],
                       json={"showtime_id": showtime.id, "seats": ["I1"]}).status_code == 400


def test_seat_map_and_vip_rules():
    for row in ROWS:
        for column in range(1, 13):
            code = f"{row}{column}"
            assert is_valid_seat(code)
            expected = 80_000 + (VIP_SURCHARGE if row in VIP_ROWS else 0)
            assert seat_price(code, 80_000) == expected
    for code in ("A0", "A13", "I1", "a1", "F01"):
        assert not is_valid_seat(code)


def test_cannot_book_showtime_for_ended_movie(client, auth_headers, showtime, movie, db):
    movie.status = "ended"
    db.commit()
    response = client.post("/api/bookings", headers=auth_headers["user"],
                           json={"showtime_id": showtime.id, "seats": ["A1"]})
    assert response.status_code == 400
    assert "đã chiếu xong" in response.json()["detail"]
