"""User business logic. Services accept and return DTOs or entities to other services, never to HTTP."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.shared.errors.exceptions import ConflictError, NotFoundError
from app.shared.logging.context import get_logger
from app.shared.security.passwords import hash_password
from app.users.models import User, UserStatus
from app.users.repository import UserRepository
from app.users.schemas import UserCreate

_logger = get_logger("cardlens.users")


class UserService:
    """Coordinates user creation and lookup with validation and password hashing."""

    def __init__(self, db: Session) -> None:
        self._repo = UserRepository(db)

    def create_user(self, data: UserCreate) -> User:
        """Create a user, enforcing unique email and hashing the password."""
        if self._repo.get_by_email(data.email) is not None:
            raise ConflictError("A user with this email already exists.")
        user = User(
            email=str(data.email).lower(),
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            status=UserStatus.ACTIVE.value,
        )
        created = self._repo.add(user)
        _logger.info("user.created", user_id=str(created.id))
        return created

    def get_user(self, user_id: UUID) -> User:
        """Return the user or raise :class:`NotFoundError`."""
        user = self._repo.get(user_id)
        if user is None:
            raise NotFoundError("User not found.")
        return user

    def get_by_email(self, email: str) -> User | None:
        """Return the user with the given email, or None."""
        return self._repo.get_by_email(email)
