"""Symmetric encryption for secrets stored at rest (for example, mailbox OAuth refresh tokens).

Uses Fernet (AES-128-CBC + HMAC). The key comes from configuration. When no key is configured in a
local environment, an ephemeral key is generated so the app still boots; this is logged loudly and is
never acceptable outside local development because restarts invalidate previously encrypted values.
"""

from __future__ import annotations

from functools import lru_cache

from cryptography.fernet import Fernet

from app.config import settings
from app.shared.logging.context import get_logger

_logger = get_logger("cardlens.security")


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    key = settings.token_encryption_key.strip()
    if not key:
        if not settings.is_local:
            raise RuntimeError("CARDLENS_TOKEN_ENCRYPTION_KEY must be set outside local environments.")
        generated = Fernet.generate_key()
        _logger.warning(
            "token_encryption.ephemeral_key",
            detail="No CARDLENS_TOKEN_ENCRYPTION_KEY set; using an ephemeral key (local only).",
        )
        return Fernet(generated)
    return Fernet(key.encode("utf-8"))


def encrypt_text(plaintext: str) -> str:
    """Encrypt a UTF-8 string, returning a URL-safe token string."""
    return _fernet().encrypt(plaintext.encode("utf-8")).decode("utf-8")


def decrypt_text(ciphertext: str) -> str:
    """Decrypt a token produced by :func:`encrypt_text` back to its plaintext string."""
    return _fernet().decrypt(ciphertext.encode("utf-8")).decode("utf-8")
