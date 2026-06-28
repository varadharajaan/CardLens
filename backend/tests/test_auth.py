"""Authentication and user-profile flow tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

_EMAIL = "user@example.com"
_PASSWORD = "Sup3rSecret!"


def _register(client: TestClient, email: str = _EMAIL, password: str = _PASSWORD) -> dict:
    return client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )


def test_register_returns_tokens_and_user(client: TestClient) -> None:
    response = _register(client)

    body = response.json()
    assert response.status_code == 201
    assert body["token_type"] == "bearer"
    assert body["access_token"]
    assert body["refresh_token"]
    assert body["user"]["email"] == _EMAIL


def test_register_duplicate_email_conflicts(client: TestClient) -> None:
    _register(client)

    response = _register(client)

    assert response.status_code == 409
    assert response.json()["errorCode"] == "CONFLICT"


def test_login_then_fetch_me(client: TestClient) -> None:
    _register(client)

    login = client.post("/api/v1/auth/login", json={"email": _EMAIL, "password": _PASSWORD})
    token = login.json()["access_token"]
    me = client.get("/api/v1/users/me", headers={"Authorization": f"Bearer {token}"})

    assert login.status_code == 200
    assert me.status_code == 200
    assert me.json()["email"] == _EMAIL


def test_login_wrong_password_is_unauthenticated(client: TestClient) -> None:
    _register(client)

    response = client.post("/api/v1/auth/login", json={"email": _EMAIL, "password": "wrong-pass"})

    assert response.status_code == 401
    assert response.json()["errorCode"] == "UNAUTHENTICATED"


def test_me_requires_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/users/me")

    assert response.status_code == 401
    assert response.json()["errorCode"] == "UNAUTHENTICATED"


def test_refresh_rotates_and_revokes_old_token(client: TestClient) -> None:
    registration = _register(client).json()
    old_refresh = registration["refresh_token"]

    rotated = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    replay = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})

    assert rotated.status_code == 200
    assert rotated.json()["access_token"]
    assert replay.status_code == 401


def test_register_validation_error_shape(client: TestClient) -> None:
    response = client.post("/api/v1/auth/register", json={"email": "not-an-email", "password": "short"})

    body = response.json()
    assert response.status_code == 422
    assert body["errorCode"] == "VALIDATION_FAILED"
    assert isinstance(body["violations"], list)
    assert body["violations"]
