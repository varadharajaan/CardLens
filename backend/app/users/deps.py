"""User-related FastAPI dependencies, including the authenticated-user resolver."""

from __future__ import annotations

from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.shared.constants.log_fields import LogFields
from app.shared.database.session import get_db
from app.shared.logging.context import bind_log_context
from app.shared.security.deps import get_current_user_id
from app.users.models import User
from app.users.service import UserService


def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """Provide a request-scoped :class:`UserService`."""
    return UserService(db)


def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> User:
    """Resolve and return the authenticated user, binding the user id into the log context."""
    bind_log_context(**{LogFields.USER_ID: str(user_id)})
    return service.get_user(user_id)
