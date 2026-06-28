"""Database access: SQLAlchemy engine, session factory, declarative base, and FastAPI dependency."""

from app.shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.shared.database.session import engine, get_db, session_scope

__all__ = ["Base", "TimestampMixin", "UUIDPrimaryKeyMixin", "engine", "get_db", "session_scope"]
