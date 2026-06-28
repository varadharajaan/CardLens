"""Auth request and response schemas (DTOs)."""

from __future__ import annotations

from pydantic import BaseModel, EmailStr, Field

from app.users.schemas import UserRead


class RegisterRequest(BaseModel):
    """Input to create an account."""

    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=200)


class LoginRequest(BaseModel):
    """Input to authenticate with email and password."""

    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class RefreshRequest(BaseModel):
    """Input carrying a refresh token to rotate or revoke."""

    refresh_token: str = Field(min_length=1)


class TokenResponse(BaseModel):
    """Issued token pair plus the authenticated user."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # noqa: S105 - OAuth2 token-type label, not a secret
    user: UserRead
