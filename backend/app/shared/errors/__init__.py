"""Application error hierarchy and RFC 7807 problem-response handlers."""

from app.shared.errors.exceptions import (
    ApplicationError,
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    DependencyUnavailableError,
    DomainValidationError,
    NotFoundError,
)
from app.shared.errors.handlers import register_exception_handlers

__all__ = [
    "ApplicationError",
    "AuthenticationError",
    "AuthorizationError",
    "ConflictError",
    "DependencyUnavailableError",
    "DomainValidationError",
    "NotFoundError",
    "register_exception_handlers",
]
