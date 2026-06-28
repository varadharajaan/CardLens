"""Authentication dependencies shared across feature modules.

These decode the bearer token and expose the caller's claims and id without importing any feature
module, keeping the shared layer free of feature dependencies. The users module builds the richer
``get_current_user`` (which loads the entity) on top of :func:`get_current_user_id`.
"""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.shared.errors.exceptions import AuthenticationError
from app.shared.security.tokens import decode_token

bearer_scheme = HTTPBearer(auto_error=False)

_ACCESS = "access"


def get_current_claims(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> dict:
    """Return the verified claims for the current request's access token."""
    if credentials is None or not credentials.credentials:
        raise AuthenticationError("Missing bearer token.")
    claims = decode_token(credentials.credentials)
    if claims.get("type") != _ACCESS:
        raise AuthenticationError("Expected an access token.")
    return claims


def get_current_user_id(claims: dict = Depends(get_current_claims)) -> UUID:
    """Return the authenticated user's id parsed from the token subject."""
    subject = claims.get("sub")
    if not subject:
        raise AuthenticationError("Token is missing a subject.")
    try:
        return UUID(str(subject))
    except ValueError as exc:
        raise AuthenticationError("Token subject is not a valid identifier.") from exc
