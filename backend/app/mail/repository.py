"""Persistence for mail accounts (per-user)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.mail.models import MailAccount


class MailRepository:
    def __init__(self, db: Session) -> None:
        self._db = db

    def get_for_user(self, user_id: UUID) -> MailAccount | None:
        return self._db.execute(
            select(MailAccount).where(MailAccount.user_id == user_id)
        ).scalar_one_or_none()

    def upsert(self, user_id: UUID, **fields: object) -> MailAccount:
        acct = self.get_for_user(user_id)
        if acct is None:
            acct = MailAccount(user_id=user_id)
            self._db.add(acct)
        for key, value in fields.items():
            setattr(acct, key, value)
        self._db.commit()
        self._db.refresh(acct)
        return acct
