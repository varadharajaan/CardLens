"""Statement intelligence endpoint tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

_UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"
_STATEMENT = {
    "bank": "HDFC",
    "card_name": "HDFC Infinia",
    "last4": "1234",
    "due_date": "2026-02-15",
    "total_due": 25000.0,
    "minimum_due": 1250.0,
    "reward_points_closing": 48000,
    "reward_parse_status": "FOUND",
    "reward_confidence": 0.95,
}


def _auth(client: TestClient, email: str = "stmt@example.com") -> dict[str, str]:
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Sup3rSecret!", "full_name": "Stmt"},
    )
    return {"Authorization": f"Bearer {registration.json()['access_token']}"}


def test_record_and_get_statement(client: TestClient) -> None:
    headers = _auth(client)

    created = client.post("/api/v1/statements", json=_STATEMENT, headers=headers)
    statement_id = created.json()["id"]
    fetched = client.get(f"/api/v1/statements/{statement_id}", headers=headers)
    listed = client.get("/api/v1/statements", headers=headers)

    assert created.status_code == 201
    assert created.json()["reward_parse_status"] == "FOUND"
    assert fetched.status_code == 200
    assert fetched.json()["total_due"] == 25000.0
    assert listed.json()["total"] == 1


def test_statement_defaults_reward_to_not_found(client: TestClient) -> None:
    headers = _auth(client, "stmt2@example.com")

    created = client.post(
        "/api/v1/statements",
        json={"bank": "SBI", "card_name": "SBI Cashback", "last4": "5678"},
        headers=headers,
    )

    assert created.status_code == 201
    assert created.json()["reward_parse_status"] == "NOT_FOUND"


def test_statements_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/statements")

    assert response.status_code == 401
    assert response.json()["errorCode"] == "UNAUTHENTICATED"


def test_get_statement_404_for_unknown(client: TestClient) -> None:
    headers = _auth(client, "stmt3@example.com")

    response = client.get(f"/api/v1/statements/{_UNKNOWN_ID}", headers=headers)

    assert response.status_code == 404
    assert response.json()["errorCode"] == "NOT_FOUND"
