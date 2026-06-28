"""Closed set of machine-readable error codes returned in RFC 7807 problem responses."""

from __future__ import annotations

from enum import StrEnum


class ErrorCode(StrEnum):
    """Stable error code identifiers surfaced to API clients.

    Values are part of the public API contract and must not be renamed once released.
    """

    VALIDATION_FAILED = "VALIDATION_FAILED"
    UNAUTHENTICATED = "UNAUTHENTICATED"
    FORBIDDEN = "FORBIDDEN"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT = "CONFLICT"
    RATE_LIMITED = "RATE_LIMITED"
    DEPENDENCY_UNAVAILABLE = "DEPENDENCY_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
