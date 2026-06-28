"""Bank account and debit-card variant tests."""

from __future__ import annotations

from fastapi.testclient import TestClient

_UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"


def _auth(client: TestClient, email: str = "bank@example.com") -> dict[str, str]:
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Sup3rSecret!", "full_name": "Bank"},
    )
    return {"Authorization": f"Bearer {registration.json()['access_token']}"}


def test_create_and_list_bank_account(client: TestClient) -> None:
    headers = _auth(client)

    created = client.post(
        "/api/v1/bank-accounts",
        json={
            "bank": "HDFC",
            "account_type": "SAVINGS",
            "display_name": "HDFC Salary",
            "last4": "4321",
            "balance": 125000.50,
        },
        headers=headers,
    )
    listed = client.get("/api/v1/bank-accounts", headers=headers)

    assert created.status_code == 201
    body = created.json()
    assert body["bank"] == "HDFC"
    assert body["account_type"] == "SAVINGS"
    assert body["balance"] == 125000.50
    assert body["status"] == "ACTIVE"
    assert listed.status_code == 200
    assert listed.json()["total"] == 1


def test_get_bank_account_404_for_unknown(client: TestClient) -> None:
    headers = _auth(client, "bank404@example.com")

    response = client.get(f"/api/v1/bank-accounts/{_UNKNOWN_ID}", headers=headers)

    assert response.status_code == 404
    assert response.json()["errorCode"] == "NOT_FOUND"


def test_bank_accounts_require_authentication(client: TestClient) -> None:
    response = client.get("/api/v1/bank-accounts")

    assert response.status_code == 401
    assert response.json()["errorCode"] == "UNAUTHENTICATED"


def test_bank_account_groups_debit_card_variants(client: TestClient) -> None:
    headers = _auth(client, "debit@example.com")

    account = client.post(
        "/api/v1/bank-accounts",
        json={"bank": "SBI", "display_name": "SBI Savings", "last4": "7788"},
        headers=headers,
    )
    account_id = account.json()["id"]
    primary = client.post(
        "/api/v1/debit-cards",
        json={
            "bank_account_id": account_id,
            "card_name": "SBI Visa Debit",
            "last4": "7788",
            "network": "VISA",
            "is_primary": True,
            "reward_format": "REWARD_POINTS",
        },
        headers=headers,
    )
    addon = client.post(
        "/api/v1/debit-cards",
        json={
            "bank_account_id": account_id,
            "card_name": "SBI RuPay Debit",
            "last4": "5566",
            "network": "RUPAY",
            "reward_format": "CASHBACK",
        },
        headers=headers,
    )
    detail = client.get(f"/api/v1/bank-accounts/{account_id}", headers=headers)

    assert account.status_code == 201
    assert primary.status_code == 201
    assert addon.status_code == 201
    assert detail.status_code == 200
    body = detail.json()
    assert body["account"]["display_name"] == "SBI Savings"
    assert len(body["debit_cards"]) == 2
    assert body["debit_cards"][0]["is_primary"] is True
    assert {c["network"] for c in body["debit_cards"]} == {"VISA", "RUPAY"}


def test_debit_card_cannot_attach_to_another_users_account(client: TestClient) -> None:
    owner = _auth(client, "acc-owner@example.com")
    other = _auth(client, "acc-other@example.com")
    account = client.post(
        "/api/v1/bank-accounts",
        json={"bank": "AXIS", "display_name": "Axis Savings"},
        headers=owner,
    )
    account_id = account.json()["id"]

    attempt = client.post(
        "/api/v1/debit-cards",
        json={"bank_account_id": account_id, "card_name": "Rogue", "last4": "0000"},
        headers=other,
    )
    seen_by_other = client.get(f"/api/v1/bank-accounts/{account_id}", headers=other)

    assert account.status_code == 201
    assert attempt.status_code == 404
    assert attempt.json()["errorCode"] == "NOT_FOUND"
    assert seen_by_other.status_code == 404
