"""JSON Web Token creation and verification (PyJWT).

Access and refresh tokens are signed with the configured secret and algorithm. Decoding failures are
translated into :class:`AuthenticationError` so they surface as RFC 7807 401 responses.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from app.config import settings
from app.shared.errors.exceptions import AuthenticationError

_ACCESS = "access"
_REFRESH = "refresh"


def _encode(subject: str, token_type: str, ttl: timedelta, extra: dict[str, Any] | None) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + ttl).timestamp()),
        "jti": str(uuid.uuid4()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str, extra_claims: dict[str, Any] | None = None) -> str:
    """Create a short-lived access token for the given subject (typically the user id)."""
    return _encode(subject, _ACCESS, timedelta(minutes=settings.access_token_ttl_minutes), extra_claims)


def create_refresh_token(subject: str) -> str:
    """Create a long-lived refresh token for the given subject."""
    return _encode(subject, _REFRESH, timedelta(days=settings.refresh_token_ttl_days), None)


def decode_token(token: str) -> dict[str, Any]:
    """Decode and verify a token, returning its claims or raising :class:`AuthenticationError`."""
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.ExpiredSignatureError as exc:
        raise AuthenticationError("Token has expired.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthenticationError("Token is invalid.") from exc
