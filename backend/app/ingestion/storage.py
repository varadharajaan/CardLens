"""Blob storage port with a local-filesystem default and an Azure Blob backend when configured.

The pipeline writes raw documents to the store; the bridge/worker read them by key. Azurite or Azure
are selected by a connection string in config; otherwise files land under logs/local for offline runs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from app.config import settings


class StoragePort(Protocol):
    """Minimal blob interface used by the ingestion pipeline."""

    def put(self, key: str, content: bytes) -> str: ...
    def get(self, key: str) -> bytes: ...
    def exists(self, key: str) -> bool: ...


class LocalStorage:
    """Filesystem-backed store under a base directory (default ingestion location)."""

    def __init__(self, base_dir: Path | None = None) -> None:
        self._base = base_dir or Path("logs/local/ingest")
        self._base.mkdir(parents=True, exist_ok=True)

    def put(self, key: str, content: bytes) -> str:
        path = self._base / key
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        return str(path)

    def get(self, key: str) -> bytes:
        return (self._base / key).read_bytes()

    def exists(self, key: str) -> bool:
        return (self._base / key).exists()


def get_storage() -> StoragePort:
    """Return the configured store: Azure Blob when a connection string is set, else local files."""
    conn = settings.azure_blob_connection_string
    if conn:
        from azure.storage.blob import ContainerClient

        container = ContainerClient.from_connection_string(conn, settings.azure_blob_container)

        class _Azure:
            def put(self, key: str, content: bytes) -> str:
                container.upload_blob(name=key, data=content, overwrite=True)
                return key

            def get(self, key: str) -> bytes:
                return container.download_blob(key).readall()

            def exists(self, key: str) -> bool:
                return container.get_blob_client(key).exists()

        return _Azure()
    return LocalStorage()
