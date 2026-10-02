# Quy tắc sơ đồ ghế — PHẢI giống frontend/src/utils/seats.js
import re

ROWS = "ABCDEFGH"
COLS = 12
VIP_ROWS = "FGH"
VIP_SURCHARGE = 20000
MAX_SEATS_PER_BOOKING = 8
_SEAT_RE = re.compile(rf"^[{ROWS}]([1-9]|1[0-{COLS - 10}])$")


def is_valid_seat(code: str) -> bool:
    return bool(_SEAT_RE.match(code))


def seat_price(code: str, base_price: int) -> int:
    return base_price + (VIP_SURCHARGE if code[0] in VIP_ROWS else 0)
