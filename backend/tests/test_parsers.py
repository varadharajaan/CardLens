"""Statement parser tests: field extraction, reward classification, profile selection, and errors."""

from __future__ import annotations

from fastapi.testclient import TestClient

_HDFC = """HDFC Bank Credit Card Statement
Product: HDFC Infinia
Card Number: XXXXXXXXXXXX1234
Statement Date: 02-06-2026
Payment Due Date: 22-06-2026
Total Amount Due: INR 25,000.00
Minimum Amount Due: INR 1,250.00
Reward Points Earned: 1,200
Closing Reward Points: 48,000
"""

_ICICI = """ICICI Bank Credit Card Statement
Card No.: XXXXXX3456
Statement Date: 05-06-2026
Due Date: 25-06-2026
Total Amount due: Rs 12,500.00
Minimum Amount due: Rs 625.00
Total PAYBACK Points: 30,000
"""

_HDFC_PARTIAL = """HDFC Bank Credit Card Statement
Card Number: XXXXXXXXXXXX1234
Total Amount Due: INR 5,000.00
Reward Points Earned: 800
"""

_UNKNOWN = """Some Random Bank Statement
Total Due: 100
"""


def _auth(client: TestClient, email: str = "parser@example.com") -> dict[str, str]:
    reg = client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": "Sup3rSecret!", "full_name": "Parser"},
    )
    return {"Authorization": f"Bearer {reg.json()['access_token']}"}


def test_parse_hdfc_statement_found(client: TestClient) -> None:
    headers = _auth(client)

    res = client.post(
        "/api/v1/parsers/preview",
        json={"bank": "HDFC", "text": _HDFC},
        headers=headers,
    )

    assert res.status_code == 200
    b = res.json()
    assert b["bank"] == "HDFC"
    assert b["profile_version"] == 1
    assert b["last4"] == "1234"
    assert b["statement_date"] == "2026-06-02"
    assert b["due_date"] == "2026-06-22"
    assert b["total_due"] == 25000.0
    assert b["minimum_due"] == 1250.0
    assert b["reward_points_closing"] == 48000
    assert b["reward_points_credited"] == 1200
    assert b["reward_type"] == "REWARD_POINTS"
    assert b["reward_parse_status"] == "FOUND"
    assert b["parse_confidence"] == 1.0
    assert b["manual_review_flag"] is False
    assert b["evidence_snippet"]


def test_parse_detects_bank_from_text(client: TestClient) -> None:
    headers = _auth(client, "parser-detect@example.com")

    res = client.post("/api/v1/parsers/preview", json={"text": _ICICI}, headers=headers)

    assert res.status_code == 200
    b = res.json()
    assert b["bank"] == "ICICI"
    assert b["last4"] == "3456"
    assert b["total_due"] == 12500.0
    assert b["reward_points_closing"] == 30000
    assert b["reward_parse_status"] == "FOUND"


def test_parse_partial_reward_flags_manual_review(client: TestClient) -> None:
    headers = _auth(client, "parser-partial@example.com")

    res = client.post(
        "/api/v1/parsers/preview",
        json={"bank": "HDFC", "text": _HDFC_PARTIAL},
        headers=headers,
    )

    assert res.status_code == 200
    b = res.json()
    assert b["reward_parse_status"] == "PARTIAL"
    assert b["reward_points_credited"] == 800
    assert b["reward_points_closing"] is None
    assert b["manual_review_flag"] is True
    assert b["parse_confidence"] < 0.5


def test_parse_unknown_layout_returns_422(client: TestClient) -> None:
    headers = _auth(client, "parser-unknown@example.com")

    res = client.post("/api/v1/parsers/preview", json={"text": _UNKNOWN}, headers=headers)

    assert res.status_code == 422
    assert res.json()["errorCode"] == "VALIDATION_FAILED"


def test_parse_requires_authentication(client: TestClient) -> None:
    res = client.post("/api/v1/parsers/preview", json={"text": _HDFC})

    assert res.status_code == 401
    assert res.json()["errorCode"] == "UNAUTHENTICATED"
