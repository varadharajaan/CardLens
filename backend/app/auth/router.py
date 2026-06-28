"""Authentication HTTP endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.schemas import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.auth.service import AuthService
from app.shared.constants.api_paths import ApiPaths
from app.shared.database.session import get_db

router = APIRouter(prefix=ApiPaths.AUTH, tags=["auth"])


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    """Provide a request-scoped :class:`AuthService`."""
    return AuthService(db)


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
def register(body: RegisterRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Create an account and return an access/refresh token pair."""
    return service.register(body)


@router.post("/login", response_model=TokenResponse, summary="Authenticate and receive tokens")
def login(body: LoginRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Authenticate with email and password and return an access/refresh token pair."""
    return service.login(body)


@router.post("/refresh", response_model=TokenResponse, summary="Rotate the refresh token")
def refresh(body: RefreshRequest, service: AuthService = Depends(get_auth_service)) -> TokenResponse:
    """Exchange a valid refresh token for a new token pair, revoking the presented token."""
    return service.refresh(body.refresh_token)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoke a refresh token",
)
def logout(body: RefreshRequest, service: AuthService = Depends(get_auth_service)) -> None:
    """Revoke the presented refresh token."""
    service.logout(body.refresh_token)
