"""Centralized typed application configuration.

All runtime configuration flows through the :class:`Settings` object. Nothing in the codebase reads
``os.environ`` directly and no urls, ports, paths, or secrets are hardcoded at class level. Domain
data that evolves (bank names, password rules, reward values) lives in external data files, not here.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve key directories relative to this file so configuration is independent of the working dir.
# config.py lives at backend/app/config.py -> parents[1] = backend/, parents[2] = repo root.
_BACKEND_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Strongly typed application settings sourced from environment and the repo-root ``.env`` file."""

    model_config = SettingsConfigDict(
        env_prefix="CARDLENS_",
        env_file=str(_REPO_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- App ---
    env: str = "local"
    debug: bool = True
    app_name: str = "CardLens"
    api_prefix: str = "/api/v1"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:3000"

    # --- Database ---
    database_url: str = "sqlite:///./cardlens.db"

    # --- Security ---
    jwt_secret: str = "change-me-in-non-local"  # noqa: S105 - non-secret default; real value via env
    jwt_algorithm: str = "HS256"
    access_token_ttl_minutes: int = 30
    refresh_token_ttl_days: int = 14
    token_encryption_key: str = ""

    # --- Logging ---
    log_level: str = "DEBUG"
    log_dir: Path = _REPO_ROOT / "logs" / "local"
    log_max_bytes: int = 10 * 1024 * 1024
    log_backup_count: int = 5
    log_json: bool = True

    # --- Ingestion / scheduler ---
    scheduler_enabled: bool = False
    scan_interval_hours: int = 6
    scan_lookback_hours: int = 24
    gmail_dry_run: bool = True

    # --- Google OAuth ---
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/v1/mail/accounts/callback"

    # --- Azure ---
    azure_blob_connection_string: str = ""
    azure_blob_container: str = "cardlens-statements"
    azure_keyvault_url: str = ""
    azure_docintel_endpoint: str = ""
    azure_docintel_key: str = ""
    azure_appinsights_connection_string: str = ""

    # --- Document vault ---
    document_vault_enabled: bool = False
    retain_raw_pdf: bool = False

    # --- Externalized config data locations ---
    config_dir: Path = _BACKEND_DIR / "app" / "shared" / "config" / "data"
    card_registry_dir: Path = _REPO_ROOT / "card_registry"

    @field_validator("log_dir", "config_dir", "card_registry_dir", mode="before")
    @classmethod
    def _expand_path(cls, value: object) -> object:
        """Allow relative path overrides to be resolved against the repo root."""
        if isinstance(value, str) and value and not Path(value).is_absolute():
            return _REPO_ROOT / value
        return value

    @property
    def cors_origin_list(self) -> list[str]:
        """CORS origins parsed from the comma-separated ``CARDLENS_CORS_ORIGINS`` value."""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        """True when the configured database is SQLite (affects engine connect args)."""
        return self.database_url.startswith("sqlite")

    @property
    def is_local(self) -> bool:
        """True for the local development environment."""
        return self.env.lower() == "local"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""
    return Settings()


settings = get_settings()
