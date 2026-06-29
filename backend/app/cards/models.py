"""Card portfolio ORM entity."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class CardStatus(StrEnum):
    """Lifecycle state of a card in the user's portfolio."""

    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    BLOCKED = "BLOCKED"


class CardAccount(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A billing account owning one or more companion card variants that share one statement and due.

    Companion variants (for example ICICI MakeMyTrip Mastercard + RuPay, or an Amex + Mastercard duo)
    bill on a single account: one statement date, one total due, one minimum due, one credit limit, and
    a single payment settles them all. Each variant keeps its own features and reward format on Card.
    """

    __tablename__ = "card_accounts"

    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True, nullable=False)
    bank: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    last4_primary: Mapped[str | None] = mapped_column(String(4), nullable=True)
    credit_limit: Mapped[float | None] = mapped_column(Float, nullable=True)
    statement_day: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=CardStatus.ACTIVE.value, nullable=False)


class Card(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A credit-card network variant held by a user, optionally matched to a registry entry.

    Variants that share a billing account reference the same ``account_id``; each variant carries its
    own ``network``, ``reward_format``, and registry features.
    """

    __tablename__ = "cards"

    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True, nullable=False)
    account_id: Mapped[UUID | None] = mapped_column(Uuid, ForeignKey("card_accounts.id"), index=True, nullable=True)
    bank: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    card_name: Mapped[str] = mapped_column(String(200), nullable=False)
    last4: Mapped[str] = mapped_column(String(4), nullable=False)
    network: Mapped[str | None] = mapped_column(String(20), nullable=True)
    registry_key: Mapped[str | None] = mapped_column(String(120), nullable=True)
    reward_format: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean(create_constraint=False), default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=CardStatus.ACTIVE.value, nullable=False)
