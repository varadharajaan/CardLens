"""Dashboard aggregation tests: overview, rewards, milestones, anomalies, and no double-counting."""

from __future__ import annotations

from datetime import date, timedelta

from fastapi.testclient import TestClient


def _auth(client: TestClient, email: str) -> dict[str, str]:
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Sup3rSecret!", "full_name": "Dash"},
    )
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def _seed(client: TestClient, headers: dict[str, str]) -> dict[str, str]:
    """Seed a companion account (two variant cards) plus a standalone card, each with statements.

    The two companion variants receive their own per-card statements so the test proves the dashboard
    collapses them onto one billing group (no double-counting) by resolving each card's account.
    """
    account = client.post(
        "/api/v1/card-accounts",
        json={
            "bank": "ICICI",
            "display_name": "ICICI MakeMyTrip",
            "credit_limit": 200000,
            "statement_day": 5,
        },
        headers=headers,
    ).json()
    master = client.post(
        "/api/v1/cards",
        json={
            "bank": "ICICI",
            "card_name": "MMT Mastercard",
            "last4": "9012",
            "network": "MASTERCARD",
            "account_id": account["id"],
            "is_primary": True,
        },
        headers=headers,
    ).json()
    rupay = client.post(
        "/api/v1/cards",
        json={
            "bank": "ICICI",
            "card_name": "MMT RuPay",
            "last4": "3456",
            "network": "RUPAY",
            "account_id": account["id"],
        },
        headers=headers,
    ).json()
    standalone = client.post(
        "/api/v1/cards",
        json={"bank": "AXIS", "card_name": "Axis Atlas", "last4": "1111"},
        headers=headers,
    ).json()
    due_soon = (date.today() + timedelta(days=3)).isoformat()
    # Earlier per-card statement on the Mastercard variant.
    client.post(
        "/api/v1/statements",
        json={
            "card_id": master["id"],
            "bank": "ICICI",
            "card_name": "MMT Mastercard",
            "last4": "9012",
            "statement_date": "2026-05-01",
            "total_due": 8000,
            "reward_points_closing": 30000,
            "reward_type": "REWARD_POINTS",
            "reward_parse_status": "FOUND",
        },
        headers=headers,
    )
    # Later per-card statement on the RuPay variant (same account -> should win, not add).
    client.post(
        "/api/v1/statements",
        json={
            "card_id": rupay["id"],
            "bank": "ICICI",
            "card_name": "MMT RuPay",
            "last4": "3456",
            "statement_date": "2026-06-01",
            "due_date": due_soon,
            "total_due": 9000,
            "minimum_due": 900,
            "reward_points_closing": 50000,
            "reward_type": "REWARD_POINTS",
            "reward_parse_status": "FOUND",
        },
        headers=headers,
    )
    # Standalone card statement (a separate billing group, cashback rewards).
    client.post(
        "/api/v1/statements",
        json={
            "card_id": standalone["id"],
            "bank": "AXIS",
            "card_name": "Axis Atlas",
            "last4": "1111",
            "statement_date": "2026-06-02",
            "total_due": 2000,
            "cashback_earned": 500,
            "reward_type": "CASHBACK",
            "reward_parse_status": "FOUND",
        },
        headers=headers,
    )
    return {"account_id": account["id"], "due_soon": due_soon}


def test_overview_aggregates_without_double_counting(client: TestClient) -> None:
    headers = _auth(client, "dash-overview@example.com")
    seed = _seed(client, headers)

    overview = client.get("/api/v1/dashboard/overview", headers=headers)

    assert overview.status_code == 200
    b = overview.json()
    # Companion variants collapse to one billing group; the standalone card is the second.
    assert b["billing_groups"] == 2
    assert b["counts"]["cards"] == 3
    assert b["counts"]["card_accounts"] == 1
    # Latest companion statement (9000) wins over the earlier one (8000), plus standalone 2000.
    assert b["total_outstanding_due"] == 11000.0
    assert b["total_reward_points"] == 50000
    assert b["total_cashback"] == 500.0
    assert b["nearest_due_date"] == seed["due_soon"]


def test_rewards_summary_breaks_down_by_format(client: TestClient) -> None:
    headers = _auth(client, "dash-rewards@example.com")
    _seed(client, headers)

    res = client.get("/api/v1/rewards/summary", headers=headers)

    assert res.status_code == 200
    b = res.json()
    assert b["total_reward_points"] == 50000
    assert b["total_cashback"] == 500.0
    formats = {f["reward_format"]: f for f in b["by_format"]}
    assert formats["REWARD_POINTS"]["reward_points"] == 50000
    assert formats["CASHBACK"]["cashback"] == 500.0
    assert b["estimated_value_inr"] > 0


def test_milestones_track_progress(client: TestClient) -> None:
    headers = _auth(client, "dash-milestones@example.com")
    _seed(client, headers)

    res = client.get("/api/v1/milestones", headers=headers)

    assert res.status_code == 200
    items = {m["key"]: m for m in res.json()["items"]}
    assert items["rp_50k"]["achieved"] is True
    assert items["rp_50k"]["progress_pct"] == 100.0
    assert items["rp_100k"]["achieved"] is False
    assert items["rp_100k"]["progress_pct"] == 50.0


def test_anomalies_flags_due_soon(client: TestClient) -> None:
    headers = _auth(client, "dash-anomalies@example.com")
    _seed(client, headers)

    res = client.get("/api/v1/anomalies", headers=headers)

    assert res.status_code == 200
    rules = {a["rule"] for a in res.json()["items"]}
    assert "DUE_SOON" in rules


def test_dashboard_requires_authentication(client: TestClient) -> None:
    assert client.get("/api/v1/dashboard/overview").status_code == 401
