"""Ingestion dedup and local storage tests."""

from __future__ import annotations

from pathlib import Path

from app.ingestion.dedup import content_hash
from app.ingestion.storage import LocalStorage


def test_content_hash_is_stable_and_unique() -> None:
    assert content_hash(b"abc") == content_hash(b"abc")
    assert content_hash(b"abc") != content_hash(b"abd")
    assert len(content_hash(b"abc")) == 64


def test_local_storage_roundtrip(tmp_path: Path) -> None:
    store = LocalStorage(tmp_path)
    key = "bank/stmt.pdf"
    assert store.exists(key) is False
    store.put(key, b"data")
    assert store.exists(key) is True
    assert store.get(key) == b"data"
