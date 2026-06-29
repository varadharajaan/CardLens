"""Statement intelligence ORM entity.

Captures the structured result of parsing a card/bank statement. Reward extraction is mandatory: every
statement records a ``reward_parse_status`` (FOUND / PARTIAL / NOT_FOUND) with confidence, an optional
reason, and a manual-review flag, so reward outcomes are never silently dropped.
"""

from __future__ import annotations

from datetime import date
from enum import StrEnum
from uuid import UUID

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class RewardParseStatus(StrEnum):
    """Outcome of the mandatory reward-points extraction for a statement."""

    FOUND = "FOUND"
    PARTIAL = "PARTIAL"
    NOT_FOUND = "NOT_FOUND"


class Statement(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A parsed statement with billing, dues, and mandatory reward-extraction fields."""

    __tablename__ = "statements"

    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True, nullable=False)
    account_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("card_accounts.id"), index=True, nullable=True)
    card_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("cards.id"), index=True, nullable=True)

    bank: Mapped[str] = mapped_column(String(40), nullable=False)
    card_name: Mapped[str] = mapped_column(String(200), nullable=False)
    last4: Mapped[str] = mapped_column(String(4), nullable=False)

    statement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    period_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    bill_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, index=True, nullable=True)

    total_due: Mapped[float | None] = mapped_column(Float, nullable=True)
    minimum_due: Mapped[float | None] = mapped_column(Float, nullable=True)

    reward_points_credited: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reward_points_redeemed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reward_points_expired: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reward_points_closing: Mapped[int | None] = mapped_column(Integer, nullable=True)
    cashback_earned: Mapped[float | None] = mapped_column(Float, nullable=True)
    reward_type: Mapped[str | None] = mapped_column(String(40), nullable=True)

    reward_parse_status: Mapped[str] = mapped_column(
        String(12), default=RewardParseStatus.NOT_FOUND.value, nullable=False
    )
    reward_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    reward_parse_reason: Mapped[str | None] = mapped_column(String(200), nullable=True)
    manual_review_flag: Mapped[bool] = mapped_column(Boolean(create_constraint=False), default=False, nullable=False)

    parse_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evidence_snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
