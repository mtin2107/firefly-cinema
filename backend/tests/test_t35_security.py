"""T35: security headers, giới hạn đăng ký theo IP, giới hạn độ dài mật khẩu."""


def test_security_headers_on_api_responses(client):
    for path in ("/api/health", "/api/khong-ton-tai"):
        res = client.get(path)
        assert res.headers["X-Content-Type-Options"] == "nosniff"
        assert res.headers["X-Frame-Options"] == "DENY"
        assert res.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_register_is_rate_limited_per_ip(client):
    for i in range(10):
        res = client.post("/api/auth/register", json={
            "full_name": "Người thử", "email": f"u{i}@example.com", "password": "secret1"})
        assert res.status_code == 201, res.text
    res = client.post("/api/auth/register", json={
        "full_name": "Người thử", "email": "u10@example.com", "password": "secret1"})
    assert res.status_code == 429
    assert "1 giờ" in res.json()["detail"]


def test_register_validation_error_does_not_use_quota(client):
    for _ in range(12):
        assert client.post("/api/auth/register", json={"email": "sai"}).status_code == 422
    res = client.post("/api/auth/register", json={
        "full_name": "Người thử", "email": "ok@example.com", "password": "secret1"})
    assert res.status_code == 201


def test_overlong_passwords_are_rejected_before_hashing(client, auth_headers):
    long = "a" * 101
    assert client.post("/api/auth/login", json={"email": "user@example.com", "password": long}).status_code == 422
    assert client.post("/api/auth/change-password", headers=auth_headers["user"],
                       json={"current_password": long, "new_password": "secret2"}).status_code == 422
    assert client.post("/api/auth/me/email", headers=auth_headers["user"],
                       json={"current_password": long, "new_email": "moi@example.com"}).status_code == 422
    # Mật khẩu 100 ký tự vẫn đi tới bước so khớp (401 vì sai, không phải 422).
    assert client.post("/api/auth/login", json={"email": "user@example.com", "password": "a" * 100}).status_code == 401
