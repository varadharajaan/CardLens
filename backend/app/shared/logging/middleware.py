"""Request-scoped logging context middleware.

Generates or accepts a request id, binds it (and any authenticated user id) into the logging context,
echoes the request id back in the response header, and emits structured access logs for each request.
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.shared.constants.headers import HeaderNames
from app.shared.constants.log_fields import LogFields
from app.shared.logging.context import bind_log_context, clear_log_context, get_logger

_logger = get_logger("cardlens.http")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Bind a correlation id to every request and produce start/finish access logs."""

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        request_id = request.headers.get(HeaderNames.REQUEST_ID) or str(uuid.uuid4())
        clear_log_context()
        bind_log_context(**{LogFields.REQUEST_ID: request_id})

        started = time.perf_counter()
        _logger.info(
            "request.start",
            method=request.method,
            path=request.url.path,
            client=request.client.host if request.client else None,
        )
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
            _logger.exception("request.error", method=request.method, path=request.url.path, elapsed_ms=elapsed_ms)
            raise
        finally:
            clear_log_context()

        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers[HeaderNames.REQUEST_ID] = request_id
        _logger.info(
            "request.finish",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            elapsed_ms=elapsed_ms,
        )
        return response
