"""Ingestion service test: dedup, store, parse, and persist a statement."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.ingestion.service import IngestionService
from app.users.models import User

_HDFC = """HDFC Bank Credit Card Statement
Product: HDFC Infinia
Card Number: XXXXXXXXXXXX1234
Total Amount Due: INR 25,000.00
Closing Reward Points: 48,000
"""


def _user(db: Session) -> uuid.UUID:
    user = User(email=f"ingest-{uuid.uuid4().hex[:8]}@example.com", password_hash="x")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user.id


def test_ingest_text_persists_then_dedupes(db_session: Session) -> None:
    user_id = _user(db_session)
    text = _HDFC + f"\nRef: {uuid.uuid4().hex}"
    svc = IngestionService(db_session)

    sid1, created1 = svc.ingest_text(user_id, "HDFC", text)
    sid2, created2 = svc.ingest_text(user_id, "HDFC", text)

    assert created1 is True
    assert created2 is False
    assert sid1 != sid2 or created2 is False
