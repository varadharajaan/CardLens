"""HTTP header name constants."""

from __future__ import annotations


class HeaderNames:
    """Canonical HTTP header names used across the application."""

    REQUEST_ID = "X-Request-Id"
    CORRELATION_ID = "X-Correlation-ID"
    IDEMPOTENCY_KEY = "Idempotency-Key"

    def __init__(self) -> None:  # pragma: no cover - constants holder
        raise RuntimeError("HeaderNames is a constants holder and must not be instantiated.")
