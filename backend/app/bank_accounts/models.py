"""Bank account and debit card ORM entities."""

from __future__ import annotations

from enum import StrEnum
from uuid import UUID

from sqlalchemy import Boolean, Float, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.database.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class BankAccountStatus(StrEnum):
    """Lifecycle state of a bank account or debit card."""

    ACTIVE = "ACTIVE"
    CLOSED = "CLOSED"
    DORMANT = "DORMANT"


class AccountType(StrEnum):
    """Kind of deposit account."""

    SAVINGS = "SAVINGS"
    CURRENT = "CURRENT"
    SALARY = "SALARY"


class BankAccount(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A deposit account that owns one or more debit-card variants.

    A single account can carry several debit cards (for example a primary Visa debit plus an add-on
    RuPay debit, or cards issued to joint holders). Each debit card keeps its own network and reward
    format, while the balance and account identity live here on the account.
    """

    __tablename__ = "bank_accounts"

    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True, nullable=False)
    bank: Mapped[str] = mapped_column(String(40), index=True, nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), default=AccountType.SAVINGS.value, nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    last4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    ifsc: Mapped[str | None] = mapped_column(String(11), nullable=True)
    balance: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default=BankAccountStatus.ACTIVE.value, nullable=False)


class DebitCard(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A debit-card network variant linked to a bank account.

    Variants on the same account share the account's balance and identity; each carries its own
    ``network``, ``reward_format``, and primary flag.
    """

    __tablename__ = "debit_cards"

    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), index=True, nullable=False)
    bank_account_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("bank_accounts.id"), index=True, nullable=False)
    card_name: Mapped[str] = mapped_column(String(200), nullable=False)
    last4: Mapped[str] = mapped_column(String(4), nullable=False)
    network: Mapped[str | None] = mapped_column(String(20), nullable=True)
    reward_format: Mapped[str | None] = mapped_column(String(40), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean(create_constraint=False), default=False, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=BankAccountStatus.ACTIVE.value, nullable=False)
