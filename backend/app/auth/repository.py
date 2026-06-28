"""Persistence for revoked refresh tokens."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.models import RevokedToken


class RevokedTokenRepository:
    """Stores and checks revoked refresh-token identifiers (jti)."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def add(self, jti: str, expires_at: datetime) -> None:
        """Record a token id as revoked."""
        self._db.add(RevokedToken(jti=jti, expires_at=expires_at))
        self._db.commit()

    def is_revoked(self, jti: str) -> bool:
        """Return True when the token id has been revoked."""
        stmt = select(RevokedToken).where(RevokedToken.jti == jti)
        return self._db.execute(stmt).scalar_one_or_none() is not None
