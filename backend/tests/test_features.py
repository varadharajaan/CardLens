"""Feature catalog contract tests."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_feature_catalog_has_all_prompt_features(client: TestClient) -> None:
    res = client.get("/api/v1/features")

    assert res.status_code == 200
    body = res.json()
    assert len(body["items"]) == 25
    assert body["live"] >= 1
    assert body["mvp"] >= 1
    assert body["framework"] >= 1
    assert {item["slug"] for item in body["items"]} >= {
        "overview-dashboard",
        "card-portfolio",
        "statement-intelligence",
        "subscription-tracker",
        "personal-finance-timeline",
    }


def test_get_one_feature(client: TestClient) -> None:
    res = client.get("/api/v1/features/reward-tracker")

    assert res.status_code == 200
    assert res.json()["title"] == "Reward tracker"


def test_unknown_feature_404(client: TestClient) -> None:
    res = client.get("/api/v1/features/nope")

    assert res.status_code == 404
