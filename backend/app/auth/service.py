"""Authentication business logic: credential checks, token issuance, rotation, and revocation."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy.orm import Session

from app.auth.repository import RevokedTokenRepository
from app.auth.schemas import LoginRequest, RegisterRequest, TokenResponse
from app.shared.errors.exceptions import AuthenticationError, AuthorizationError
from app.shared.logging.context import get_logger
from app.shared.security.passwords import verify_password
from app.shared.security.tokens import (
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.users.models import User, UserStatus
from app.users.schemas import UserCreate, UserRead
from app.users.service import UserService

_logger = get_logger("cardlens.auth")

_REFRESH = "refresh"


class AuthService:
    """Coordinates authentication flows over the user and revocation stores."""

    def __init__(self, db: Session) -> None:
        self._users = UserService(db)
        self._revoked = RevokedTokenRepository(db)

    def register(self, data: RegisterRequest) -> TokenResponse:
        """Create an account and return an issued token pair."""
        user = self._users.create_user(UserCreate(email=data.email, password=data.password, full_name=data.full_name))
        _logger.info("auth.registered", user_id=str(user.id))
        return self._issue(user)

    def login(self, data: LoginRequest) -> TokenResponse:
        """Authenticate by email and password and return an issued token pair."""
        user = self._users.get_by_email(str(data.email))
        if user is None or not verify_password(data.password, user.password_hash):
            raise AuthenticationError("Invalid email or password.")
        if user.status != UserStatus.ACTIVE.value:
            raise AuthorizationError("Account is disabled.")
        _logger.info("auth.login", user_id=str(user.id))
        return self._issue(user)

    def refresh(self, refresh_token: str) -> TokenResponse:
        """Validate a refresh token, rotate it, and return a fresh token pair."""
        claims = decode_token(refresh_token)
        if claims.get("type") != _REFRESH:
            raise AuthenticationError("Expected a refresh token.")
        jti = str(claims.get("jti"))
        if self._revoked.is_revoked(jti):
            raise AuthenticationError("Refresh token has been revoked.")
        user = self._users.get_user(UUID(str(claims["sub"])))
        self._revoke(claims)
        _logger.info("auth.refreshed", user_id=str(user.id))
        return self._issue(user)

    def logout(self, refresh_token: str) -> None:
        """Revoke a refresh token. Invalid tokens are treated as already logged out."""
        try:
            claims = decode_token(refresh_token)
        except AuthenticationError:
            return
        if claims.get("type") == _REFRESH:
            self._revoke(claims)

    def _revoke(self, claims: dict) -> None:
        expires_at = datetime.fromtimestamp(int(claims["exp"]), tz=UTC)
        self._revoked.add(str(claims["jti"]), expires_at)

    def _issue(self, user: User) -> TokenResponse:
        access = create_access_token(str(user.id), {"email": user.email})
        refresh = create_refresh_token(str(user.id))
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            user=UserRead.model_validate(user),
        )
