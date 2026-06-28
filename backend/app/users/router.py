"""User HTTP endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.shared.constants.api_paths import ApiPaths
from app.users.deps import get_current_user
from app.users.models import User
from app.users.schemas import UserRead

router = APIRouter(prefix=ApiPaths.USERS, tags=["users"])


@router.get(
    "/me",
    response_model=UserRead,
    status_code=status.HTTP_200_OK,
    summary="Get the authenticated user's profile",
)
def get_me(current_user: User = Depends(get_current_user)) -> User:
    """Return the profile of the currently authenticated user."""
    return current_user
