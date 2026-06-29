"""Gmail onboarding and scan endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def _auth(client: TestClient, email: str = "mail@example.com") -> dict[str, str]:
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Sup3rSecret!", "full_name": "Mail"},
    )
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def test_mail_connect_status_and_scan_dry_run(client: TestClient) -> None:
    headers = _auth(client)

    connected = client.post("/api/v1/mail/accounts/connect", headers=headers)
    status = client.get("/api/v1/mail/accounts", headers=headers)
    scan = client.post("/api/v1/ingestion/scan", headers=headers)
    statements = client.get("/api/v1/statements", headers=headers)

    assert connected.status_code == 200
    assert connected.json()["dry_run"] is True
    assert status.status_code == 200
    assert status.json()["status"] == "CONNECTED"
    assert scan.status_code == 200
    assert scan.json()["scanned"] == 1
    assert scan.json()["statements_ingested"] in {0, 1}
    assert statements.status_code == 200
    assert statements.json()["total"] >= 1


def test_mail_requires_auth(client: TestClient) -> None:
    assert client.post("/api/v1/mail/accounts/connect").status_code == 401
    assert client.post("/api/v1/ingestion/scan").status_code == 401
