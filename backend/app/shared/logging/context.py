"""Logging context helpers backed by structlog context variables.

Context bound here (request id, user id, ingestion/parser run ids) is automatically merged into every
log line emitted within the same execution context, without threading the values through call sites.
"""

from __future__ import annotations

from typing import Any

import structlog


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """Return a structlog logger, optionally named (use dotted names like ``cardlens.parser``)."""
    return structlog.get_logger(name) if name else structlog.get_logger()


def bind_log_context(**fields: Any) -> None:
    """Bind non-null fields into the current logging context.

    Keys should come from :class:`app.shared.constants.log_fields.LogFields`.
    """
    present = {key: value for key, value in fields.items() if value is not None}
    if present:
        structlog.contextvars.bind_contextvars(**present)


def clear_log_context() -> None:
    """Clear all fields from the current logging context (call at the end of a request or job)."""
    structlog.contextvars.clear_contextvars()
