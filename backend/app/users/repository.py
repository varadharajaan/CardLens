"""Persistence access for users. Repositories persist only; business rules live in the service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.users.models import User


class UserRepository:
    """Data-access methods for the :class:`User` entity."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def get(self, user_id: UUID) -> User | None:
        """Return the user with the given id, or None."""
        return self._db.get(User, user_id)

    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email (case-insensitive), or None."""
        stmt = select(User).where(func.lower(User.email) == email.lower())
        return self._db.execute(stmt).scalar_one_or_none()

    def add(self, user: User) -> User:
        """Persist a new user and return it with generated fields populated."""
        self._db.add(user)
        self._db.commit()
        self._db.refresh(user)
        return user

    def list(self, offset: int, limit: int) -> tuple[list[User], int]:
        """Return a page of users and the total count."""
        total = self._db.execute(select(func.count()).select_from(User)).scalar_one()
        rows = (
            self._db.execute(select(User).order_by(User.created_at.desc()).offset(offset).limit(limit)).scalars().all()
        )
        return list(rows), int(total)
