"""Sensitive-data masking utilities and a structlog processor.

Financial data is sensitive. Card numbers are reduced to their last four digits, emails are partially
masked, and any value under a known-sensitive key (token, password, secret, authorization) is redacted.
These helpers are used both by the logging pipeline and at call sites that must log user-adjacent data.
"""

from __future__ import annotations

import re
from typing import Any

_SENSITIVE_KEY_TOKENS = (
    "password",
    "secret",
    "token",
    "authorization",
    "api_key",
    "apikey",
    "client_secret",
    "refresh_token",
    "access_token",
    "encryption_key",
    "pdf_password",
)

_CARD_NUMBER_RE = re.compile(r"\b(?:\d[ -]?){12,15}\d\b")
_REDACTED = "***REDACTED***"


def mask_card_number(value: str) -> str:
    """Return a card number masked to its last four digits (``************1234``)."""
    digits = re.sub(r"\D", "", value)
    if len(digits) < 4:
        return _REDACTED
    return ("*" * (len(digits) - 4)) + digits[-4:]


def mask_email(value: str) -> str:
    """Return an email with the local part partially masked (``v***d@example.com``)."""
    if "@" not in value:
        return _REDACTED
    local, _, domain = value.partition("@")
    if len(local) <= 2:  # noqa: SIM108 - explicit branches read clearer than a nested ternary
        masked_local = local[0] + "*" if local else "*"
    else:
        masked_local = f"{local[0]}***{local[-1]}"
    return f"{masked_local}@{domain}"


def redact(value: Any) -> str:
    """Return a fully redacted placeholder for a sensitive value."""
    return _REDACTED


def _is_sensitive_key(key: str) -> bool:
    lowered = key.lower()
    return any(token in lowered for token in _SENSITIVE_KEY_TOKENS)


def mask_mapping(data: dict[str, Any]) -> dict[str, Any]:
    """Return a shallow copy of ``data`` with sensitive keys redacted and card numbers masked."""
    masked: dict[str, Any] = {}
    for key, value in data.items():
        if _is_sensitive_key(key):
            masked[key] = _REDACTED
        elif isinstance(value, str) and _CARD_NUMBER_RE.search(value):
            masked[key] = _CARD_NUMBER_RE.sub(lambda m: mask_card_number(m.group(0)), value)
        elif isinstance(value, dict):
            masked[key] = mask_mapping(value)
        else:
            masked[key] = value
    return masked


def masking_processor(_logger: Any, _method: str, event_dict: dict[str, Any]) -> dict[str, Any]:
    """structlog processor that masks sensitive keys and card numbers on every event."""
    return mask_mapping(event_dict)
