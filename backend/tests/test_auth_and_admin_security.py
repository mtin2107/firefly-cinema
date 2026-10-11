import re
from datetime import datetime, timedelta, timezone

import jwt

from app.config import SECRET_KEY
from app.main import app


def test_register_login_me_and_invalid_tokens(client):
    payload = {"full_name": "Lê Minh", "email": "MINH@example.com", "password": "secret1"}
    registered = client.post("/api/auth/register", json=payload)
    assert registered.status_code == 201
    token = registered.json()["access_token"]
    assert client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"}).status_code == 200
    assert client.post("/api/auth/login", json={"email": "minh@example.com", "password": "secret1"}).status_code == 200
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"}).status_code == 401

    expired = jwt.encode(
        {"sub": str(registered.json()["user"]["id"]),
         "exp": datetime.now(timezone.utc) - timedelta(seconds=1)},
        SECRET_KEY, algorithm="HS256",
    )
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert response.status_code == 401
    assert "hết hạn" in response.json()["detail"]

    malformed = jwt.encode({"sub": "không-phải-id"}, SECRET_KEY, algorithm="HS256")
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {malformed}"})
    assert response.status_code == 401
    assert "không hợp lệ" in response.json()["detail"]


def test_every_admin_endpoint_requires_login_and_admin_role(client, auth_headers):
    admin_routes = [
        route for route in app.routes
        if getattr(route, "path", "").startswith("/api/admin/")
    ]
    assert admin_routes
    checked = set()
    for route in admin_routes:
        path = re.sub(r"\{[^}]+\}", "1", route.path)
        for method in route.methods - {"HEAD", "OPTIONS"}:
            method = method.lower()
            unauthenticated = client.request(method, path, json={})
            regular_user = client.request(method, path, headers=auth_headers["user"], json={})
            assert unauthenticated.status_code == 401, (method, path, unauthenticated.text)
            assert regular_user.status_code == 403, (method, path, regular_user.text)
            checked.add((method, route.path))
    expected = {
        (method.lower(), route.path)
        for route in admin_routes for method in route.methods - {"HEAD", "OPTIONS"}
    }
    assert checked == expected
