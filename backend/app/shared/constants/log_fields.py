"""Structured-logging field (MDC-equivalent) key names.

These keys are bound into the logging context and appear on every JSON log line where applicable.
Never use raw string keys at call sites; reference these constants instead.
"""

from __future__ import annotations


class LogFields:
    """Canonical context keys for structured logging."""

    REQUEST_ID = "request_id"
    USER_ID = "user_id"
    INGESTION_RUN_ID = "ingestion_run_id"
    PARSER_RUN_ID = "parser_run_id"
    MAIL_ACCOUNT_ID = "mail_account_id"
    BANK = "bank"
    CARD_LAST4 = "card_last4"

    def __init__(self) -> None:  # pragma: no cover - constants holder
        raise RuntimeError("LogFields is a constants holder and must not be instantiated.")
