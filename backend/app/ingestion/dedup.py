"""Content-addressed dedup: a statement's SHA-256 is its identity, so re-ingests are detected."""

from __future__ import annotations

import hashlib


def content_hash(content: bytes) -> str:
    """Return the SHA-256 hex digest used to dedupe an ingested document."""
    return hashlib.sha256(content).hexdigest()
