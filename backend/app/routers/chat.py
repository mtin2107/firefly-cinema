"""Authenticated, user-only AI assistance with per-account in-memory quotas."""
import logging
import threading
import time
from collections import defaultdict, deque
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import chat_assistant
from ..config import CHAT_API_KEY, CHAT_RATE_PER_DAY, CHAT_RATE_PER_MINUTE
from ..database import get_db
from ..models import User
from ..schemas import ChatIn, ChatOut
from ..security import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Trợ lý phim"])
_lock = threading.Lock()
_usage = defaultdict(lambda: {"day": "", "daily": 0, "minutes": deque()})
_LIMIT_MESSAGE = "Bạn gửi tin nhắn quá nhanh. Hãy thử lại sau ít phút."
_BUSY_MESSAGE = "Trợ lý đang bận, bạn thử lại sau ít phút."


def _check_quota(user_id: int):
    # shortcut: counters reset on restart and are not shared across workers.
    now = time.monotonic()
    local_date = datetime.now(ZoneInfo("Asia/Ho_Chi_Minh")).date().isoformat()
    with _lock:
        record = _usage[user_id]
        if record["day"] != local_date:
            record["day"] = local_date
            record["daily"] = 0
            record["minutes"].clear()
        minute = record["minutes"]
        while minute and now - minute[0] >= 60:
            minute.popleft()
        if len(minute) >= CHAT_RATE_PER_MINUTE or record["daily"] >= CHAT_RATE_PER_DAY:
            raise HTTPException(429, _LIMIT_MESSAGE)
        minute.append(now)
        record["daily"] += 1


@router.post("/chat", response_model=ChatOut)
def chat(payload: ChatIn, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if user.role == "admin":
        raise HTTPException(403, "Trợ lý chỉ dành cho khách hàng.")
    if not CHAT_API_KEY:
        raise HTTPException(503, "Trợ lý chưa được bật.")
    _check_quota(user.id)
    try:
        return chat_assistant.answer_chat(payload.messages, db)
    except Exception as exc:
        # Do not print provider exception strings: they can contain keys, URLs or prompts.
        logger.warning("Chat provider unavailable (exception class: %s)", type(exc).__name__)
        raise HTTPException(503, _BUSY_MESSAGE) from None
