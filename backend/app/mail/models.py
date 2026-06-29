"""Mail account ORM: a user's connected mailbox with encrypted OAuth tokens and scan state."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class MailAccount(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A connected mailbox. Tokens are Fernet-encrypted; raw tokens never persist in clear text."""

    __tablename__ = "mail_accounts"

    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True, nullable=False)
    provider: Mapped[str] = mapped_column(String(20), default="gmail", nullable=False)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING", nullable=False)
    access_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    password_hints_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    scopes: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_scan_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    statements_found: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
