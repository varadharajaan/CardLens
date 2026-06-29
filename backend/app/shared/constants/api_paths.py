"""Centralized REST route path literals.

Paths are declared once here and referenced by routers so the API surface is discoverable in a single
place. All paths are mounted under the configured API prefix (default ``/api/v1``).
"""

from __future__ import annotations


class ApiPaths:
    """Route path constants, grouped by module."""

    # Health (mounted at the application root, outside the API prefix).
    HEALTHZ = "/healthz"
    READYZ = "/readyz"

    # Auth
    AUTH = "/auth"
    AUTH_REGISTER = "/auth/register"
    AUTH_LOGIN = "/auth/login"
    AUTH_REFRESH = "/auth/refresh"
    AUTH_LOGOUT = "/auth/logout"

    # Users
    USERS = "/users"
    USERS_ME = "/users/me"

    # Mail accounts / ingestion
    MAIL_ACCOUNTS = "/mail/accounts"
    MAIL_ACCOUNTS_CONNECT = "/mail/accounts/connect"
    MAIL_ACCOUNTS_CALLBACK = "/mail/accounts/callback"
    INGESTION_SCAN = "/ingestion/scan"
    INGESTION_RUNS = "/ingestion/runs"

    # Domain
    STATEMENTS = "/statements"
    PARSERS_PREVIEW = "/parsers/preview"
    PARSERS_PREVIEW_PDF = "/parsers/preview-pdf"
    CARDS = "/cards"
    CARD_ACCOUNTS = "/card-accounts"
    BANK_ACCOUNTS = "/bank-accounts"
    DEBIT_CARDS = "/debit-cards"
    REWARDS_SUMMARY = "/rewards/summary"
    MILESTONES = "/milestones"
    ANOMALIES = "/anomalies"
    REGISTRY_CARDS = "/registry/cards"
    DASHBOARD_OVERVIEW = "/dashboard/overview"
    CORRECTIONS = "/corrections"
    ADMIN_PARSER_FAILURES = "/admin/parser-failures"

    def __init__(self) -> None:  # pragma: no cover - constants holder
        raise RuntimeError("ApiPaths is a constants holder and must not be instantiated.")
