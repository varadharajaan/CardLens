"""Card portfolio and companion-card billing account tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

_UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"
_CARD = {"bank": "HDFC", "card_name": "HDFC Infinia", "last4": "1234", "network": "VISA"}


def _auth(client: TestClient, email: str = "cards@example.com") -> dict[str, str]:
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Sup3rSecret!", "full_name": "Cards"},
    )
    return {"Authorization": f"Bearer {registration.json()['access_token']}"}


def test_add_and_list_card(client: TestClient) -> None:
    headers = _auth(client)

    created = client.post("/api/v1/cards", json=_CARD, headers=headers)
    listed = client.get("/api/v1/cards", headers=headers)

    assert created.status_code == 201
    body = created.json()
    assert body["bank"] == "HDFC"
    assert body["is_primary"] is False
    assert body["account_id"] is None
    assert listed.status_code == 200
    assert listed.json()["total"] == 1


def test_get_card_404_for_unknown(client: TestClient) -> None:
    headers = _auth(client)

    response = client.get(f"/api/v1/cards/{_UNKNOWN_ID}", headers=headers)

    assert response.status_code == 404
    assert response.json()["errorCode"] == "NOT_FOUND"


def test_cards_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/cards")

    assert response.status_code == 401
    assert response.json()["errorCode"] == "UNAUTHENTICATED"


def test_companion_account_groups_variants(client: TestClient) -> None:
    headers = _auth(client, "companion@example.com")

    account = client.post(
        "/api/v1/card-accounts",
        json={
            "bank": "ICICI",
            "display_name": "ICICI MakeMyTrip",
            "last4_primary": "9012",
            "statement_day": 5,
        },
        headers=headers,
    )
    account_id = account.json()["id"]
    master = client.post(
        "/api/v1/cards",
        json={
            "bank": "ICICI",
            "card_name": "MakeMyTrip Mastercard",
            "last4": "9012",
            "network": "MASTERCARD",
            "account_id": account_id,
            "is_primary": True,
            "reward_format": "REWARD_POINTS",
        },
        headers=headers,
    )
    rupay = client.post(
        "/api/v1/cards",
        json={
            "bank": "ICICI",
            "card_name": "MakeMyTrip RuPay",
            "last4": "3456",
            "network": "RUPAY",
            "account_id": account_id,
            "reward_format": "CASHBACK",
        },
        headers=headers,
    )
    detail = client.get(f"/api/v1/card-accounts/{account_id}", headers=headers)

    assert account.status_code == 201
    assert master.status_code == 201
    assert rupay.status_code == 201
    assert detail.status_code == 200
    body = detail.json()
    assert body["account"]["display_name"] == "ICICI MakeMyTrip"
    assert len(body["variants"]) == 2
    assert body["variants"][0]["is_primary"] is True
    assert {v["network"] for v in body["variants"]} == {"MASTERCARD", "RUPAY"}


def test_card_account_is_isolated_per_user(client: TestClient) -> None:
    owner = _auth(client, "owner@example.com")
    other = _auth(client, "other@example.com")
    account = client.post(
        "/api/v1/card-accounts",
        json={"bank": "AXIS", "display_name": "Axis Atlas"},
        headers=owner,
    )
    account_id = account.json()["id"]

    seen_by_other = client.get(f"/api/v1/card-accounts/{account_id}", headers=other)
    other_list = client.get("/api/v1/card-accounts", headers=other)

    assert account.status_code == 201
    assert seen_by_other.status_code == 404
    assert other_list.json()["total"] == 0
