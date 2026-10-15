"""Small in-memory sliding-window limits for a single-process local deployment."""
import threading
import time
from collections import defaultdict, deque
from collections.abc import Hashable

from fastapi import HTTPException


class SlidingWindowRateLimiter:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._events: dict[Hashable, deque[float]] = defaultdict(deque)

    def hit(self, key: Hashable, *, limit: int, seconds: float, message: str) -> None:
        # shortcut: counters reset on restart and are not shared across workers.
        now = time.monotonic()
        with self._lock:
            events = self._events[key]
            while events and now - events[0] >= seconds:
                events.popleft()
            if len(events) >= limit:
                raise HTTPException(429, message)
            events.append(now)

    def clear(self, key: Hashable) -> None:
        with self._lock:
            self._events.pop(key, None)

    def clear_all(self) -> None:
        with self._lock:
            self._events.clear()
