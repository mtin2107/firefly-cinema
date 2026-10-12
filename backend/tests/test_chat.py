"""T17: all AI calls use a fake client, never the network or real SQLite."""
from datetime import datetime, timedelta
from types import SimpleNamespace

import pytest

from app import chat_assistant
from app.routers import chat
from app.schemas import ChatMessage


def _message(content=None, tool_calls=None):
    return SimpleNamespace(content=content, tool_calls=tool_calls or [])


def _call(name, args, id="tool-1"):
    return SimpleNamespace(
        id=id, function=SimpleNamespace(name=name, arguments=args),
        model_dump=lambda **kwargs: {
            "id": id, "type": "function", "function": {"name": name, "arguments": args},
        },
    )


class FakeAI:
    def __init__(self, messages):
        self.messages = list(messages)
        self.requests = []
        self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))

    def create(self, **kwargs):
        self.requests.append(kwargs)
        assert len(self.requests) <= 4, "More than 3 tool rounds!"
        return SimpleNamespace(choices=[SimpleNamespace(message=self.messages.pop(0))])


@pytest.fixture(autouse=True)
def fresh_limit(monkeypatch):
    chat._usage.clear()
    monkeypatch.setattr(chat, "CHAT_API_KEY", "unit-test-key")


def test_login_required(client):
    assert client.post("/api/chat", json={"messages": [{"role": "user", "content": "Tối nay?"}]}).status_code == 401


@pytest.mark.parametrize("messages", [
    [{"role": "user", "content": "test"}] * 11,
    [{"role": "user", "content": "x" * 501}],
    [{"role": "assistant", "content": "hỏi"}],
    [{"role": "system", "content": "hỏi"}],
    [],
])
def test_invalid_messages(client, auth_headers, messages):
    response = client.post("/api/chat", json={"messages": messages}, headers=auth_headers["user"])
    assert response.status_code == 422
    assert isinstance(response.json()["detail"], str)
    assert "Trường" in response.json()["detail"]


def test_admin_not_allowed(client, auth_headers):
    response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Xin chào"}]}, headers=auth_headers["admin"])
    assert response.status_code == 403


def test_no_key_does_not_disable_health(client, auth_headers, monkeypatch):
    monkeypatch.setattr(chat, "CHAT_API_KEY", "")
    response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Chào"}]}, headers=auth_headers["user"])
    assert response.status_code == 503
    assert response.json() == {"detail": "Trợ lý chưa được bật."}
    health = client.get("/api/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"


def test_get_showtimes_and_links_from_tools(client, db, movie, showtime, auth_headers, monkeypatch):
    ai = FakeAI([
        _message(tool_calls=[_call("get_showtimes", f'{{"movie_id":{movie.id}}}')]),
        _message(f"Phim {movie.title} có suất chiếu và giá vé theo lịch của rạp."),
    ])
    monkeypatch.setattr(chat_assistant, "_create_client", lambda: ai)
    response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Phim thử nghiệm chiếu khi nào?"}]}, headers=auth_headers["user"])
    assert response.status_code == 200
    data = response.json()
    assert data["movies"] == [{"id": movie.id, "title": movie.title}]
    assert "Phim thử nghiệm" in data["reply"]
    assert ai.requests[1]["messages"][-1]["role"] == "tool"
    assert str(showtime.price) in ai.requests[1]["messages"][-1]["content"]


def test_three_rounds_maximum(client, movie, auth_headers, monkeypatch):
    ai = FakeAI([_message(tool_calls=[_call("search_movies", "{}", f"id-{i}")]) for i in range(3)] +
                [_message("Vui lòng xem chi tiết phim trên website.")])
    monkeypatch.setattr(chat_assistant, "_create_client", lambda: ai)
    response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Có phim gì?"}]}, headers=auth_headers["user"])
    assert response.status_code == 200
    assert len(ai.requests) == 4
    assert "tools" not in ai.requests[-1]
    assert len(ai.requests[0]["messages"]) > 1


def test_rate_limit_independent_accounts(client, db, auth_headers, monkeypatch, users):
    monkeypatch.setattr(chat_assistant, "_create_client", lambda: FakeAI([_message("Chào bạn")]))
    headers = auth_headers["user"]
    payload = {"messages": [{"role": "user", "content": "Xin chào"}]}
    for _ in range(5):
        assert client.post("/api/chat", json=payload, headers=headers).status_code == 200
    hit = client.post("/api/chat", json=payload, headers=headers)
    assert hit.status_code == 429
    assert hit.json()["detail"] == "Bạn gửi tin nhắn quá nhanh. Hãy thử lại sau ít phút."
    # Another non-admin account is not throttled.
    from app.models import User
    from app.security import create_token, hash_password
    second = User(full_name="Người dùng 2", email="user2@example.com", role="user", password_hash=hash_password("secret"))
    db.add(second)
    db.commit()
    second_headers = {"Authorization": "Bearer " + create_token(second.id)}
    assert client.post("/api/chat", json=payload, headers=second_headers).status_code == 200


def test_provider_errors_are_sanitized(client, auth_headers, monkeypatch):
    class BadClient:
        def __init__(self):
            self.chat = SimpleNamespace(completions=SimpleNamespace(create=self.create))
        def create(self, **kwargs):
            raise RuntimeError("secret-key and https://provider.example/private")
    monkeypatch.setattr(chat_assistant, "_create_client", BadClient)
    response = client.post("/api/chat", json={"messages": [{"role": "user", "content": "Xin chào"}]}, headers=auth_headers["user"])
    assert response.status_code == 503
    assert response.json() == {"detail": "Trợ lý đang bận, bạn thử lại sau ít phút."}
    assert "secret-key" not in response.text
    assert "provider.example" not in response.text


def test_tools_do_not_write_to_db(db, movie, showtime):
    before = (len(db.new), len(db.dirty), len(db.deleted))
    assert chat_assistant.search_movies(db, keyword="phim thu nghiem")[0]["id"] == movie.id
    assert chat_assistant.get_showtimes(db, movie_id=movie.id)["showtimes"]
    assert chat_assistant.get_price_rules()["vip_surcharge"] > 0
    assert (len(db.new), len(db.dirty), len(db.deleted)) == before
    assert db.get(type(movie), movie.id).title == movie.title


def test_no_movie_links_from_model_only(db):
    ai = FakeAI([_message("Có phim tưởng tượng siêu hot không nằm trong kho dữ liệu.")])
    result = chat_assistant.answer_chat([ChatMessage(role="user", content="Gợi ý")], db, client=ai)
    assert result["movies"] == []
