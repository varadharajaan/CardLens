"""Domain exception hierarchy.

A single :class:`ApplicationError` root carries an :class:`ErrorCode` and an HTTP status. Feature code
raises these typed exceptions; the global handlers translate them into RFC 7807 problem responses. Code
never swallows exceptions to hide them - unhandled errors propagate to the global handler.
"""

from __future__ import annotations

from app.shared.constants.error_codes import ErrorCode


class ApplicationError(Exception):
    """Base class for all expected, translatable application errors."""

    status_code: int = 500
    error_code: ErrorCode = ErrorCode.INTERNAL_ERROR

    def __init__(
        self,
        detail: str | None = None,
        *,
        error_code: ErrorCode | None = None,
        status_code: int | None = None,
    ) -> None:
        self.detail = detail or self.__class__.__name__
        if error_code is not None:
            self.error_code = error_code
        if status_code is not None:
            self.status_code = status_code
        super().__init__(self.detail)


class DomainValidationError(ApplicationError):
    """A domain-level validation rule was violated."""

    status_code = 422
    error_code = ErrorCode.VALIDATION_FAILED


class AuthenticationError(ApplicationError):
    """The request lacks valid authentication credentials."""

    status_code = 401
    error_code = ErrorCode.UNAUTHENTICATED


class AuthorizationError(ApplicationError):
    """The authenticated principal is not permitted to perform the action."""

    status_code = 403
    error_code = ErrorCode.FORBIDDEN


class NotFoundError(ApplicationError):
    """A requested resource does not exist or is not visible to the caller."""

    status_code = 404
    error_code = ErrorCode.NOT_FOUND


class ConflictError(ApplicationError):
    """The request conflicts with the current state of the resource."""

    status_code = 409
    error_code = ErrorCode.CONFLICT


class DependencyUnavailableError(ApplicationError):
    """A required downstream dependency (database, provider) is unavailable."""

    status_code = 503
    error_code = ErrorCode.DEPENDENCY_UNAVAILABLE
