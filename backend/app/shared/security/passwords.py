"""Password hashing using Argon2id.

Argon2 is the default per the security gate. Raw passwords are never logged or stored; only the hash
is persisted. ``verify_password`` returns a boolean and never raises on a mismatch.
"""

from __future__ import annotations

from argon2 import PasswordHasher
from argon2.exceptions import Argon2Error

_hasher = PasswordHasher()


def hash_password(raw_password: str) -> str:
    """Return an Argon2id hash for the given raw password."""
    return _hasher.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    """Return True when the raw password matches the stored hash, False otherwise."""
    try:
        return _hasher.verify(hashed_password, raw_password)
    except Argon2Error:
        return False


def needs_rehash(hashed_password: str) -> bool:
    """Return True when the stored hash should be upgraded to current parameters."""
    try:
        return _hasher.check_needs_rehash(hashed_password)
    except Argon2Error:
        return False
