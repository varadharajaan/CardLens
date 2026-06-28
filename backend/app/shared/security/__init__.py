"""Security primitives: password hashing, JWT tokens, at-rest encryption, and auth dependencies."""

from app.shared.security.crypto import decrypt_text, encrypt_text
from app.shared.security.deps import bearer_scheme, get_current_claims, get_current_user_id
from app.shared.security.passwords import hash_password, verify_password
from app.shared.security.tokens import create_access_token, create_refresh_token, decode_token

__all__ = [
    "bearer_scheme",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
    "decrypt_text",
    "encrypt_text",
    "get_current_claims",
    "get_current_user_id",
    "hash_password",
    "verify_password",
]
