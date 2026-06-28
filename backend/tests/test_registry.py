"""Card registry: schema validation, matching logic, and HTTP endpoint tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from jsonschema.exceptions import ValidationError

from app.registry.loader import RegistryLoader
from app.registry.matcher import best_match

_VALID_ENTRY = {
    "schema_version": "1",
    "key": "test-card",
    "bank": "HDFC",
    "card_name": "Test Premium Card",
    "network": "VISA",
    "version": 1,
    "source_confidence": 0.5,
    "last_verified_at": "2026-01-01",
    "features": {"annual_fee": 1000},
}


class _Candidate:
    """Minimal match candidate exposing the attributes the matcher reads."""

    def __init__(self, bank: str, card_name: str, key: str) -> None:
        self.bank = bank
        self.card_name = card_name
        self.key = key


def _auth_header(client: TestClient) -> dict[str, str]:
    registration = client.post(
        "/api/v1/auth/register",
        json={"email": "registry@example.com", "password": "Sup3rSecret!", "full_name": "Reg"},
    )
    return {"Authorization": f"Bearer {registration.json()['access_token']}"}


def test_loader_validates_all_sample_files() -> None:
    entries = RegistryLoader().load_files()

    keys = {entry.key for entry in entries}

    assert len(entries) >= 4
    assert "axis-magnus" in keys


def test_loader_rejects_invalid_network() -> None:
    invalid = dict(_VALID_ENTRY, network="BITCOIN")

    with pytest.raises(ValidationError):
        RegistryLoader().validate_data(invalid)


def test_matcher_prefers_bank_and_name_overlap() -> None:
    entries = [
        _Candidate("HDFC", "HDFC Infinia", "hdfc-infinia"),
        _Candidate("AXIS", "Axis Magnus", "axis-magnus"),
    ]

    best, score = best_match("HDFC", "Infinia Credit Card", entries)

    assert best is not None
    assert best.key == "hdfc-infinia"
    assert score > 0.5


def test_matcher_no_entries_returns_none() -> None:
    best, score = best_match("HDFC", "Infinia", [])

    assert best is None
    assert score == 0.0


def test_upsert_requires_authentication(client: TestClient) -> None:
    response = client.post("/api/v1/registry/cards", json=_VALID_ENTRY)

    assert response.status_code == 401
    assert response.json()["errorCode"] == "UNAUTHENTICATED"


def test_upsert_then_get_and_list(client: TestClient) -> None:
    headers = _auth_header(client)

    created = client.post("/api/v1/registry/cards", json=_VALID_ENTRY, headers=headers)
    got = client.get("/api/v1/registry/cards/test-card")
    listed = client.get("/api/v1/registry/cards")

    assert created.status_code == 201
    assert created.json()["key"] == "test-card"
    assert got.status_code == 200
    assert got.json()["bank"] == "HDFC"
    assert listed.json()["total"] == 1


def test_upsert_is_idempotent_by_key(client: TestClient) -> None:
    headers = _auth_header(client)

    client.post("/api/v1/registry/cards", json=_VALID_ENTRY, headers=headers)
    second = client.post(
        "/api/v1/registry/cards", json=dict(_VALID_ENTRY, version=2), headers=headers
    )
    listed = client.get("/api/v1/registry/cards")

    assert second.status_code == 201
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["version"] == 2


def test_upsert_invalid_network_returns_422(client: TestClient) -> None:
    headers = _auth_header(client)

    response = client.post(
        "/api/v1/registry/cards", json=dict(_VALID_ENTRY, network="BITCOIN"), headers=headers
    )

    assert response.status_code == 422
    assert response.json()["errorCode"] == "VALIDATION_FAILED"


def test_match_endpoint_finds_upserted_card(client: TestClient) -> None:
    headers = _auth_header(client)
    client.post("/api/v1/registry/cards", json=_VALID_ENTRY, headers=headers)

    response = client.post(
        "/api/v1/registry/cards/match",
        json={"bank": "HDFC", "card_name": "Test Premium Card"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["matched"] is True
    assert body["key"] == "test-card"


def test_get_unknown_key_returns_404(client: TestClient) -> None:
    response = client.get("/api/v1/registry/cards/does-not-exist")

    assert response.status_code == 404
    assert response.json()["errorCode"] == "NOT_FOUND"
