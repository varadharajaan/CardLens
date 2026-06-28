"""Global exception handlers producing RFC 7807 ``application/problem+json`` responses.

Every error response carries a consistent shape: type, title, status, detail, instance, errorCode,
timestamp, requestId, and (for validation failures) a violations array. The request id is echoed from
the correlation context so clients and operators can correlate a failure with its logs.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.shared.constants.error_codes import ErrorCode
from app.shared.constants.headers import HeaderNames
from app.shared.errors.exceptions import ApplicationError
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.errors")
_PROBLEM_MEDIA_TYPE = "application/problem+json"


def _request_id(request: Request) -> str | None:
    return request.headers.get(HeaderNames.REQUEST_ID)


def _problem(
    *,
    request: Request,
    status: int,
    title: str,
    detail: str,
    error_code: ErrorCode,
    violations: list[dict[str, Any]] | None = None,
) -> JSONResponse:
    body: dict[str, Any] = {
        "type": "about:blank",
        "title": title,
        "status": status,
        "detail": detail,
        "instance": str(request.url.path),
        "errorCode": error_code.value,
        "timestamp": datetime.now(UTC).isoformat(),
        "requestId": _request_id(request),
    }
    if violations is not None:
        body["violations"] = violations
    return JSONResponse(status_code=status, content=body, media_type=_PROBLEM_MEDIA_TYPE)


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI application."""

    @app.exception_handler(ApplicationError)
    async def _handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        _logger.warning(
            "application.error",
            error_code=exc.error_code.value,
            status_code=exc.status_code,
            detail=exc.detail,
        )
        return _problem(
            request=request,
            status=exc.status_code,
            title=exc.error_code.value.replace("_", " ").title(),
            detail=exc.detail,
            error_code=exc.error_code,
        )

    @app.exception_handler(RequestValidationError)
    async def _handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        violations = [
            {
                "field": ".".join(str(part) for part in error.get("loc", []) if part != "body"),
                "message": error.get("msg", "invalid value"),
                "type": error.get("type", "value_error"),
            }
            for error in exc.errors()
        ]
        return _problem(
            request=request,
            status=422,
            title="Validation Failed",
            detail="One or more fields failed validation.",
            error_code=ErrorCode.VALIDATION_FAILED,
            violations=violations,
        )

    @app.exception_handler(StarletteHTTPException)
    async def _handle_http_exception(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        code = ErrorCode.NOT_FOUND if exc.status_code == 404 else ErrorCode.INTERNAL_ERROR
        if exc.status_code == 401:
            code = ErrorCode.UNAUTHENTICATED
        elif exc.status_code == 403:
            code = ErrorCode.FORBIDDEN
        return _problem(
            request=request,
            status=exc.status_code,
            title=str(exc.detail) if exc.detail else "Error",
            detail=str(exc.detail) if exc.detail else "Request could not be completed.",
            error_code=code,
        )

    @app.exception_handler(Exception)
    async def _handle_unexpected(request: Request, exc: Exception) -> JSONResponse:
        _logger.exception("unexpected.error", error_type=type(exc).__name__)
        return _problem(
            request=request,
            status=500,
            title="Internal Server Error",
            detail="An unexpected error occurred.",
            error_code=ErrorCode.INTERNAL_ERROR,
        )
