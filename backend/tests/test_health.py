"""Health endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_healthz_returns_ok(client: TestClient) -> None:
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_readyz_reports_database_up(client: TestClient) -> None:
    response = client.get("/readyz")

    body = response.json()
    assert response.status_code == 200
    assert body["status"] == "ready"
    assert body["database"] == "up"


def test_request_id_header_is_echoed(client: TestClient) -> None:
    response = client.get("/healthz", headers={"X-Request-Id": "test-correlation-1"})

    assert response.headers["X-Request-Id"] == "test-correlation-1"
